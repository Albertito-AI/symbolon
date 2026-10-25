"""Portable evidence snapshots, checked against a separately trusted digest.

Unsigned local records cannot prove identity, real-world truth or completeness
against a malicious operator who can rewrite the database and its checkpoint.
"""

import hashlib
import hmac
import re
from .contracts import Contract, ContractService
from .ledger import GENESIS_HASH, MAX_AMOUNT, canonical_json, digest, identifier, strict_int
from .verification import content_digest, validate_json_value, verify_invoice


def bundle_digest(bundle):
    validate_json_value(bundle)
    return hashlib.sha256(canonical_json(bundle).encode("utf-8")).hexdigest()


def build_bundle(service, contract_id, output, verification):
    """Snapshot under one transaction; full ledger is for synthetic demos only."""
    with service.ledger._transaction():
        service.ledger.verify_integrity()
        record = service.get(contract_id)
        events = [{"previous_hash": row["previous_hash"], "event_hash": row["event_hash"],
                   "event": row["event"]} for row in service.events(contract_id)]
        bundle = {"bundle_version": "symbolon-evidence-0.1", "environment": "sandbox",
                  "asset": "TEST", "authorship": "unsigned_local_actor_labels",
                  "roles": {"resolver": service.resolver, "settlement": service.settlement_actor},
                  "contract": record, "output": output, "verification": verification,
                  "events": events, "ledger": service.ledger.entries()}
        verify_bundle(bundle, bundle_digest(bundle))
    return bundle


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _verify_journal(entries):
    previous, balances, keys = GENESIS_HASH, {}, set()
    fields = {"journal_id", "operation_key", "source", "destination", "amount_minor",
              "currency", "previous_hash", "entry_hash"}
    _require(isinstance(entries, list), "missing journal")
    for expected_id, row in enumerate(entries, 1):
        _require(isinstance(row, dict) and set(row) == fields, "unexpected journal fields")
        strict_int(row["journal_id"], "journal_id", minimum=1)
        strict_int(row["amount_minor"], "amount_minor", minimum=1)
        _require(row["journal_id"] == expected_id and row["previous_hash"] == previous, "journal sequence mismatch")
        _require(row["currency"] == "TEST" and row["source"] != row["destination"], "invalid journal transfer")
        identifier(row["source"], internal=True)
        identifier(row["destination"], internal=True)
        _require(isinstance(row["operation_key"], str) and row["operation_key"] not in keys, "duplicate journal operation")
        keys.add(row["operation_key"])
        previous = digest({k: v for k, v in row.items() if k != "entry_hash"})
        _require(row["entry_hash"] == previous, "journal hash mismatch")
        for account, amount in ((row["source"], -row["amount_minor"]), (row["destination"], row["amount_minor"])):
            balances[account] = balances.get(account, 0) + amount
            _require(-MAX_AMOUNT <= balances[account] <= MAX_AMOUNT, "journal balance overflow")
            _require(account == "sys:faucet" or balances[account] >= 0, "journal overdraw")
    _require(sum(balances.values()) == 0, "journal does not conserve TEST units")


