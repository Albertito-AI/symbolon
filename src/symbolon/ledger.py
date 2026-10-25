"""Atomic, double-entry ledger for non-redeemable TEST units only.

This is an in-process sandbox. Anyone who controls its database controls its
trust boundary. Hashes detect inconsistent records; they are not an external
proof of history or a substitute for authenticated payment-provider receipts.
"""

from contextlib import contextmanager
import hashlib
import json
import re
import sqlite3
import threading


# The exported evidence profile uses JSON integers that survive JavaScript
# round trips exactly. SQLite's wider integer range must not leak into it.
MAX_AMOUNT = 2**53 - 1
GENESIS_HASH = "0" * 64


class LedgerError(ValueError):
    """Invalid request or inconsistent sandbox ledger."""


class IdempotencyConflict(LedgerError):
    pass


class InsufficientFunds(LedgerError):
    pass


def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                      allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def strict_int(value, label, minimum=0, maximum=MAX_AMOUNT):
    if type(value) is not int or not minimum <= value <= maximum:
        raise LedgerError(f"{label} must be an integer from {minimum} to {maximum}")
    return value


def identifier(value, label="identifier", internal=False):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}", value):
        raise LedgerError(f"invalid {label}")
    if not internal and value.startswith("sys:"):
        raise LedgerError("sys: identifiers are reserved")
    return value


