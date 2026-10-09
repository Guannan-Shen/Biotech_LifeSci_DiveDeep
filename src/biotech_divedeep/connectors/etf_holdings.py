"""ETF holdings files from the sponsors: SSGA (XBI, XPH, XHE) and iShares (IBB) (D-038).

Both sponsors publish a free daily holdings file. Neither host resolves from the cloud research
environment, so the fetch runs on the local machine (`scripts/fetch_etf_holdings.py`); the parsers
here are pure functions tested on recorded fixtures.

- SSGA: an `.xlsx` whose first rows are metadata ("Fund Name:", "Ticker Symbol:", "Holdings:",
  "As of 08-Oct-2026"), then a header row (Name, Ticker, Identifier, SEDOL, Weight, Sector,
  Shares Held, Local Currency), then one row per holding, then disclaimers.
- iShares: a `.csv` with about nine metadata lines (`Fund Holdings as of,"Oct 08, 2026"`), a header
  row starting with `Ticker`, one row per holding (cash and futures rows carry another
  `Asset Class`), then disclaimers.

Raw files are kept unmodified under `data/raw/etf/<date>/` before parsing (AGENTS.md).
"""

from __future__ import annotations

import csv
import io
import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

SSGA_URL = "https://www.ssga.com/us/en/intermediary/library-content/products/fund-data/etfs/us/holdings-daily-us-en-{t}.xlsx"
ISHARES_URLS = {
    # Product id taken from the IBB product page; other iShares funds need their own id.
    "IBB": "https://www.ishares.com/us/products/239699/ishares-nasdaq-biotechnology-etf/1467271812596.ajax"
    "?fileType=csv&fileName=IBB_holdings&dataType=fund",
}
SSGA_FUNDS = ("XBI", "XPH", "XHE")


@dataclass(frozen=True)
class Holding:
    fund: str
    as_of: str  # ISO date printed in the file
    ticker: str
    name: str
    weight_pct: float | None
    shares: float | None
    sector: str


