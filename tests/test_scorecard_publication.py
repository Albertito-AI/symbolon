"""Offline publication-boundary checks; no Scorecard API requests are made."""

import copy
from contextlib import redirect_stderr, redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import unittest
from unittest.mock import Mock, patch
from urllib.error import HTTPError, URLError


SCRIPT = Path(__file__).resolve().parents[1] / ".github/scripts/verify_scorecard.py"
SPEC = importlib.util.spec_from_file_location("verify_scorecard", SCRIPT)
verifier = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verifier)
REPOSITORY = "Albertito-AI/symbolon"
COMMIT = "1" * 40


class ScorecardPublicationTests(unittest.TestCase):
    def setUp(self):
        self.result = {"repo": {"name": "github.com/" + REPOSITORY, "commit": COMMIT},
                       "date": "2026-11-15", "score": 5.1,
                       "checks": [{"name": "Example", "score": -1, "reason": "inconclusive"}]}

    def encoded(self, result=None):
        return json.dumps(self.result if result is None else result).encode()

    def test_valid_results_include_zero_scores_and_inconclusive_checks(self):
        for score in (0, 5.1, 10):
            with self.subTest(score=score):
                self.result["score"] = score
                self.assertEqual(verifier.validate_payload(self.encoded(), REPOSITORY, COMMIT), self.result)

    def test_wrong_repository_and_stale_or_short_commit_rejected(self):
        for field, value in (("name", "github.com/other/project"), ("name", None),
                             ("commit", "2" * 40), ("commit", COMMIT[:7]), ("commit", None)):
            with self.subTest(field=field, value=value):
                altered = copy.deepcopy(self.result)
                altered["repo"][field] = value
                with self.assertRaises(verifier.VerificationError):
                    verifier.validate_payload(self.encoded(altered), REPOSITORY, COMMIT)

    def test_missing_null_or_collection_fields_rejected(self):
        for field in ("repo", "score", "checks"):
            for value in (None, {}, []):
                with self.subTest(field=field, value=value):
                    with self.assertRaises(verifier.VerificationError):
                        verifier.validate_payload(self.encoded(self.result | {field: value}), REPOSITORY, COMMIT)
            incomplete = {key: value for key, value in self.result.items() if key != field}
            with self.subTest(missing=field), self.assertRaises(verifier.VerificationError):
                verifier.validate_payload(self.encoded(incomplete), REPOSITORY, COMMIT)

    def test_invalid_numeric_scores_rejected(self):
        for score in (True, False, "5.1", -1, 10.1, float("nan"), float("inf"), -float("inf")):
            with self.subTest(score=score), self.assertRaises(verifier.VerificationError):
                verifier.validate_payload(self.encoded(self.result | {"score": score}), REPOSITORY, COMMIT)
        for check in (None, [], {}, {"name": "", "score": 0}, {"name": "Example", "score": True},
                      {"name": "Example", "score": -2}, {"name": "Example", "score": 11}):
            with self.subTest(check=check), self.assertRaises(verifier.VerificationError):
                verifier.validate_payload(self.encoded(self.result | {"checks": [check]}), REPOSITORY, COMMIT)
        for score in (-0.5, 0.5, 1.0):
            with self.subTest(check_score=score), self.assertRaises(verifier.VerificationError):
                verifier.validate_payload(self.encoded(self.result | {"checks": [{"name": "Example", "score": score}]}), REPOSITORY, COMMIT)

    def test_malformed_duplicate_oversized_and_non_object_json_rejected(self):
        duplicate_score = self.encoded().replace(b'"score": 5.1', b'"score": 4, "score": 5.1', 1)
        unused_nonfinite = self.encoded()[:-1] + b', "unused": NaN}'
        for payload in (b"not JSON", b"\xff", b"null", b"[]", duplicate_score, unused_nonfinite,
                        b" " * (verifier.MAX_BYTES + 1), b"[" * 2000 + b"]" * 2000):
            with self.subTest(length=len(payload)), self.assertRaises(verifier.VerificationError):
                verifier.validate_payload(payload, REPOSITORY, COMMIT)

    def test_expected_identity_cannot_change_the_fixed_endpoint(self):
        self.assertEqual(verifier.result_url(REPOSITORY, COMMIT),
                         "https://api.scorecard.dev/projects/github.com/" + REPOSITORY + "?commit=" + COMMIT)
        for repository, commit in (("../other", COMMIT), ("owner/..", COMMIT),
                                   ("owner/.", COMMIT), ("other/repo?redirect=1", COMMIT),
                                   ("https://other/repo", COMMIT), (REPOSITORY, "short")):
            with self.subTest(repository=repository, commit=commit), self.assertRaises(verifier.VerificationError):
                verifier.result_url(repository, commit)

    def test_get_is_credential_free_bounded_and_redirects_refused(self):
        response = Mock(status=200)
        response.read.return_value = self.encoded()
        opener = Mock()
        opener.open.return_value.__enter__ = Mock(return_value=response)
        opener.open.return_value.__exit__ = Mock(return_value=False)
        with patch.object(verifier, "build_opener", return_value=opener):
            self.assertEqual(verifier.fetch_payload(verifier.result_url(REPOSITORY, COMMIT)), self.encoded())
        request = opener.open.call_args.args[0]
        self.assertEqual(request.get_method(), "GET")
        self.assertEqual(dict(request.header_items()), {"Accept": "application/json"})
        self.assertEqual(opener.open.call_args.kwargs, {"timeout": 20})
        response.read.assert_called_once_with(verifier.MAX_BYTES + 1)
        self.assertIsNone(verifier.NoRedirects().redirect_request(request, None, 302, "", {}, "https://other.example"))
        response.read.return_value = b" " * (verifier.MAX_BYTES + 1)
        with patch.object(verifier, "build_opener", return_value=opener), self.assertRaises(verifier.VerificationError):
            verifier.fetch_payload(request.full_url)

    def test_http_and_transport_retry_classification(self):
        for error, expected in ((HTTPError("url", 404, "", {}, io.BytesIO()), verifier.PublicationPending),
                                (HTTPError("url", 503, "", {}, io.BytesIO()), verifier.PublicationPending),
                                (URLError("offline"), verifier.PublicationPending),
                                (HTTPError("url", 302, "", {}, io.BytesIO()), verifier.VerificationError),
                                (HTTPError("url", 403, "", {}, io.BytesIO()), verifier.VerificationError)):
            opener = Mock()
            opener.open.side_effect = error
            with self.subTest(error=error), patch.object(verifier, "build_opener", return_value=opener):
                with self.assertRaises(expected) as caught:
                    verifier.fetch_payload(verifier.result_url(REPOSITORY, COMMIT))
                self.assertIs(type(caught.exception), expected)

    def test_retry_can_receive_delayed_publication_and_is_bounded(self):
        fetch = Mock(side_effect=[verifier.PublicationPending("not yet"), self.encoded()])
        sleep = Mock()
        self.assertEqual(verifier.verify_publication(REPOSITORY, COMMIT, fetch, sleep), self.result)
        self.assertEqual(fetch.call_count, 2)
        sleep.assert_called_once_with(15)
        fetch = Mock(side_effect=verifier.PublicationPending("not yet"))
        sleep = Mock()
        with self.assertRaises(verifier.VerificationError):
            verifier.verify_publication(REPOSITORY, COMMIT, fetch, sleep)
        self.assertEqual(fetch.call_count, 6)
        self.assertEqual(sleep.call_count, 5)

    def test_identity_failure_is_not_retried_or_replaced_by_later_success(self):
        stale = copy.deepcopy(self.result)
        stale["repo"]["commit"] = "2" * 40
        fetch = Mock(side_effect=[self.encoded(stale), self.encoded()])
        sleep = Mock()
        with self.assertRaises(verifier.VerificationError):
            verifier.verify_publication(REPOSITORY, COMMIT, fetch, sleep)
        self.assertEqual(fetch.call_count, 1)
        sleep.assert_not_called()

    def test_cli_exit_status_follows_actual_result_validation(self):
        response = Mock(status=200)
        opener = Mock()
        opener.open.return_value.__enter__ = Mock(return_value=response)
        opener.open.return_value.__exit__ = Mock(return_value=False)
        for payload, expected in ((self.encoded(), 0), (b"{}", 1)):
            response.read.return_value = payload
            output, errors = io.StringIO(), io.StringIO()
            with self.subTest(expected=expected), patch.object(verifier, "build_opener", return_value=opener):
                with redirect_stdout(output), redirect_stderr(errors):
                    self.assertEqual(verifier.main([REPOSITORY, COMMIT]), expected)
            if expected == 0:
                self.assertIs(json.loads(output.getvalue())["publication_verified"], True)
            else:
                self.assertEqual(output.getvalue(), "")
                self.assertIn("Publication verification failed", errors.getvalue())
