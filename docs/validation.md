# Initial release validation

Validation date: 25 October 2026. Version: 0.1.0a1.

## Local results

The full local suite passed **66 tests** using the documented command:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

The suite covers atomic reservation and rollback, derived balances, strict
integer limits, conflicting idempotency keys, competing SQLite connections,
restart persistence, role boundaries, delivery and challenge deadlines,
terminal payout prevention, dispute allocation, malformed JSON, evidence
integrity and the constrained economic calculation.

An independent review added targeted tests for plausible faults. Those tests
led to alignment of ledger and JSON numeric limits, state replay and transfer
reconciliation in evidence verification, recomputation of invoice reports, and
rejection of numerical overflow and underflow. Rehashed inconsistent journal
entries and wrong-role verification events are rejected. This is an internal
engineering review, not independent certification or a security audit.

## End to end demonstration

`python -m symbolon demo --output artifacts/first-run` completed the accepted
fixture in SETTLED and the incorrect fixture in RESOLVED after refunding its
price. The resulting journal contained 10 balanced transfers and 20 postings.
Final user balances were 96,000 and 104,000 TEST minor units. The faucet offset
was negative 200,000; the sum of all balances remained zero. No real funds moved.

The accepted evidence checkpoint was
`bd5891793eda0d9a5577912aceb87d899336c97e6954ea594932e15d121fa420`.
The failed-work evidence checkpoint was
`67309131f92ba8c39eb8eddb2d85fe339c258b4c7570e2f8a2998d3a25d824b2`.
These fixed fixture outputs can be reproduced. The evidence verifier correctly
distinguishes valid records of failed work from a passing acceptance result.

## Economics example

With P=40, saved cost=12, audit cost=6, annual capital rate=0.1,
lock=7 days, detection=1, false positives=0 and bond cap=200, the calculation
returned bond=153.7597923793, audit probability=0.0619323537 and combined audit
and capital cost=0.6664759160. This is a numerical model under explicit
assumptions, not a calibrated price or enforceable penalty recommendation.

## CI configuration and boundaries

The GitHub Actions definition targets Python 3.11, 3.12 and 3.13. It uses
read-only repository permissions, `push` and `pull_request` events, and pinned
official actions. The retrieved official release commits were:

- [actions/checkout v7.0.1](https://github.com/actions/checkout/commit/3d3c42e5aac5ba805825da76410c181273ba90b1)
- [actions/setup-python v7.1.0](https://github.com/actions/setup-python/commit/6d4fd22b20465ccc0f7354476588e8df7c9ca0e0)

Local validation does not establish that hosted GitHub Actions has run. A
remote run, branch settings and other hosting controls require verification
after the repository exists. No throughput benchmark, model welfare experiment,
external protocol conformance, TLA+ proof, paid demand or live payment result
is asserted by this release.

