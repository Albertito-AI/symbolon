<!-- atlas-whitepaper:managed:v1 -->

# Symbolon: making machine work answerable to an agreement


## Abstract and scope

Symbolon studies a bounded procurement problem: how to connect agreed acceptance conditions, delivered data, accountable review and a reconstructable transfer decision. Its contribution is an inspectable reference workflow using synthetic TEST units, not a general proof of work quality or an operating marketplace. This paper distinguishes internal consistency, source truth and authority; demonstrates why a structurally valid invoice may still fail its reference; and proposes an evaluation that counts both buyer errors and provider burdens. Source inspection and existing tests support implementation claims. Commercial benefit, fair outcomes and production readiness remain research questions.

This revision was prepared on 15 November 2026 against the exact source revision identified below. It adds static source analysis and reproducibility instructions; it reports no newly executed software test, independent review or customer result.

## Thesis

An economy of software agents needs more than the ability to request and deliver work. It needs a way to say what was agreed, what counts as delivery, what was checked, what remains disputed and why a transfer is permitted. Symbolon's central proposal is that these questions should share an inspectable transaction record. The objective is a world in which small providers can demonstrate reliable work and buyers can question defective work without depending entirely on a platform's private account of events.

This is a design whitepaper prepared for Albert Tan Sin Hon with AI assistance, dated 2 November 2026. It synthesises the inspected project and proposes future directions. It is not an independent evaluation, legal opinion, offer of financial services or claim of deployed agent commerce. The present implementation uses non-redeemable TEST units.

## First principles: an output is not yet an accepted obligation

Three distinctions organise the project. First, producing an artifact differs from satisfying a contract. A valid JSON invoice may contain an invented debt. Second, checking a result differs from deciding who has authority to accept it. Third, recording a transfer differs from moving real money or resolving a legal dispute. Collapsing these distinctions would make an attractive demo and an unreliable institution.

The useful unit is a versioned agreement with named roles, a defined output, acceptance procedure, price, bond, deadlines and challenge conditions. Agreement must precede evaluation: changing the reference answer after delivery changes the bargain. A digest binds particular bytes, while an acceptance profile explains which properties of those bytes matter. Neither alone authenticates the underlying facts.

Consider a small supplier asked to extract invoice totals. An exact-reference task can establish whether the supplied result matches a known answer. A source-backed task additionally needs the original document, traceable locations, treatment of unreadable entries and a way to contest the reference. The latter is the commercially interesting problem; the current `exact-json-v1` sandbox establishes a narrower foundation.

## Fundamental logic: agreement, evidence and balanced state

The implemented path connects acceptance, funding, delivery, verification, a challenge window and settlement. A failed comparison opens a dispute. Silence does not make unverified work acceptable, and a failed check does not automatically confiscate a bond. Nondelivery and dispute resolution have explicit recorded paths.

Balanced postings provide an accounting invariant: for each supported transfer, value debited and credited must reconcile. Atomic SQLite transactions and conflicting-retry rejection protect local consistency. They do not create a trustworthy payment institution. A privileged database administrator remains within the trust boundary, and caller-supplied identities and time remain assertions.

Evidence bundles bring the agreement, event history, journal and reproduced checks together. A recipient should be able to reconstruct the decision rather than accept a green badge. A hash retained independently can expose later alteration; a hash stored beside editable evidence cannot protect against replacement of both. The next evidence format should reveal the relevant transaction without disclosing an entire shared customer ledger.

## Operational definitions and a worked counterexample

An **acceptance profile** is the versioned rule used to judge a delivery. An **evidence bundle** records the inputs and history needed to check that rule's application. A **trust anchor** is a digest or key retained through a separately trusted route. **TEST settlement** is a state transition and balanced local accounting entry; it is not discharge of a real debt.

Consider the following synthetic invoice, also used in the verification tests:

```json
{"invoice_id":"I-1","currency":"TEST","items":[{"line_id":"L1","quantity":2,"unit_minor":100}],"total_minor":200}
```

The arithmetic is 2 × 100 = 200. The invoice checker tests required fields, types, line identifiers and the total. When an expected reference is supplied, it additionally compares content digests.

| Delivery | Structural/arithmetic check | Against the original reference | What follows |
| --- | --- | --- | --- |
| Original invoice | Pass | Pass | Supported fixture checks agree |
| Only total changed to 100 | Fail | Fail | Arithmetic and reference disagree |
| Only identifier changed to `I-2` | Pass | Fail | Plausible structure is insufficient for this agreement |
| Original invoice with invented underlying debt | May pass | May pass | The checker has no source evidence establishing the debt |

