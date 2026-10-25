# Initial architecture and product decisions

Decision date: 25 October 2026. These decisions describe the first reference implementation and its intended direction. Revisit them through documented proposals and measured results.

## One bounded business workflow

Begin with B2B structured extraction and verification. The buyer receives explicit acceptance results and a portable handover record. Broad discovery, auctions, insurance and a verifier marketplace depend on evidence of recurring demand. The commercial plan defines the first validation gates.

## One Python package

Use Python 3.11 or later with standard-library runtime components, including SQLite, JSON and hashing. This keeps the demonstration inspectable and easy to run. Packaging uses setuptools. The report's four-language architecture is deferred until a concrete operational requirement justifies additional components.

## TEST units only

The ledger records synthetic, non-redeemable TEST units. Its faucet demonstrates accounting and retry behaviour. It neither holds money nor establishes escrow, a financial entitlement or a payment-provider connection. Live financial operations require the separate readiness work in the roadmap.

## Agreed prices before auctions

The current service receives already agreed contract terms and a fixed price. It does not discover a market price. Posted or negotiated prices support the first pilot; auction design needs supplier participation and a comparative benchmark before adoption.

## Deterministic fixtures have a limited purpose

Exact-digest acceptance and the small invoice profile demonstrate lifecycle and verification mechanics. They check predefined content and enumerated constraints. They do not extract documents, establish source truth or prove the quality of unknown work. Versioned source acceptance profiles are planned separately.

## Checkpoints require independent trust

Evidence snapshots are unsigned. Actor strings identify local roles rather than authenticated people or organisations. Hash chains and replay checks detect inconsistencies against a trusted digest, but an operator controlling both the records and their checkpoint can rewrite both. Full-ledger exports are confined to synthetic demonstrations. Selective disclosure, signatures and independently held checkpoints remain planned work.

## Open source and working name

The intended source licence is Apache 2.0; the repository's licence file governs the actual grant. Open code supports inspection but does not itself establish neutral institutional governance, certification or commercial trust. Symbolon remains a working name. Trademark and naming clearance have not been performed.

## No native token

The project does not require a tradable token. Any later payment integration should follow an actual buyer workflow and an assessed operating arrangement. Synthetic TEST units carry no proposed conversion or redemption promise.
