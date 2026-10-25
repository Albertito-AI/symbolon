# Contributing

Start with an issue describing the buyer problem or reproducible defect. Keep
changes bounded and describe the resulting behaviour. For changes to accounting,
acceptance or evidence, include tests that would fail without the fix. Follow
the source audit when making factual claims and pin mutable specifications.

Run `PYTHONPATH=src python -m unittest discover -s tests -v` and the documented
demo before submitting a change. Do not commit credentials, personal customer
data, database files or generated run output. Examples must be synthetic.

Contributions are accepted under Apache-2.0. Include a Developer Certificate
of Origin 1.1 sign-off only after reading and agreeing to the certificate at
https://developercertificate.org/ . Use `git commit -s` with your own identity.
Do not sign for somebody else. The founding import identifies its provenance
separately; it does not invent a contributor attestation.

Describe what changed, why, validation performed and remaining limitations in
the pull request. A maintainer reviews accounting or acceptance changes. A
future multi-maintainer release should require an independent reviewer for those
paths. No branch protection or review requirement is claimed until configured.