The first three outcomes are specified in [tests/test_verification.py](https://github.com/Albertito-AI/symbolon/blob/007a8f3cadfec5700ed52db967b90ad9c6597f85/tests/test_verification.py); the fourth is a logical counterexample to treating conformance as truth. Reordering object members preserves the local content digest, while changing an integer to a Boolean does not. The bounded parser rejects duplicate keys, floats and excessive size/depth. These are deliberate profile restrictions, not support for arbitrary JSON or proof of RFC 8785 conformance.

## Reproducibility and claim-evidence map

In a separate checkout, select source revision `007a8f3cadfec5700ed52db967b90ad9c6597f85` before running the following commands from its root. Python 3.11 or later and the standard library are sufficient. Choose a fresh output directory.

```sh
PYTHONPATH=src python -m symbolon demo --output artifacts/paper-review
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m symbolon verify-bundle artifacts/paper-review/accepted-evidence.json --expected-sha256 YOUR_RETAINED_DIGEST
```

Replace the digest placeholder with the accepted bundle digest retained separately during the run. Retaining it alongside editable evidence is only a demonstration convenience. Record commit, Python/SQLite versions, commands, exit status, failures and digest custody. This paper's revision did not execute these commands. The older [docs/demo/README.md](https://github.com/Albertito-AI/symbolon/blob/007a8f3cadfec5700ed52db967b90ad9c6597f85/docs/demo/README.md) records a particular executed run and its environment; its counts are not fresh measurements of this revision.

| Claim | Inspectable source or test | Evidential boundary |
| --- | --- | --- |
| Exact reference differs from structural validity | [src/symbolon/verification.py](https://github.com/Albertito-AI/symbolon/blob/007a8f3cadfec5700ed52db967b90ad9c6597f85/src/symbolon/verification.py); `test_exact_reference_is_stronger_than_schema` in [tests/test_verification.py](https://github.com/Albertito-AI/symbolon/blob/007a8f3cadfec5700ed52db967b90ad9c6597f85/tests/test_verification.py) | No invoice authenticity or legal debt finding |
| Identical retries do not create a second transfer; conflicting retries are rejected | [src/symbolon/ledger.py](https://github.com/Albertito-AI/symbolon/blob/007a8f3cadfec5700ed52db967b90ad9c6597f85/src/symbolon/ledger.py); retry and concurrency cases in [tests/test_ledger.py](https://github.com/Albertito-AI/symbolon/blob/007a8f3cadfec5700ed52db967b90ad9c6597f85/tests/test_ledger.py) | Local database behaviour, not distributed payment finality |
| A failed comparison is retained through an explicit dispute path | [src/symbolon/contracts.py](https://github.com/Albertito-AI/symbolon/blob/007a8f3cadfec5700ed52db967b90ad9c6597f85/src/symbolon/contracts.py); [docs/demo/README.md](https://github.com/Albertito-AI/symbolon/blob/007a8f3cadfec5700ed52db967b90ad9c6597f85/docs/demo/README.md) | Fictional identities, time and TEST balances |
| A recipient can check a retained bundle | [src/symbolon/evidence.py](https://github.com/Albertito-AI/symbolon/blob/007a8f3cadfec5700ed52db967b90ad9c6597f85/src/symbolon/evidence.py); [tests/test_evidence.py](https://github.com/Albertito-AI/symbolon/blob/007a8f3cadfec5700ed52db967b90ad9c6597f85/tests/test_evidence.py) | Trust in an independently retained digest remains external |

## Related work and the boundary of this contribution

[SQLite's transaction documentation](https://www.sqlite.org/lang_transaction.html), sections 2.1–2.2, describes its single simultaneous writer and explicit transaction modes. This supplies the storage mechanism, not the correctness of Symbolon's business rules. Atomic execution can preserve a mistaken rule perfectly.

[Rundgren, Jordan and Erdtman, RFC 8785 (June 2020)](https://www.rfc-editor.org/rfc/rfc8785), sections 3.1–3.2, defines a particular canonical JSON representation for repeatable cryptographic operations. Symbolon's restricted local representation serves a related purpose but is not claimed to implement that specification. Interoperable evidence would require a separately versioned encoding contract and cross-language vectors.

[Moreau and Missier, PROV-DM (W3C Recommendation, 30 April 2013)](https://www.w3.org/TR/2013/REC-prov-dm-20130430/), abstract and section 2, distinguishes entities, activities and responsible agents. This offers a vocabulary for future evidence exchange. Symbolon's current bundle is not a PROV export, and a provenance representation is not itself independent authentication. These sources frame design choices; they do not establish novelty or superiority over commercial systems.

## The hard question is the acceptance profile

Verification cost can consume the benefit of outsourcing. A profile that checks only easy formatting is cheap but weak; a profile requiring complete expert re-performance may be robust but economically pointless. Symbolon should therefore treat acceptance profiles as products with stated domains, failure modes and cost, rather than as universal truth machines.

For source extraction, a strong profile would distinguish correct, defective and indeterminate cases; preserve the original task and sources; resist selective omission; and report the reviewer work still required. Independently labelled examples should include ambiguous documents, mistaken reference labels and adversarially plausible outputs. It should be possible to contest the verifier itself without losing the evidence trail.

Collateral deserves similar discipline. A larger bond may deter some misconduct while excluding competent providers with little capital. An audit rate that appears economically optimal under one error model can be unfair under another. Economic illustrations must expose false positives, capital constraints and assumptions about recovery. No mathematical incentive calculation supplies consent, enforceability or institutional legitimacy.

## Aim, hope and social value

The immediate aim is reliable handover of one bounded kind of machine work. The larger hope is portable accountability: a freelancer, small enterprise or public-interest organisation can demonstrate quality without surrendering its relationships and history to a dominant intermediary. Evidence portability can make switching providers less costly and disagreements more specific.

That benefit is conditional. Cheap automated evaluation could otherwise become automated rejection, with marginalised providers unable to challenge an opaque reference. The design should retain accessible explanations, proportionate evidence requirements, human escalation and room for novel valid solutions. Success means fewer unresolved defects and fairer resolution at an acceptable total cost, not simply more transactions or more collateral locked.

## Ideal progression and wishlist

| Stage | Desired capability | Evidence required to advance |
| --- | --- | --- |
| Inspectable sandbox | Reproducible accounting and decision history | Fresh-user reproduction, adversarial cases and clear trust limits |
| Useful acceptance profile | Source-backed extraction with explicit uncertainty | Held-out labels, defect and abstention rates, whole-workflow review effort |
| Portable trust | Selective evidence, authenticated roles and independently retained checkpoints | Privacy review, key rotation/revocation and independent verifier interoperability |
| Authorised shadow operation | Compare proposed outcomes with an existing permitted process | Accountable participants, agreed scope, dispute handling and documented failures |
| Scoped production | Reliable service and any separately authorised payment integration | Security, operational recovery, applicable legal review and repeat demand |

The ideal wishlist includes interoperable profiles, accessible dispute dossiers, evidence minimisation, alternative verifiers, reproducible economic assumptions and migration between operators. A2A, MCP, x402, MPP and card interfaces remain integration proposals requiring conformance work. A protocol badge must not outrun the implemented contract.

## How the thesis could fail

A pilot should compare the entire process with ordinary review: specifying the task, preparing sources, checking results, handling disagreements and recovering from failures. Measure defects missed, valid work wrongly rejected, review time, provider burden and fully costed delivery. Preserve indeterminate outcomes and all failed attempts. If reference preparation costs more than the avoided work, or challenge procedures routinely disadvantage smaller providers, the scope or mechanism should change.

The best case is an accountable substrate for useful cooperation. The project should remain willing to discover that a simpler agreement, checklist or human review process is better for a particular task. That is a result, not a failure of ambition.

## Research design and teaching use

A useful study would prelabel a held-out set of synthetic or properly authorised source documents, including unreadable fields, plausible false totals, valid alternatives and mistaken reference answers. Compare the full Symbolon-assisted workflow with ordinary review under the same task criteria. Record reference-preparation time, false acceptance, false rejection, abstention, challenge outcomes and costs separately for buyer and provider. Define how unresolved disagreements will be adjudicated before seeing results. A lower average review time is insufficient if the process merely transfers work or error to weaker participants.

For teaching, ask a learner to explain why `I-2` can be structurally valid yet unacceptable under the fixed reference; construct a false invoice that passes; and identify which additional evidence would be needed to challenge it. A second exercise is to replace both a bundle and its adjacent digest, then explain the missing trust relationship without calling the hash algorithm broken. Assessment should reward precise limits and reproducible reasoning, not confident approval.

## Inspected foundation and status

Current implementation assessment: [`007a8f3cadfec5700ed52db967b90ad9c6597f85`](https://github.com/Albertito-AI/symbolon/tree/007a8f3cadfec5700ed52db967b90ad9c6597f85), inspected 15 November 2026. The original foundation baseline below is retained as a historical record. Links in the added claim-evidence map identify the current assessed source. This documentation revision changes no implementation, licence, operating permission or release gate.

Source baseline: [`925f00fb06780bc35a039884126f4f8c06c5d1d1`](https://github.com/Albertito-AI/symbolon/tree/925f00fb06780bc35a039884126f4f8c06c5d1d1). Read the [README](https://github.com/Albertito-AI/symbolon/blob/925f00fb06780bc35a039884126f4f8c06c5d1d1/README.md), [architecture](https://github.com/Albertito-AI/symbolon/blob/925f00fb06780bc35a039884126f4f8c06c5d1d1/docs/architecture.md), [economic limitations](https://github.com/Albertito-AI/symbolon/blob/925f00fb06780bc35a039884126f4f8c06c5d1d1/docs/economics.md) and [roadmap](https://github.com/Albertito-AI/symbolon/blob/925f00fb06780bc35a039884126f4f8c06c5d1d1/docs/roadmap.md). These records govern implemented scope. Original project licensing remains Apache-2.0; this paper changes no licence, financial authority or release gate.
