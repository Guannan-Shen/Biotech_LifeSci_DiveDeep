"""Supply after a run: heavy-volume down days in stocks that have doubled (H18 part A).

The investor's rule of thumb: block selling after a big rally marks the stock as somewhat
overvalued, even if it does not fall at once. Two explanations compete:

1. information: the seller (insider, fund, the company itself through an offering) knows the
   price is ahead of the value;
2. the run itself: big rallies in small biotech mean-revert whether or not anyone sells (H13).

So the test never compares a post-sale stock with the benchmark alone. Each supply event gets
**run-matched controls**: stocks in the same run state on the same date, same size band, that
printed no supply day. The matched difference isolates what the supply adds to the run.

Without seller identity (Form 4 and 13F come in part B, `signals/insider.py` and
`signals/fund_flow.py`), a supply day is approximated from closes and volume only: a down close
of at least 3%, at least 3% below the benchmark, on at least 3x the volume of days [-60, -11].
That mixes holder blocks, company offerings priced overnight and plain distribution; all three
add float at a price the market had to absorb.

Pure functions over `drift.Series` objects (one per contiguous symbol segment), oldest first.
Point-in-time: run state and supply on day t use closes and volumes through day t only (the run
is measured to t-1, the supply on t). Controls are picked with information up to t.
"""

from __future__ import annotations

import math
import random
from collections import defaultdict, deque
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date

from biotech_divedeep.signals.drift import Series

CAP_BANDS: tuple[tuple[str, float, float], ...] = (
    ("micro", 50e6, 300e6),
    ("small", 300e6, 2e9),
    ("mid", 2e9, 20e9),
)


@dataclass(frozen=True)
class SupplyParams:
    lookback: int = 126  # sessions over which the run is measured
    run_mult: float = 2.0  # close(t-1) / close(t-1-lookback)
    near_high: float = 0.75  # close(t-1) / max close over the lookback window
    ret_max: float = -0.03  # stock return on the supply day
    abn_max: float = -0.03  # stock minus benchmark on the supply day
    vol_mult: float = 3.0  # volume / mean volume over vol_base
    vol_base: tuple[int, int] = (-60, -11)
    dedupe: int = 60  # sessions between events in one symbol
    min_close: float = 1.0
    min_cap: float = 50e6
    max_cap: float = 20e9


DEFAULT_PARAMS = SupplyParams()


@dataclass(frozen=True)
class DayState:
    """Per-session features of one symbol segment (lists aligned with `Series.dates`)."""

    run_ratio: list[float | None]
    near_high: list[float | None]
    in_run: list[bool]
    rel_volume: list[float | None]
    supply: list[bool]


def cap_band(cap: float | None) -> str | None:
    if cap is None:
        return None
    for name, lo, hi in CAP_BANDS:
        if lo <= cap < hi:
            return name
    return None


def _rolling_max(values: Sequence[float], window: int) -> list[float | None]:
    """Max over [i-window+1, i] with a monotonic deque; None until the window is full."""
    out: list[float | None] = []
    dq: deque[int] = deque()
    for i, v in enumerate(values):
        while dq and values[dq[-1]] <= v:
            dq.pop()
        dq.append(i)
        if dq[0] <= i - window:
            dq.popleft()
        out.append(values[dq[0]] if i >= window - 1 else None)
    return out


def day_states(s: Series, caps: Sequence[float | None], p: SupplyParams = DEFAULT_PARAMS) -> DayState:
    """Run state and supply flag for every session of a segment.

    Run state on day i uses closes through i-1: close(i-1) / close(i-1-lookback) >= run_mult and
    close(i-1) at least `near_high` of the max close over the window. Supply on day i: run state,
    return and abnormal return at or below the thresholds, relative volume at or above
    `vol_mult`, and the day -1 close and market cap inside the universe filters.
    """
    n = len(s.dates)
    roll = _rolling_max(s.close, p.lookback + 1)
    vol_prefix = [0.0]
    for v in s.volume:
        vol_prefix.append(vol_prefix[-1] + (v or 0.0))
    run_ratio: list[float | None] = [None] * n
    nh: list[float | None] = [None] * n
    in_run = [False] * n
    rel_vol: list[float | None] = [None] * n
    supply = [False] * n
    lo, hi = p.vol_base
    for i in range(1, n):
        j = i - 1
        if j - p.lookback >= 0 and s.close[j - p.lookback] > 0:
            run_ratio[i] = s.close[j] / s.close[j - p.lookback]
            mx = roll[j]
            nh[i] = s.close[j] / mx if mx else None
            cap_prev = caps[j]
            in_run[i] = (
                run_ratio[i] >= p.run_mult  # type: ignore[operator]
                and nh[i] is not None
                and nh[i] >= p.near_high  # type: ignore[operator]
                and s.close[j] >= p.min_close
                and cap_prev is not None
                and p.min_cap <= cap_prev < p.max_cap
            )
        a, b = i + lo, i + hi
        if a >= 0:
            base = (vol_prefix[b + 1] - vol_prefix[a]) / (b - a + 1)
            rel_vol[i] = s.volume[i] / base if base > 0 and s.volume[i] is not None else None
        if not in_run[i]:
            continue
        r, br = s.stock_ret[i], s.bench_ret[i]
        if r is None or br is None or rel_vol[i] is None:
            continue
        supply[i] = r <= p.ret_max and (r - br) <= p.abn_max and rel_vol[i] >= p.vol_mult  # type: ignore[operator]
    return DayState(run_ratio, nh, in_run, rel_vol, supply)


