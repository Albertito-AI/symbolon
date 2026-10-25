import copy
import tempfile
from pathlib import Path
import unittest
from symbolon.cli import demo, main
from symbolon.evidence import verify_bundle
from symbolon.verification import load_json
from symbolon.specification import parse_contract


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.result = demo(self.directory)
        self.bundle = load_json(self.directory / "accepted-evidence.json")
        self.checkpoint = (self.directory / "accepted-evidence.sha256").read_text().strip()

    def test_end_to_end_states_and_conservation(self):
        self.assertEqual([c["state"] for c in self.result["contracts"]], ["SETTLED", "RESOLVED"])
        self.assertEqual(self.result["balances_minor"], {"buyer-demo": 96000, "provider-demo": 104000})
        self.assertEqual(self.result["ledger"]["sum_balances"], 0)
        self.assertTrue(verify_bundle(self.bundle, self.checkpoint)["checkpoint_matches"])

    def test_modified_output_fails_pinned_checkpoint(self):
        altered = copy.deepcopy(self.bundle)
        altered["output"]["total_minor"] = 1
        with self.assertRaises(ValueError):
            verify_bundle(altered, self.checkpoint)

    def test_missing_external_anchor_fails(self):
        with self.assertRaises(ValueError):
            verify_bundle(self.bundle, "")

    def test_contract_loader_rejects_unimplemented_rail_and_extras(self):
        contract = load_json(self.directory / "example-contract.json")
        self.assertEqual(parse_contract(contract).price_minor, 4000)
        with self.assertRaises(ValueError):
            parse_contract(contract | {"asset": "USD"})
        with self.assertRaises(ValueError):
            parse_contract(contract | {"extra": "ignored?"})

    def test_existing_output_not_overwritten(self):
        with self.assertRaises(ValueError):
            demo(self.directory)

