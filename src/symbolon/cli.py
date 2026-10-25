"""Dependency-free command line examples. Only synthetic, non-redeemable units."""

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys

from .contracts import Contract, ContractService
from .economics import plan_deterrence
from .evidence import build_bundle, bundle_digest, verify_bundle
from .ledger import Ledger
from .specification import SPEC_VERSION, parse_contract
from .verification import content_digest, load_json, verify_invoice


def demo(directory):
    """Run a deterministic accepted invoice fixture and an incorrect delivery."""
    output = Path(directory)
    output.mkdir(parents=True, exist_ok=True)
    names = ["accepted-evidence.json", "accepted-evidence.sha256", "disputed-evidence.json",
             "disputed-evidence.sha256", "demo-summary.json", "example-contract.json"]
    if any((output / name).exists() for name in names):
        raise ValueError("output contains demo files; select a new directory to preserve the existing run")
    ledger = Ledger()
    try:
        service = ContractService(ledger)
        for actor in ("buyer-demo", "provider-demo"):
            ledger.create_account(actor)
            ledger.mint_test_funds(actor, 100000, "faucet-" + actor)
        expected = {"invoice_id": "INV-001", "currency": "TEST",
                    "items": [{"line_id": "line-1", "quantity": 2, "unit_minor": 1500}],
                    "total_minor": 3000}
        delivered = {**expected, "total_minor": 3999}
        now = 1792886400
        summaries = []
        for suffix, value in (("accepted", expected), ("disputed", delivered)):
            cid = "task-" + suffix
            terms = Contract(cid, "buyer-demo", "provider-demo", "verifier-demo",
                             content_digest(expected), 4000, 1500, now + 3600, 60)
            envelope = {"spec_version": SPEC_VERSION, "asset": "TEST",
                        "acceptance_profile": "exact-json-v1", "contract": asdict(terms)}
            parse_contract(envelope)
            service.accept(terms, "accept-" + suffix, now)
            service.fund(cid, "buyer-demo", "fund-" + suffix, now + 1)
            service.deliver(cid, content_digest(value), "provider-demo", "deliver-" + suffix, now + 2)
            checks = verify_invoice(value, expected)
            service.verify(cid, "verifier-demo", "verify-" + suffix, now + 3)
            if suffix == "accepted":
                service.settle(cid, "settlement-service", "settle-" + suffix, now + 63)
            else:
                service.resolve(cid, 10000, 0, "human-resolver", "resolve-" + suffix, now + 64,
                                "Fixture output failed the agreed total; refund price and return bond.")
            bundle = build_bundle(service, cid, value, checks)
            checkpoint = bundle_digest(bundle)
            verified = verify_bundle(bundle, checkpoint)
            (output / (suffix + "-evidence.json")).write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8")
            (output / (suffix + "-evidence.sha256")).write_text(checkpoint + "\n", encoding="ascii")
            if suffix == "accepted":
                (output / "example-contract.json").write_text(json.dumps(envelope, indent=2) + "\n", encoding="utf-8")
            summaries.append({"contract_id": cid, "state": service.get(cid)["state"],
                              "acceptance_checks_passed": checks["passed"],
                              "evidence_sha256": checkpoint, "snapshot_integrity": verified})
        result = {"environment": "local sandbox", "asset": "TEST", "real_money_moved": False,
                  "contracts": summaries, "ledger": ledger.verify_integrity(),
                  "balances_minor": {"buyer-demo": ledger.balance("buyer-demo"),
                                     "provider-demo": ledger.balance("provider-demo")}}
        (output / "demo-summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        return result
    finally:
        ledger.close()


def main(argv=None):
    parser = argparse.ArgumentParser(prog="symbolon", description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("demo", help="run two synthetic contracts and export evidence")
    run.add_argument("--output", default="artifacts/demo")
    verify = commands.add_parser("verify-bundle", help="check a bundle against a separately trusted digest")
    verify.add_argument("bundle")
    verify.add_argument("--expected-sha256", required=True)
    profile = commands.add_parser("verify-invoice", help="validate the small TEST invoice profile")
    profile.add_argument("invoice")
    profile.add_argument("--reference")
    contract = commands.add_parser("validate-contract", help="validate one dated sandbox contract")
    contract.add_argument("contract")
    commands.add_parser("economics", help="reproduce the report's illustrative example")
    args = parser.parse_args(argv)
    try:
        if args.command == "demo":
            result = demo(args.output)
        elif args.command == "verify-bundle":
            result = verify_bundle(load_json(args.bundle), args.expected_sha256)
        elif args.command == "verify-invoice":
            result = verify_invoice(load_json(args.invoice), load_json(args.reference) if args.reference else None)
        elif args.command == "validate-contract":
            result = {"valid": True, "contract": asdict(parse_contract(load_json(args.contract)))}
        else:
            result = {"status": "illustrative_model_only", **plan_deterrence(
                price=40, saved_cost=12, audit_cost=6, annual_capital_rate=0.1,
                lock_days=7, detection=1, false_positive=0, bond_cap=200).to_dict()}
        print(json.dumps(result, indent=2))
        return 1 if result.get("passed") is False else 0
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2

