"""Deterministic validation for bounded structured work and reference fixtures.

No arbitrary code or remote URLs are executed. A profile pass attests only to
its enumerated checks. Exact reference equality is useful for conformance
fixtures, not proof that unknown real-world work is correct.
"""

import hashlib
import json
import re
from pathlib import Path

from .ledger import canonical_json

MAX_JSON_BYTES = 1_048_576
MAX_SAFE_INTEGER = 2**53 - 1


def _pairs(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError(f"duplicate JSON member: {key}")
        obj[key] = value
    return obj


def _reject(value):
    raise ValueError(f"unsupported JSON numeric value: {value}")


def validate_json_value(value, depth=0):
    if depth > 30:
        raise ValueError("JSON exceeds the profile's maximum depth")
    if value is None or isinstance(value, (str, bool)):
        if isinstance(value, str):
            value.encode("utf-8", errors="strict")
        return
    if type(value) is int and abs(value) <= MAX_SAFE_INTEGER:
        return
    if isinstance(value, list):
        if len(value) > 10000:
            raise ValueError("too many list items")
        for item in value:
            validate_json_value(item, depth + 1)
        return
    if isinstance(value, dict):
        if len(value) > 10000:
            raise ValueError("too many object members")
        for key, item in value.items():
            if not isinstance(key, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.-]{0,127}", key):
                raise ValueError("object keys must be bounded ASCII identifiers")
            validate_json_value(item, depth + 1)
        return
    raise ValueError("profile permits only safe integers, strings, booleans, null, arrays and objects")


def load_json(path):
    """Read at most one MiB; reject duplicate keys, floats and non-finite values."""
    with Path(path).open("rb") as stream:
        raw = stream.read(MAX_JSON_BYTES + 1)
    if len(raw) > MAX_JSON_BYTES:
        raise ValueError("JSON input exceeds one MiB")
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs,
                           parse_float=_reject, parse_constant=_reject)
    except (UnicodeError, RecursionError) as exc:
        raise ValueError("invalid or excessively nested UTF-8 JSON") from exc
    validate_json_value(value)
    return value


def content_digest(value):
    validate_json_value(value)
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def verify_invoice(value, expected=None):
    """Validate the deliberately small invoice-v1 profile, optionally a fixture.

    Does not establish that an invoice exists, that amounts are owed, or that
    the record matches a source. Provenance is a separate acceptance condition.
    """
    checks = []
    def check(name, passed):
        checks.append({"check": name, "passed": bool(passed)})
    try:
        validate_json_value(value)
    except (ValueError, UnicodeError):
        return {"profile": "invoice-v1", "passed": False,
                "checks": [{"check": "bounded_json", "passed": False}]}
    keys = {"invoice_id", "currency", "items", "total_minor"}
    exact_keys = isinstance(value, dict) and set(value) == keys
    check("exact_fields", exact_keys)
    if exact_keys:
        check("invoice_id", isinstance(value["invoice_id"], str) and bool(
            re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", value["invoice_id"])))
        check("currency", value["currency"] == "TEST")
        items = value["items"]
        valid_items = isinstance(items, list) and 1 <= len(items) <= 1000
        total = 0
        ids = set()
        if valid_items:
            for item in items:
                if not isinstance(item, dict) or set(item) != {"line_id", "quantity", "unit_minor"}:
                    valid_items = False
                    break
                line = item["line_id"]
                if not isinstance(line, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", line) or line in ids:
                    valid_items = False
                    break
                ids.add(line)
                qty, unit = item["quantity"], item["unit_minor"]
                if type(qty) is not int or type(unit) is not int or not 1 <= qty <= 100000 or not 0 <= unit <= MAX_SAFE_INTEGER:
                    valid_items = False
                    break
                total += qty * unit
        check("line_items_and_unique_ids", valid_items)
        check("total_arithmetic", valid_items and type(value["total_minor"]) is int
              and 0 <= total <= MAX_SAFE_INTEGER and value["total_minor"] == total)
    if expected is not None:
        # Hash comparison also distinguishes booleans from integers.
        check("pinned_reference", content_digest(value) == content_digest(expected))
    return {"profile": "invoice-v1", "passed": all(c["passed"] for c in checks),
            "output_sha256": content_digest(value), "checks": checks}

