<!-- atlas-whitepaper:managed:v1 -->

# Symbolon: making machine work answerable to an agreement

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

## Inspected foundation and status

Source baseline: [`925f00fb06780bc35a039884126f4f8c06c5d1d1`](https://github.com/Albertito-AI/symbolon/tree/925f00fb06780bc35a039884126f4f8c06c5d1d1). Read the [README](https://github.com/Albertito-AI/symbolon/blob/925f00fb06780bc35a039884126f4f8c06c5d1d1/README.md), [architecture](https://github.com/Albertito-AI/symbolon/blob/925f00fb06780bc35a039884126f4f8c06c5d1d1/docs/architecture.md), [economic limitations](https://github.com/Albertito-AI/symbolon/blob/925f00fb06780bc35a039884126f4f8c06c5d1d1/docs/economics.md) and [roadmap](https://github.com/Albertito-AI/symbolon/blob/925f00fb06780bc35a039884126f4f8c06c5d1d1/docs/roadmap.md). These records govern implemented scope. Original project licensing remains Apache-2.0; this paper changes no licence, financial authority or release gate.