def _num(text: object) -> float | None:
    if text is None:
        return None
    if isinstance(text, (int, float)):
        return float(text)
    s = str(text).replace(",", "").replace("%", "").strip()
    if s in ("", "-", "--"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _iso(text: str) -> str:
    text = text.strip().strip('"')
    for fmt in ("%d-%b-%Y", "%b %d, %Y", "%m/%d/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, fmt).date().isoformat()
        except ValueError:
            continue
    raise ValueError(f"unrecognised date {text!r}")


def parse_ssga_rows(rows: Sequence[Sequence[object]], fund: str) -> list[Holding]:
    """Parse SSGA holdings from worksheet rows (lists of cell values)."""
    as_of = ""
    header_idx = None
    for i, row in enumerate(rows):
        cells = [str(c).strip() if c is not None else "" for c in row]
        joined = " ".join(cells)
        m = re.search(r"As of (\d{2}-[A-Za-z]{3}-\d{4})", joined)
        if m:
            as_of = _iso(m.group(1))
        if cells and cells[0] == "Name" and "Ticker" in cells:
            header_idx = i
            break
    if header_idx is None:
        raise ValueError("SSGA header row not found")
    header = [str(c).strip() for c in rows[header_idx]]
    col = {name: header.index(name) for name in header if name}
    out: list[Holding] = []
    for row in rows[header_idx + 1 :]:
        if not row or row[0] is None or str(row[0]).strip() == "":
            break
        def get(k: str, row: Sequence[object] = row) -> object:
            return row[col[k]] if k in col and col[k] < len(row) else None

        ticker = str(get("Ticker") or "").strip().upper()
        if not ticker or ticker in {"-", "CASH_USD"}:
            continue
        out.append(
            Holding(
                fund=fund,
                as_of=as_of,
                ticker=ticker,
                name=str(get("Name") or "").strip(),
                weight_pct=_num(get("Weight")),
                shares=_num(get("Shares Held")),
                sector=str(get("Sector") or "").strip(),
            )
        )
    return out


def read_ssga_xlsx(path: str | Path, fund: str) -> list[Holding]:
    try:
        import openpyxl
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise RuntimeError("install the data extra: pip install -e '.[data]'") from exc
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    rows = [list(r) for r in wb.worksheets[0].iter_rows(values_only=True)]
    return parse_ssga_rows(rows, fund)


def parse_ishares_csv(text: str, fund: str) -> list[Holding]:
    lines = text.lstrip("﻿").splitlines()
    as_of = ""
    header_idx = None
    for i, line in enumerate(lines):
        if line.startswith("Fund Holdings as of"):
            as_of = _iso(line.split(",", 1)[1])
        if line.startswith("Ticker,") or line.startswith('"Ticker",'):
            header_idx = i
            break
    if header_idx is None:
        raise ValueError("iShares header row not found")
    body: list[str] = []
    for line in lines[header_idx:]:
        if not line.strip() or line.startswith('"The content') or line.startswith("\xa0"):
            break
        body.append(line)
    out: list[Holding] = []
    for r in csv.DictReader(io.StringIO("\n".join(body))):
        if (r.get("Asset Class") or "").strip() != "Equity":
            continue
        out.append(
            Holding(
                fund=fund,
                as_of=as_of,
                ticker=(r.get("Ticker") or "").strip().upper(),
                name=(r.get("Name") or "").strip(),
                weight_pct=_num(r.get("Weight (%)")),
                shares=_num(r.get("Quantity") or r.get("Shares")),
                sector=(r.get("Sector") or "").strip(),
            )
        )
    return out


def membership(holdings: Iterable[Holding]) -> dict[str, dict[str, float | None]]:
    """ticker -> {fund: weight_pct}."""
    out: dict[str, dict[str, float | None]] = {}
    for h in holdings:
        out.setdefault(h.ticker, {})[h.fund] = h.weight_pct
    return out


# --------------------------------------------------------------------------------------------
# Rule proxies for when the sponsor files are not available (own_assumption)
# --------------------------------------------------------------------------------------------


def ibb_rule_proxy(exchange: str, layer: str, market_cap_usd: float | None) -> bool:
    """NASDAQ Biotechnology Index (IBB) eligibility, approximately.

    Rules (Nasdaq methodology, as summarised by search on 2026-10-09, unverified): primary listing
    on the Nasdaq Global Select or Global Market, ICB Biotechnology or Pharmaceuticals subsector,
    market cap at least USD 200M, average daily volume at least 100,000 shares, no bankruptcy;
    reconstituted each December. The proxy cannot see the Nasdaq tier, ICB code or volume history.
    """
    return exchange == "nasdaq" and layer == "therapeutics" and (market_cap_usd or 0) >= 2e8


# US-domiciled large drug makers classified GICS Pharmaceuticals rather than Biotechnology (A).
# Vertex, Regeneron, Amgen, Gilead, AbbVie and Biogen are GICS Biotechnology and stay eligible.
GICS_PHARMA_US = {"LLY", "JNJ", "MRK", "PFE", "BMY", "ZTS", "ELAN", "VTRS", "OGN", "JAZZ", "CORT", "SUPN", "PCRX"}


def xbi_rule_proxy(ticker: str, country: str, layer: str, sublayer: str, market_cap_usd: float | None) -> bool:
    """S&P Biotechnology Select Industry Index (XBI) eligibility, approximately.

    Rules (S&P methodology via secondary sources, unverified): member of the S&P Total Market Index
    (US domicile), GICS Biotechnology sub-industry, float-adjusted market cap and liquidity ratio
    thresholds (new entrants about USD 500M float cap, A), at least 35 names. Weights have followed
    3-month median traded value since June 2024. GICS Pharmaceuticals names (large pharma,
    generics, most specialty pharma such as HROW or PCRX) are outside XBI; the proxy can only drop
    the sublayers that are clearly pharma.
    """
    if country != "United States" or layer != "therapeutics":
        return False
    if ticker in GICS_PHARMA_US or sublayer in {"generics", "animal_health", "royalty"}:
        return False
    return (market_cap_usd or 0) >= 5e8
