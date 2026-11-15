"""Check a public Scorecard result's identity, not a project's security quality."""

import argparse
import json
import math
import re
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener


API_ROOT = "https://api.scorecard.dev/projects/github.com/"
MAX_BYTES = 1024 * 1024
TIMEOUT_SECONDS = 20
ATTEMPTS = 6
RETRY_SECONDS = 15


class VerificationError(ValueError):
    pass


class PublicationPending(VerificationError):
    """Only a missing result or temporary transport failure may be retried."""


class NoRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def result_url(repository, commit):
    if (not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]*/[A-Za-z0-9_.-]+", repository)
            or repository.split("/")[1] in (".", "..")):
        raise VerificationError("expected an owner/repository name")
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise VerificationError("expected a full lowercase Git commit SHA")
    return API_ROOT + repository + "?" + urlencode({"commit": commit})


def fetch_payload(url):
    request = Request(url, headers={"Accept": "application/json"}, method="GET")
    try:
        with build_opener(NoRedirects()).open(request, timeout=TIMEOUT_SECONDS) as response:
            if response.status != 200:
                raise VerificationError("unexpected HTTP response status")
            payload = response.read(MAX_BYTES + 1)
    except HTTPError as exc:
        message = "Scorecard API returned HTTP " + str(exc.code)
        if exc.code in (404, 408, 429) or 500 <= exc.code <= 599:
            raise PublicationPending(message) from exc
        raise VerificationError(message) from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise PublicationPending("Scorecard API transport temporarily unavailable") from exc
    if len(payload) > MAX_BYTES:
        raise VerificationError("Scorecard result exceeds the 1 MiB response limit")
    return payload


def unique_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise VerificationError("duplicate JSON object key")
        value[key] = item
    return value


def reject_constant(value):
    raise VerificationError("non-finite JSON numeric constant")


def numeric_score(value, minimum):
    return (type(value) in (int, float) and minimum <= value <= 10
            and (type(value) is int or math.isfinite(value)))


def validate_payload(payload, repository, commit):
    result_url(repository, commit)
    if len(payload) > MAX_BYTES:
        raise VerificationError("Scorecard result exceeds the 1 MiB response limit")
    try:
        result = json.loads(payload.decode("utf-8"), object_pairs_hook=unique_object,
                            parse_constant=reject_constant)
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise VerificationError("Scorecard result is not valid bounded JSON") from exc
    if not isinstance(result, dict) or not isinstance(result.get("repo"), dict):
        raise VerificationError("Scorecard result has no repository object")
    if result["repo"].get("name") != "github.com/" + repository:
        raise VerificationError("Scorecard result repository does not match")
    if result["repo"].get("commit") != commit:
        raise VerificationError("Scorecard result commit does not match")
    if not numeric_score(result.get("score"), 0):
        raise VerificationError("aggregate score must be a finite number from 0 to 10")
    checks = result.get("checks")
    if not isinstance(checks, list) or not checks:
        raise VerificationError("Scorecard result has no check records")
    for check in checks:
        if (not isinstance(check, dict) or not isinstance(check.get("name"), str)
                or not check["name"].strip() or type(check.get("score")) is not int
                or not -1 <= check["score"] <= 10):
            raise VerificationError("Scorecard result contains an invalid check record")
    return result


def verify_publication(repository, commit, fetch=fetch_payload, sleep=time.sleep):
    url = result_url(repository, commit)
    for attempt in range(ATTEMPTS):
        try:
            return validate_payload(fetch(url), repository, commit)
        except PublicationPending as exc:
            if attempt + 1 == ATTEMPTS:
                raise VerificationError("no verified publication after six attempts") from exc
            print(str(exc) + "; retrying publication lookup", file=sys.stderr)
            sleep(RETRY_SECONDS)
    raise AssertionError("unreachable")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository")
    parser.add_argument("commit")
    args = parser.parse_args(argv)
    try:
        result = verify_publication(args.repository, args.commit)
    except VerificationError as exc:
        print("Publication verification failed: " + str(exc), file=sys.stderr)
        return 1
    print(json.dumps({"publication_verified": True, "repository": result["repo"]["name"],
                      "commit": result["repo"]["commit"], "score": result["score"],
                      "checks": len(result["checks"]), "reported_date": result.get("date"),
                      "scope": "Published source identity; no security certification"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
