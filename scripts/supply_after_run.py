"""H18 part A: heavy-volume down days after a run, against run-matched controls.

Reads the life-science price panel (`data/silver/prices/mirror_daily_lifesci.csv.gz`, built by
`scripts/mirror_daily_prices.py`) and the `EW_LIFESCI_200M` benchmark, finds supply events
(`signals/supply.py`), matches each to up to three stocks in the same run state on the same date,
and reports matched BHAR differences with a calendar-month block bootstrap.

Pre-registration: `notes/backtests/2026-10-12_H18_insider_and_holder_flow.md`. The `--period`
flag filters events by day 0 *before* anything is summarized or written, so running the in-sample
period does not reveal out-of-sample results.

Usage:
    python scripts/supply_after_run.py --period in_sample [--variants] \
        [--events-out data/reference/h18a_supply_events_in_sample.csv]
"""

from __future__ import annotations

import argparse
import csv
import gzip
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from biotech_divedeep.signals.drift import align  # noqa: E402
from biotech_divedeep.signals.supply import (  # noqa: E402
    MatchedEvent,
    Segment,
    SupplyParams,
    block_bootstrap,
    day_states,
    holm,
    match_events,
    split_adjust,
)

SILVER = ROOT / "data" / "silver" / "prices" / "mirror_daily_lifesci.csv.gz"
BENCH_FILE = ROOT / "data" / "reference" / "qsi_naut_daily_2021_2026.csv"
LAYERS = {"therapeutics", "tools", "diagnostics"}
PERIODS = {
    "in_sample": (date(2021, 6, 1), date(2023, 12, 31)),
    "out_of_sample": (date(2024, 1, 1), date(2025, 9, 30)),
    "holdout": (date(2025, 10, 1), date(2099, 1, 1)),
}
MAX_GAP = 10  # sessions; a longer gap splits a symbol into separate segments (ticker reuse)
HORIZONS = (20, 60, 126, 252)


def _f(x: str) -> float | None:
    try:
        return float(x) if x not in ("", None) else None
    except ValueError:
        return None


def load_bench(path: Path, name: str = "EW_LIFESCI_200M") -> dict[date, float]:
    out: dict[date, float] = {}
    with open(path, newline="") as fh:
        for r in csv.DictReader(fh):
            if r["symbol"] == name and r["ret_1d"]:
                out[date.fromisoformat(r["date"])] = float(r["ret_1d"])
    return out


def load_segments(path: Path, calendar: list[date], bench: dict[date, float], p: SupplyParams) -> list[Segment]:
    pos = {d: g for g, d in enumerate(calendar)}
    rows: dict[str, list[tuple[date, float, float, float | None, str, float | None]]] = defaultdict(list)
    with gzip.open(path, "rt", newline="") as fh:
        for r in csv.DictReader(fh):
            if r["layer"] not in LAYERS:
                continue
            c = _f(r["close"])
            if c is None or c <= 0:
                continue
            d = date.fromisoformat(r["date"])
            if d not in pos:
                continue
            rows[r["symbol"]].append(
                (d, c, _f(r["volume"]) or 0.0, _f(r["market_cap_usd"]), r["layer"], _f(r["ret_1d"]))
            )
    segments: list[Segment] = []
    n_splits = 0
    for sym, rs in rows.items():
        rs.sort()
        chunks: list[list] = [[rs[0]]]
        for prev, cur in zip(rs, rs[1:], strict=False):
            if pos[cur[0]] - pos[prev[0]] > MAX_GAP:
                chunks.append([])
            chunks[-1].append(cur)
        for ch in chunks:
            if len(ch) < p.lookback + 30:
                continue
            adj_c, adj_v, splits = split_adjust([x[1] for x in ch], [x[5] for x in ch], [x[2] for x in ch])
            n_splits += len(splits)
            series = align([(x[0], c, v) for x, c, v in zip(ch, adj_c, adj_v, strict=True)], bench)
            caps = [x[3] for x in ch]
            layers = [x[4] for x in ch]
            layer = max(set(layers), key=layers.count)
            segments.append(Segment(sym, layer, series, caps, day_states(series, caps, p)))
    print(f"split-adjusted {n_splits} split days")
    return segments


