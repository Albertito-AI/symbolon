"""A deterministic local contract state machine using synthetic TEST balances.

Actor strings are labels provided by a trusted in-process caller, not verified
identities. An accepted contract represents already agreed sandbox terms.
The exact-digest verifier checks content equality, not commercial usefulness.
"""

from dataclasses import asdict, dataclass
import json
import re

from .ledger import GENESIS_HASH, LedgerError, canonical_json, digest, identifier, strict_int


class ContractError(LedgerError):
    pass


class AuthorizationError(ContractError):
    pass


def valid_hash(value):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise ContractError("sha256 must be 64 lowercase hexadecimal characters")
    return value


@dataclass(frozen=True)
class Contract:
    contract_id: str
    buyer: str
    provider: str
    verifier: str
    accepted_output_sha256: str
    price_minor: int
    bond_minor: int
    delivery_deadline: int
    challenge_window_seconds: int

    def __post_init__(self):
        identifier(self.contract_id, "contract_id")
        for name in (self.buyer, self.provider, self.verifier):
            identifier(name, "actor")
        if len({self.buyer, self.provider, self.verifier}) != 3:
            raise ContractError("buyer, provider and verifier must be distinct")
        valid_hash(self.accepted_output_sha256)
        strict_int(self.price_minor, "price_minor", minimum=1)
        strict_int(self.bond_minor, "bond_minor")
        strict_int(self.delivery_deadline, "delivery_deadline", minimum=1)
        strict_int(self.challenge_window_seconds, "challenge_window_seconds", maximum=31536000)


