# Public reference and private operations boundary

## Public repository purpose

Symbolon is the inspectable reference implementation for bounded machine-work contracts, synthetic TEST-unit accounting, acceptance checks and portable evidence. Public material may include original code, protocol specifications, synthetic fixtures, tests, research documentation and reproducible local demonstrations.

The public repository is not a production marketplace, payment service, customer ledger or identity provider.

## Material that may remain public

- generic contract and evidence schemas;
- synthetic TEST-unit scenarios and fictional actors;
- deterministic acceptance profiles suitable for public inspection;
- source code, tests, architecture notes and public interoperability proposals;
- aggregate or anonymised research findings cleared for publication.

## Material that must remain private

- customer contracts, invoices, ledgers, disputes or delivery evidence;
- real payment instructions, banking records or redeemable-value transactions;
- customer-specific acceptance policies and commercial pricing;
- private identity, onboarding, fraud, sanctions or risk records;
- API credentials, signing keys, tokens, production databases and infrastructure configuration;
- unpublished partner integrations, security incidents and restricted third-party material.

## Production split trigger

Create a private operational repository or workspace when the project first acquires a real customer configuration, payment or identity integration, non-public commercial rule, production deployment artifact or confidential dataset. Do not create an empty private clone merely because a production edition might exist later.

A public interface specification can be maintained here while its private adapter, credentials and customer configuration remain separate. Public tests should use synthetic substitutes and should not require production secrets.

## Release check

Before publication, confirm ownership and licence, inspect the full change for secrets and personal data, use only cleared examples, bound claims to observed behaviour, and verify that production or customer material is neither committed nor recoverable through generated artifacts. Removing a file from the current branch does not by itself remove it from Git history.

The Apache-2.0 licence applies to the material identified by the repository's licence and notices. Public visibility creates no payment, service, customer or institutional relationship.
