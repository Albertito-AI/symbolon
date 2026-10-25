# Development roadmap

These development items are tracked in [GitHub issues](https://github.com/Albertito-AI/symbolon/issues). They remain planned capabilities. The current package demonstrates local TEST-unit accounting, a contract state machine, deterministic invoice fixtures and unsigned evidence snapshots. Dependencies below refer to roadmap IDs; the table maps them to live GitHub issues. Commercial targets are defined in [the commercial plan](commercial-plan.md).

| Roadmap item | GitHub issue |
| --- | --- |
| R01 | [#1](https://github.com/Albertito-AI/symbolon/issues/1) |
| R02 | [#2](https://github.com/Albertito-AI/symbolon/issues/2) |
| R03 | [#3](https://github.com/Albertito-AI/symbolon/issues/3) |
| R04 | [#4](https://github.com/Albertito-AI/symbolon/issues/4) |
| R05 | [#5](https://github.com/Albertito-AI/symbolon/issues/5) |
| R06 | [#6](https://github.com/Albertito-AI/symbolon/issues/6) |
| R07 | [#7](https://github.com/Albertito-AI/symbolon/issues/7) |
| R08 | [#8](https://github.com/Albertito-AI/symbolon/issues/8) |
| R09 | [#9](https://github.com/Albertito-AI/symbolon/issues/9) |

## Prioritised issues

### R01 P0 Authenticate principals and delegated authority

Bind buyer, provider, verifier and resolver actions to authenticated principals. Acceptance criteria: signatures or authenticated sessions bind the complete request and intended audience; delegation carries scope, expiry and spending limits; replay, revocation, role confusion and unauthorised bond use fail explicit adversarial tests. Preserve local fixtures as a separate trusted-caller mode. Dependencies: none.

### R02 P0 Introduce versioned source acceptance profiles

Replace the requirement to know an exact output digest with a pluggable, bounded acceptance interface. Acceptance criteria: pin source manifests and profile versions; reproduce structural, arithmetic and source-location checks; expose unresolved semantic questions; reject unsupported profiles; keep arbitrary submitted code outside the process. Demonstrate good, defective and indeterminate outputs against a labelled holdout corpus. Dependencies: none for local work; R01 for external submissions.

### R03 P0 Minimise and sign portable evidence

The demonstration bundle includes the full synthetic ledger. Acceptance criteria: export only authorised contract evidence; exclude unrelated transactions and unnecessary personal data; define canonical bytes and signed statements; verify signers and key status; obtain a checkpoint through an independently trusted channel. Tests must expose altered, omitted, reordered and substituted records. Document remaining completeness and collusion limits. Dependencies: R01, R02.

### R04 P0 Design transactional production persistence

Extend the existing SQLite transaction model to a documented multi-process architecture. Acceptance criteria: preserve balanced postings, non-negative permitted balances, immutable terms, payload-bound idempotency and at-most-once economic effects under races and crash recovery; use an outbox and reconciliation strategy for external effects; exercise migration and restore. Model-check a bounded lifecycle if a formal specification is added, and report its assumptions. Dependencies: none for architecture; R01 for service boundaries.

### R05 P1 Implement one protocol adapter with conformance

Select A2A or MCP from the first pilot's actual integration need. Acceptance criteria: pin one protocol and SDK release; test request, error, cancellation and retry semantics against official fixtures or an independent implementation; preserve authority and acceptance boundaries; document unsupported features. Keep payment adapters separate. Dependencies: R01, R02, R04.

### R06 P1 Run the commercial benchmark

Recruit one defined B2B extraction segment and compare the workflow with its existing review process. Acceptance criteria: authorised representative samples, labelled defects, published denominators, review-time measurements, itemised support cost and recorded buyer feedback; distinguish internal tests from independent users and paid demand. Apply the commercial plan's chosen gates without presenting them as forecasts. Dependencies: R02; discovery interviews can begin independently.

### R07 P0 Establish payment and legal readiness

Keep live payment paths disabled while evaluating an actual operating model. Acceptance criteria: identify contracting parties, authority, custody and release powers; confirm applicable obligations with qualified advisers and the proposed provider; agree fees, refunds, disputes and data responsibilities; test reconciliation and provider failures in provider test mode. A documented launch decision must specify exposure limits. No simulated balance counts as customer funds. Dependencies: R01, R03, R04, R06.

### R08 P1 Add observability and recovery procedures

Acceptance criteria: structured operational events, measured transition latency, verification outcomes, replay conflicts and reconciliation exceptions; redact sensitive fields; define alert ownership, incident response, backup restore and reconciliation halt conditions. Test the response to injected failures. Separate service telemetry from independently verified historical evidence. Dependencies: R04; pilot instrumentation also supports R06.

### R09 P1 Publish an implementation and conformance matrix

Acceptance criteria: map each specification requirement to code and a meaningful test; identify fixture-only behaviour, unsupported integrations and production gaps; make installation and examples reproducible in clean CI; document release provenance and supported versions. A release must not imply completed legal, security or protocol certification. Dependencies: existing sandbox now; update with R01–R08 as implemented.
