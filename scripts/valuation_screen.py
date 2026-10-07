"""Sales multiples, required growth and stretch for the AI-bio cohort and the launch layer.

Usage: python scripts/valuation_screen.py

Reads the two 2026-10-06 profile snapshots and data/reference/revenue_baseline_2026.csv, then prints
the tables in docs/research/2026-10-07_valuation_stretch_and_launch_layer.md:
1. Per name: day return, run size, 52-week range position before the day, P/S on the revenue base,
   growth-adjusted P/S, revenue CAGR required for a 0% and a 10% annual return at a 5x exit multiple.
2. Layer medians.
3. Rank tests of each feature against the 2026-10-06 return, with bootstrap intervals and
   permutation p-values, so the weakness of one-day evidence is visible in numbers.
"""

from __future__ import annotations

import csv
from pathlib import Path
from statistics import median

from biotech_divedeep.models.multiples import growth_adjusted_ps, price_to_sales, required_cagr
from biotech_divedeep.signals.cohort import (
    DaySnapshot,
    load_snapshot,
    spearman,
    spearman_bootstrap_ci,
    spearman_permutation_p,
)

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "data" / "reference"
AI_COHORT = REF / "ai_bio_cohort_snapshot_2026-10-06.csv"
LAUNCH = REF / "launch_commercial_snapshot_2026-10-06.csv"
REVENUE = REF / "revenue_baseline_2026.csv"
AI_LAYERS = {"data_generator", "clinical_genomics_dx", "ai_drug_design", "genomic_medicine"}
TERMINAL_PS = 5.0  # own_assumption: a mature, profitable life-science business; sensitivity in the doc
YEARS = 5.0


def pct(x: float | None, digits: int = 1) -> str:
    return "n/a" if x is None else f"{x * 100:+.{digits}f}%"


def num(x: float | None, fmt: str = "{:.1f}") -> str:
    return "n/a" if x is None else fmt.format(x)


def load_revenue() -> dict[str, dict[str, str]]:
    with open(REVENUE, newline="") as fh:
        return {r["ticker"]: r for r in csv.DictReader(fh)}


def rows() -> list[tuple[DaySnapshot, dict[str, str] | None]]:
    revenue = load_revenue()
    ai = [s for s in load_snapshot(AI_COHORT) if s.layer in AI_LAYERS]
    launch = load_snapshot(LAUNCH)
    return [(s, revenue.get(s.ticker)) for s in ai + launch]


def metrics(s: DaySnapshot, rev: dict[str, str] | None) -> dict[str, float | None]:
    out: dict[str, float | None] = {
        "ret": s.ret,
        "off_low": s.off_low,
        "prev_pos": s.prev_range_position,
        "from_high": s.from_high,
        "ps": None,
        "growth": None,
        "psg": None,
        "cagr0": None,
        "cagr10": None,
        "gap": None,
    }
    if rev is None:
        return out
    revenue = float(rev["value_usd_m"]) * 1e6
    ps = price_to_sales(s.market_cap_usd, revenue)
    growth = float(rev["yoy_growth"]) if rev["yoy_growth"] else None
    out.update(
        ps=ps,
        growth=growth,
        psg=None if growth is None else growth_adjusted_ps(ps, growth),
        cagr0=required_cagr(s.market_cap_usd, revenue, TERMINAL_PS, YEARS, 0.0),
        cagr10=required_cagr(s.market_cap_usd, revenue, TERMINAL_PS, YEARS, 0.10),
    )
    if growth is not None:
        out["gap"] = growth - out["cagr0"]  # current growth minus the growth the price needs
    return out


def test_row(label: str, xs: list[float], ys: list[float]) -> str:
    rho = spearman(xs, ys)
    lo, hi = spearman_bootstrap_ci(xs, ys)
    p = spearman_permutation_p(xs, ys)
    return f"| {label} | {len(xs)} | {rho:+.2f} | [{lo:+.2f}, {hi:+.2f}] | {p:.3f} |"


def main() -> None:
    data = [(s, rev, metrics(s, rev)) for s, rev in rows()]

    print(f"## Per name (P/S on the revenue base; required CAGR at {TERMINAL_PS:.0f}x sales in {YEARS:.0f} years)\n")
    print(
        "| Ticker | Layer | 10-06 | Close / low | Range pos. before | From high | Basis | P/S | Growth | PSG "
        "| CAGR for 0% | CAGR for 10% | Growth gap |"
    )
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for s, rev, m in sorted(data, key=lambda t: (t[0].layer, -(t[2]["ps"] or 0.0))):
        basis = "none" if rev is None else rev["basis"]
        print(
            f"| {s.ticker}{'*' if s.investor_named else ''} | {s.layer} | {pct(m['ret'])} | {m['off_low']:.1f}x | "
            f"{m['prev_pos']:.2f} | {pct(m['from_high'], 0)} | {basis} | {num(m['ps'])} | {pct(m['growth'], 0)} | "
            f"{num(m['psg'], '{:.2f}')} | {pct(m['cagr0'], 0)} | {pct(m['cagr10'], 0)} | {pct(m['gap'], 0)} |"
        )

    print("\n## Layer medians\n")
    print("| Layer | n | Median 10-06 | Median close / low | Median P/S | Median growth | Median PSG |")
    print("|---|---|---|---|---|---|---|")
    layers: dict[str, list[dict[str, float | None]]] = {}
    for s, _, m in data:
        layers.setdefault(s.layer, []).append(m)
    for layer, ms in sorted(layers.items(), key=lambda kv: median(m["ret"] for m in kv[1])):

        def med(key: str, ms: list[dict[str, float | None]] = ms) -> float | None:
            vals = [m[key] for m in ms if m[key] is not None]
            return median(vals) if vals else None

        print(
            f"| {layer} | {len(ms)} | {pct(med('ret'))} | {num(med('off_low'), '{:.1f}x')} | {num(med('ps'))} | "
            f"{pct(med('growth'), 0)} | {num(med('psg'), '{:.2f}')} |"
        )

    print("\n## Rank tests vs the 2026-10-06 return (90% bootstrap interval, two-sided permutation p)\n")
    print("| Feature and set | n | rho | 90% interval | p |")
    print("|---|---|---|---|---|")
    ai = [(s, m) for s, _, m in data if s.layer in AI_LAYERS]
    everyone = [(s, m) for s, _, m in data]
    for set_label, members in (("AI cohort", ai), ("AI cohort + launch layer", everyone)):
        for key, label in (
            ("off_low", "Close / 52w low"),
            ("prev_pos", "Range position before the day"),
            ("ps", "P/S on revenue base (required CAGR is a monotone transform; same rho)"),
            ("psg", "Growth-adjusted P/S"),
        ):
            pairs = [(m[key], m["ret"]) for _, m in members if m[key] is not None]
            if len(pairs) < 8:
                continue
            xs, ys = [float(p[0]) for p in pairs], [float(p[1]) for p in pairs]
            print(test_row(f"{label}, {set_label}", xs, ys))


if __name__ == "__main__":
    main()
