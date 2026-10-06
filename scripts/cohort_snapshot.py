"""Print the cohort tables used in docs/research/2026-10-06_ai_bio_theme_reversal.md.

Usage: python scripts/cohort_snapshot.py [path/to/snapshot.csv]

Reads the one-day profile snapshot, prints markdown tables (per name, per layer, two-day path for
names that also carry a pre-spike close in config/universe.yaml) and the cross-sectional rank
correlations the case study cites.
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

from biotech_divedeep.signals.cohort import (
    classify_day,
    crowding_score,
    load_snapshot,
    spearman,
    summarize,
    two_day_path,
)
from biotech_divedeep.universe import load_universe

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = ROOT / "data" / "reference" / "ai_bio_cohort_snapshot_2026-10-06.csv"
# universe.yaml snapshots fetched 2026-10-05 before the open carry the 2026-10-02 close (D-022).
PRE_SPIKE_AS_OF = date(2026, 10, 5)
STOCK_LAYERS = {"data_generator", "clinical_genomics_dx", "ai_drug_design", "genomic_medicine", "launch"}


def pct(x: float) -> str:
    return f"{x * 100:+.1f}%"


def main(path: Path) -> None:
    snaps = load_snapshot(path)
    by = {s.ticker: s for s in snaps}
    cohort = [s for s in snaps if s.layer in STOCK_LAYERS]
    arkg, xbi = by["ARKG"].ret, by["XBI"].ret

    print("## Per name (cohort, sorted by day return)\n")
    print(
        "| Ticker | Layer | Day | vs ARKG | vs XBI | RVOL | Close / 52w low | From 52w high | Beta | Mkt cap B "
        "| Day class |"
    )
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    for s in sorted(cohort, key=lambda s: s.ret):
        print(
            f"| {s.ticker}{'*' if s.investor_named else ''} | {s.layer} | {pct(s.ret)} | {pct(s.ret - arkg)} | "
            f"{pct(s.ret - xbi)} | {s.rvol:.1f} | {s.off_low:.1f}x | {pct(s.from_high)} | {s.beta:.2f} | "
            f"{s.market_cap_usd / 1e9:.1f} | {classify_day(s)} |"
        )

    print("\n## Controls and benchmarks\n")
    print("| Ticker | Layer | Day | RVOL | Close / 52w low | From 52w high |")
    print("|---|---|---|---|---|---|")
    for s in sorted((s for s in snaps if s.layer not in STOCK_LAYERS), key=lambda s: s.ret):
        print(f"| {s.ticker} | {s.layer} | {pct(s.ret)} | {s.rvol:.1f} | {s.off_low:.1f}x | {pct(s.from_high)} |")

    print("\n## By layer (cohort)\n")
    print(
        "| Layer | n | Median day | $-vol weighted | Share down | Median RVOL | Median close/low "
        "| Median from high |"
    )
    print("|---|---|---|---|---|---|---|---|")
    for g in summarize(cohort, key=lambda s: s.layer):
        print(
            f"| {g.group} | {g.n} | {pct(g.median_ret)} | {pct(g.dollar_weighted_ret)} | {g.breadth_down:.0%} | "
            f"{g.median_rvol:.1f} | {g.median_off_low:.1f}x | {pct(g.median_from_high)} |"
        )

    print("\n## Two-day path (2026-10-02 close from config/universe.yaml -> 10-05 -> 10-06)\n")
    print("| Ticker | Mon 10-05 | Tue 10-06 | Net two days |")
    print("|---|---|---|---|")
    universe = load_universe()
    for c in universe.companies:
        if c.ticker in by and c.snapshot is not None and c.snapshot.as_of == PRE_SPIKE_AS_OF:
            spike, rev, net = two_day_path(c.snapshot.price, by[c.ticker])
            print(f"| {c.ticker} | {pct(spike)} | {pct(rev)} | {pct(net)} |")

    crowd = crowding_score(cohort)
    rets = [s.ret for s in cohort]
    print(f"\n## Rank correlations with the day return (cohort, n = {len(cohort)})\n")
    print("| Feature | Spearman rho |")
    print("|---|---|")
    for label, xs in [
        ("Range multiple (52w high / low)", [s.range_multiple for s in cohort]),
        ("Close / 52w low", [s.off_low for s in cohort]),
        ("Beta", [s.beta for s in cohort]),
        ("Relative volume", [s.rvol for s in cohort]),
        ("Market cap", [s.market_cap_usd for s in cohort]),
        ("Crowding score", [crowd[s.ticker] for s in cohort]),
    ]:
        print(f"| {label} | {spearman(xs, rets):+.2f} |")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT)
