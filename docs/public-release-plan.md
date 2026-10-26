# Public release and market entry

Decision paper: 25 October 2026. Working name: Symbolon.

**Publication status update, 26 October 2026:** The original [`Albertito-AI/symbolon`](https://github.com/Albertito-AI/symbolon) repository is public as an experimental reference implementation. Repository visibility is distinct from a tagged software release, hosted deployment, independent operator evaluation, or a paid customer engagement. The planning stages and their original 25 October context are retained below; remaining release and commercial gates still require their own evidence.

**Recommendation: publish a carefully reviewed experimental core soon, then expand promotion as independent usage and measured customer value develop.** Aim for a modest public alpha in the next seven days if the publication gates are satisfied. The date is a planning target, subject to the existing development priorities. At the time of this 25 October decision paper, the repository remained private. That planning exercise did not itself record a visibility change, public announcement, customer engagement or paid sale.

## What should become public

Use one canonical public code repository for the reference implementation, synthetic fixtures, tests, architecture, research corrections, contribution guidance and release history approved for publication. Keep the original private report, internal archive index, prospect identities, contracts, payment records, client data and confidential commercial discussions in the existing private project archive. A later hosted service may have private operational components; no such service exists today.

Prefer the current repository if its complete publication surface is suitable. If historical material must remain private, publish a reviewed snapshot in a new public code repository and preserve the existing private archive. Do not erase history or change licences to avoid an unresolved disclosure decision. Maintaining two active codebases would add unnecessary work, so any clean export should identify one canonical development destination.

Changing a GitHub repository from private to public exposes code and Actions history and logs; public forks can remain public even if the original becomes private later. Review the intended release as a durable disclosure. GitHub's visibility documentation describes those consequences [S1].

The intended public tree, history, issues, workflow records and release artefacts require a bounded publication review. Removing private archive navigation from the current tree does not remove earlier committed references. Keep the detailed review record privately. The final release record should identify the reviewed revision, scope and remaining limitations.

## What the alpha actually establishes

The recorded baseline is 66 passing local tests and hosted validation on Python 3.11, 3.12 and 3.13 at [commit 7642dd2](https://github.com/Albertito-AI/symbolon/commit/7642dd2d6ad7a7bd45776f8e2c58c44ac124c406), with [Actions run 40188384075](https://github.com/Albertito-AI/symbolon/actions/runs/40188384075). A separate package check built a wheel from that tracked source tree, installed it into a clean virtual environment and ran the installed demonstration and evidence verifier outside the checkout. That is an engineering check by an AI-assisted reviewer, not evidence of independent customer adoption.

The alpha demonstrates local task terms, deterministic fixture acceptance, synthetic accounting, disputes and evidence reconciliation. It does not implement authenticated external operators, real payments, a live marketplace, an extraction engine, signed evidence or a working external protocol adapter. Its exact-output rule requires a known reference. Structural invoice checks do not establish source accuracy, the genuineness of an invoice or an obligation to pay. The exported journal is synthetic and not suitable for disclosing a shared customer ledger.

A defensible current description is: **an experimental contract, verification and evidence core for machine work**. For a practical explanation, show how an agreed structured delivery is checked, how a failed check is explained, and how the decision record can be reproduced. Describe source-backed acceptance and authenticated authority as planned work until implemented and tested.

## Market position to test

The strongest initial hypothesis is a small toolkit for agreed acceptance rules and portable handover evidence across a supplier and buyer. A potential user already has an extraction or automation system but struggles to specify completion, inspect exceptions and reconstruct why a delivery was accepted. This is a proposed niche, not a demonstrated market gap or novelty claim.

| Existing capability | Current primary evidence | Implication for our next experiment |
| --- | --- | --- |
| General evaluation and observability | Langfuse describes MIT-licensed product capabilities with commercial enterprise modules; DeepEval documents application and agent evaluation [S4, S5]. | Test whether the cross-party acceptance record adds value beside an existing evaluation tool. |
| Invoice extraction | Google Document AI documents a generally available Invoice Parser covering header and line-item fields [S6]. | Use an existing extraction system where appropriate. Measure acceptance and review value separately from extraction performance. |
| Agent agreements, payment and evaluation | Virtuals describes signed agreements, escrow and evaluation in Agent Commerce Protocol [S7]. | Compare the actual handover problem and evidence requirements. Do not claim that contractual coordination or evaluation is absent from the market. |

These sources establish advertised capabilities, not independently tested competitor performance. The simplest serious comparator is also the buyer's existing script, spreadsheet and manual review. If that already achieves the required outcome more cheaply, record the result and reconsider the product.

Start with small B2B automation suppliers and data operations teams handling recurring structured-document deliveries. Seek the person accountable for review effort, corrections and the budget. Keep the first task family narrow, such as one agreed record schema for an authorised batch. Establish whether the recurring problem is missing records, inconsistent totals, invalid references, poorly explained rejection or evidence preparation. Defer legal-merits judgments, open-ended autonomous work and payment custody from the first offer.

## Release and launch gates

| Stage | Planning window | Evidence required | Permitted next step |
| --- | --- | --- | --- |
| Publication preparation | Days 1–7 | Approved tree and history; working quick start; selected alpha revision with passing CI; licence and provenance review; working issue and confidential reporting routes; accurate limitations. | Owner decides whether the prepared release should become public. |
| Quiet public alpha | After publication approval, ideally in week one | Runnable synthetic example, accepted and rejected cases, reproducible record, clear contribution tasks and maintainer capacity. | Share the implemented experiment through the owner's chosen channels and invite reproduction. |
| Useful workflow validation | Days 8–45, depending on gates | R02 source acceptance profile; declared defect corpus and unresolved judgments; three independent people reproduce the advertised workflow; prospective buyers describe a recurring problem. | Publish measured technical results and prepare one bounded service offer. |
| Focused launch and scoped engagements | Days 31–60 when ready | Clear audience and value claim, authorised samples, priced deliverables, human responsibilities, selective evidence and relevant controls. | Conduct authorised targeted promotion and seek fully prepaid scoped orders. |
| Repeatability decision | Days 61–90 | Completed paid work, actual delivery labour, buyer outcomes, positive contribution and repeat demand. | Continue, narrow, reprice or stop the offer; expand only the part supported by evidence. |

The three-user reproduction threshold applies to broader promotion. A separately scoped and fully prepaid research engagement may proceed earlier once its own delivery, data, authority and payment conditions are satisfied.

These windows and numbers are management choices, not forecasts. They supplement the [commercial validation plan](commercial-plan.md), whose selected targets include ten discovery conversations, a 100-case benchmark with at least 30 deliberate defects, three unrelated paid pilots and two repeat paid batches. The first public release need not wait for all commercial gates. A meaningful paid research or implementation phase can precede production readiness if its limited scope is honest, feasible and fully prepaid.

Before a broader launch, require at least two prospective buyers to confirm the recurring workflow problem and purchasing responsibility, and three external users to reproduce the advertised useful workflow. AI review passes and repeated internal runs do not count as those people. Treat the numbers as deliberate decision thresholds, not a claim that three users prove product-market fit.

Before accepting network submissions, implement R01's authority boundary. Before exporting real customer evidence, complete R03's selective disclosure work and the relevant data controls. Before hosting a live service, complete the applicable storage, recovery, security and operational work. Live marketplace funds require the separate R07 decision. Taking ordinary payment for a clearly scoped professional service does not mean the sandbox can hold or release client funds.

## Publication preparation checklist

- Review every intended public file, reachable commit, issue, pull request, workflow log and release artefact for rights, confidential content and inappropriate internal navigation. Include commit author identity and email metadata in the disclosure decision. The current-tree pattern scan is bounded and is not a security certification.
- Keep the original private research document out of the public source distribution. Check rights for any future dataset, screenshot, quotation or client example.
- Preserve Apache-2.0, notices and the explanation of AI-assisted development. Identify the maintainer and accurately state which checks and reviews were performed.
- Select an exact alpha commit and tag after checking the final CI run. Repeat the clean installation check at that revision; add a distribution smoke check to CI when implementing release hardening under R09.
- Show a successful example and a meaningful failure, with commands that run without paid credentials or a signup. State the supported Python versions and the TEST-only boundary.
- Verify a confidential vulnerability reporting route before inviting reports. Require passing checks when accepting external changes; do not describe unenforced review rules as branch protection.
- Review the working name before investing in a domain or a campaign. No trademark clearance has been completed.
- Obtain the owner's decision on the exact publication surface and public announcement. Record the actual visibility and release result only after success.

The project already has a licence, README, contribution guide and governance documents. GitHub's Open Source Guide identifies basic documentation and maintenance capacity as foundations for launch [S3]. A few truthful, usable assets matter more than a large promotional site.

## Promotion sequence

### Start with evidence people can inspect

Prepare four connected assets: the runnable release; a short demonstration showing an acceptance and a failure; one article explaining a concrete limitation or design choice; and one clear invitation. For the alpha, ask relevant developers to run the example and report friction. For commercial discovery, ask people responsible for recurring handovers to describe their present process. Do not advertise unmeasured savings.

Keep the repository front page direct: who the experiment is for, the present behaviour, quick start, one failure example, limitations, roadmap and an enquiry route approved by the owner. Pin the project on the owner's GitHub profile when publication is approved. Use accurate repository topics for Python, structured validation and evidence; GitHub documents their role in discovery [S8]. Do not imply MCP compatibility until a real adapter exists.

### Use a small number of relevant channels

| Channel | Contribution | Entry condition and outcome |
| --- | --- | --- |
| GitHub | Runnable release, useful issues, change records and contribution tasks. | Public alpha approved; measure successful external runs and returning contributors. |
| Professional website and LinkedIn | A practical account of the buyer problem, a short demonstration and specific questions. | Owner approves the post and destination; measure relevant enquiries and qualified conversations. |
| Evaluation, data and automation communities | A reproducible defect, small integration or useful explanation responsive to that community's work. | Respect local rules and contribute substantively; measure technical feedback and adoption. |
| Show HN | A substantial workflow that people can try, with the owner available to discuss its development. | Wait for the useful source acceptance workflow and independent reproductions. Follow the site's rules [S9]. |
| MCP Registry | Accurate metadata for an actual publicly available MCP server. | Implement and test the server first. Registry discovery is not a security certification [S10]. |

Show HN permits early work but expects a non-trivial personally developed project that others can try. It discourages quickly generated one-offs, landing pages, routine minor-update submissions and solicited upvotes [S9]. Prepare the owner to explain the work, its AI assistance and its limitations accurately. A report or a plan alone is not an appropriate Show HN submission.

The MCP Registry is currently described as preview and is a metadata service for public servers. It distinguishes authenticity of a namespace from a security review [S10]. It is a later distribution option, not an immediate launch asset for the current Python sandbox.

Aim for one substantive public update per week when there is a result worth showing. A useful sequence is a working example, a documented failure and correction, a measured comparison, then an authorised case study. Respond to substantive questions before increasing posting volume. Avoid paid advertising during initial problem validation; spend effort on the demonstration and a small number of relevant conversations. No outreach, posting, registry submission or spending occurs merely because this plan exists.

## Converting attention into paid work

### First offer

Test an **acceptance profile and evidence handover engagement** for one recurring record type. Define the schema, enumerated checks, representative good and defective examples, source references, test commands, human-review boundary and handover document. A buyer pays for translating its requirements into a maintained, reproducible workflow. The public toolkit helps the buyer inspect the approach.

Potential later offers are a bounded verification benchmark, integration into an existing pipeline, a training workshop and a limited support agreement. Hosted operation, recurring assurance fees and marketplace commissions require separate evidence and operating capacity. Do not build them merely to create a subscription.

Quote from scope, preparation, implementation, qualified review, revisions, support, infrastructure and risk. Use a declared labour rate and compare the quote with the buyer's present review and correction cost. The first accepted quote is a demand observation; it is not a general market price. No fixed fee, conversion rate, market size or revenue forecast is established in this plan.

### Qualification and payment

Before bespoke work, verify the real buyer or legal entity, an accountable human representative, authority to commission the work, lawful and ethical intended use, budget, and rights to provide the material. Agree deliverables, exclusions, acceptance conditions, correction allowance, timetable, data treatment, intellectual-property terms and price.

**No customer-specific benchmark, compatibility test, executable, evaluation pack, implementation or other bespoke deliverable begins until full payment for that defined order is independently verified by the human account owner as posted and available in the seller's verified bank account.** Payment screenshots, processor status, pending funds and synthetic TEST balances do not satisfy this rule. A larger engagement may have independently scoped phases, each fully paid before that phase begins.

Discovery and scope discussions may precede payment. Use the existing reusable public synthetic demonstration to explain the method. Do not turn an unpaid discovery conversation into customised work. Delivery records remain private unless the client separately authorises a case study; permission for a job does not authorise use of the client's name, logo, data or results in promotion.

### Licence and commercial value

Retain Apache-2.0 for the reference core. It allows commercial use and redistribution subject to its terms, includes notice requirements and a defined patent grant, and does not generally grant trademark rights. Its copyright grant is irrevocable subject to its terms. The Apache FAQ confirms that modifications may be kept private and sold without a compulsory contribution back [S2, S11]. Publication therefore does not create a right to royalties from every user or prevent a competitor offering hosting.

Build the business around useful implementation, trustworthy maintenance, demonstrated domain understanding, lawful access to relevant examples and reliable service. Future separately licensed components need their own rights and product decision; a later strategy must respect rights already granted in published versions. Public source creates an opportunity for scrutiny and adoption. It does not prove that customers will pay.

## Measures, review and decisions

Track attention separately from use and commercial outcomes. Stars, followers and views show reach. Successful external installations, reproduced workflows, useful defect reports and returning users show engagement. Verified buyer problems, agreed paid scopes, completed orders, repeat work and contribution after all delivery labour show stronger commercial evidence.

Use existing issue and project records rather than creating a competing finance tracker. Keep customer identity and payment records private. Record unknown values as unknown; free trials, internal tests and promises to pay are not sales.

| Observation at review | Decision to consider |
| --- | --- |
| Readers cannot explain the project's practical use. | Improve the explanation and demonstration before buying traffic. |
| Ten relevant discovery conversations produce fewer than three recurring problems with usable evidence. | Change the task family or buyer segment before adding broad features. |
| The source profile adds no measurable value over a simple comparator. | Simplify, integrate with the existing method or stop that approach. |
| Usage rises but buyers do not allocate budget. | Revisit the economic buyer and offer; do not treat stars as demand. |
| Paid delivery has negative contribution after full labour. | Reduce scope, reprice or stop the service. |
| Buyers value verification but do not need matching or auctions. | Concentrate on the verification product and postpone the marketplace. |
| Repeat paid work supports a stable service. | Invest in the specific automation and support capacity that improves that service. |

The [continuous improvement process](continuous-improvement.md) defines daily triage and a deeper Tuesday review within the existing development routine. Review the market evidence, benchmark and user feedback together, select one bounded improvement, test it and record retain, revise, defer or stop. Publish meaningful outcomes after the appropriate publication decision. There is no daily posting or commit quota.

## Source register

Primary sources checked 25 October 2026. Most are current documentation and can change. Competitor descriptions are their own stated capabilities. The management choices and proposed thresholds above are our recommendations, not claims made by these sources.

- **S1:** [GitHub, Setting repository visibility](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/setting-repository-visibility). Code, fork and Actions exposure on visibility changes.
- **S2:** [Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0). Sections 2–9 govern the licensed rights, notices, patent and trademark boundaries and additional obligations.
- **S3:** [GitHub Open Source Guide, Starting a project](https://opensource.guide/starting-a-project/). Launch documentation, goals and maintenance capacity.
- **S4:** [Langfuse open-source handbook](https://langfuse.com/handbook/chapters/open-source). Product and enterprise licensing; not independent performance evidence.
- **S5:** [DeepEval repository](https://github.com/confident-ai/deepeval). Evaluation scope and Apache-2.0 licensing; default-branch description, not a benchmark.
- **S6:** [Google Document AI processor list](https://docs.cloud.google.com/document-ai/docs/processors-list). Invoice Parser fields and availability; suitability for our task remains untested.
- **S7:** [Virtuals Commerce Layer](https://whitepaper.virtuals.io/about-virtuals/commerce-layer). Documented agreements, escrow and evaluation; no operational assessment performed here.
- **S8:** [GitHub repository topics](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/classifying-your-repository-with-topics). Discovery mechanics; no guarantee of traffic.
- **S9:** [Show HN guidelines](https://news.ycombinator.com/showhn.html). Submission suitability and community rules.
- **S10:** [MCP Registry documentation](https://modelcontextprotocol.io/registry/about). Public-server scope, preview status and registry limits.
- **S11:** [Apache licensing FAQ](https://www.apache.org/foundation/license-faq.html). Commercial and private modifications and contribution obligations.