class ContractService:
    settlement_actor = "settlement-service"

    def __init__(self, ledger, resolver="human-resolver"):
        self.ledger = ledger
        self.db = ledger.db
        self.resolver = identifier(resolver, "resolver")
        if resolver == self.settlement_actor:
            raise ContractError("resolver and settlement service must differ")
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS contract_terms (
                contract_id TEXT PRIMARY KEY,
                terms_json TEXT NOT NULL,
                terms_digest TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS contract_state (
                contract_id TEXT PRIMARY KEY REFERENCES contract_terms(contract_id),
                state TEXT NOT NULL,
                delivered_sha256 TEXT,
                delivered_at INTEGER,
                challenge_until INTEGER,
                updated_at INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS contract_events (
                event_id INTEGER PRIMARY KEY,
                contract_id TEXT NOT NULL REFERENCES contract_terms(contract_id),
                event_json TEXT NOT NULL,
                previous_hash TEXT NOT NULL,
                event_hash TEXT NOT NULL
            );
            CREATE TRIGGER IF NOT EXISTS terms_no_update BEFORE UPDATE ON contract_terms
                BEGIN SELECT RAISE(ABORT, 'terms are immutable'); END;
            CREATE TRIGGER IF NOT EXISTS terms_no_delete BEFORE DELETE ON contract_terms
                BEGIN SELECT RAISE(ABORT, 'terms are immutable'); END;
            CREATE TRIGGER IF NOT EXISTS events_no_update BEFORE UPDATE ON contract_events
                BEGIN SELECT RAISE(ABORT, 'events are append-only'); END;
            CREATE TRIGGER IF NOT EXISTS events_no_delete BEFORE DELETE ON contract_events
                BEGIN SELECT RAISE(ABORT, 'events are append-only'); END;
        """)

    @staticmethod
    def _escrow(contract_id, part):
        # Fixed-length account IDs even for the longest permitted contract IDs.
        return f"sys:{part}:{digest(contract_id)}"

    def _get(self, contract_id):
        identifier(contract_id, "contract_id")
        row = self.db.execute("SELECT * FROM contract_terms JOIN contract_state USING(contract_id) WHERE contract_id=?",
                              (contract_id,)).fetchone()
        if row is None:
            raise ContractError("unknown contract")
        result = dict(row)
        result["terms"] = json.loads(result.pop("terms_json"))
        if digest(result["terms"]) != result["terms_digest"]:
            raise ContractError("contract terms digest does not match")
        return result

    def get(self, contract_id):
        with self.ledger._lock:
            return self._get(contract_id)

    def events(self, contract_id):
        with self.ledger._lock:
            self._get(contract_id)
            return [{**dict(row), "event": json.loads(row["event_json"])}
                    for row in self.db.execute("SELECT * FROM contract_events WHERE contract_id=? ORDER BY event_id",
                                               (contract_id,))]

    def _event(self, contract_id, action, actor, now, details=None):
        previous = self.db.execute("SELECT event_hash FROM contract_events WHERE contract_id=? ORDER BY event_id DESC LIMIT 1",
                                   (contract_id,)).fetchone()
        previous_hash = previous["event_hash"] if previous else GENESIS_HASH
        event = {"contract_id": contract_id, "action": action, "actor": actor,
                 "at": now, "details": details or {}}
        self.db.execute("INSERT INTO contract_events(contract_id,event_json,previous_hash,event_hash) VALUES (?,?,?,?)",
                        (contract_id, canonical_json(event), previous_hash,
                         digest({"previous_hash": previous_hash, "event": event})))

    def _set_state(self, contract_id, state, now):
        self.db.execute("UPDATE contract_state SET state=?,updated_at=? WHERE contract_id=?", (state, now, contract_id))

    @staticmethod
    def _clock(record, now):
        strict_int(now, "now")
        if now < record["updated_at"]:
            raise ContractError("time cannot move backwards")

    @staticmethod
    def _role(actor, expected):
        if actor != expected:
            raise AuthorizationError(f"this action requires the {expected} actor")

    @staticmethod
    def _state(record, *allowed):
        if record["state"] not in allowed:
            raise ContractError(f"action is invalid in {record['state']} state")

    def _run(self, contract_id, actor, key, now, action, payload, operation):
        identifier(actor, "actor")
        strict_int(now, "now")
        request = {"action": f"contract.{action}", "contract_id": contract_id,
                   "actor": actor, **payload}
        def transaction():
            record = self._get(contract_id)
            self._clock(record, now)
            operation(record)
            return self._get(contract_id)
        return self.ledger._atomic(key, request, transaction)

    def accept(self, contract, key, now):
        """Record already agreed sandbox terms; no external signature is inferred."""
        if not isinstance(contract, Contract):
            raise ContractError("contract must be a Contract instance")
        strict_int(now, "now")
        terms = asdict(contract)
        if {contract.buyer, contract.provider, contract.verifier} & {self.resolver, self.settlement_actor}:
            raise ContractError("contract parties cannot use service or resolver roles")
        def operation():
            if now >= contract.delivery_deadline:
                raise ContractError("delivery deadline must be in the future")
            for party in (contract.buyer, contract.provider):
                if self.ledger._kind(party) != "user":
                    raise ContractError("buyer and provider must have user accounts")
            if self.db.execute("SELECT 1 FROM contract_terms WHERE contract_id=?", (contract.contract_id,)).fetchone():
                raise ContractError("contract_id already exists")
            self.db.execute("INSERT INTO contract_terms VALUES (?,?,?)",
                            (contract.contract_id, canonical_json(terms), digest(terms)))
            self.db.execute("INSERT INTO contract_state VALUES (?,'ACCEPTED',NULL,NULL,NULL,?)", (contract.contract_id, now))
            self.ledger._create_escrow(self._escrow(contract.contract_id, "price"))
            self.ledger._create_escrow(self._escrow(contract.contract_id, "bond"))
            self._event(contract.contract_id, "accept", "trusted-coordinator", now,
                        {"terms_digest": digest(terms)})
            return self._get(contract.contract_id)
        return self.ledger._atomic(key, {"action": "contract.accept", "terms": terms}, operation)

    def fund(self, contract_id, actor, key, now):
        def operation(r):
            self._role(actor, r["terms"]["buyer"])
            self._state(r, "ACCEPTED")
            if now >= r["terms"]["delivery_deadline"]:
                raise ContractError("contract cannot be funded at or after its deadline")
            t = r["terms"]
            self.ledger._move(t["buyer"], self._escrow(contract_id, "price"), t["price_minor"], key + ":price")
            if t["bond_minor"]:
                self.ledger._move(t["provider"], self._escrow(contract_id, "bond"), t["bond_minor"], key + ":bond")
            self._set_state(contract_id, "FUNDED", now)
            self._event(contract_id, "fund", actor, now)
        return self._run(contract_id, actor, key, now, "fund", {}, operation)

    def deliver(self, contract_id, output_sha256, actor, key, now):
        valid_hash(output_sha256)
        def operation(r):
            self._role(actor, r["terms"]["provider"])
            self._state(r, "FUNDED")
            if now >= r["terms"]["delivery_deadline"]:
                raise ContractError("delivery deadline has passed")
            until = now + r["terms"]["challenge_window_seconds"]
            strict_int(until, "challenge_until")
            self.db.execute("UPDATE contract_state SET state='DELIVERED',delivered_sha256=?,delivered_at=?,challenge_until=?,updated_at=? WHERE contract_id=?",
                            (output_sha256, now, until, now, contract_id))
            self._event(contract_id, "deliver", actor, now, {"output_sha256": output_sha256})
        return self._run(contract_id, actor, key, now, "deliver", {"output_sha256": output_sha256}, operation)

    def verify(self, contract_id, actor, key, now):
        def operation(r):
            self._role(actor, r["terms"]["verifier"])
            self._state(r, "DELIVERED")
            passed = r["delivered_sha256"] == r["terms"]["accepted_output_sha256"]
            self._set_state(contract_id, "VERIFIED" if passed else "DISPUTED", now)
            # Give the buyer the full agreed window after a successful check.
            if passed:
                until = now + r["terms"]["challenge_window_seconds"]
                strict_int(until, "challenge_until")
                self.db.execute("UPDATE contract_state SET challenge_until=? WHERE contract_id=?", (until, contract_id))
            self._event(contract_id, "verify", actor, now,
                        {"method": "exact_sha256", "passed": passed,
                         "output_sha256": r["delivered_sha256"]})
        return self._run(contract_id, actor, key, now, "verify", {}, operation)

    def challenge(self, contract_id, actor, key, now, reason):
        self._reason(reason)
        def operation(r):
            self._role(actor, r["terms"]["buyer"])
            self._state(r, "DELIVERED", "VERIFIED")
            # Unverified work can always be challenged; it never auto-settles.
            if r["state"] == "VERIFIED" and now >= r["challenge_until"]:
                raise ContractError("challenge window has closed")
            self._set_state(contract_id, "DISPUTED", now)
            self._event(contract_id, "challenge", actor, now, {"reason": reason})
        return self._run(contract_id, actor, key, now, "challenge", {"reason": reason}, operation)

    def settle(self, contract_id, actor, key, now):
        def operation(r):
            self._role(actor, self.settlement_actor)
            self._state(r, "VERIFIED")
            if now < r["challenge_until"]:
                raise ContractError("challenge window is still open")
            t = r["terms"]
            self.ledger._move(self._escrow(contract_id, "price"), t["provider"], t["price_minor"], key + ":price")
            if t["bond_minor"]:
                self.ledger._move(self._escrow(contract_id, "bond"), t["provider"], t["bond_minor"], key + ":bond")
            self._set_state(contract_id, "SETTLED", now)
            self._event(contract_id, "settle", actor, now)
        return self._run(contract_id, actor, key, now, "settle", {}, operation)

    def expire(self, contract_id, actor, key, now):
        def operation(r):
            self._role(actor, self.settlement_actor)
            self._state(r, "ACCEPTED", "FUNDED")
            t = r["terms"]
            if now < t["delivery_deadline"]:
                raise ContractError("delivery deadline is still open")
            if r["state"] == "FUNDED":
                self.ledger._move(self._escrow(contract_id, "price"), t["buyer"], t["price_minor"], key + ":price")
                if t["bond_minor"]:
                    self.ledger._move(self._escrow(contract_id, "bond"), t["provider"], t["bond_minor"], key + ":bond")
            self._set_state(contract_id, "REFUNDED", now)
            self._event(contract_id, "expire", actor, now,
                        {"bond_policy": "return_on_nondelivery_no_automatic_penalty"})
        return self._run(contract_id, actor, key, now, "expire", {}, operation)

    @staticmethod
    def _reason(reason):
        if not isinstance(reason, str) or not reason.strip() or len(reason) > 2000:
            raise ContractError("reason must contain 1 to 2000 characters")

    def resolve(self, contract_id, buyer_share_bps, bond_to_buyer_bps, actor, key, now, reason):
        strict_int(buyer_share_bps, "buyer_share_bps", maximum=10000)
        strict_int(bond_to_buyer_bps, "bond_to_buyer_bps", maximum=10000)
        self._reason(reason)
        def operation(r):
            self._role(actor, self.resolver)
            self._state(r, "DISPUTED")
            t = r["terms"]
            details = {"reason": reason, "buyer_share_bps": buyer_share_bps,
                       "bond_to_buyer_bps": bond_to_buyer_bps,
                       "rounding": "buyer allocations floor to integer; remainder to provider"}
            for part, total, bps in (("price", t["price_minor"], buyer_share_bps),
                                     ("bond", t["bond_minor"], bond_to_buyer_bps)):
                buyer_amount = total * bps // 10000
                provider_amount = total - buyer_amount
                for recipient, amount, suffix in ((t["buyer"], buyer_amount, "buyer"),
                                                  (t["provider"], provider_amount, "provider")):
                    if amount:
                        self.ledger._move(self._escrow(contract_id, part), recipient, amount,
                                          key + ":" + part + ":" + suffix)
                details[part + "_buyer_minor"] = buyer_amount
                details[part + "_provider_minor"] = provider_amount
            self._set_state(contract_id, "RESOLVED", now)
            self._event(contract_id, "resolve", actor, now, details)
        return self._run(contract_id, actor, key, now, "resolve",
                         {"buyer_share_bps": buyer_share_bps, "bond_to_buyer_bps": bond_to_buyer_bps,
                          "reason": reason}, operation)
