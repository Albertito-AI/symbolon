# Source audit and research corrections

Audit date: 25 October 2026, Asia/Singapore.

This audit supports the first Symbolon implementation and its commercial plan. It checks selected market, protocol and competition claims in the supplied *Clearing Machine Work Agent Marketplace Report* against primary publications. It records corrections and the limits of the evidence. It does not certify every statement or footnote in the original report, independently reproduce the cited experiments, or establish legal compliance. Legal commencement dates and jurisdictional analysis require their separate legal review.

References to numbered paragraphs identify the extracted body paragraphs of the supplied DOCX; section references make the findings usable without that extraction. The source register records what was inspected on the audit date. Pages described as current or latest can change, so implementation work should pin a released specification, dependency version and conformance fixtures.

## Required corrections

### x402 announcement and operational launch

Section 2.1, paragraph 75, says Coinbase completed its contribution of x402 on 2 April 2026. The Linux Foundation's later announcement expressly dates the operational launch and completed contribution to **14 July 2026**, describing April as the intent to launch. Table 1 should distinguish the April announcement from the July operational milestone. The foundation and contribution are real; their chronology needs correction. Use SRC03 in preference to inference from earlier reporting.

### Scope of measured agent commerce

Section 2.3, paragraphs 124–125, accurately reproduces TRM's approximate 198.9 million settlements, US$52.7 million total, US$25.62 million screened commerce and 0.6–7.5% agentic range. However, these are observations and classifications of **known x402 facilitator activity**, not measurements of all autonomous commerce. The filters exclude concentrated and thin-buyer activity; agent classification depends partly on variable prices, persistence and multiple sellers or registry evidence. TRM acknowledges that a single-purpose agent repeatedly buying one service may be classified as a script. Retain this limitation in the abstract and any market discussion. Neither this dataset nor retail forecasts establish Symbolon's addressable market. See SRC06.

### Competition and proposed differentiation

Section 2.2, paragraph 122, asserts too broadly that existing systems lack the proposed assurance functions. Virtuals documents signed agreements, escrow, evaluation against agreed terms, recorded outcomes and a specialised evaluator market. ERC-8183 specifies escrowed jobs, evaluator decisions, attestation commitments and expiry refunds, with examples of signed bidding and fee extensions. ERC-8004 explicitly describes validation registries, auditor networks and insurance pools. See SRC07–SRC09.

Replace a universal novelty claim with a testable proposition: Symbolon may make bounded procurement easier through versioned acceptance profiles, reproducible checks, recorded authority, explicit review boundaries and portable evidence. The reviewed sources establish overlap. They do not establish that a competitor offers every proposed combination, nor that Symbolon is superior. Distinguish Virtuals' **Agent Commerce Protocol** from OpenAI and Stripe's **Agentic Commerce Protocol** whenever using the acronym ACP.

### Bibliographic accuracy

The Zhu citation in section 2.4, footnote 24 and the bibliography associates arXiv:2506.00073 with a title that does not match the inspected record. Version 4 is *The Automated but Risky Game: Modeling and Benchmarking Agent-to-Agent Negotiations and Transactions in Consumer Markets*, revised 20 September 2025. Use the version-specific SRC11 URL. The findings about unequal bargaining outcomes and overspending remain supported by its abstract; this audit did not reproduce those experiments.

The Fish, Gonczarowski and Shorrer citation identifies version 5, dated 5 March 2026. That is a genuine version. The current record is version 6, dated 31 August 2026, and records acceptance at EC 2026. Either cite v5 explicitly or update the discussion and citation together to SRC12. Do not silently combine one version's date with another version's text.

### Commercial claims requiring evidence

Sections 3 and 8 should treat willingness to pay, durable margins, neutrality and supplier availability as hypotheses. Costly verification does not by itself create pricing power. An MCP endpoint count does not count willing, qualified commercial suppliers. Internal enterprise use can validate a workflow without establishing independent marketplace demand. A public repository can improve inspectability; neutral governance and institutional trust require additional evidence and practices. The commercial plan converts these assumptions into explicit experiments.

## Findings retained with qualifications

The official MCP release supports the report's account of the 2026-07-28 move to a stateless protocol core and the relocation of Tasks into an extension. A2A's specification documents task handling, Agent Cards and signatures. These are protocol capabilities, not evidence that this repository implements or conforms to them. SRC01–SRC02 support the architecture's integration direction.