class Ledger:
    """SQLite ledger; all balances are derived from immutable journal postings."""

    currency = "TEST"

    def __init__(self, path=":memory:"):
        self._lock = threading.RLock()
        self.db = sqlite3.connect(str(path), isolation_level=None, timeout=10,
                                  check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys = ON")
        self.db.execute("PRAGMA busy_timeout = 10000")
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS accounts (
                account_id TEXT PRIMARY KEY,
                kind TEXT NOT NULL CHECK(kind IN ('user','system','escrow'))
            );
            CREATE TABLE IF NOT EXISTS operations (
                operation_key TEXT PRIMARY KEY,
                request_digest TEXT NOT NULL,
                result_json TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS journal (
                journal_id INTEGER PRIMARY KEY,
                operation_key TEXT NOT NULL UNIQUE,
                source TEXT NOT NULL REFERENCES accounts(account_id),
                destination TEXT NOT NULL REFERENCES accounts(account_id),
                amount_minor INTEGER NOT NULL CHECK(amount_minor > 0),
                currency TEXT NOT NULL CHECK(currency = 'TEST'),
                previous_hash TEXT NOT NULL,
                entry_hash TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS postings (
                posting_id INTEGER PRIMARY KEY,
                journal_id INTEGER NOT NULL REFERENCES journal(journal_id),
                account_id TEXT NOT NULL REFERENCES accounts(account_id),
                amount_minor INTEGER NOT NULL
            );
            CREATE INDEX IF NOT EXISTS postings_account ON postings(account_id);
            CREATE TRIGGER IF NOT EXISTS journal_no_update BEFORE UPDATE ON journal
                BEGIN SELECT RAISE(ABORT, 'journal is append-only'); END;
            CREATE TRIGGER IF NOT EXISTS journal_no_delete BEFORE DELETE ON journal
                BEGIN SELECT RAISE(ABORT, 'journal is append-only'); END;
            CREATE TRIGGER IF NOT EXISTS postings_no_update BEFORE UPDATE ON postings
                BEGIN SELECT RAISE(ABORT, 'postings are append-only'); END;
            CREATE TRIGGER IF NOT EXISTS postings_no_delete BEFORE DELETE ON postings
                BEGIN SELECT RAISE(ABORT, 'postings are append-only'); END;
            CREATE TRIGGER IF NOT EXISTS operations_no_update BEFORE UPDATE ON operations
                BEGIN SELECT RAISE(ABORT, 'operations are append-only'); END;
            CREATE TRIGGER IF NOT EXISTS operations_no_delete BEFORE DELETE ON operations
                BEGIN SELECT RAISE(ABORT, 'operations are append-only'); END;
        """)
        self.db.execute("INSERT OR IGNORE INTO accounts VALUES ('sys:faucet','system')")

    def close(self):
        with self._lock:
            self.db.close()

    @contextmanager
    def _transaction(self):
        with self._lock:
            self.db.execute("BEGIN IMMEDIATE")
            try:
                yield
                self.db.execute("COMMIT")
            except BaseException:
                self.db.execute("ROLLBACK")
                raise

    def _atomic(self, key, request, operation):
        identifier(key, "idempotency key")
        fingerprint = digest(request)
        with self._transaction():
            old = self.db.execute("SELECT * FROM operations WHERE operation_key=?", (key,)).fetchone()
            if old:
                if old["request_digest"] != fingerprint:
                    raise IdempotencyConflict("idempotency key was used for a different request")
                return json.loads(old["result_json"])
            result = operation()
            self.db.execute("INSERT INTO operations VALUES (?,?,?)",
                            (key, fingerprint, canonical_json(result)))
            return result

    def create_account(self, account_id):
        identifier(account_id, "account")
        with self._transaction():
            self.db.execute("INSERT OR IGNORE INTO accounts VALUES (?,'user')", (account_id,))
            if self._kind(account_id) != "user":
                raise LedgerError("account has a reserved role")
        return account_id

    def _create_escrow(self, account_id):
        identifier(account_id, "escrow account", internal=True)
        self.db.execute("INSERT INTO accounts VALUES (?,'escrow')", (account_id,))

    def _kind(self, account_id):
        row = self.db.execute("SELECT kind FROM accounts WHERE account_id=?", (account_id,)).fetchone()
        if row is None:
            raise LedgerError(f"unknown account: {account_id}")
        return row["kind"]

    def _balance(self, account_id):
        self._kind(account_id)
        return sum(row[0] for row in self.db.execute(
            "SELECT amount_minor FROM postings WHERE account_id=?", (account_id,)))

    def balance(self, account_id):
        with self._lock:
            return self._balance(account_id)

    def _move(self, source, destination, amount_minor, operation_key):
        """Internal: caller must hold an enclosing transaction and authorise roles."""
        strict_int(amount_minor, "amount_minor", minimum=1)
        if source == destination:
            raise LedgerError("source and destination must differ")
        source_kind = self._kind(source)
        self._kind(destination)
        source_after = self._balance(source) - amount_minor
        destination_after = self._balance(destination) + amount_minor
        if source_after < 0 and source_kind != "system":
            raise InsufficientFunds(f"insufficient TEST funds in {source}")
        if not -MAX_AMOUNT <= source_after <= MAX_AMOUNT or not 0 <= destination_after <= MAX_AMOUNT:
            raise LedgerError("balance exceeds supported integer range")
        prior = self.db.execute("SELECT journal_id,entry_hash FROM journal ORDER BY journal_id DESC LIMIT 1").fetchone()
        record = {
            "journal_id": prior["journal_id"] + 1 if prior else 1,
            "operation_key": operation_key, "source": source, "destination": destination,
            "amount_minor": amount_minor, "currency": "TEST",
            "previous_hash": prior["entry_hash"] if prior else GENESIS_HASH,
        }
        record["entry_hash"] = digest(record)
        self.db.execute("INSERT INTO journal VALUES (?,?,?,?,?,?,?,?)", tuple(record.values()))
        self.db.executemany("INSERT INTO postings(journal_id,account_id,amount_minor) VALUES (?,?,?)", [
            (record["journal_id"], source, -amount_minor),
            (record["journal_id"], destination, amount_minor),
        ])
        return record

    def mint_test_funds(self, account_id, amount_minor, key):
        """Issue explicitly non-redeemable test balances from a synthetic faucet."""
        identifier(account_id, "account")
        strict_int(amount_minor, "amount_minor", minimum=1)
        def operation():
            if self._kind(account_id) != "user":
                raise LedgerError("test funds may only be issued to a user account")
            return self._move("sys:faucet", account_id, amount_minor, key)
        return self._atomic(key, {"action": "mint_test_funds", "account": account_id,
                                  "amount_minor": amount_minor}, operation)

    def transfer(self, source, destination, amount_minor, key):
        identifier(source, "source")
        identifier(destination, "destination")
        strict_int(amount_minor, "amount_minor", minimum=1)
        def operation():
            if self._kind(source) != "user" or self._kind(destination) != "user":
                raise LedgerError("public transfers cannot access reserved accounts")
            return self._move(source, destination, amount_minor, key)
        return self._atomic(key, {"action": "transfer", "source": source,
                                  "destination": destination, "amount_minor": amount_minor}, operation)

    def entries(self):
        with self._lock:
            return [dict(row) for row in self.db.execute("SELECT * FROM journal ORDER BY journal_id")]

    def verify_integrity(self):
        """Return a check report, or raise LedgerError on any inconsistency."""
        with self._lock:
            previous = GENESIS_HASH
            entries = self.entries()
            for expected_id, record in enumerate(entries, 1):
                contents = {k: v for k, v in record.items() if k != "entry_hash"}
                if record["journal_id"] != expected_id or record["previous_hash"] != previous:
                    raise LedgerError("journal sequence or hash link is inconsistent")
                if digest(contents) != record["entry_hash"]:
                    raise LedgerError("journal entry hash is inconsistent")
                posting_rows = self.db.execute(
                    "SELECT account_id,amount_minor FROM postings WHERE journal_id=? ORDER BY posting_id",
                    (expected_id,)).fetchall()
                expected = [(record["source"], -record["amount_minor"]),
                            (record["destination"], record["amount_minor"])]
                if [tuple(row) for row in posting_rows] != expected:
                    raise LedgerError("journal is not balanced double-entry")
                previous = record["entry_hash"]
            if self.db.execute("PRAGMA foreign_key_check").fetchone():
                raise LedgerError("invalid ledger foreign key")
            balances = {row["account_id"]: self._balance(row["account_id"])
                        for row in self.db.execute("SELECT account_id FROM accounts")}
            if sum(balances.values()) != 0:
                raise LedgerError("TEST units were not conserved")
            if any(amount < 0 for name, amount in balances.items() if name != "sys:faucet"):
                raise LedgerError("non-faucet account has a negative balance")
            return {"valid": True, "currency": "TEST", "journal_entries": len(entries),
                    "total_postings": self.db.execute("SELECT COUNT(*) FROM postings").fetchone()[0],
                    "sum_balances": 0, "head_hash": previous}
