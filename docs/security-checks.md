# Automated checks and badge scope

The README links two live reports. Neither badge certifies security, legal
correctness, authenticated consent, production readiness or independent use.

| Badge | What it reports | Important limit |
| --- | --- | --- |
| Sandbox validation | The existing `ci.yml` workflow's main-branch push status, covering tests, examples and installed-wheel checks. | A green run concerns its recorded source and environment. It does not establish every contract requirement or production behaviour. |
| OpenSSF Scorecard | The latest public Scorecard aggregate and its detailed repository-practice checks. | This is an evolving heuristic assessment, with possible false positives, false negatives and inapplicable checks. It is not a perfect-score target or a GitHub profile achievement. |

## Execution and publication

[The workflow](../.github/workflows/scorecard.yml) runs on pushes to `main` in
`Albertito-AI/symbolon`. It adds no schedule, pull-request trigger, manual event,
new account, personal access token or paid runner. Both jobs use standard
GitHub-hosted Ubuntu runners, which are [free for public
repositories](https://docs.github.com/en/actions/concepts/billing-and-usage).
Cache access is disabled. There are no artifact uploads, cache actions, package publications or code-scanning
uploads. The publishing and receiving jobs have 15- and 5-minute time limits.

The publisher uses the official Scorecard action
[`v2.5.0`, pinned to `fa7117db83c52d787ae5a89f350999701505d78e`](https://github.com/ossf/scorecard-action/tree/fa7117db83c52d787ae5a89f350999701505d78e).
Its only other step is the SHA-pinned checkout with credential persistence
disabled. Contents permission is read-only; only the publisher has
`id-token: write`. This permission permits requesting an OIDC identity token,
[not writing repository contents](https://docs.github.com/en/actions/reference/security/oidc#required-permission).
The separate receiving job has only `contents: read`.

Publishing is a public data operation. The action uses GitHub OIDC and Sigstore
to sign the result and place an attestation in the public Rekor transparency
log. It sends the result, log reference and short-lived default `GITHUB_TOKEN`
to the official Scorecard API for verification. That token is scoped here to
read-only repository contents; no PAT or repository secret is supplied. The
[API data is published under CDLA Permissive 2.0](https://github.com/ossf/scorecard/blob/34496c8af50df71ce3d78b7380c27ddf83e012b9/README.md#scorecard-rest-api).
These are public repository observations, not private case or customer data.

The action SHA pins its metadata, but that metadata loads the container image
`ghcr.io/ossf/scorecard-action:v2.5.0` by tag. That upstream image reference is
not digest-pinned. A successful source review does not establish immutable
container bytes; retain the resolved image identity from the actual run when
reviewing execution. No complete third-party dependency audit is claimed.

## Receiving checks and freshness

In this stable release, a failed API upload can produce a warning while the
analysis step remains green. Consequently, the separate
[receiving script](../.github/scripts/verify_scorecard.py) makes an unauthenticated
GET to the fixed official API, using `?commit=` with the full triggering SHA.
It also requires the response body's exact repository and commit, a finite
aggregate score within 0–10, and nonempty named check records with integer scores. It permits an
individual check score of `-1` as inconclusive, and accepts an aggregate of
zero: this is a publication check, not a numerical quality gate.

The script rejects malformed, duplicate-key, non-finite, oversized or
identity-mismatched responses. It refuses redirects, accepts responses up to
1 MiB (reading at most one extra byte to detect oversize) and
uses a 20-second socket timeout. Missing results and temporary HTTP/network
failures receive at most six attempts, with 15-second pauses; the job timeout
bounds the overall run. Invalid content fails immediately. The
[offline tests](../tests/test_scorecard_publication.py) use controlled responses
and never query the API.

The action analyses the latest default-branch state, which can advance after a
workflow is triggered. The API's commit-addressed storage key can follow the
workflow identity while the result body identifies the analysed source. Both
identities therefore matter. A newer push can cause an older run to fail our
exact-commit check; that is an explicit mismatch, not evidence of insecure code.
Concurrency cancels superseded runs where possible, but does not eliminate this
race. Do not loosen the expected SHA to obtain a green result.

The receiving check establishes that an official API result exists for the
expected source. It does not independently verify Sigstore signatures or prove
that this particular workflow run created the result: the API may already have
a matching result, including from its scan store. The README Scorecard badge
shows the **latest** public result, not the commit-addressed response. Inspect
its linked report's source and date separately at delivery. Without a new main
push, no new scan is scheduled by this workflow, and the displayed result can
age as dependencies or repository settings change.

Classic branch-protection settings may not be visible to the default token.
Retain that limitation rather than adding an administrative PAT just to change
a score. Review individual findings against the project's actual requirements;
do not add artificial contributors, releases or settings changes for points.

## Maintenance and archive boundaries

The maintenance caller and dated archive workflow deny token permissions by
default. Their existing jobs declare the access each operation needs:

| Job | Token scopes | Purpose |
| --- | --- | --- |
| Maintenance | `contents: read`, `actions: write`, `issues: write` | Check out source, retry eligible failed runs and maintain the remediation issue. |
| Dated archive | `contents: write` | Read the existing archive release or create the already-authorised dated snapshot when absent. |

This limits permission inheritance by future jobs. It preserves the necessary
scopes of the current jobs; Scorecard can still flag those writes. The
[GitHub permission rules](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#permissions)
and [reusable-workflow rules](https://docs.github.com/en/actions/reference/workflows-and-actions/reusing-workflow-configurations#supported-keywords-for-jobs-that-call-a-reusable-workflow)
describe these boundaries.

The maintenance caller pins its shared workflow to the reviewed
[commit `e80498f303a515353dc5678941a727e0e473cbde`](https://github.com/Albertito-AI/Albertito-AI/blob/e80498f303a515353dc5678941a727e0e473cbde/.github/workflows/atlas-flexible-zero-fail.yml),
the same definition used by successful [run 43672524624](https://github.com/Albertito-AI/symbolon/actions/runs/43672524624).
Changes to that repository's `main` branch no longer replace the called
definition automatically. Review the shared workflow and its dependencies,
preserve the required permissions, and verify a native maintenance run when
updating this pin. The shared workflow still checks out the caller's source;
the pin does not freeze Symbolon, hosted runners or every transitive dependency.
The existing maintenance schedule and monthly Dependabot configuration remain.

Editing the archive workflow itself triggers its main-branch job. Its existing
release check must retain `archive-2026-11-13` when present. Verify the actual
job log and unchanged release/tag identity after such edits; a green job alone
does not prove that no release was created or replaced.

## Sources and reversal

The reviewed upstream sources are the stable action's
[metadata](https://github.com/ossf/scorecard-action/blob/fa7117db83c52d787ae5a89f350999701505d78e/action.yaml),
[signing/publication implementation](https://github.com/ossf/scorecard-action/blob/fa7117db83c52d787ae5a89f350999701505d78e/signing/signing.go),
[supported workflow restrictions](https://github.com/ossf/scorecard-action/blob/fa7117db83c52d787ae5a89f350999701505d78e/README.md#workflow-restrictions),
and the current API's
[workflow verifier](https://github.com/ossf/scorecard-infra/blob/655baf79190465b9aa83c9885d5b0212e44d32f8/api/app/server/verify_workflow.go)
and [result lookup](https://github.com/ossf/scorecard-infra/blob/655baf79190465b9aa83c9885d5b0212e44d32f8/api/app/server/get_results.go).
Newer unreleased action options are not configured here.

To stop future scans, remove `scorecard.yml`; the receiving script/tests and
badge documentation can then be removed together. This does not erase already
published Scorecard results or public transparency-log attestations. It changes
no existing CI, release, Wiki or maintenance workflow, and no Symbolon runtime
or dated contract schema.
