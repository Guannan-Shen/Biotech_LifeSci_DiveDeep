"""Technical and similarity panel for the AI-bio cohort and the launch layer (local machine).

Usage:
    python scripts/technical_panel.py --fetch                    # download daily bars from Stooq
    python scripts/technical_panel.py --event 2026-10-06         # features at the prior close vs the event return

Bars are read from data/raw/prices/stooq/<ticker>.csv (Date,Open,High,Low,Close,Volume). `--fetch` writes
those files first; Stooq is free and needs no key but is blocked from this cloud sandbox (Q-017).

Point-in-time: every feature is computed from bars up to the close BEFORE the event day, and the
outcome is the event-day return, so no feature can see the move it is asked to explain.
Features: RSI(14), KDJ(9) K and J, Bollinger(20, 2) %b and bandwidth, distance from the 50 and 200-day
averages, 12-1 momentum, acceleration (share of the 252-day log return earned in the last 63 days),
63-day return correlation with ARKG and with the equal-weight cohort, and the count of
heavy-distribution days in the prior 25 sessions.
"""

from __future__ import annotations

import argparse
import csv
import sys
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from statistics import median

from biotech_divedeep.signals.cohort import (
    HEAVY_RET,
    HEAVY_RVOL,
    load_snapshot,
    spearman,
    spearman_bootstrap_ci,
    spearman_permutation_p,
)
from biotech_divedeep.signals.technical import (
    acceleration,
    bollinger,
    equal_weight_index,
    kdj,
    momentum_12_1,
    pct_from_sma,
    range_position,
    return_similarity,
    rsi,
)

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "data" / "reference"
BARS = ROOT / "data" / "raw" / "prices" / "stooq"
STOOQ = "https://stooq.com/q/d/l/?s={symbol}.us&i=d"
THEME_ETF = "ARKG"
EXTRA = ["ARKG", "XBI", "IBB", "SPY", "QQQ"]


@dataclass(frozen=True)
class Bars:
    dates: list[str]
    high: list[float]
    low: list[float]
    close: list[float]
    volume: list[float]

    def upto(self, last_date: str) -> Bars:
        n = sum(1 for d in self.dates if d <= last_date)
        return Bars(self.dates[:n], self.high[:n], self.low[:n], self.close[:n], self.volume[:n])


def tickers() -> list[str]:
    names = [s.ticker for s in load_snapshot(REF / "ai_bio_cohort_snapshot_2026-10-06.csv")]
    names += [s.ticker for s in load_snapshot(REF / "launch_commercial_snapshot_2026-10-06.csv")]
    return sorted(set(names) | set(EXTRA))


