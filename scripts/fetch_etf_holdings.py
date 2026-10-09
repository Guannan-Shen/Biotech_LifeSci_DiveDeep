"""Download and parse sponsor holdings for XBI, XPH, XHE (SSGA) and IBB (iShares) (D-038).

Run on a machine that can reach ssga.com and ishares.com (the cloud environment cannot):

    python scripts/fetch_etf_holdings.py            # all funds
    python scripts/fetch_etf_holdings.py XBI IBB    # a subset

Raw files go to `data/raw/etf/<today>/` unmodified; the parsed union goes to
`data/silver/etf/holdings_<today>.csv` (fund, as_of, ticker, name, weight_pct, shares, sector).
`scripts/build_lifesci_universe.py` picks up the newest parsed file automatically.
Commit a dated copy to `data/reference/` only when a snapshot is needed for a study.
"""

from __future__ import annotations

import csv
import datetime as dt
import os
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from biotech_divedeep.connectors.etf_holdings import (  # noqa: E402
    ISHARES_URLS,
    SSGA_FUNDS,
    SSGA_URL,
    parse_ishares_csv,
    read_ssga_xlsx,
)

UA = os.environ.get("SEC_USER_AGENT", "biotech-divedeep research (set SEC_USER_AGENT)")


def main() -> None:
    funds = [f.upper() for f in sys.argv[1:]] or [*SSGA_FUNDS, *ISHARES_URLS]
    today = dt.date.today().isoformat()
    raw_dir = ROOT / "data" / "raw" / "etf" / today
    raw_dir.mkdir(parents=True, exist_ok=True)
    out_dir = ROOT / "data" / "silver" / "etf"
    out_dir.mkdir(parents=True, exist_ok=True)
    holdings = []
    with httpx.Client(headers={"User-Agent": UA}, timeout=60, follow_redirects=True) as client:
        for fund in funds:
            if fund in SSGA_FUNDS:
                resp = client.get(SSGA_URL.format(t=fund.lower()))
                resp.raise_for_status()
                path = raw_dir / f"{fund}.xlsx"
                path.write_bytes(resp.content)
                rows = read_ssga_xlsx(path, fund)
            elif fund in ISHARES_URLS:
                resp = client.get(ISHARES_URLS[fund])
                resp.raise_for_status()
                path = raw_dir / f"{fund}.csv"
                path.write_bytes(resp.content)
                rows = parse_ishares_csv(resp.content.decode("utf-8-sig"), fund)
            else:
                print(f"{fund}: no source configured", file=sys.stderr)
                continue
            print(f"{fund}: {len(rows)} holdings as of {rows[0].as_of if rows else '?'}", file=sys.stderr)
            holdings.extend(rows)
    out = out_dir / f"holdings_{today}.csv"
    with open(out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["fund", "as_of", "ticker", "name", "weight_pct", "shares", "sector"])
        for h in holdings:
            w.writerow([h.fund, h.as_of, h.ticker, h.name, h.weight_pct, h.shares, h.sector])
    print(out)


if __name__ == "__main__":
    main()
