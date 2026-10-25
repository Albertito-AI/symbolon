# Legal design and deployment boundaries

This document translates the report into design requirements. The reference project demonstrates contracting records and simulated settlement. It does not establish a licensed payment service, binding legal identity, insurance coverage or a legally recognised arbitration process. The launch requirements below are recommendations for a future deployment, rather than claims about capabilities already implemented.

## Operators and authority

Singapore's Electronic Transactions Act 2010, section 15, recognises contracts formed through automated message systems without requiring human review of every action. That rule removes a particular objection to electronic formation; it does not resolve capacity, authority, incorporation of terms, mistake or illegality. An agent identifier should therefore be linked to the actual contracting person or entity and to the mandate effective when the agreement was formed. Preserve the agreed terms, authority limits, relevant versions and acceptance event. [Singapore Statutes Online](https://sso.agc.gov.sg/Act/ETA2010?ProvIds=pr15-).

The original report substantially describes *Quoine Pte Ltd v B2C2 Ltd* [2020] SGCA(I) 2 correctly. The majority considered deterministic algorithms and the programmer's relevant knowledge between programming and contract formation, particularly paragraphs 97–103. Paragraph 105 distinguishes actual knowledge for common-law unilateral mistake from constructive knowledge together with unconscionability in equity. Applying that reasoning to language-model agents requires analysis of the actual system and facts. A signature or prompt log does not itself settle attribution or mistake. [Judgment](https://www.elitigation.sg/gd/s/2020_SGCAI_2).

## Collateral and remedies

The most consequential omission in the original report is the enforceability of automatic bond forfeiture. In *Denka Advantech Pte Ltd v Seraya Energy Pte Ltd* [2020] SGCA 119, paragraphs 151–155 and 185, the Court of Appeal retained the compensatory approach to contractual penalties. A forfeiture triggered by breach and calibrated mainly to deter cheating may require scrutiny even if its mathematics is sound. Collateral secures an obligation; depositing it does not establish that the whole amount is owed. [Judgment](https://www.elitigation.sg/gd/s/2020_SGCA_119).

Recommended behaviour is to record a failed check, preserve the evidence and place the outcome into a review or dispute process. Separate refunds, compensation, agreed liquidated damages and release of unused security. Record reasons and provide a correction route for verifier error. Do not describe a private reviewer as an arbitrator without an applicable arbitration agreement and procedure. Platform terms cannot conclusively exclude statutory duties or third-party claims merely by allocating responsibility between participants.

## Money and risk transfer

The Payment Services Act 2019 requires analysis of the actual payment service, relevant definitions, exclusions and exemptions. Using a licensed custodian can reduce operational risk, but does not automatically exclude the marketplace's own instructions, transfer facilitation or digital-token activity from regulation. The original report already acknowledges this qualification and it should remain explicit. Before any real-money deployment, map the complete funds flow and each party's contractual role, licensing position and insolvency treatment. [Act and First Schedule](https://sso.agc.gov.sg/Act/PSA2019?ProvIds=Sc1-).

The report's US chronology is supported by the OCC's own Bulletin 2026-50, dated 21 October 2026. It announces a final GENIUS Act rule for entities within OCC jurisdiction, effective 18 January 2027, and separates Bank Secrecy Act, anti-money-laundering and sanctions rulemaking. This is not a general authorisation for an agent marketplace to handle stablecoins. [OCC bulletin](https://occ.gov/news-issuances/bulletins/2026/bulletin-2026-50.html).

Charging a risk premium while promising to absorb customers' losses introduces a separate insurance or guarantee question. Treat insurer partnerships and underwriting as later legal and commercial work. The initial software should use simulated units and should not offer custody, investment returns or compensated risk transfer.

## AI regulation and data

The European Commission's AI Act Service Desk reproduces Article 113 as amended by Regulation (EU) 2026/1744. It confirms 2 December 2027 for the specified Annex III high-risk obligations and 2 August 2028 for the corresponding Annex I obligations. It also identifies added prohibitions applicable from 2 December 2026. The report's principal amended dates are therefore supported, but a statement that all prohibitions have applied since February 2025 needs qualification. Determine the system's intended purpose and each actor's actual role; a marketplace label does not establish compliance or exemption. [Article 113](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-113).

Singapore's IMDA announced its Model AI Governance Framework for Agentic AI on 22 January 2026. Mandates, limits and human escalation are relevant implementation measures, but alignment with voluntary guidance should not be advertised as official certification. [Official announcement](https://www.imda.gov.sg/resources/press-releases-factsheets-and-speeches/press-releases/2026/new-model-ai-governance-framework-for-agentic-ai).

Hashing does not automatically anonymise personal data. Linkable identifiers, predictable source material and retained lookup information may keep an evidence record within data-protection law. Keep substantive evidence access-controlled, minimise public metadata and define retention, deletion and lawful disclosure rules. An integrity proof establishes a relationship between bytes and a trusted checkpoint; it does not establish the truth of a statement, the author's legal identity or admissibility in every forum. See the EDPB's [pseudonymisation summary](https://www.edpb.europa.eu/system/files/2025-02/edpb_summary_202501_pseudonymisation_en.pdf), page 1, and assess the applicable law and recipient context before disclosure.

## Gates before a commercial pilot

Use a narrow class of business tasks with objective acceptance criteria, an identified operator for every participant, a documented complaints process and caps on outstanding exposure. Obtain jurisdiction-specific review of the terms, bond remedy, money flow, privacy roles and any insurance promise. Reconcile internal records against the payment partner, distinguish reversible payment events from final settlement, and reserve collateral across all concurrent obligations. These are prerequisites for evaluating a live service. They do not prevent development, simulation or local conformance testing now.
