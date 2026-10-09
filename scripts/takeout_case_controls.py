"""Pick matched controls for takeout case studies from the point-in-time listing panel (D-041).

For each case (a strategic or contested deal in `data/reference/biotech_takeouts.csv`), take the
monthly snapshot about 90 days before the announcement and choose the `--n` therapeutics companies
nearest in log market cap to the target that:

- share the target's stable layer and cap band at that snapshot;
- are not large pharma, generics, animal health or royalty vehicles;
- are still listed in the snapshot nearest the announcement (no dead companies);
- were not announced as targets within 365 days after the case's announcement.

Controls whose 365-day window runs past the latest snapshot are flagged `censored`: a deal may
still come. Size is the only automatic match because it is the strongest measured driver
(`takeout_base_rates_2021_2026.csv`). The output is a ranked pool in `data/silver/`; the coder picks
controls with the same business stage (commercial, launch, clinical) and, where possible, area,
and records them with a `match_reason` in `data/reference/takeout_case_controls.csv`.

    python scripts/takeout_case_controls.py --cases TK-2026-01 TK-2026-03 --n 3
    python scripts/takeout_case_controls.py --all --since 2022-01-01 --n 2
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import math
import sys
from bisect import bisect_right
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from biotech_divedeep.connectors.listings import (  # noqa: E402
    cap_band,
    load_overrides,
    read_snapshot_csv,
    stable_key,
    stable_layers,
)
from biotech_divedeep.models.takeout import STRATEGIC_KINDS, load_deals  # noqa: E402

SILVER = ROOT / "data" / "silver" / "listings"
OUT = ROOT / "data" / "silver" / "takeout_control_pools.csv"  # working pool; curated picks go to data/reference
EXCLUDED_SUBLAYERS = {"large_pharma", "generics", "animal_health", "royalty"}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--cases", nargs="*", default=[])
    p.add_argument("--all", action="store_true")
    p.add_argument("--since", default="2021-06-01")
    p.add_argument("--n", type=int, default=15)
    p.add_argument("--lag-days", type=int, default=90)
    args = p.parse_args()

    overrides = load_overrides(ROOT / "data" / "reference" / "lifesci_layer_overrides.csv")
    files = sorted(SILVER.glob("*.csv.gz"))
    snapshots = [(f.name[:10], read_snapshot_csv(f, overrides)) for f in files]
    stable = stable_layers(snapshots)
    dates = [d for d, _ in snapshots]
    by_date = dict(snapshots)

    deals = load_deals(ROOT / "data" / "reference" / "biotech_takeouts.csv")
    targets_by_ticker: dict[str, list[str]] = {}
    for d in deals:
        targets_by_ticker.setdefault(d.target_ticker, []).append(d.announced_on)
    wanted = [
        d for d in deals
        if d.deal_kind in STRATEGIC_KINDS
        and (d.deal_id in args.cases or (args.all and d.announced_on >= args.since))
    ]

    rows = []
    for d in sorted(wanted, key=lambda x: x.announced_on):
        t0 = dt.date.fromisoformat(d.announced_on)
        ref = (t0 - dt.timedelta(days=args.lag_days)).isoformat()
        i = bisect_right(dates, ref) - 1
        j = bisect_right(dates, d.announced_on) - 1
        if i < 0 or j < 0:
            print(f"{d.deal_id}: before the panel starts", file=sys.stderr)
            continue
        snap = {x.symbol: x for x in by_date[dates[i]]}
        at_t0 = {x.symbol for x in by_date[dates[j]]}
        target = snap.get(d.target_ticker)
        if target is None or not target.market_cap_usd:
            print(f"{d.deal_id} {d.target_ticker}: not in the {dates[i]} snapshot", file=sys.stderr)
            continue
        band = cap_band(target.market_cap_usd)
        horizon = (t0 + dt.timedelta(days=365)).isoformat()
        pool = []
        for x in snap.values():
            hit = stable.get(stable_key(x))
            if not hit or hit[0] != "therapeutics" or hit[1] in EXCLUDED_SUBLAYERS:
                continue
            if x.symbol == d.target_ticker or x.symbol not in at_t0 or not x.market_cap_usd:
                continue
            if cap_band(x.market_cap_usd) != band:
                continue
            if any(d.announced_on <= a <= horizon for a in targets_by_ticker.get(x.symbol, [])):
                continue
            pool.append((abs(math.log(x.market_cap_usd / target.market_cap_usd)), x))
        pool.sort(key=lambda t: (t[0], t[1].symbol))
        for rank, (_, x) in enumerate(pool[: args.n], start=1):
            rows.append([
                d.deal_id, d.target_ticker, d.announced_on, rank, x.symbol, x.name, dates[i],
                round(target.market_cap_usd / 1e6, 1), round(x.market_cap_usd / 1e6, 1), band,
                horizon > dates[-1], "to_code",
            ])
        print(f"{d.deal_id} {d.target_ticker}: {len(pool)} candidates in {band}", file=sys.stderr)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow([
            "case_id", "target_ticker", "t0", "rank", "control_ticker", "control_name", "match_snapshot",
            "target_mcap_usd_m", "control_mcap_usd_m", "cap_band", "censored", "coding_status",
        ])
        w.writerows(rows)
    print(OUT, file=sys.stderr)


if __name__ == "__main__":
    main()
