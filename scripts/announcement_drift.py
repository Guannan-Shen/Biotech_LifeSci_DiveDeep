"""Post-announcement drift for named tickers (H17 method applied company by company).

Reads daily closes and benchmark returns (`scripts/mirror_daily_prices.py` output) and the event
log `data/reference/announcement_events.csv`; for every logged event computes the reaction (EAR,
SEAR, abnormal volume) and the drift that followed (BHAR from the close of day +1 to day +5,
+20, +60); scans for no-news shocks; writes one row per event and prints a summary by surprise
class and event type.

Two tickers cannot test H17: about 20 events each, overlapping windows and one benchmark. The
output is a case study that shows the method and how these two stocks behave around their own
news; the pre-registered test (`notes/backtests/2026-10-11_H17_post_announcement_drift.md`) runs
on the research universe.

Usage:
    python scripts/announcement_drift.py QSI NAUT [--bench EW_LIFESCI_200M] \
        [--prices data/reference/qsi_naut_daily_2021_2026.csv] [--out data/reference/announcement_drift_qsi_naut.csv]
"""

from __future__ import annotations

import argparse
import csv
from datetime import date
from pathlib import Path

from biotech_divedeep.signals.drift import (
    EventStats,
    Series,
    align,
    bhar,
    event_stats,
    no_news_shocks,
    resolve_event_index,
    summarize,
)

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "data" / "reference"
HORIZONS = (5, 20, 60)


def load_prices(path: Path) -> tuple[dict[str, list[tuple[date, float, float]]], dict[str, dict[date, float]]]:
    stocks: dict[str, list[tuple[date, float, float]]] = {}
    series: dict[str, dict[date, float]] = {}
    with open(path, newline="") as fh:
        for r in csv.DictReader(fh):
            d = date.fromisoformat(r["date"])
            if r["close"]:
                stocks.setdefault(r["symbol"], []).append((d, float(r["close"]), float(r["volume_or_n"] or 0)))
            elif r["ret_1d"]:
                series.setdefault(r["symbol"], {})[d] = float(r["ret_1d"])
    return stocks, series


def fmt(x: float | None, pct: bool = True) -> str:
    if x is None:
        return ""
    return f"{x:.4f}" if pct else f"{x:.2f}"


def run_ticker(ticker: str, s: Series, events: list[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    known: list[int] = []
    for ev in events:
        release = date.fromisoformat(ev["available_at"])
        i0, moved = resolve_event_index(s, release, ev["timing"], ev["date_precision"])
        if i0 is None:
            continue
        known.append(i0)
        st = event_stats(s, i0, HORIZONS, moved)
        rows.append(as_row(ticker, ev["event_id"], ev["event_type"], ev["guidance_effect"], st, s))
    for i in no_news_shocks(s, known):
        st = event_stats(s, i, HORIZONS)
        rows.append(as_row(ticker, f"{ticker}-X{s.dates[i]:%Y%m%d}", "no_news_shock", "", st, s))
    rows.sort(key=lambda r: r["day0"])
    return rows


def as_row(ticker: str, event_id: str, event_type: str, guidance: str, st: EventStats, s: Series) -> dict[str, str]:
    return {
        "event_id": event_id,
        "ticker": ticker,
        "event_type": event_type,
        "guidance_effect": guidance,
        "day0": st.day0.isoformat(),
        "day0_moved_by_volume": str(st.moved).lower(),
        "close_before": fmt(s.close[st.index - 1] if st.index > 0 else None, pct=False),
        "ear_0_1": fmt(st.ear),
        "sear": fmt(st.sear, pct=False),
        "abn_volume_0_1": fmt(st.av01, pct=False),
        "surprise": st.surprise(),
        "pre_run_m20_m2": fmt(st.pre_run),
        **{f"bhar_2_{k}": fmt(st.drift.get(k)) for k in HORIZONS},
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("tickers", nargs="+")
    p.add_argument("--prices", type=Path, default=REF / "qsi_naut_daily_2021_2026.csv")
    p.add_argument("--events", type=Path, default=REF / "announcement_events.csv")
    p.add_argument("--bench", default="EW_LIFESCI_200M")
    p.add_argument("--out", type=Path, default=REF / "announcement_drift_qsi_naut.csv")
    args = p.parse_args()

    stocks, series = load_prices(args.prices)
    with open(args.events, newline="") as fh:
        events = list(csv.DictReader(fh))
    out: list[dict[str, str]] = []
    stats_by: dict[str, list[EventStats]] = {}
    for t in args.tickers:
        t = t.upper()
        s = align(stocks[t], series[args.bench])
        rows = run_ticker(t, s, [e for e in events if e["ticker"] == t])
        out.extend(rows)
        for r in rows:
            i = s.dates.index(date.fromisoformat(r["day0"]))
            st = event_stats(s, i, HORIZONS)
            kind = "shock" if r["event_type"] == "no_news_shock" else "announcement"
            sign = "up" if (st.ear or 0) > 0 else "down"
            keys = [
                f"{t}|{kind}|{sign}",
                f"{t}|type={r['event_type']}",
                f"ALL|{kind}|surprise={st.surprise()}",
                f"ALL|{kind}|{sign}",
                f"ALL|guidance={r['guidance_effect'] or 'n/a'}",
            ]
            for key in keys:
                stats_by.setdefault(key, []).append(st)

    for t in args.tickers:
        s = align(stocks[t.upper()], series[args.bench])
        for h in (20, 60):
            base = [b for i in range(1, len(s.dates), 5) if (b := bhar(s, i + 2, i + h)) is not None]
            base.sort()
            print(
                f"baseline {t.upper()} every 5th day, BHAR[+2,+{h}]: n={len(base)} "
                f"mean={sum(base) / len(base):.3f} median={base[len(base) // 2]:.3f}"
            )

    with open(args.out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    print(f"{len(out)} rows -> {args.out} (benchmark {args.bench})\n")
    print(f"{'group':44s} {'h':>3s} {'n':>3s} {'EAR':>7s} {'mean':>7s} {'median':>7s} {'t':>6s} {'cont':>5s}")
    for key in sorted(stats_by):
        for h in (20, 60):
            sm = summarize(key, stats_by[key], h)
            if not sm.n:
                continue
            t = "" if sm.t_stat is None else f"{sm.t_stat:6.2f}"
            c = "" if sm.continuation is None else f"{sm.continuation:5.2f}"
            nums = f"{sm.mean_ear:7.3f} {sm.mean_drift:7.3f} {sm.median_drift:7.3f}"
            print(f"{key:44s} {h:3d} {sm.n:3d} {nums} {t:>6s} {c:>5s}")


if __name__ == "__main__":
    main()