def fetch_all(symbols: list[str]) -> None:
    BARS.mkdir(parents=True, exist_ok=True)
    for sym in symbols:
        url = STOOQ.format(symbol=sym.lower())
        req = urllib.request.Request(url, headers={"User-Agent": "BiotechDiveDeep research"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            (BARS / f"{sym}.csv").write_bytes(resp.read())
        time.sleep(0.5)


def load_bars(sym: str) -> Bars | None:
    path = BARS / f"{sym}.csv"
    if not path.exists():
        return None
    with open(path, newline="") as fh:
        rows = [r for r in csv.DictReader(fh) if r.get("Close")]
    return Bars(
        [r["Date"] for r in rows],
        [float(r["High"]) for r in rows],
        [float(r["Low"]) for r in rows],
        [float(r["Close"]) for r in rows],
        [float(r["Volume"] or 0) for r in rows],
    )


def heavy_days(b: Bars, sessions: int = 25) -> int:
    count = 0
    for i in range(max(51, len(b.close) - sessions), len(b.close)):
        base = median(b.volume[i - 50 : i]) or 1.0
        ret = b.close[i] / b.close[i - 1] - 1.0
        if ret <= HEAVY_RET and b.volume[i] / base >= HEAVY_RVOL:
            count += 1
    return count


def features(b: Bars, theme: Bars, basket: list[float]) -> dict[str, float | None]:
    c = b.close
    band = bollinger(c)[-1]
    k = kdj(b.high, b.low, c)[-1]
    lo, hi = min(b.low[-252:]), max(b.high[-252:])
    aligned = len(theme.close) == len(c) and len(basket) == len(c)
    return {
        "rsi14": rsi(c)[-1],
        "kdj_k": None if k is None else k.k,
        "kdj_j": None if k is None else k.j,
        "boll_pct_b": None if band is None else band.pct_b(c[-1]),
        "boll_bw": None if band is None else band.bandwidth,
        "from_sma50": pct_from_sma(c, 50)[-1],
        "from_sma200": pct_from_sma(c, 200)[-1],
        "mom_12_1": momentum_12_1(c),
        "accel": acceleration(c),
        "range_pos_252": range_position(c[-1], lo, hi),
        "sim_arkg_63": return_similarity(c, theme.close) if aligned else None,
        "sim_basket_63": return_similarity(c, basket) if aligned else None,
        "heavy_days_25": float(heavy_days(b)),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--event", default="2026-10-06", help="event date; features use the prior close")
    args = ap.parse_args()
    syms = tickers()
    if args.fetch:
        fetch_all(syms)
    loaded = {s: load_bars(s) for s in syms}
    missing = [s for s, b in loaded.items() if b is None]
    if missing:
        print(f"Missing bars for {missing}; run with --fetch on a machine that can reach Stooq.")
    bars = {s: b for s, b in loaded.items() if b is not None and args.event in b.dates}
    if THEME_ETF not in bars:
        print("ARKG bars are required for the similarity features.")
        return 2

    prior_day = {s: b.dates[b.dates.index(args.event) - 1] for s, b in bars.items()}
    event_ret = {
        s: b.close[b.dates.index(args.event)] / b.close[b.dates.index(args.event) - 1] - 1.0 for s, b in bars.items()
    }
    common = sorted(set.intersection(*(set(b.dates) for b in bars.values())))
    cutoff = prior_day[THEME_ETF]
    window = [d for d in common if d <= cutoff]

    def on(b: Bars) -> Bars:
        idx = {d: i for i, d in enumerate(b.dates)}
        keep = [idx[d] for d in window]
        return Bars(
            window,
            [b.high[i] for i in keep],
            [b.low[i] for i in keep],
            [b.close[i] for i in keep],
            [b.volume[i] for i in keep],
        )

    stocks = [s for s in bars if s not in EXTRA]
    aligned = {s: on(bars[s]) for s in bars}
    basket = equal_weight_index([aligned[s].close for s in stocks])
    panel = {s: features(aligned[s], aligned[THEME_ETF], basket) for s in stocks}

    keys = list(next(iter(panel.values())).keys())
    print(f"## Features at the {cutoff} close (event {args.event})\n")
    print("| Ticker | Event ret | " + " | ".join(keys) + " |")
    print("|---|---|" + "---|" * len(keys))
    for s in sorted(stocks, key=lambda s: event_ret[s]):
        vals = " | ".join("n/a" if panel[s][k] is None else f"{panel[s][k]:.2f}" for k in keys)
        print(f"| {s} | {event_ret[s] * 100:+.1f}% | {vals} |")

    print("\n## Rank tests vs the event return (exploratory; pre-registered in H13 amendment A1)\n")
    print("| Feature | n | rho | 90% interval | p |")
    print("|---|---|---|---|---|")
    for k in keys:
        pairs = [(panel[s][k], event_ret[s]) for s in stocks if panel[s][k] is not None]
        if len(pairs) < 8 or len({p[0] for p in pairs}) < 3:
            continue  # too few names or a near-constant feature (e.g., no heavy days anywhere)
        xs, ys = [float(p[0]) for p in pairs], [p[1] for p in pairs]
        lo, hi = spearman_bootstrap_ci(xs, ys)
        rho, p = spearman(xs, ys), spearman_permutation_p(xs, ys)
        print(f"| {k} | {len(xs)} | {rho:+.2f} | [{lo:+.2f}, {hi:+.2f}] | {p:.3f} |")
    return 0


if __name__ == "__main__":
    sys.exit(main())