def in_period(e: MatchedEvent, period: str) -> bool:
    lo, hi = PERIODS[period]
    return lo <= e.day0 <= hi


def summarize(events: list[MatchedEvent], k: int) -> dict:
    pairs = [(e.diff(k), e.day0.strftime("%Y-%m")) for e in events if e.diff(k) is not None]
    diff = block_bootstrap([p[0] for p in pairs], [p[1] for p in pairs])
    ev = [e.event_bhar[k] for e in events if e.event_bhar.get(k) is not None]
    ct = [e.control_bhar[k] for e in events if e.control_bhar.get(k) is not None]
    return {
        "k": k,
        "n": diff.n,
        "months": diff.n_clusters,
        "event_mean": sum(ev) / len(ev) if ev else None,
        "control_mean": sum(ct) / len(ct) if ct else None,
        "diff_mean": diff.mean,
        "diff_median": diff.median,
        "diff_lo": diff.lo,
        "diff_hi": diff.hi,
        "share_diff_negative": diff.share_negative,
        "diff_trimmed": diff.trimmed_mean,
        "p": diff.p_two_sided,
        "event_doubled": sum(x >= 1.0 for x in ev) / len(ev) if ev else None,
        "control_doubled": sum(x >= 1.0 for x in ct) / len(ct) if ct else None,
    }


def pct(x: float | None, nd: int = 1) -> str:
    return "" if x is None else f"{100 * x:.{nd}f}%"


def secondary(events: list[MatchedEvent]) -> dict:
    with_c = [e for e in events if e.controls]
    dd = [(e.drawdown_event, e.drawdown_controls) for e in with_c if e.drawdown_event is not None]
    sh = [(e.shares_event, e.shares_controls) for e in with_c if e.shares_event is not None]
    dd_e = [a for a, _ in dd]
    dd_c = [b for _, b in dd if b is not None]
    sh_e = [a for a, _ in sh]
    sh_c = [b for _, b in sh if b is not None]
    return {
        "dd40_event": sum(x <= -0.4 for x in dd_e) / len(dd_e) if dd_e else None,
        "dd40_controls_mean_dd": sum(dd_c) / len(dd_c) if dd_c else None,
        "dd_event_mean": sum(dd_e) / len(dd_e) if dd_e else None,
        "shares10_event": sum(x >= 0.10 for x in sh_e) / len(sh_e) if sh_e else None,
        "shares10_controls": sum(x >= 0.10 for x in sh_c) / len(sh_c) if sh_c else None,
        "n_with_controls": len(with_c),
    }