def split_adjust(
    close: Sequence[float],
    ret_1d: Sequence[float | None],
    volume: Sequence[float],
    band: tuple[float, float] = (0.55, 1.8),
    tol: float = 0.15,
) -> tuple[list[float], list[float], list[int]]:
    """Back-adjust closes and volumes for splits the mirror's raw `lastsale` does not adjust.

    The screener's one-day return is computed against the split-adjusted prior close, so on a
    split day the raw close ratio and the reported return disagree by the split factor
    f = (close_t / close_{t-1}) / (1 + ret_t). A day counts as a split when f falls outside `band`
    and the next session is consistent again (|close_{t+1} / close_t / (1 + ret_{t+1}) - 1| <= tol);
    a stale `lastsale` fails that second test because the missed move shows up the next day.
    Earlier closes are multiplied by f and earlier volumes divided by f. A 1-for-20 reverse split
    otherwise reads as a 20x run.
    """
    n = len(close)
    factors = [1.0] * n
    splits: list[int] = []
    for t in range(1, n):
        r = ret_1d[t]
        if r is None or r <= -1.0 or close[t - 1] <= 0:
            continue
        f = (close[t] / close[t - 1]) / (1.0 + r)
        if band[0] <= f <= band[1]:
            continue
        if t + 1 >= n:
            continue  # no next session to confirm the new level
        r2 = ret_1d[t + 1]
        if r2 is None or r2 <= -1.0 or close[t] <= 0:
            continue
        if abs(close[t + 1] / close[t] / (1.0 + r2) - 1.0) > tol:
            continue
        factors[t] = f
        splits.append(t)
    adj_c, adj_v = list(close), list(volume)
    cum = 1.0
    for t in range(n - 1, -1, -1):
        adj_c[t] = close[t] * cum
        adj_v[t] = volume[t] / cum if cum else volume[t]
        cum *= factors[t]
    return adj_c, adj_v, splits


def pick_events(state: DayState, dedupe: int) -> list[int]:
    """First supply day of each episode; later supply days within `dedupe` sessions are skipped."""
    out: list[int] = []
    for i, flag in enumerate(state.supply):
        if flag and (not out or i - out[-1] >= dedupe):
            out.append(i)
    return out


def bhar_dates(s: Series, bench: Mapping[date, float], start: date, end: date) -> float | None:
    """BHAR of the stock vs the benchmark over trading dates in [start, end].

    Stock returns are the series' close-to-close returns dated on or after `start`. If the series
    ends before `end` (takeout, delisting, symbol gap), the proceeds earn the benchmark from then
    on, so the abnormal return freezes rather than vanishes: (ps - pb_to_last) x pb_after.
    Returns None if the series has no return in the window or `start` precedes the series.
    """
    if not s.dates or start < s.dates[0] or start > end:
        return None
    ps, pb_in, last = 1.0, 1.0, None
    for i, d in enumerate(s.dates):
        if d < start or i == 0:
            continue
        if d > end:
            break
        r, b = s.stock_ret[i], s.bench_ret[i]
        if r is None or b is None:
            return None
        ps *= 1.0 + r
        pb_in *= 1.0 + b
        last = d
    if last is None:
        return None
    pb_after = 1.0
    for d, b in bench.items():
        if last < d <= end:
            pb_after *= 1.0 + b
    return (ps - pb_in) * pb_after


def max_drawdown_after(s: Series, i0: int, k: int) -> float | None:
    """Lowest close over (i0, i0+k] relative to the close at i0, minus 1."""
    if i0 >= len(s.dates) - 1:
        return None
    base = s.close[i0]
    window = s.close[i0 + 1 : i0 + k + 1]
    return min(window) / base - 1.0 if base > 0 and window else None