Stripe's MPP announcement is dated 18 March 2026 and describes an open standard co-authored with Tempo. FIDO's 28 April announcement confirms standardisation work drawing on AP2 and Verifiable Intent. A named standard or industry working group does not establish that Symbolon has a working adapter, certified integration or commercial relationship. See SRC04–SRC05.

Microsoft's Magentic Marketplace provides a simulation framework and reports first-proposal bias. It is a useful benchmark candidate. Applying those observations to Symbolon's jobs, participants or proposed clearing rules is an inference that requires an experiment. Sealed or structured offers should not be described as proven welfare improvements before comparable trials. See SRC10.

## Primary source register

Confidence describes support for the stated finding, not confidence in a provider's entire product. All sources were accessed on 25 October 2026. Undated means no dependable publication date was established in the inspected page.

| ID | Source and publication date | Supported finding and evidential bound |
| --- | --- | --- |
| SRC01 | [MCP maintainers, The 2026-07-28 Specification](https://blog.modelcontextprotocol.io/posts/2026-07-28), 28 July 2026 | High: official release description. Pin the actual specification and SDK version before claiming conformance. |
| SRC02 | [A2A Protocol specification](https://a2a-protocol.org/latest/specification/), current documentation, undated | High: documented task, discovery and signature semantics. The latest URL is mutable. |
| SRC03 | [Linux Foundation x402 operational launch](https://www.linuxfoundation.org/press/linux-foundation-announces-operational-launch-of-x402-foundation-to-standardize-internet-native-payments-for-ai-agents-and-applications), 14 July 2026 | High: distinguishes April intent from July operational launch and completed contribution. |
| SRC04 | [Stripe, Introducing the Machine Payments Protocol](https://stripe.com/blog/machine-payments-protocol), 18 March 2026 | High: official announcement and stated capabilities. No independent performance validation. |
| SRC05 | [FIDO Alliance, Standards for Trusted AI Agent Interactions](https://fidoalliance.org/fido-alliance-to-develop-standards-for-trusted-ai-agent-interactions/), 28 April 2026 | High: standardisation initiative and contributions. Does not establish universal deployment. |
| SRC06 | [Noah Hodge, Who's Actually Paying](https://www.trmlabs.com/trm-tech-blog/whos-actually-paying-measuring-ai-agent-payments-onchain), TRM Labs, 9 September 2026 | High for faithful attribution; bounded for market inference. Proprietary cohort and behavioural classification were not independently reproduced. |
| SRC07 | [Virtuals Commerce Layer](https://whitepaper.virtuals.io/about-virtuals/commerce-layer), current documentation, undated | High for documented design overlap. Product effectiveness and transaction quality were not independently tested. |
| SRC08 | [ERC-8183 Agentic Commerce](https://eips.ethereum.org/EIPS/eip-8183), created 25 February 2026, draft at audit | High for specification content. A draft and reference implementation are not evidence of audited production reliability. |
| SRC09 | [ERC-8004 Trustless Agents](https://eips.ethereum.org/EIPS/eip-8004), created 13 August 2025, draft at audit | High for registry and trust-model design. Registries alone do not prove identity quality or truthful evaluations. |
| SRC10 | [Microsoft Magentic Marketplace repository](https://github.com/microsoft/multi-agent-marketplace) and [research paper](https://www.microsoft.com/en-us/research/wp-content/uploads/2025/10/multi-agent-marketplace.pdf), October 2025 | High for existence and reported experiments. Simulation outcomes are conditional on models, prompts, tasks and experimental design. |
| SRC11 | [Shenzhe Zhu and others, The Automated but Risky Game](https://arxiv.org/abs/2506.00073v4), version 4, 20 September 2025 | High for corrected metadata and abstract-level findings. No replication was run. |
| SRC12 | [Sara Fish, Yannai Gonczarowski and Ran Shorrer, Algorithmic Collusion by Large Language Models](https://arxiv.org/abs/2404.00806v6), version 6, 31 August 2026 | High for metadata and reported experimental claims. Does not prove collusion in this proposed marketplace. |

## Maintenance rule

Before relying on a changing source, record its version or publication date, access date, supported claim and limitation. A failed retrieval is not evidence that a claim is false. Unresolved facts should remain unresolved in the research record and should not become a product promise. A successful test of local software should be reported separately from market evidence, protocol conformance and legal readiness.