def _replay_contract(bundle):
    record, events = bundle["contract"], bundle["events"]
    _require(isinstance(record, dict), "contract must be an object")
    t = record["terms"]
    _require(isinstance(t, dict), "contract terms must be an object")
    Contract(**t)
    cid = t["contract_id"]
    _require(cid == record["contract_id"] and digest(t) == record["terms_digest"], "contract terms mismatch")
    roles = bundle["roles"]
    _require(isinstance(roles, dict), "roles must be an object")
    _require(set(roles) == {"resolver", "settlement"}, "unexpected role map")
    identifier(roles["resolver"])
    _require(roles["settlement"] == "settlement-service", "unsupported settlement role")
    _require(len({roles["resolver"], roles["settlement"], t["buyer"], t["provider"], t["verifier"]}) == 5, "roles overlap")
    price_account, bond_account = (ContractService._escrow(cid, part) for part in ("price", "bond"))
    movements = []
    def move(source, dest, amount):
        if amount:
            movements.append((source, dest, amount))
    state, delivered, delivered_at, until = None, None, None, None
    previous, last_time = GENESIS_HASH, 0
    _require(isinstance(events, list) and bool(events), "contract event history is missing")
    for row in events:
        _require(set(row) == {"previous_hash", "event_hash", "event"}, "unexpected event fields")
        event = row["event"]
        _require(isinstance(event, dict), "event must be an object")
        _require(set(event) == {"contract_id", "action", "actor", "at", "details"}, "unexpected event contents")
        _require(event["contract_id"] == cid and row["previous_hash"] == previous, "event chain mismatch")
        previous = digest({"previous_hash": previous, "event": event})
        _require(row["event_hash"] == previous, "event hash mismatch")
        at = strict_int(event["at"], "event time")
        _require(at >= last_time, "event time moved backwards")
        last_time = at
        action, actor, details = event["action"], event["actor"], event["details"]
        _require(isinstance(details, dict), "event details must be an object")
        if action == "accept":
            _require(state is None and actor == "trusted-coordinator" and at < t["delivery_deadline"], "invalid acceptance event")
            _require(details == {"terms_digest": record["terms_digest"]}, "acceptance terms mismatch")
            state = "ACCEPTED"
        elif action == "fund":
            _require(state == "ACCEPTED" and actor == t["buyer"] and at < t["delivery_deadline"], "invalid funding event")
            move(t["buyer"], price_account, t["price_minor"])
            move(t["provider"], bond_account, t["bond_minor"])
            state = "FUNDED"
        elif action == "deliver":
            _require(state == "FUNDED" and actor == t["provider"] and at < t["delivery_deadline"], "invalid delivery event")
            delivered = details["output_sha256"]
            _require(isinstance(delivered, str) and bool(re.fullmatch("[0-9a-f]{64}", delivered)), "invalid output digest")
            delivered_at, until, state = at, at + t["challenge_window_seconds"], "DELIVERED"
        elif action == "verify":
            _require(state == "DELIVERED" and actor == t["verifier"], "invalid verification event")
            passed = delivered == t["accepted_output_sha256"]
            expected = {"method": "exact_sha256", "passed": passed, "output_sha256": delivered}
            _require(canonical_json(details) == canonical_json(expected), "verification event contradicts reference")
            state = "VERIFIED" if passed else "DISPUTED"
            if passed:
                until = at + t["challenge_window_seconds"]
        elif action == "challenge":
            _require(state in {"DELIVERED", "VERIFIED"} and actor == t["buyer"], "invalid challenge event")
            _require(state != "VERIFIED" or at < until, "challenge occurred after its window")
            ContractService._reason(details.get("reason"))
            state = "DISPUTED"
        elif action == "settle":
            _require(state == "VERIFIED" and actor == roles["settlement"] and at >= until, "invalid settlement event")
            move(price_account, t["provider"], t["price_minor"])
            move(bond_account, t["provider"], t["bond_minor"])
            state = "SETTLED"
        elif action == "expire":
            _require(state in {"ACCEPTED", "FUNDED"} and actor == roles["settlement"] and at >= t["delivery_deadline"], "invalid expiry event")
            if state == "FUNDED":
                move(price_account, t["buyer"], t["price_minor"])
                move(bond_account, t["provider"], t["bond_minor"])
            state = "REFUNDED"
        elif action == "resolve":
            _require(state == "DISPUTED" and actor == roles["resolver"], "invalid resolution event")
            ContractService._reason(details.get("reason"))
            for part, account, total, share in (("price", price_account, t["price_minor"], details["buyer_share_bps"]),
                                                 ("bond", bond_account, t["bond_minor"], details["bond_to_buyer_bps"])):
                strict_int(share, "allocation", maximum=10000)
                buyer_amount = total * share // 10000
                _require(details[part + "_buyer_minor"] == buyer_amount and details[part + "_provider_minor"] == total - buyer_amount, "resolution arithmetic mismatch")
                move(account, t["buyer"], buyer_amount)
                move(account, t["provider"], total - buyer_amount)
            state = "RESOLVED"
        else:
            raise ValueError("unknown contract event")
    expected_state = {"state": state, "delivered_sha256": delivered, "delivered_at": delivered_at,
                      "challenge_until": until, "updated_at": last_time}
    _require(all(record.get(k) == v for k, v in expected_state.items()), "materialised state contradicts event history")
    actual = [(r["source"], r["destination"], r["amount_minor"]) for r in bundle["ledger"]
              if r["source"] in {price_account, bond_account} or r["destination"] in {price_account, bond_account}]
    _require(actual == movements, "contract transfers contradict event history")


def verify_bundle(bundle, expected_sha256):
    """Check anchor, journal, event replay, delivery and reproducible invoice checks."""
    required = {"bundle_version", "environment", "asset", "authorship", "roles", "contract",
                "output", "verification", "events", "ledger"}
    _require(isinstance(bundle, dict) and set(bundle) == required, "unexpected or missing bundle fields")
    if not isinstance(expected_sha256, str) or not re.fullmatch("[0-9a-f]{64}", expected_sha256):
        raise ValueError("a separately trusted lowercase SHA-256 checkpoint is required")
    _require(hmac.compare_digest(bundle_digest(bundle), expected_sha256), "bundle checkpoint mismatch")
    _require(bundle.get("bundle_version") == "symbolon-evidence-0.1" and bundle.get("asset") == "TEST"
             and bundle.get("environment") == "sandbox" and bundle.get("authorship") == "unsigned_local_actor_labels",
             "unsupported evidence profile")
    _verify_journal(bundle["ledger"])
    _replay_contract(bundle)
    record = bundle["contract"]
    output_hash = content_digest(bundle["output"])
    _require(output_hash == record["delivered_sha256"], "output does not match delivery")
    computed = verify_invoice(bundle["output"])
    computed["checks"].append({"check": "pinned_reference", "passed": output_hash == record["terms"]["accepted_output_sha256"]})
    computed["passed"] = all(c["passed"] for c in computed["checks"])
    _require(canonical_json(bundle["verification"]) == canonical_json(computed), "verification report is not reproducible")
    return {"checkpoint_matches": True, "output_matches_delivery": True, "event_chain_valid": True,
            "event_state_consistent": True, "ledger_chain_valid": True, "contract_transfers_match": True,
            "invoice_profile_passed": computed["passed"], "contract_state": record["state"],
            "authorship_verified": False, "semantic_correctness_verified": False}

