"""Strict loader for the first dated, deliberately narrow contract envelope."""

from dataclasses import fields
from .contracts import Contract

SPEC_VERSION = "2026-10-25.alpha1"


def parse_contract(envelope):
    required = {"spec_version", "asset", "acceptance_profile", "contract"}
    if not isinstance(envelope, dict) or set(envelope) != required:
        raise ValueError("unexpected or missing envelope fields")
    if envelope["spec_version"] != SPEC_VERSION:
        raise ValueError("unsupported contract specification version")
    if envelope["asset"] != "TEST" or envelope["acceptance_profile"] != "exact-json-v1":
        raise ValueError("only TEST units and exact-json-v1 are implemented")
    terms = envelope["contract"]
    if not isinstance(terms, dict) or set(terms) != {f.name for f in fields(Contract)}:
        raise ValueError("unexpected or missing contract fields")
    return Contract(**terms)

