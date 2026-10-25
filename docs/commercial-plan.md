# Commercial plan for a bounded verification pilot

Plan date: 25 October 2026, Asia/Singapore.

Symbolon's first commercial hypothesis is that a business buying recurring structured extraction can reduce review effort and avoid costly handover errors when acceptance rules and supporting evidence travel with every delivery. The first implementation is a sandbox using simulated balances. It does not collect customer funds, provide live escrow, sell insurance or establish a payment relationship. The plan below prepares a measurable pilot before those activities are considered.

The targets and timetable are management choices for testing the hypothesis. They are not forecasts, customer commitments, evidence of existing demand or claims about market size. Progress depends on exit evidence, so a missed gate changes the scope or timing rather than being hidden by a calendar deadline.

## First buyer and job family

Focus on B2B data operations teams and small service providers that repeatedly convert a known set of documents into structured records. The initial economic buyer is the person accountable for the workflow's budget and errors. Agents may perform or coordinate the work, but their existence does not create purchasing authority or demand.

A bounded job supplies a source manifest, a versioned record schema, explicit constraints and a reference set where accuracy will be measured. A provider returns structured records with source locations. The verification result identifies which checks passed, which failed and which remain for human judgment. The resulting evidence package preserves the input and output identifiers, accepted profile, verifier version and decision.

Start with non-sensitive or properly authorised test materials. A JSON schema can check structure, required fields and types. Source hashes can establish correspondence with particular bytes. Neither proves that a source is true or that an extracted proposition correctly states the law. Record semantic accuracy and human review separately; an unresolved judgment cannot silently become an accepted deterministic result.

## Product offered in the pilot

The minimum useful package is a reproducible acceptance workflow and an evidence export. It should let a buyer state requirements before submission, see the exact reason for rejection, distinguish an incomplete delivery from a failed check, and reproduce checks later. The supplier should know the requirements and permitted correction process before doing the work.

Use posted prices or a negotiated fixed batch price for the pilot. Competitive auctions are a later experiment requiring enough qualified suppliers and repeated comparable jobs. A simulated provider registry is useful for software testing but is not marketplace supply. Defer broad agent discovery, multiple payment rails, public reputation scores and an independent verifier marketplace until the initial buyer problem is demonstrated.

## Concierge benchmark before paid readiness

First observe the buyer's existing process on a representative, labelled batch. Record time spent preparing instructions, reviewing output, correcting errors and assembling handover records. Then run the same task family through Symbolon's workflow with comparable inputs and reviewers. Where possible, randomise batch order and conceal the processing route from the reviewer. Record differences in task difficulty and learning effects rather than attributing every change to the software.

The benchmark needs deliberately defective cases as well as good deliveries: omitted records, wrong types, invalid references, duplicate identifiers, arithmetic discrepancies and mismatched source hashes. Maintain a holdout set that providers cannot tune against. A verifier's sensitivity on known defect classes is not a guarantee about unfamiliar failures. Publish the denominator and unresolved cases with every performance figure.

Early concierge work may involve manual onboarding and human decisions. Measure that labour. A service that works with substantial unpriced assistance has not demonstrated a scalable software margin. Paid readiness requires a defined scope, price, correction allowance, review responsibility, retention rules and treatment of disputes. Any eventual live financial operation requires its own verified controls and legal and payment-provider readiness.

## Economics per accepted job

Separate the price of the underlying extraction work from Symbolon's own revenue. Funds notionally moved between buyer and provider in a simulation are not revenue. For an eventual commercial service, define:

`contribution = assurance revenue + billed verification revenue + allocated onboarding revenue - verification cost - support cost - payment cost - expected refund and loss cost - variable infrastructure cost - allocated onboarding cost`

Use actual staff time and a stated labour rate for manual work. Allocate one-off onboarding across a conservative number of expected jobs, and show the unallocated total alongside it. Report gross billings, platform revenue, pass-through amounts and contribution separately. Also show contribution per submitted job: reporting only accepted jobs can hide the cost of rejection and rework.

The buyer's decision depends on avoided expected error loss, review time saved and integration effort saved, less fees and additional operational burden. Ask for evidence of their present costs and an actual purchasing decision. A stated willingness to pay in an interview is weaker evidence than a paid pilot followed by a repeat order. A verification fee should therefore emerge from measured costs and buyer value rather than an assumed percentage of a large task price.

## Ninety day sequence and chosen gates

| Window | Work and chosen target | Exit evidence or response |
| --- | --- | --- |
| Days 1–15 | Interview ten people in one buyer segment; document current review workflows, error consequences and purchasing authority. | At least three identify a recurring problem, provide a representative authorised sample and agree to evaluate a benchmark. Otherwise narrow or change the task family. |
| Days 16–30 | Build a labelled challenge set and run one acceptance profile on at least 100 cases, including at least 30 deliberate defects. | All mandatory structural defects are rejected in the test set; human review boundaries and remaining failures are disclosed. Failure prompts a verifier or profile revision. |
| Days 31–45 | Complete three concierge benchmarks with independent prospective users. | Reproducible evidence exports, measured review effort and itemised operating costs. Investigate regressions and false acceptance before adding features. |
| Days 46–60 | Ask three independent users to run the documented workflow and prepare a priced pilot offer. | Users can reproduce the stated checks; scope and correction rules are understood. Claims of interoperability require separate conformance results. |
| Days 61–90 | If commercial and operational readiness is established, seek three paid pilots from unrelated buyers and two repeat paid batches. | Measure contribution and buyer outcomes. If willingness to pay or repeat demand fails, revise the offer or stop expansion. Do not count simulated settlements, free tests or related-party trades as sales. |

The 100-case benchmark is an engineering gate, not statistical certification. For example, observing zero failures in 100 independent representative trials does not prove a zero failure rate; it supports only a bounded estimate under those assumptions. Deliberately constructed defects also differ from a random sample of future production work. Keep counts, task distributions and uncertainty visible.

## Metrics and decisions

Track accepted and rejected submissions, correction cycles, false acceptance, false rejection, unresolved review decisions, median and slowest-tail review time, and reproducibility of evidence exports. For business evaluation, track unrelated paying buyers, repeat paid batches, realised revenue, support minutes and contribution. Compare results against the buyer's previous process and identify what each comparison can and cannot establish.

Exclude staff demonstrations, free trials, internal transfers and related-party activity from independent-demand metrics. Keep them in engineering statistics with clear labels. If a benchmark saves review time but adds more onboarding and support than it removes, reduce integration burden before expanding distribution. If buyers value the evidence package but do not want marketplace matching, prioritise the verification and handover product. If no buyer pays at a sustainable cost, the commercial thesis needs revision.

## Growth after demonstrated demand

Expand first to adjacent profiles for the same buyer rather than unrelated task categories. Qualified third-party suppliers become useful when buyers repeatedly request work beyond the initial capacity. Independent verifiers become useful when a measurable conflict or specialist requirement justifies their cost. Payment adapters become useful when an actual operating arrangement requires them. Each expansion should have its own acceptance evidence, cost estimate and accountable owner.

The research audit documents meaningful overlap with existing protocols and marketplaces. Symbolon's proposed advantage is operational: clear requirements, reproducible verification, controlled authority and usable evidence at a price that buyers accept. Commercial success, broader interoperability and institutional trust remain outcomes to establish through work and evidence.
