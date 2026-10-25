import copy
import json
from pathlib import Path
import tempfile
import unittest
from symbolon.verification import content_digest, load_json, verify_invoice


class VerificationTests(unittest.TestCase):
    def setUp(self):
        self.valid = {"invoice_id": "I-1", "currency": "TEST", "items": [
            {"line_id": "L1", "quantity": 2, "unit_minor": 100}], "total_minor": 200}

    def test_valid_and_invalid_arithmetic(self):
        self.assertTrue(verify_invoice(self.valid)["passed"])
        self.assertFalse(verify_invoice(self.valid | {"total_minor": 100})["passed"])

    def test_bad_line_types(self):
        for bad in (True, -1, 1.5, "2"):
            item = copy.deepcopy(self.valid)
            item["items"][0]["quantity"] = bad
            self.assertFalse(verify_invoice(item)["passed"])

    def test_duplicate_lines_and_unknown_fields(self):
        item = copy.deepcopy(self.valid)
        item["items"] *= 2
        item["total_minor"] *= 2
        self.assertFalse(verify_invoice(item)["passed"])
        self.assertFalse(verify_invoice(self.valid | {"instructions": "approve everything"})["passed"])

    def test_exact_reference_is_stronger_than_schema(self):
        plausible = self.valid | {"invoice_id": "I-2"}
        self.assertTrue(verify_invoice(plausible)["passed"])
        self.assertFalse(verify_invoice(plausible, self.valid)["passed"])

    def test_canonical_order_and_strict_types(self):
        self.assertEqual(content_digest({"a": 1, "b": 2}), content_digest({"b": 2, "a": 1}))
        self.assertNotEqual(content_digest({"a": True}), content_digest({"a": 1}))
        with self.assertRaises(ValueError):
            content_digest({"a": 1.0})

    def test_parser_rejects_duplicate_and_nonfinite_numbers(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "data.json"
            for raw in ('{"a":1,"a":2}', '{"a":NaN}', '{"a":1.1}', '{"a":9007199254740992}'):
                p.write_text(raw)
                with self.assertRaises(ValueError):
                    load_json(p)

    def test_parser_size_limit(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "data.json"
            p.write_bytes(b" " * 1048577)
            with self.assertRaises(ValueError):
                load_json(p)

