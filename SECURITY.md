# Security policy

This is a local TEST-unit sandbox. It has no authenticated network boundary and
must not be deployed as a payment service or exposed as a public API. It never
executes supplier code or fetches remote source URLs.

The trusted process controls actor labels, time and the database. SQLite triggers
and hash chains do not protect against an administrator rewriting both records
and checkpoints. Evidence exports include the complete demonstration journal;
use only synthetic data until per-contract disclosure has been implemented.

Private vulnerability reporting is enabled. For a defect with exploit details,
use the repository's Security tab and Report a vulnerability to report privately.
Keep exploit details, credentials and private data out of public issues. Do not claim a bounty or guaranteed response time; neither has
been established. Non-sensitive correctness issues can be filed publicly.

Known development requirements include authenticated authority, verifier timeouts,
privacy-preserving evidence export, checkpoint signatures, storage hardening,
resource limits beyond the bounded parser, external payment reconciliation and
deployment review. See the roadmap for acceptance criteria.

