"""Point-in-time US life-science listing history from the Nasdaq screener mirror (D-038).

The public repository https://github.com/rreichel3/US-Stock-Symbols commits the Nasdaq screener
(all NASDAQ, NYSE and NYSE American stocks) about once a day since 2021-01-30. Its git history is
a free, survivorship-free listing record. This script samples one commit per month (or week),
classifies every row with `connectors/listings.py`, and writes:

- `data/silver/listings/<date>.csv.gz`: the classified full snapshot, all rows (git-ignored);
- `data/reference/lifesci_listing_counts_monthly.csv`: companies per month, layer and cap band
  (the denominator for a takeout hazard);
- `data/reference/lifesci_listing_exits.csv`: every universe symbol that stopped trading, with the
  last market cap, a ticker-change check and the matching takeout `deal_id` when one exists.

Usage:
    python scripts/listing_history.py --repo /path/to/US-Stock-Symbols [--freq monthly] [--since 2021-02]

If `--repo` does not exist the script clones it without file contents (`--filter=blob:none`);
`git show` then fetches only the sampled snapshots (about 2.5 MB each).
"""

from __future__ import annotations

import argparse
import csv
import gzip
import io
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from biotech_divedeep.connectors.listings import (  # noqa: E402
    EXCHANGES,
    DealRef,
    Listing,
    build_spells,
    classify_snapshot,
    detect_exits,
    load_overrides,
    match_exits_to_deals,
    panel_counts,
    read_snapshot_csv,
    stable_layers,
)

MIRROR = "https://github.com/rreichel3/US-Stock-Symbols.git"
OVERRIDES = ROOT / "data" / "reference" / "lifesci_layer_overrides.csv"
DEALS = ROOT / "data" / "reference" / "biotech_takeouts.csv"
SILVER = ROOT / "data" / "silver" / "listings"
COUNTS_OUT = ROOT / "data" / "reference" / "lifesci_listing_counts_monthly.csv"
EXITS_OUT = ROOT / "data" / "reference" / "lifesci_listing_exits.csv"
RESOLUTIONS = ROOT / "data" / "reference" / "lifesci_exit_resolutions.csv"
MIN_ROWS = 5000  # a sampled snapshot with fewer rows across the three exchanges is a glitch; skip it


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True).stdout


def ensure_repo(repo: Path) -> None:
    if (repo / ".git").exists():
        subprocess.run(["git", "-C", str(repo), "fetch", "-q", "origin"], check=False)
        return
    subprocess.run(["git", "clone", "-q", "--filter=blob:none", "--no-checkout", MIRROR, str(repo)], check=True)


def sample_commits(repo: Path, freq: str, since: str) -> list[tuple[str, str]]:
    """First commit in each period touching the NASDAQ file: [(date, sha)], oldest first."""
    log = git(repo, "log", "--reverse", "--format=%H %cs", "origin/HEAD", "--", "nasdaq/nasdaq_full_tickers.json")
    picked: dict[str, tuple[str, str]] = {}
    for line in log.splitlines():
        sha, date = line.split()
        if date < since:
            continue
        if freq == "weekly":
            import datetime as dt

            y, w, _ = dt.date.fromisoformat(date).isocalendar()
            key = f"{y}-W{w:02d}"
        else:
            key = date[:7]
        picked.setdefault(key, (date, sha))
    # Always include the latest commit so the final state is current.
    last = log.splitlines()[-1].split()
    picked.setdefault("latest", (last[1], last[0]))
    return sorted(set(picked.values()))


def load_snapshot(repo: Path, sha: str) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for ex in EXCHANGES:
        try:
            raw = git(repo, "show", f"{sha}:{ex}/{ex}_full_tickers.json")
        except subprocess.CalledProcessError:
            out[ex] = []
            continue
        try:
            out[ex] = json.loads(raw)
        except json.JSONDecodeError:
            out[ex] = []
    return out