def write_events(path: Path, events: list[MatchedEvent]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        head = ["day0", "symbol", "band", "run_ratio", "rel_volume", "ret0", "controls"]
        for k in HORIZONS:
            head += [f"bhar_{k}", f"ctrl_bhar_{k}", f"diff_{k}"]
        head += ["drawdown_252", "ctrl_drawdown_252", "share_growth_120", "ctrl_share_growth_120"]
        w.writerow(head)

        def f(x: float | None) -> str:
            return "" if x is None else f"{x:.4f}"

        for e in events:
            row = [e.day0.isoformat(), e.symbol, e.band, f(e.run_ratio), f(e.rel_volume), f(e.ret0)]
            row.append(" ".join(e.controls))
            for k in HORIZONS:
                row += [f(e.event_bhar.get(k)), f(e.control_bhar.get(k)), f(e.diff(k))]
            row += [f(e.drawdown_event), f(e.drawdown_controls), f(e.shares_event), f(e.shares_controls)]
            w.writerow(row)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--prices", type=Path, default=SILVER)
    ap.add_argument("--bench", type=Path, default=BENCH_FILE)
    ap.add_argument("--period", choices=sorted(PERIODS), required=True)
    ap.add_argument("--variants", action="store_true", help="also run the 18 pre-registered cells")
    ap.add_argument("--events-out", type=Path)
    args = ap.parse_args()

    bench = load_bench(args.bench)
    calendar = sorted(bench)
    base = SupplyParams()
    # Price loading does not depend on the thresholds except the lookback, so one load serves all.
    segments = load_segments(args.prices, calendar, bench, base)
    print(f"{len(segments)} symbol segments, calendar {calendar[0]} to {calendar[-1]}")

    def run(p: SupplyParams) -> list[MatchedEvent]:
        segs = [Segment(s.symbol, s.layer, s.series, s.caps, day_states(s.series, s.caps, p)) for s in segments]
        return [e for e in match_events(segs, calendar, bench, p, HORIZONS) if in_period(e, args.period)]

    events = run(base)
    print(f"\nBase cell ({args.period}): {len(events)} events, {sum(1 for e in events if e.controls)} with controls")
    print(
        "| k | n | months | event BHAR | control BHAR | matched diff | median | trimmed | 90% interval | p | "
        "share diff < 0 | event BHAR >= +100% | control mean >= +100% |"
    )
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for k in HORIZONS:
        s = summarize([e for e in events if e.controls], k)
        print(
            f"| {k} | {s['n']} | {s['months']} | {pct(s['event_mean'])} | {pct(s['control_mean'])} | "
            f"{pct(s['diff_mean'])} | {pct(s['diff_median'])} | {pct(s['diff_trimmed'])} | "
            f"{pct(s['diff_lo'])} to {pct(s['diff_hi'])} | {s['p']:.4f} | {pct(s['share_diff_negative'], 0)} | "
            f"{pct(s['event_doubled'], 0)} | {pct(s['control_doubled'], 0)} |"
        )
    sec = secondary(events)
    print(
        f"\nDrawdown >= 40% within 252 sessions: events {pct(sec['dd40_event'], 0)}; "
        f"mean max drawdown events {pct(sec['dd_event_mean'], 0)}, controls {pct(sec['dd40_controls_mean_dd'], 0)}"
    )
    print(
        f"Implied share count +10% within 120 sessions: events {pct(sec['shares10_event'], 0)}, "
        f"controls {pct(sec['shares10_controls'], 0)}"
    )
    by_band: dict[str, list[MatchedEvent]] = defaultdict(list)
    for e in events:
        if e.controls:
            by_band[e.band].append(e)
    print("\nBy cap band, k = 126:")
    for band in ("micro", "small", "mid"):
        s = summarize(by_band.get(band, []), 126)
        print(f"  {band}: n {s['n']}, diff {pct(s['diff_mean'])} ({pct(s['diff_lo'])} to {pct(s['diff_hi'])})")

    if args.events_out:
        write_events(args.events_out, events)
        print(f"\nevents -> {args.events_out}")

    if args.variants:
        print("\nVariants, k = 126 matched difference (raw 90% intervals; Holm adjustment in the note):")
        cells = []
        for rm in (1.75, 2.0, 3.0):
            for vm in (2.5, 3.0, 4.0):
                for rx in (-0.03, -0.06):
                    p = SupplyParams(run_mult=rm, vol_mult=vm, ret_max=rx, abn_max=rx)
                    cells.append((rm, vm, rx, summarize([e for e in run(p) if e.controls], 126)))
        adj = holm([c[3]["p"] for c in cells])
        print("| run_mult | vol_mult | ret_max | n | mean diff | median diff | trimmed | 90% interval | p | Holm p |")
        print("|---|---|---|---|---|---|---|---|---|---|")
        for (rm, vm, rx, s), pa in zip(cells, adj, strict=True):
            print(
                f"| {rm} | {vm} | {rx:.0%} | {s['n']} | {pct(s['diff_mean'])} | {pct(s['diff_median'])} | "
                f"{pct(s['diff_trimmed'])} | {pct(s['diff_lo'])} to {pct(s['diff_hi'])} | {s['p']:.4f} | {pa:.4f} |"
            )


if __name__ == "__main__":
    main()
