from dataclasses import replace
import hashlib
import sqlite3
import tempfile
import unittest
from pathlib import Path

from symbolon.contracts import Contract, ContractService, ContractError, AuthorizationError
from symbolon.ledger import Ledger, LedgerError, IdempotencyConflict, InsufficientFunds


GOOD = hashlib.sha256(b'accepted structured output').hexdigest()
BAD = hashlib.sha256(b'different output').hexdigest()


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.ledger = Ledger()
        self.ledger.create_account("buyer")
        self.ledger.create_account("provider")
        self.ledger.mint_test_funds("buyer", 1000, "seed-buyer")
        self.ledger.mint_test_funds("provider", 500, "seed-provider")
        self.service = ContractService(self.ledger)
        self.contract = Contract("job-1", "buyer", "provider", "checker", GOOD, 400, 150, 100, 10)
        self.service.accept(self.contract, "accept", 0)

    def tearDown(self):
        self.ledger.close()

    def fund(self):
        return self.service.fund("job-1", "buyer", "fund", 1)

    def deliver(self, output=GOOD):
        self.fund()
        return self.service.deliver("job-1", output, "provider", "deliver", 20)

    def verify(self, output=GOOD):
        self.deliver(output)
        return self.service.verify("job-1", "checker", "verify", 21)

    def test_full_lifecycle_conserves_and_returns_bond(self):
        r = self.verify()
        self.assertEqual(r["state"], "VERIFIED")
        self.assertEqual(r["challenge_until"], 31)
        r = self.service.settle("job-1", "settlement-service", "settle", 31)
        self.assertEqual(r["state"], "SETTLED")
        self.assertEqual(self.ledger.balance("buyer"), 600)
        self.assertEqual(self.ledger.balance("provider"), 900)
        self.assertEqual(len(self.service.events("job-1")), 5)
        self.ledger.verify_integrity()

    def test_funding_reserves_price_and_bond(self):
        self.fund()
        self.assertEqual(self.ledger.balance("buyer"), 600)
        self.assertEqual(self.ledger.balance("provider"), 350)
        self.assertEqual(self.ledger.balance(self.service._escrow("job-1", "price")), 400)
        self.assertEqual(self.ledger.balance(self.service._escrow("job-1", "bond")), 150)

    def test_failed_bond_funding_rolls_back_price_state_and_events(self):
        self.ledger.transfer("provider", "buyer", 500, "drain")
        before = self.ledger.entries()
        with self.assertRaises(InsufficientFunds):
            self.fund()
        self.assertEqual(self.service.get("job-1")["state"], "ACCEPTED")
        self.assertEqual(self.ledger.entries(), before)
        self.assertEqual(len(self.service.events("job-1")), 1)
        self.assertEqual(self.ledger.balance("buyer"), 1500)

    def test_wrong_local_actor_rejected(self):
        with self.assertRaises(AuthorizationError):
            self.service.fund("job-1", "provider", "bad-fund", 1)
        self.fund()
        with self.assertRaises(AuthorizationError):
            self.service.deliver("job-1", GOOD, "buyer", "bad-deliver", 20)
        self.service.deliver("job-1", GOOD, "provider", "deliver", 20)
        with self.assertRaises(AuthorizationError):
            self.service.verify("job-1", "provider", "bad-verify", 21)

    def test_cannot_settle_before_verification_or_window_end(self):
        self.deliver()
        with self.assertRaises(ContractError):
            self.service.settle("job-1", "settlement-service", "early", 30)
        self.service.verify("job-1", "checker", "verify", 31)
        with self.assertRaises(ContractError):
            self.service.settle("job-1", "settlement-service", "early", 40)
        self.assertEqual(self.service.settle("job-1", "settlement-service", "settle", 41)["state"], "SETTLED")

    def test_unverified_work_never_optimistically_settles(self):
        self.deliver()
        with self.assertRaises(ContractError):
            self.service.settle("job-1", "settlement-service", "late-settle", 1000)
        self.assertEqual(self.service.challenge("job-1", "buyer", "challenge", 1000, "no check")["state"], "DISPUTED")

    def test_failing_exact_digest_check_freezes_funds(self):
        r = self.verify(BAD)
        self.assertEqual(r["state"], "DISPUTED")
        self.assertEqual(self.ledger.balance("provider"), 350)
        with self.assertRaises(ContractError):
            self.service.settle("job-1", "settlement-service", "settle", 50)
        with self.assertRaises(ContractError):
            self.service.expire("job-1", "settlement-service", "expire", 100)

    def test_challenge_wins_before_window_boundary(self):
        self.verify()
        self.service.challenge("job-1", "buyer", "challenge", 30, "reference was defective")
        with self.assertRaises(ContractError):
            self.service.settle("job-1", "settlement-service", "settle", 31)

    def test_window_boundary_is_unambiguous(self):
        self.verify()
        with self.assertRaises(ContractError):
            self.service.challenge("job-1", "buyer", "challenge", 31, "too late")
        self.assertEqual(self.service.settle("job-1", "settlement-service", "settle", 31)["state"], "SETTLED")

    def test_resolve_splits_price_and_bond_with_conserved_rounding(self):
        self.verify(BAD)
        r = self.service.resolve("job-1", 3333, 5000, "human-resolver", "resolve", 30, "reviewed")
        self.assertEqual(r["state"], "RESOLVED")
        self.assertEqual(self.ledger.balance("buyer"), 808)  # 600 + floor(400*.3333) + 75
        self.assertEqual(self.ledger.balance("provider"), 692)
        self.ledger.verify_integrity()

    def test_only_resolver_can_allocate_bond(self):
        self.verify(BAD)
        with self.assertRaises(AuthorizationError):
            self.service.resolve("job-1", 10000, 10000, "checker", "resolve", 30, "reviewed")
        self.assertEqual(self.service.get("job-1")["state"], "DISPUTED")

    def test_resolution_requires_valid_shares_and_reason(self):
        self.verify(BAD)
        for value in (-1, 10001, True, 1.5):
            with self.subTest(value=value), self.assertRaises(LedgerError):
                self.service.resolve("job-1", value, 0, "human-resolver", "bad", 30, "reviewed")
        with self.assertRaises(ContractError):
            self.service.resolve("job-1", 10000, 0, "human-resolver", "bad", 30, " ")

    def test_nondelivery_expiry_refunds_price_returns_bond(self):
        self.fund()
        with self.assertRaises(ContractError):
            self.service.expire("job-1", "settlement-service", "expiry", 99)
        self.assertEqual(self.service.expire("job-1", "settlement-service", "expiry", 100)["state"], "REFUNDED")
        self.assertEqual(self.ledger.balance("buyer"), 1000)
        self.assertEqual(self.ledger.balance("provider"), 500)
        self.ledger.verify_integrity()

    def test_unfunded_expiry_moves_no_money(self):
        before = self.ledger.entries()
        self.service.expire("job-1", "settlement-service", "expiry", 100)
        self.assertEqual(self.ledger.entries(), before)

    def test_delivery_and_funding_close_at_deadline(self):
        with self.assertRaises(ContractError):
            self.service.fund("job-1", "buyer", "fund-at-deadline", 100)
        self.fund()
        with self.assertRaises(ContractError):
            self.service.deliver("job-1", GOOD, "provider", "late", 100)
        self.service.expire("job-1", "settlement-service", "expiry", 100)

    def test_terminal_retries_idempotent_but_new_key_rejected(self):
        self.verify()
        original = self.service.settle("job-1", "settlement-service", "settle", 31)
        before = self.ledger.entries()
        self.assertEqual(original, self.service.settle("job-1", "settlement-service", "settle", 99))
        with self.assertRaises(ContractError):
            self.service.settle("job-1", "settlement-service", "another-settle", 99)
        with self.assertRaises(ContractError):
            self.service.expire("job-1", "settlement-service", "refund-after-settle", 100)
        self.assertEqual(self.ledger.entries(), before)

    def test_changed_payload_replay_is_rejected(self):
        self.deliver()
        with self.assertRaises(IdempotencyConflict):
            self.service.deliver("job-1", BAD, "provider", "deliver", 21)
        self.assertEqual(self.service.get("job-1")["delivered_sha256"], GOOD)

    def test_backward_time_and_invalid_timestamp_rejected(self):
        self.deliver()
        for now in (19, True, -1, 20.5):
            with self.subTest(now=now), self.assertRaises(LedgerError):
                self.service.verify("job-1", "checker", "verify-invalid", now)

    def test_contract_validation_and_immutable_terms(self):
        for changes in ({"price_minor": 0}, {"price_minor": True}, {"bond_minor": -1},
                        {"buyer": "provider"}, {"accepted_output_sha256": "invalid"},
                        {"challenge_window_seconds": -1}):
            with self.subTest(changes=changes), self.assertRaises(LedgerError):
                replace(self.contract, **changes)
        with self.assertRaises(sqlite3.IntegrityError):
            self.ledger.db.execute("UPDATE contract_terms SET terms_digest='rewritten'")
        with self.assertRaises(sqlite3.IntegrityError):
            self.ledger.db.execute("DELETE FROM contract_events")

    def test_zero_bond_and_zero_window_are_defined(self):
        contract = replace(self.contract, contract_id="job-2", bond_minor=0, challenge_window_seconds=0)
        self.service.accept(contract, "accept2", 1)
        self.service.fund("job-2", "buyer", "fund2", 2)
        self.service.deliver("job-2", GOOD, "provider", "deliver2", 3)
        self.service.verify("job-2", "checker", "verify2", 4)
        self.service.settle("job-2", "settlement-service", "settle2", 4)
        self.assertEqual(self.ledger.balance("provider"), 900)

    def test_restart_preserves_contract_and_terminal_idempotency(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "restart.db"
            first = Ledger(path)
            first.create_account("buyer")
            first.create_account("provider")
            first.mint_test_funds("buyer", 400, "seed-buyer")
            first.mint_test_funds("provider", 150, "seed-provider")
            service = ContractService(first)
            service.accept(self.contract, "accept", 0)
            service.fund("job-1", "buyer", "fund", 1)
            first.close()
            second = Ledger(path)
            try:
                service = ContractService(second)
                self.assertEqual(service.get("job-1")["state"], "FUNDED")
                service.expire("job-1", "settlement-service", "expire", 100)
                service.expire("job-1", "settlement-service", "expire", 101)
                self.assertEqual(second.balance("buyer"), 400)
                self.assertEqual(second.balance("provider"), 150)
                second.verify_integrity()
            finally:
                second.close()


if __name__ == "__main__":
    unittest.main()
