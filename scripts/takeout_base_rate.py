"""Measured takeout hazard by market-cap band, 2021-02 to the latest snapshot (H8, Q-032, D-040).

Numerator: strategic and contested deals in `data/reference/biotech_takeouts.csv` whose target was a
listed therapeutics company in the month before the announcement. Its band is read from that
snapshot. Denominator: therapeutics company-months per band in the monthly listing panel
(`data/silver/listings/`, written by `scripts/listing_history.py`), divided by 12.

The numerator is only as complete as the deal table. `data/reference/lifesci_listing_exits.csv`
lists every exit, so unmatched large exits show what the table still misses; small and mid exits are
not yet resolved, which biases the micro band hazard down.

    python scripts/takeout_base_rate.py            # print and write the table
"""

from __future__ import annotations

import csv
import sys
from bisect import bisect_right
from collections import defaultdict
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
from biotech_divedeep.models.takeout import STRATEGIC_KINDS, hazard_from_counts, load_deals  # noqa: E402

SILVER = ROOT / "data" / "silver" / "listings"
OUT = ROOT / "data" / "reference" / "takeout_base_rates_2021_2026.csv"
BANDS = ["micro_under_0.3", "small_0.3_to_2", "mid_2_to_10", "large_10_to_25", "mega_over_25"]
EXCLUDED_SUBLAYERS = {"large_pharma", "generics", "animal_health", "royalty"}  # acquirers, not targets


def main() -> None:
    files = sorted(SILVER.glob("*.csv.gz"))
    if not files:
        raise SystemExit("run scripts/listing_history.py first")
    overrides = load_overrides(ROOT / "data" / "reference" / "lifesci_layer_overrides.csv")
    snapshots = [(path.name[:10], read_snapshot_csv(path, overrides)) for path in files]
    stable = stable_layers(snapshots)
    dates: list[str] = []
    snap: dict[str, dict[str, float | None]] = {}
    months = defaultdict(int)
    for date, listings in snapshots:
        dates.append(date)
        rows: dict[str, float | None] = {}
        for item in listings:
            hit = stable.get(stable_key(item))
            if hit is None or hit[0] != "therapeutics" or hit[1] in EXCLUDED_SUBLAYERS:
                continue
            rows[item.symbol] = item.market_cap_usd
            months[cap_band(item.market_cap_usd)] += 1
        snap[date] = rows
    # The last snapshot is days after the previous one; count only whole months of exposure.
    if len(dates) > 1 and dates[-1][:7] == dates[-2][:7]:
        for cap in snap[dates[-1]].values():
            months[cap_band(cap)] -= 1

    deals_by_band = defaultdict(list)
    skipped = []
    for d in load_deals(ROOT / "data" / "reference" / "biotech_takeouts.csv"):
        if d.deal_kind not in STRATEGIC_KINDS or not (dates[0] < d.announced_on <= dates[-1]):
            continue
        i = bisect_right(dates, d.announced_on) - 1  # latest snapshot on or before the announcement
        # Step back one snapshot when the announcement falls in the snapshot month itself, so the
        # band reflects the unaffected price where possible.
        i = max(0, i - 1) if dates[i][:7] == d.announced_on[:7] else i
        if d.target_ticker not in snap[dates[i]]:
            skipped.append(d.target_ticker)
            continue
        deals_by_band[cap_band(snap[dates[i]][d.target_ticker])].append(d.target_ticker)

    years_total = (len(dates) - 1) / 12
    print(f"{len(dates)} monthly snapshots {dates[0]} to {dates[-1]} (about {years_total:.1f} years)")
    print(f"{'band':<18}{'co-years':>9}{'deals':>7}{'hazard':>8}{'80% interval':>18}")
    out_rows = []
    for band in BANDS + ["all_under_25"]:
        if band == "all_under_25":
            cy = sum(months[b] for b in BANDS[:4]) / 12
            n = sum(len(deals_by_band[b]) for b in BANDS[:4])
        else:
            cy = months[band] / 12
            n = len(deals_by_band[band])
        post = hazard_from_counts(n, cy, prior_a=1.0, prior_b=25.0)
        lo, hi = post.interval
        print(f"{band:<18}{cy:>9.0f}{n:>7}{post.mean:>8.1%}   {lo:>6.1%} to {hi:>5.1%}")
        out_rows.append([band, round(cy, 1), n, round(post.mean, 4), round(lo, 4), round(hi, 4)])
    if skipped:
        print(f"Deals not found in the prior snapshot (not counted): {', '.join(sorted(set(skipped)))}")
    with open(OUT, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["cap_band", "company_years", "strategic_deals", "hazard_mean", "hazard_p10", "hazard_p90"])
        w.writerows(out_rows)
    print(OUT)


if __name__ == "__main__":
    main()