FIELDS = [
    "symbol", "name", "exchange", "sector", "industry", "country", "ipo_year",
    "market_cap_usd", "last_price_usd", "volume", "layer", "sublayer", "rule",
]


def write_silver(date: str, listings: list[Listing]) -> None:
    SILVER.mkdir(parents=True, exist_ok=True)
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(FIELDS)
    for x in listings:
        w.writerow([getattr(x, f) for f in FIELDS])
    with gzip.open(SILVER / f"{date}.csv.gz", "wt") as fh:
        fh.write(buf.getvalue())


def load_resolutions() -> dict[str, tuple[str, str]]:
    """Curated outcomes for exits that are not takeouts in the deal table (symbol -> resolution, note)."""
    if not RESOLUTIONS.exists():
        return {}
    with open(RESOLUTIONS, newline="") as fh:
        return {r["symbol"]: (r["resolution"], r["note"]) for r in csv.DictReader(fh)}


def resolve(m, resolutions: dict[str, tuple[str, str]]) -> tuple[str, str]:
    if m.deal_id:
        return "takeout_in_db", ""
    if m.spell.exit_class == "ticker_change":
        return "ticker_change", f"successor {m.spell.successor}"
    return resolutions.get(m.spell.symbol, ("unresolved", ""))


def load_deal_refs() -> list[DealRef]:
    with open(DEALS, newline="") as fh:
        return [DealRef(r["deal_id"], r["target_ticker"], r["announced_on"]) for r in csv.DictReader(fh)]


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--repo", type=Path, required=True)
    p.add_argument("--freq", choices=["monthly", "weekly"], default="monthly")
    p.add_argument("--since", default="2021-01-30")
    p.add_argument("--no-fetch", action="store_true", help="skip git fetch; sample the local clone as it is")
    args = p.parse_args()

    if not args.no_fetch:
        ensure_repo(args.repo)
    overrides = load_overrides(OVERRIDES)
    snapshots: list[tuple[str, list[Listing]]] = []
    for date, sha in sample_commits(args.repo, args.freq, args.since):
        path = SILVER / f"{date}.csv.gz"
        cached = read_snapshot_csv(path, overrides) if path.exists() else None
        if cached is None:
            raw = load_snapshot(args.repo, sha)
            n = sum(len(v) for v in raw.values())
            if n < MIN_ROWS:
                print(f"{date} skipped: {n} rows", file=sys.stderr)
                continue
            cached = classify_snapshot(raw, overrides)
            write_silver(date, cached)
        snapshots.append((date, cached))
        print(f"{date} {sum(x.in_universe for x in cached)} universe rows of {len(cached)}", file=sys.stderr)

    stable = stable_layers(snapshots)
    counts = panel_counts(snapshots, stable)
    with open(COUNTS_OUT, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["snapshot_date", "layer", "cap_band", "n_companies"])
        for c in counts:
            w.writerow([c.date, c.layer, c.cap_band, c.n])

    spells = build_spells(snapshots, stable)
    exits = detect_exits(spells, snapshots[-1][0])
    matches = match_exits_to_deals(exits, load_deal_refs(), panel_start=snapshots[0][0])
    resolutions = load_resolutions()
    with open(EXITS_OUT, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow([
            "symbol", "name", "layer", "first_seen", "last_seen", "n_snapshots", "last_market_cap_usd_m",
            "max_market_cap_usd_m", "exit_class", "successor_symbol", "matched_deal_id", "flags",
            "resolution", "resolution_note",
        ])
        for m in matches:
            s = m.spell
            w.writerow([
                s.symbol, s.name, s.layer, s.first_seen, s.last_seen, s.n_snapshots,
                round((s.last_market_cap_usd or 0) / 1e6, 1), round((s.max_market_cap_usd or 0) / 1e6, 1),
                s.exit_class, s.successor, m.deal_id, ";".join(m.flags),
                *resolve(m, resolutions),
            ])
    print(f"{len(snapshots)} snapshots, {len(spells)} symbols, {len(exits)} exits", file=sys.stderr)


if __name__ == "__main__":
    main()
