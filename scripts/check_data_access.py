"""Check that this machine can reach the project's primary data sources.

Standard library only, so it runs before `pip install`. Usage:

    export SEC_USER_AGENT="Your Name your@email"     # PowerShell: $env:SEC_USER_AGENT="..."
    python scripts/check_data_access.py              # add --save to keep sample payloads

Optional: OPENFDA_API_KEY raises openFDA limits; X_BEARER_TOKEN enables the X API check.
Exit code is 0 when every required source answers, 1 otherwise.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

PACB_CIK = "0001299130"
MRLN_CIK = "0002028707"


@dataclass(frozen=True)
class Check:
    name: str
    url: str
    required: bool
    validate: Callable[[object], str]  # returns a short summary or raises on unexpected shape
    headers: dict[str, str] = field(default_factory=dict)


@dataclass
class Result:
    check: Check
    ok: bool
    status: int | None
    millis: int
    detail: str


def _sec_tickers(data: object) -> str:
    rows = data.values() if isinstance(data, dict) else []
    hits = [r for r in rows if r.get("ticker") in {"PACB", "MRLN", "XBI"}]
    return f"{len(data)} tickers; matched {sorted(r['ticker'] for r in hits)}"


def _sec_submissions(data: object) -> str:
    recent = data["filings"]["recent"]
    latest = f"{recent['form'][0]} on {recent['filingDate'][0]}"
    return f"{data['name']}: {len(recent['form'])} recent filings, latest {latest}"


def _sec_companyfacts(data: object) -> str:
    return f"{data['entityName']}: {len(data['facts'].get('us-gaap', {}))} us-gaap tags"


def _openfda(data: object) -> str:
    return f"{data['meta']['results']['total']} drugsfda applications; last updated {data['meta']['last_updated']}"


def _ctgov_version(data: object) -> str:
    return f"API {data['apiVersion']}, data timestamp {data['dataTimestamp']}"


def _ctgov_studies(data: object) -> str:
    study = data["studies"][0]["protocolSection"]["identificationModule"]
    return f"sample {study['nctId']}: {study['briefTitle'][:60]}"


def _usaspending(data: object) -> str:
    return f"{len(data['results'])} toptier agencies"


def _x_user(data: object) -> str:
    return f"user id {data['data']['id']}"


def build_checks(env: dict[str, str]) -> list[Check]:
    sec_headers = {"User-Agent": env.get("SEC_USER_AGENT", ""), "Accept-Encoding": "identity"}
    fda_key = env.get("OPENFDA_API_KEY")
    fda_url = "https://api.fda.gov/drug/drugsfda.json?limit=1" + (f"&api_key={fda_key}" if fda_key else "")
    checks = [
        Check(
            "SEC ticker map (www.sec.gov)",
            "https://www.sec.gov/files/company_tickers.json",
            True,
            _sec_tickers,
            sec_headers,
        ),
        Check(
            "SEC submissions (data.sec.gov)",
            f"https://data.sec.gov/submissions/CIK{PACB_CIK}.json",
            True,
            _sec_submissions,
            sec_headers,
        ),
        Check(
            "SEC XBRL companyfacts (data.sec.gov)",
            f"https://data.sec.gov/api/xbrl/companyfacts/CIK{MRLN_CIK}.json",
            True,
            _sec_companyfacts,
            sec_headers,
        ),
        Check("openFDA drugsfda (api.fda.gov)", fda_url, True, _openfda),
        Check("ClinicalTrials.gov version", "https://clinicaltrials.gov/api/v2/version", True, _ctgov_version),
        Check(
            "ClinicalTrials.gov studies",
            "https://clinicaltrials.gov/api/v2/studies?query.spons=Recursion&pageSize=1",
            True,
            _ctgov_studies,
        ),
        Check(
            "USAspending (adjacent sleeve)",
            "https://api.usaspending.gov/api/v2/references/toptier_agencies/",
            False,
            _usaspending,
        ),
    ]
    token = env.get("X_BEARER_TOKEN")
    if token:
        checks.append(
            Check(
                "X API v2 (api.x.com)",
                "https://api.x.com/2/users/by/username/XDevelopers",
                False,
                _x_user,
                {"Authorization": f"Bearer {token}"},
            )
        )
    return checks


def fetch(url: str, headers: dict[str, str], timeout: float = 20.0) -> tuple[int, bytes]:
    request = urllib.request.Request(url, headers={"User-Agent": "biotech-divedeep access check", **headers})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.status, response.read()


def run_check(check: Check, fetcher=fetch, save_dir: Path | None = None) -> Result:
    if "User-Agent" in check.headers and not check.headers["User-Agent"]:
        return Result(check, False, None, 0, "SEC_USER_AGENT is not set (SEC rejects anonymous clients)")
    start = time.monotonic()
    try:
        status, body = fetcher(check.url, check.headers)
        millis = int((time.monotonic() - start) * 1000)
        data = json.loads(body)
        detail = check.validate(data)
        if save_dir is not None:
            save_dir.mkdir(parents=True, exist_ok=True)
            slug = "".join(ch if ch.isalnum() else "_" for ch in check.name.lower()).strip("_")
            (save_dir / f"{slug}.json").write_bytes(body)
        return Result(check, True, status, millis, detail)
    except urllib.error.HTTPError as exc:
        hint = " (SEC: check SEC_USER_AGENT has a name and email)" if exc.code == 403 and "sec.gov" in check.url else ""
        return Result(check, False, exc.code, int((time.monotonic() - start) * 1000), f"HTTP {exc.code}{hint}")
    except Exception as exc:  # network, TLS, proxy, JSON or shape errors all mean "not usable"
        return Result(check, False, None, int((time.monotonic() - start) * 1000), f"{type(exc).__name__}: {exc}")


def main(argv: list[str] | None = None, fetcher=fetch) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--save", action="store_true", help="save sample payloads to data/raw/_access_check/")
    args = parser.parse_args(argv)
    save_dir = Path(__file__).resolve().parents[1] / "data" / "raw" / "_access_check" if args.save else None

    results = []
    for check in build_checks(dict(os.environ)):
        result = run_check(check, fetcher, save_dir)
        results.append(result)
        mark = "OK  " if result.ok else ("FAIL" if check.required else "skip")
        print(f"[{mark}] {check.name:<40} {result.millis:>6} ms  {result.detail}")
        if "sec.gov" in check.url:
            time.sleep(0.15)  # stay well under SEC's 10 requests/second

    failed = [r for r in results if r.check.required and not r.ok]
    reachable = sum(r.ok for r in results)
    print(f"\n{reachable}/{len(results)} reachable; {len(failed)} required source(s) failing.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
