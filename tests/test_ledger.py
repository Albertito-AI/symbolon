import sqlite3
import tempfile
import threading
import unittest
from pathlib import Path

from symbolon.ledger import Ledger, LedgerError, IdempotencyConflict, InsufficientFunds, MAX_AMOUNT


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.ledger = Ledger()
        self.ledger.create_account("buyer")
        self.ledger.create_account("provider")
        self.ledger.mint_test_funds("buyer", 1000, "seed")

    def tearDown(self):
        self.ledger.close()

    def test_transfer_conserves_units_and_posts_both_sides(self):
        self.ledger.transfer("buyer", "provider", 250, "pay")
        self.assertEqual(self.ledger.balance("buyer"), 750)
        self.assertEqual(self.ledger.balance("provider"), 250)
        self.assertEqual(self.ledger.balance("sys:faucet"), -1000)
        report = self.ledger.verify_integrity()
        self.assertEqual(report["sum_balances"], 0)
        self.assertEqual(report["total_postings"], 4)

    def test_identical_retry_is_one_operation(self):
        first = self.ledger.transfer("buyer", "provider", 250, "pay")
        self.assertEqual(first, self.ledger.transfer("buyer", "provider", 250, "pay"))
        self.assertEqual(self.ledger.balance("provider"), 250)
        self.assertEqual(len(self.ledger.entries()), 2)

    def test_changed_payload_for_same_key_is_rejected(self):
        self.ledger.transfer("buyer", "provider", 250, "pay")
        with self.assertRaises(IdempotencyConflict):
            self.ledger.transfer("buyer", "provider", 251, "pay")
        self.assertEqual(self.ledger.balance("buyer"), 750)

    def test_same_key_across_different_operation_is_rejected(self):
        with self.assertRaises(IdempotencyConflict):
            self.ledger.transfer("buyer", "provider", 1000, "seed")

    def test_overdraw_rolls_back_without_consuming_key(self):
        with self.assertRaises(InsufficientFunds):
            self.ledger.transfer("buyer", "provider", 1001, "retry")
        self.assertEqual(len(self.ledger.entries()), 1)
        self.ledger.transfer("buyer", "provider", 1000, "retry")
        self.assertEqual(self.ledger.balance("buyer"), 0)

    def test_invalid_money_types_and_values_rejected(self):
        for value in (0, -1, True, False, 1.5, "1", None, MAX_AMOUNT + 1):
            with self.subTest(value=value), self.assertRaises(LedgerError):
                self.ledger.transfer("buyer", "provider", value, "invalid")

    def test_missing_account_and_self_transfer_do_not_mutate(self):
        for destination in ("missing", "buyer"):
            with self.subTest(destination=destination), self.assertRaises(LedgerError):
                self.ledger.transfer("buyer", destination, 20, "invalid")
        self.assertEqual(len(self.ledger.entries()), 1)

    def test_reserved_accounts_cannot_be_created_or_transferred(self):
        with self.assertRaises(LedgerError):
            self.ledger.create_account("sys:unauthorised")
        with self.assertRaises(LedgerError):
            self.ledger.transfer("sys:faucet", "buyer", 1, "unauthorised")
        with self.assertRaises(LedgerError):
            self.ledger.mint_test_funds("sys:faucet", 1, "unauthorised")

    def test_create_account_is_idempotent(self):
        self.ledger.create_account("buyer")
        self.assertEqual(self.ledger.balance("buyer"), 1000)

    def test_invalid_identifiers_rejected(self):
        for value in ("", "a b", "a\n", "\u202ebuyer", "x" * 129, 123):
            with self.subTest(value=value), self.assertRaises(LedgerError):
                self.ledger.create_account(value)

    def test_append_only_database_triggers(self):
        for table in ("journal", "postings", "operations"):
            with self.subTest(table=table), self.assertRaises(sqlite3.IntegrityError):
                self.ledger.db.execute(f"DELETE FROM {table}")

    def test_balance_limit_rejects_overflow_atomically(self):
        with self.assertRaises(LedgerError):
            self.ledger.mint_test_funds("buyer", MAX_AMOUNT, "overflow")
        self.assertEqual(self.ledger.balance("buyer"), 1000)
        self.assertEqual(len(self.ledger.entries()), 1)

    def test_restart_preserves_idempotency_and_history(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ledger.db"
            first = Ledger(path)
            first.create_account("a")
            first.mint_test_funds("a", 100, "seed")
            first.close()
            second = Ledger(path)
            try:
                second.mint_test_funds("a", 100, "seed")
                self.assertEqual(second.balance("a"), 100)
                self.assertTrue(second.verify_integrity()["valid"])
            finally:
                second.close()

    def test_concurrent_connections_cannot_double_spend(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ledger.db"
            first = Ledger(path)
            first.create_account("a")
            first.create_account("b")
            first.mint_test_funds("a", 100, "seed")
            second = Ledger(path)
            barrier = threading.Barrier(2)
            successes, failures = [], []
            def pay(ledger, key):
                barrier.wait()
                try:
                    ledger.transfer("a", "b", 100, key)
                    successes.append(key)
                except InsufficientFunds:
                    failures.append(key)
            threads = [threading.Thread(target=pay, args=(first, "one")),
                       threading.Thread(target=pay, args=(second, "two"))]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
            try:
                self.assertEqual(len(successes), 1)
                self.assertEqual(len(failures), 1)
                self.assertEqual(first.balance("b"), 100)
                first.verify_integrity()
            finally:
                first.close()
                second.close()


if __name__ == "__main__":
    unittest.main()