def share_growth(s: Series, caps: Sequence[float | None], i0: int, k: int) -> float | None:
    """Implied share count (market cap / close) at i0+k, or the last session before it, over i0-1."""
    if i0 < 1:
        return None
    j = min(i0 + k, len(s.dates) - 1)

    def shares(i: int) -> float | None:
        c, cap = s.close[i], caps[i]
        return cap / c if cap and c else None

    a, b = shares(i0 - 1), shares(j)
    return b / a - 1.0 if a and b else None


@dataclass
class Segment:
    """One contiguous symbol history: the series, market caps and precomputed day states."""

    symbol: str
    layer: str
    series: Series
    caps: list[float | None]
    state: DayState
    index: dict[date, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.index:
            self.index = {d: i for i, d in enumerate(self.series.dates)}


@dataclass(frozen=True)
class MatchedEvent:
    symbol: str
    day0: date
    band: str
    run_ratio: float
    rel_volume: float
    ret0: float
    controls: tuple[str, ...]
    event_bhar: dict[int, float | None]
    control_bhar: dict[int, float | None]  # mean over controls with a value
    drawdown_event: float | None
    drawdown_controls: float | None
    shares_event: float | None
    shares_controls: float | None

    def diff(self, k: int) -> float | None:
        e, c = self.event_bhar.get(k), self.control_bhar.get(k)
        return None if e is None or c is None else e - c


def _mean(xs: Sequence[float]) -> float | None:
    return sum(xs) / len(xs) if xs else None


def match_events(
    segments: Sequence[Segment],
    calendar: Sequence[date],
    bench: Mapping[date, float],
    p: SupplyParams = DEFAULT_PARAMS,
    horizons: Sequence[int] = (20, 60, 126, 252),
    n_controls: int = 3,
    clean_window: int = 20,
    share_horizon: int = 120,
    dd_horizon: int = 252,
    dated: Sequence[tuple[str, date]] | None = None,
    require_run: bool = True,
) -> list[MatchedEvent]:
    """Events with matched controls and forward outcomes.

    By default the events are the supply days of each segment (part A). With `dated`, the events
    are given as (symbol, available date) pairs instead, e.g. Form 4 clusters (part B): each maps
    to the first session of that symbol on or after the date; with `require_run` it is kept only
    if the symbol is in run state that day. Controls come from the same date and cap band, nearest
    log run ratio; with `require_run` they must be in run state, and they never had a supply day
    (part A) or a dated event (part B) in the `clean_window` sessions up to day 0.

    Windows are counted on the global `calendar` (trading dates) so the event and its controls
    cover the same dates: entry at the close of day +1, BHAR over [+2, +k].
    """
    pos = {d: g for g, d in enumerate(calendar)}
    picks: dict[str, list[int]] = defaultdict(list)
    seg_by_symbol: dict[str, list[Segment]] = defaultdict(list)
    for seg in segments:
        seg_by_symbol[seg.symbol].append(seg)
    targets: list[tuple[Segment, int]] = []
    if dated is None:
        for seg in segments:
            for i in pick_events(seg.state, p.dedupe):
                targets.append((seg, i))
    else:
        for sym, d in dated:
            for seg in seg_by_symbol.get(sym, []):
                if not seg.series.dates or not seg.series.dates[0] <= d <= seg.series.dates[-1]:
                    continue
                i = seg.series.index_on_or_after(d)
                if i is not None and (not require_run or seg.state.in_run[i]):
                    targets.append((seg, i))
                break
    for seg, i in targets:
        picks[seg.symbol].append(i)

    # Candidate controls per date.
    by_date: dict[date, list[tuple[Segment, int]]] = {}
    for seg in segments:
        flagged = sorted(picks.get(seg.symbol, [])) if dated is not None else []
        last_flag = -10**9
        fi = 0
        for i, d in enumerate(seg.series.dates):
            if dated is None and seg.state.supply[i]:
                last_flag = i
            while fi < len(flagged) and flagged[fi] <= i:
                last_flag = flagged[fi]
                fi += 1
            if seg.state.run_ratio[i] is None or i - last_flag <= clean_window:
                continue
            if require_run and not seg.state.in_run[i]:
                continue
            by_date.setdefault(d, []).append((seg, i))

    out: list[MatchedEvent] = []
    for seg, i in targets:
        d0 = seg.series.dates[i]
        g0 = pos.get(d0)
        band = cap_band(seg.caps[i - 1]) if i >= 1 else None
        rr = seg.state.run_ratio[i]
        if g0 is None or band is None or rr is None or g0 + 2 >= len(calendar):
            continue
        cands = [
            (abs(math.log(c.state.run_ratio[j] / rr)), c, j)  # type: ignore[operator]
            for c, j in by_date.get(d0, [])
            if c.symbol != seg.symbol and cap_band(c.caps[j - 1]) == band and c.state.run_ratio[j]
        ]
        cands.sort(key=lambda x: (x[0], x[1].symbol))
        chosen = cands[:n_controls]
        start = calendar[g0 + 2]
        ev_b: dict[int, float | None] = {}
        ct_b: dict[int, float | None] = {}
        for k in horizons:
            if g0 + k >= len(calendar):
                ev_b[k] = ct_b[k] = None
                continue
            end = calendar[g0 + k]
            ev_b[k] = bhar_dates(seg.series, bench, start, end)
            vals = [v for _, c, _j in chosen if (v := bhar_dates(c.series, bench, start, end)) is not None]
            ct_b[k] = _mean(vals)
        i1 = min(i + 1, len(seg.series.dates) - 1)
        dd_c = [
            v for _, c, j in chosen
            if (v := max_drawdown_after(c.series, min(j + 1, len(c.series.dates) - 1), dd_horizon)) is not None
        ]
        sh_c = [v for _, c, j in chosen if (v := share_growth(c.series, c.caps, j, share_horizon)) is not None]
        out.append(
            MatchedEvent(
                symbol=seg.symbol,
                day0=d0,
                band=band,
                run_ratio=rr,
                rel_volume=seg.state.rel_volume[i] or 0.0,
                ret0=seg.series.stock_ret[i] or 0.0,
                controls=tuple(c.symbol for _, c, _j in chosen),
                event_bhar=ev_b,
                control_bhar=ct_b,
                drawdown_event=max_drawdown_after(seg.series, i1, dd_horizon),
                drawdown_controls=_mean(dd_c),
                shares_event=share_growth(seg.series, seg.caps, i, share_horizon),
                shares_controls=_mean(sh_c),
            )
        )
    out.sort(key=lambda e: (e.day0, e.symbol))
    return out


@dataclass(frozen=True)
class BootstrapSummary:
    n: int
    n_clusters: int
    mean: float | None
    median: float | None
    lo: float | None  # 5th percentile of the bootstrap mean
    hi: float | None  # 95th percentile
    share_negative: float | None
    p_two_sided: float | None = None  # 2 x the share of bootstrap means on the far side of 0
    trimmed_mean: float | None = None  # 10% trimmed each side


def block_bootstrap(
    values: Sequence[float], clusters: Sequence[str], n_boot: int = 2000, seed: int = 20261012
) -> BootstrapSummary:
    """Mean with a 90% interval from resampling whole clusters (calendar months) with replacement."""
    if not values:
        return BootstrapSummary(0, 0, None, None, None, None, None, None, None)
    groups: dict[str, list[float]] = {}
    for v, c in zip(values, clusters, strict=True):
        groups.setdefault(c, []).append(v)
    keys = sorted(groups)
    rng = random.Random(seed)
    means: list[float] = []
    for _ in range(n_boot):
        tot, cnt = 0.0, 0
        for _k in keys:
            g = groups[keys[rng.randrange(len(keys))]]
            tot += sum(g)
            cnt += len(g)
        means.append(tot / cnt)
    means.sort()
    srt = sorted(values)
    m = len(srt)
    median = srt[m // 2] if m % 2 else (srt[m // 2 - 1] + srt[m // 2]) / 2.0
    cut = m // 10
    trimmed = srt[cut : m - cut] if m - 2 * cut > 0 else srt
    p_two = min(1.0, 2.0 * min(sum(x >= 0 for x in means), sum(x <= 0 for x in means)) / n_boot)
    return BootstrapSummary(
        n=m,
        n_clusters=len(keys),
        mean=sum(values) / m,
        median=median,
        lo=means[int(0.05 * n_boot)],
        hi=means[int(0.95 * n_boot) - 1],
        share_negative=sum(v < 0 for v in values) / m,
        p_two_sided=p_two,
        trimmed_mean=sum(trimmed) / len(trimmed),
    )


def holm(pvalues: Sequence[float]) -> list[float]:
    """Holm step-down adjusted p-values, in the input order."""
    m = len(pvalues)
    order = sorted(range(m), key=lambda i: pvalues[i])
    adj = [0.0] * m
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (m - rank) * pvalues[i]))
        adj[i] = running
    return adj
