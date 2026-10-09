"""Build the full US-listed biotech and life-science universe table (D-038).

Inputs, all optional except the first:

1. the newest classified listing snapshot in `data/silver/listings/` (written by
   `scripts/listing_history.py`), or `--snapshot-dir` pointing at a folder holding the three raw
   `<exchange>_full.json` screener files;
2. the newest sponsor holdings file in `data/silver/etf/` (written by `scripts/fetch_etf_holdings.py`);
   without it the XBI and IBB columns hold rule proxies only;
3. the watchlist (`config/universe.yaml`) and the AI-bio fit matrix, for membership flags.

Output: `data/reference/us_lifesci_universe.csv`, one row per listed company in the six layers
(therapeutics, tools, services, diagnostics, software_data, medtech).

    python scripts/build_lifesci_universe.py
    python scripts/build_lifesci_universe.py --summary   # print counts only
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import sys
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from biotech_divedeep.connectors.etf_holdings import ibb_rule_proxy, xbi_rule_proxy  # noqa: E402
from biotech_divedeep.connectors.listings import (  # noqa: E402
    EXCHANGES,
    LAYERS,
    classify_snapshot,
    load_overrides,
)

REF = ROOT / "data" / "reference"
SILVER_LISTINGS = ROOT / "data" / "silver" / "listings"
SILVER_ETF = ROOT / "data" / "silver" / "etf"
OUT = REF / "us_lifesci_universe.csv"

COLUMNS = [
    "symbol", "name", "layer", "sublayer", "exchange", "country", "ipo_year", "market_cap_usd_m", "cap_band",
    "last_price_usd", "is_adr", "in_xbi", "xbi_weight_pct", "in_ibb", "ibb_weight_pct", "xbi_rule_proxy",
    "ibb_rule_proxy", "in_watchlist", "in_ai_fit_matrix", "first_seen_in_history", "classification_rule",
    "nasdaq_industry", "snapshot_date", "evidence_class",
]


def newest(folder: Path, pattern: str) -> Path | None:
    files = sorted(folder.glob(pattern)) if folder.exists() else []
    return files[-1] if files else None


def first_seen() -> dict[str, str]:
    out: dict[str, str] = {}
    for path in sorted(SILVER_LISTINGS.glob("*.csv.gz")) if SILVER_LISTINGS.exists() else []:
        date = path.name[:10]
        with gzip.open(path, "rt") as fh:
            for r in csv.DictReader(fh):
                out.setdefault(r["symbol"], date)
    return out


def load_listings(snapshot_dir: Path | None):
    overrides = load_overrides(REF / "lifesci_layer_overrides.csv")
    if snapshot_dir is not None:
        raw = {ex: json.loads((snapshot_dir / f"{ex}_full.json").read_text()) for ex in EXCHANGES}
        date = snapshot_dir.name if snapshot_dir.name[:4].isdigit() else ""
        return date, classify_snapshot(raw, overrides)
    path = newest(SILVER_LISTINGS, "*.csv.gz")
    if path is None:
        raise SystemExit("no listing snapshot: run scripts/listing_history.py or pass --snapshot-dir")
    # Re-classify from the stored fields so override edits apply without a new fetch.
    with gzip.open(path, "rt") as fh:
        rows = list(csv.DictReader(fh))
    raw: dict[str, list[dict]] = {ex: [] for ex in EXCHANGES}
    for r in rows:
        raw[r["exchange"]].append(
            {
                "symbol": r["symbol"], "name": r["name"], "sector": r["sector"], "industry": r["industry"],
                "country": r["country"], "ipoyear": r["ipo_year"], "marketCap": r["market_cap_usd"],
                "lastsale": r["last_price_usd"], "volume": r["volume"],
            }
        )
    return path.name[:10], classify_snapshot(raw, overrides)


def etf_weights() -> tuple[dict[str, dict[str, float]], str]:
    path = newest(SILVER_ETF, "holdings_*.csv")
    if path is None:
        return {}, ""
    out: dict[str, dict[str, float]] = {}
    with open(path, newline="") as fh:
        for r in csv.DictReader(fh):
            w = float(r["weight_pct"]) if r["weight_pct"] not in ("", "None") else 0.0
            out.setdefault(r["ticker"], {})[r["fund"]] = w
    return out, path.name


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--snapshot-dir", type=Path)
    p.add_argument("--summary", action="store_true")
    args = p.parse_args()

    date, listings = load_listings(args.snapshot_dir)
    weights, etf_file = etf_weights()
    watch = {c["ticker"] for c in yaml.safe_load((ROOT / "config" / "universe.yaml").read_text())["companies"]}
    with open(REF / "ai_bio_fit_matrix.csv", newline="") as fh:
        ai = {r["ticker"] for r in csv.DictReader(fh)}
    seen = first_seen()

    rows = []
    for x in listings:
        if x.layer not in LAYERS:
            continue
        w = weights.get(x.symbol, {})
        rows.append(
            {
                "symbol": x.symbol,
                "name": x.name,
                "layer": x.layer,
                "sublayer": x.sublayer,
                "exchange": x.exchange,
                "country": x.country,
                "ipo_year": x.ipo_year,
                "market_cap_usd_m": round((x.market_cap_usd or 0) / 1e6, 1),
                "cap_band": x.cap_band,
                "last_price_usd": x.last_price_usd,
                "is_adr": x.is_adr,
                "in_xbi": ("XBI" in w) if etf_file else "",
                "xbi_weight_pct": w.get("XBI", ""),
                "in_ibb": ("IBB" in w) if etf_file else "",
                "ibb_weight_pct": w.get("IBB", ""),
                "xbi_rule_proxy": xbi_rule_proxy(x.symbol, x.country, x.layer, x.sublayer, x.market_cap_usd),
                "ibb_rule_proxy": ibb_rule_proxy(x.exchange, x.layer, x.market_cap_usd),
                "in_watchlist": x.symbol in watch,
                "in_ai_fit_matrix": x.symbol in ai,
                "first_seen_in_history": seen.get(x.symbol, ""),
                "classification_rule": x.rule,
                "nasdaq_industry": x.industry,
                "snapshot_date": date,
                "evidence_class": "own_assumption",
            }
        )
    rows.sort(key=lambda r: (LAYERS.index(r["layer"]), -r["market_cap_usd_m"]))

    by_layer = Counter(r["layer"] for r in rows)
    print(f"snapshot {date}; ETF file: {etf_file or 'none (rule proxies only)'}", file=sys.stderr)
    for layer in LAYERS:
        sub = [r for r in rows if r["layer"] == layer]
        bands = Counter(r["cap_band"] for r in sub)
        band_text = "  ".join(f"{b}={n}" for b, n in sorted(bands.items()))
        print(f"{layer:14s} {by_layer[layer]:4d}  {band_text}", file=sys.stderr)
    total = lambda col: sum(bool(r[col]) for r in rows)  # noqa: E731
    print(
        f"xbi_rule_proxy={total('xbi_rule_proxy')} ibb_rule_proxy={total('ibb_rule_proxy')}"
        f" watchlist={total('in_watchlist')}/{len(watch)} ai_fit={total('in_ai_fit_matrix')}/{len(ai)}",
        file=sys.stderr,
    )
    missing = sorted(watch - {r["symbol"] for r in rows})
    if missing:
        print(f"watchlist names outside the universe: {', '.join(missing)}", file=sys.stderr)
    if args.summary:
        return
    with open(OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    print(OUT, file=sys.stderr)


if __name__ == "__main__":
    main()
