"""Fetch free attention proxies (Wikimedia pageviews, GDELT news volume) and print z-scores.

Usage (local machine; this cloud sandbox blocks both hosts):
    ATTENTION_USER_AGENT="BiotechDiveDeep research you@example.org" \
        python scripts/attention_proxies.py --start 2026-07-01 --end 2026-10-07

Raw responses go to data/raw/attention/<fetch date>/ before parsing (AGENTS.md). The printout lists,
per term, the last 10 days of abnormal attention (z of log views against the trailing 60 days) and
the date of the peak. Read with docs/modules/social_x.md section 7.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

import yaml

from biotech_divedeep.signals.attention import abnormal_attention, parse_gdelt_timeline, parse_wikimedia_pageviews

ROOT = Path(__file__).resolve().parents[1]
TERMS = ROOT / "config" / "attention_terms.yaml"
WIKI = (
    "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/"
    "{article}/daily/{start}/{end}"
)
GDELT = "https://api.gdeltproject.org/api/v2/doc/doc?query={query}&mode=timelinevol&format=json&startdatetime={start}000000&enddatetime={end}235959"


def fetch(url: str, user_agent: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": user_agent})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def save_raw(payload: dict, source: str, name: str) -> None:
    out = ROOT / "data" / "raw" / "attention" / date.today().isoformat() / source
    out.mkdir(parents=True, exist_ok=True)
    safe = "".join(ch if ch.isalnum() else "_" for ch in name)
    (out / f"{safe}.json").write_text(json.dumps(payload))


def report(label: str, series: list[tuple[date, float]]) -> None:
    if not series:
        print(f"| {label} | no data |")
        return
    days = [d for d, _ in series]
    z = abnormal_attention([v for _, v in series])
    scored = [(v, d) for d, v in zip(days, z, strict=True) if v is not None]
    peak = max(scored) if scored else None
    tail = ", ".join(
        f"{d.isoformat()[5:]}:{'n/a' if v is None else f'{v:+.1f}'}" for d, v in zip(days[-10:], z[-10:], strict=True)
    )
    peak_txt = "n/a" if peak is None else f"{peak[1].isoformat()} (z {peak[0]:+.1f})"
    print(f"| {label} | {peak_txt} | {tail} |")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", required=True, help="YYYY-MM-DD")
    ap.add_argument("--end", required=True, help="YYYY-MM-DD")
    args = ap.parse_args()
    user_agent = os.environ.get("ATTENTION_USER_AGENT") or os.environ.get("SEC_USER_AGENT")
    if not user_agent:
        print("Set ATTENTION_USER_AGENT (Wikimedia requires a descriptive User-Agent with contact).")
        return 2
    start, end = args.start.replace("-", ""), args.end.replace("-", "")
    terms = yaml.safe_load(TERMS.read_text())
    entries = [(c["ticker"], c) for c in terms["companies"]] + [(t["name"], t) for t in terms["themes"]]

    print("| Term | Peak abnormal attention | Last 10 days (MM-DD:z) |")
    print("|---|---|---|")
    for label, entry in entries:
        wiki_url = WIKI.format(article=urllib.parse.quote(entry["wiki"], safe=""), start=start, end=end)
        gdelt_url = GDELT.format(query=urllib.parse.quote(entry["gdelt"]), start=start, end=end)
        try:
            wiki = fetch(wiki_url, user_agent)
            save_raw(wiki, "wikimedia", label)
            report(f"{label} wiki", [(d, float(v)) for d, v in parse_wikimedia_pageviews(wiki)])
        except Exception as exc:  # noqa: BLE001 - report and continue with the next term
            print(f"| {label} wiki | error: {exc} | |")
        time.sleep(1.0)  # GDELT asks for at most one request per second or so
        try:
            gdelt = fetch(gdelt_url, user_agent)
            save_raw(gdelt, "gdelt", label)
            report(f"{label} news", parse_gdelt_timeline(gdelt))
        except Exception as exc:  # noqa: BLE001
            print(f"| {label} news | error: {exc} | |")
    return 0


if __name__ == "__main__":
    sys.exit(main())
