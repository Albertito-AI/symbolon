"""Direct checks of the dated sandbox contract envelope, using synthetic terms."""

import copy
from dataclasses import asdict
import unittest

from symbolon.specification import parse_contract


class SpecificationTests(unittest.TestCase):
    def setUp(self):
        self.envelope = {
            "spec_version": "2026-10-25.alpha1",
            "asset": "TEST",
            "acceptance_profile": "exact-json-v1",
            "contract": {
                "contract_id": "loader-example",
                "buyer": "buyer-example",
                "provider": "provider-example",
                "verifier": "verifier-example",
                "accepted_output_sha256": "a" * 64,
                "price_minor": 4000,
                "bond_minor": 1000,
                "delivery_deadline": 100,
                "challenge_window_seconds": 10,
            },
        }

    def test_supported_envelope_preserves_terms(self):
        original = copy.deepcopy(self.envelope)
        self.assertEqual(asdict(parse_contract(self.envelope)), original["contract"])
        self.assertEqual(self.envelope, original)

    def test_unsupported_specification_versions_rejected(self):
        for version in ("2026-10-24.alpha1", "2026-10-25.alpha2", "", None, True):
            with self.subTest(version=version):
                with self.assertRaises(ValueError):
                    parse_contract(self.envelope | {"spec_version": version})

    def test_unsupported_assets_and_profiles_rejected(self):
        for field, values in (
            ("asset", ("USD", "test", "", None, True)),
            ("acceptance_profile", ("invoice-v1", "exact-json-v2", "", None, True)),
        ):
            for value in values:
                with self.subTest(field=field, value=value):
                    with self.assertRaises(ValueError):
                        parse_contract(self.envelope | {field: value})

    def test_envelope_requires_exact_fields(self):
        for missing in self.envelope:
            incomplete = {key: value for key, value in self.envelope.items() if key != missing}
            with self.subTest(missing=missing):
                with self.assertRaises(ValueError):
                    parse_contract(incomplete)
            with self.subTest(replaced=missing):
                with self.assertRaises(ValueError):
                    parse_contract(incomplete | {"unexpected": "not a replacement"})
        with self.assertRaises(ValueError):
            parse_contract(self.envelope | {"unexpected": "not allowed"})

    def test_contract_requires_exact_fields(self):
        terms = self.envelope["contract"]
        for missing in terms:
            incomplete = {key: value for key, value in terms.items() if key != missing}
            with self.subTest(missing=missing):
                with self.assertRaises(ValueError):
                    parse_contract(self.envelope | {"contract": incomplete})
            with self.subTest(replaced=missing):
                with self.assertRaises(ValueError):
                    parse_contract(self.envelope | {"contract": incomplete | {"unexpected": 0}})
        with self.assertRaises(ValueError):
            parse_contract(self.envelope | {"contract": terms | {"unexpected": 0}})

    def test_non_object_inputs_rejected(self):
        for value in (None, False, 0, 1.5, "contract", [], list(self.envelope)):
            with self.subTest(envelope=value):
                with self.assertRaises(ValueError):
                    parse_contract(value)
        for value in (None, False, 0, 1.5, "contract", [], list(self.envelope["contract"])):
            with self.subTest(contract=value):
                with self.assertRaises(ValueError):
                    parse_contract(self.envelope | {"contract": value})
