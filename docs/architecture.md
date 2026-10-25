# Architecture of the first sandbox

## Scope and trust boundary

The implementation runs in one trusted Python process with a SQLite database.
Multiple SQLite connections serialize competing writes through `BEGIN IMMEDIATE`.
The only asset is non-redeemable TEST. No network server, external program,
remote URL, model API or payment rail is invoked.

The Python interface assumes the caller has already established consent and
authority. The `actor` parameter is a local role label, not an authentication
credential. The `now` parameter is a trusted simulation clock. Neither is safe
as an unvalidated field in a future HTTP request. The `accept` operation records
already agreed terms; it does not form a signed bilateral agreement.

## Components

| Module | Responsibility |
| --- | --- |
| `contracts.py` | Immutable terms, transitions, roles, deadlines, disputes and transfers |
| `ledger.py` | Accounts, balanced journal, derived balances, transaction boundary and idempotency |
| `verification.py` | Bounded JSON loader, canonical digest and invoice fixture checks |
| `specification.py` | Strict envelope and supported profile validation |
| `evidence.py` | Consistent snapshot, checkpoint, journal replay and contract reconciliation |
| `economics.py` | Illustrative constrained deterrence model, isolated from transfers |
| `cli.py` | Reproducible local demonstration and validation commands |

## Money and atomicity

All ledger amounts and balances are integers bounded by `2**53 - 1`, preserving
the safe integer range of the exported JSON profile. Non-faucet accounts cannot
be overdrawn. The synthetic faucet creates an equal negative offset for each
issuance, so the sum of all TEST balances is zero.

Every transfer creates one journal record and two postings with opposite signs.
Database triggers reject ordinary updates and deletes to postings, journal,
terms and events. Balances are derived, never overwritten. Price and bond
reservations and the state/event updates share a transaction. If funding either
reservation fails, the entire operation rolls back. Dedicated escrow accounts
prevent one posted balance from funding several contracts at the same time.

The operation key is global to the database. Its fingerprint includes the action,
contract, actor and material request payload. Identical retries return the
original snapshot, even after later transitions; callers can request current
state separately. Changed payloads conflict. Request time is excluded from the
fingerprint so a delayed retry does not become a new financial operation.

## Deadlines and terminal states

Funding and delivery close exactly at `delivery_deadline`; expiry is allowed
at that boundary. A successful verification starts a full challenge window from
its own timestamp. Challenges to verified work close at `challenge_until`, when
settlement becomes eligible. Unverified delivered work remains challengeable.
There is no verification timeout service yet, so operators must resolve stalled
work; it never becomes automatically payable.

Failed reference comparison enters DISPUTED. Only the local resolver role can
allocate the disputed price and bond. Allocations use basis points, floor the
buyer's share to integer minor units and give the remainder to the provider.
SETTLED, RESOLVED and REFUNDED are terminal. A new operation key cannot pay again.
For nondelivery the current policy returns the bond; it imposes no automatic
penalty. Changes to these rules require a specification change.

## Profiles and canonical encoding

`spec/2026-10-25.alpha1.contract.schema.json` publishes the envelope shape. The
Python loader also enforces distinct buyer/provider/verifier roles and supported
profile values. JSON Schema alone does not express every cross-field rule.

The input loader accepts at most one MiB, rejects duplicate object keys, floats,
non-finite numbers, invalid UTF-8, unsafe integers and nesting beyond 30 levels.
Keys are bounded ASCII identifiers. Hash input is Python JSON with sorted keys,
no insignificant whitespace, `ensure_ascii=True` and `allow_nan=False`, UTF-8
encoded. This is the versioned **Symbolon JSON profile**, not an implementation
claim for RFC 8785 or cross-language protocol certification.

The exact reference rule is useful for conformance fixtures. The `invoice-v1`
profile checks declared fields, TEST currency, unique line IDs, integer item
quantities and totals. Neither rule establishes source truth. Extracting new
facts requires a separate source manifest and acceptance policy.

## Evidence verification

A bundle includes immutable terms and their digest, materialised state, actual
output, reproducible invoice checks, contract events, local role names and the
complete synthetic journal. Export obtains a transactionally consistent snapshot
and rejects internal contradictions. Verification:

1. Compares the whole bundle to a separately retained SHA-256 checkpoint.
2. Replays the journal chain and checks integer balance limits and conservation.
3. Replays the contract events, roles and deadlines to reproduce stored state.
4. Reconciles contract escrow movements with those events.
5. Recomputes the delivered digest and invoice checks, including the agreed reference.

The resulting integrity findings are separate from the invoice acceptance result.
A valid evidence bundle can faithfully document a failed job. The verifier reports
`authorship_verified: false` and `semantic_correctness_verified: false`.

The hash chain is not a Merkle transparency log. There are no inclusion proofs,
witnesses, signed checkpoints, authenticated attribution or independent
time-stamping. A production service must implement these selectively where they
solve a buyer's evidential requirement. It must minimise exports to authorised
contract data; exporting a complete shared ledger would disclose other customers.

## Subsequent integration seams

Use the accepted contract ID, profile digest, delivery digest and idempotency key
as explicit boundaries for a future authenticated gateway. Adopt one pinned A2A
or MCP version once a design partner requires it. Payment adapters should consume
an authorised settlement instruction and return independent receipts, with
reconciliation and recovery tests. The local SQLite transaction cannot make an
external payment atomically commit; an outbox, deduplication and compensating
workflow must address that gap before real money moves.

