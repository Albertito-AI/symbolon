"""Independent regression cases for evidence and numerical boundary risks."""

import math
import unittest

from symbolon.contracts import Contract, ContractService
from symbolon.economics import plan_deterrence
from symbolon.evidence import build_bundle, bundle_digest, verify_bundle
from symbolon.ledger import GENESIS_HASH, Ledger, MAX_AMOUNT, digest
from symbolon.verification import content_digest, verify_invoice


OUTPUT = {
    "invoice_id": "INV-1", "currency": "TEST",
    "items": [{"line_id": "a", "quantity": 1, "unit_minor": 400}],
    "total_minor": 400,
}


class AdversarialBoundaryTests(unittest.TestCase):
    def make_delivery(self, buyer_funds=1000):
        ledger = Ledger()
        self.addCleanup(ledger.close)
        ledger.create_account("buyer")
        ledger.create_account("provider")
        ledger.mint_test_funds("buyer", buyer_funds, "seed-buyer")
        ledger.mint_test_funds("provider", 500, "seed-provider")
        service = ContractService(ledger)
        contract = Contract("job", "buyer", "provider", "checker",
                            content_digest(OUTPUT), 400, 150, 100, 10)
        service.accept(contract, "accept", 0)
        service.fund("job", "buyer", "fund", 1)
        service.deliver("job", content_digest(OUTPUT), "provider", "deliver", 2)
        return service

    def test_maximum_supported_ledger_balance_has_serialisable_evidence(self):
        # A valid ledger value must remain valid in its mandatory evidence format.
        service = self.make_delivery(MAX_AMOUNT - 500)
        report = verify_invoice(OUTPUT, expected=OUTPUT)
        bundle = build_bundle(service, "job", OUTPUT, report)
        result = verify_bundle(bundle, bundle_digest(bundle))
        self.assertTrue(result["checkpoint_matches"])

    def test_claimed_settlement_without_verification_and_money_movements_rejected(self):
        service = self.make_delivery()
        service.db.execute("UPDATE contract_state SET state='SETTLED' WHERE contract_id='job'")
        report = verify_invoice(OUTPUT, expected=OUTPUT)
        with self.assertRaises(ValueError):
            bundle = build_bundle(service, "job", OUTPUT, report)
            verify_bundle(bundle, bundle_digest(bundle))

    def test_verification_report_cannot_claim_pass_with_a_failed_check(self):
        service = self.make_delivery()
        service.verify("job", "checker", "verify", 3)
        report = verify_invoice(OUTPUT, expected=OUTPUT)
        report["checks"][0]["passed"] = False
        self.assertTrue(report["passed"])
        with self.assertRaises(ValueError):
            bundle = build_bundle(service, "job", OUTPUT, report)
            verify_bundle(bundle, bundle_digest(bundle))

    def test_deterrence_does_not_return_infinite_bond_from_finite_inputs(self):
        # Either reject the out-of-range model or return a wholly finite plan.
        try:
            plan = plan_deterrence(price=40, saved_cost=12, audit_cost=1e308,
                                   annual_capital_rate=0.1, lock_days=7)
        except ValueError:
            return
        for name, value in plan.to_dict().items():
            if isinstance(value, (float, int)):
                self.assertTrue(math.isfinite(value), name)
        self.assertGreater(plan.audit_probability, 0)

    def test_rehashed_journal_still_must_match_contract_funding(self):
        service = self.make_delivery()
        bundle = build_bundle(service, "job", OUTPUT, verify_invoice(OUTPUT, expected=OUTPUT))
        # Preserve conservation and every hash, but withhold one unit of bond.
        bundle["ledger"][-1]["amount_minor"] -= 1
        previous = GENESIS_HASH
        for row in bundle["ledger"]:
            row["previous_hash"] = previous
            row["entry_hash"] = digest({k: v for k, v in row.items() if k != "entry_hash"})
            previous = row["entry_hash"]
        with self.assertRaises(ValueError):
            verify_bundle(bundle, bundle_digest(bundle))

    def test_rehashed_event_does_not_grant_provider_verifier_authority(self):
        service = self.make_delivery()
        service.verify("job", "checker", "verify", 3)
        bundle = build_bundle(service, "job", OUTPUT, verify_invoice(OUTPUT, expected=OUTPUT))
        bundle["events"][-1]["event"]["actor"] = "provider"
        previous = GENESIS_HASH
        for row in bundle["events"]:
            row["previous_hash"] = previous
            row["event_hash"] = digest({"previous_hash": previous, "event": row["event"]})
            previous = row["event_hash"]
        with self.assertRaises(ValueError):
            verify_bundle(bundle, bundle_digest(bundle))

    def test_non_object_evidence_fails_with_a_validation_error(self):
        for malformed in ([], None, 5, "not a bundle"):
            with self.subTest(malformed=malformed), self.assertRaises(ValueError):
                verify_bundle(malformed, bundle_digest(malformed))

    def test_positive_saved_cost_cannot_underflow_to_zero_audit_probability(self):
        try:
            plan = plan_deterrence(price=1e308, saved_cost=1e-300, audit_cost=6,
                                   annual_capital_rate=.1, lock_days=7, bond_cap=0)
        except ValueError:
            return
        self.assertGreater(plan.audit_probability, 0)
        self.assertGreaterEqual(plan.audit_probability * (1e308 + plan.bond), 1e-300)


if __name__ == "__main__":
    unittest.main()
