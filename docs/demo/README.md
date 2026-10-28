# Recorded invoice-workflow demonstration

This is an executed synthetic example, recorded on 28 October 2026 from
[`cc60a5de595b5f9a560a26dcca3dbe139b76ee0d`](https://github.com/Albertito-AI/symbolon/tree/cc60a5de595b5f9a560a26dcca3dbe139b76ee0d).
Environment: CPython 3.12.14 on Linux x86_64; standard library only.
The README image is a static illustration of these observations, not a screenshot.

## Input and reproduction

The built-in demo uses the same data as [the valid invoice](../../examples/invoice-valid.json)
and [the incorrect-total invoice](../../examples/invoice-invalid.json): two items at
1,500 TEST minor units require a total of 3,000; the second delivery says 3,999.
It also supplies fictional actors, reference digests, contract terms and times.

From the repository root, using a new output directory:

```sh
PYTHONPATH=src python -m symbolon demo --output artifacts/readme-demo
```

The recorded execution used a temporary directory in place of `artifacts/readme-demo`
and exited with status 0. Selected fields from its actual stdout follow:

```json
{
  "asset": "TEST",
  "real_money_moved": false,
  "contracts": [
    {
      "contract_id": "task-accepted",
      "state": "SETTLED",
      "acceptance_checks_passed": true
    },
    {
      "contract_id": "task-disputed",
      "state": "RESOLVED",
      "acceptance_checks_passed": false
    }
  ],
  "ledger": {
    "valid": true,
    "journal_entries": 10,
    "total_postings": 20,
    "sum_balances": 0
  }
}
```

Both exported evidence bundles also passed the separate `verify-bundle` command
against their recorded SHA-256 digests. The disputed bundle correctly retains
`invoice_profile_passed: false`; a consistent evidence record can describe failed work.
The accepted contract waits for its challenge window. The disputed fixture uses
an explicit resolver action to refund the price and return the bond.

[The complete recorded output and verifier results](recorded-run.json) preserve
the source version and digests. Follow the [main reproduction instructions](../../README.md#run-the-demonstration)
to verify your freshly generated bundles against separately retained digests.

## What this establishes

The run exercises fixed-reference acceptance, distinct workflow paths, balanced
TEST accounting and evidence replay. It moved no real money. Authorship and semantic
correctness both remain unverified; invoice authenticity, actual debt, identity and
real payment settlement are outside this demonstration. A digest supplied beside
the same bundle is a demo checkpoint, not an independently trusted anchor.

The existing 66-test suite passed on the same source and environment. This was an
owner-authorised development run, not independent customer use or a security audit.
