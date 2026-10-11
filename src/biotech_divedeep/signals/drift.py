"""Post-announcement drift (PEAD and its cousins) for small-cap life-science stocks (H17).

Classic PEAD sorts on the standardized unexpected earnings (SUE) against analyst consensus
(Ball and Brown 1968; Bernard and Thomas 1989). For pre-revenue tools and clinical names the EPS
"surprise" is mostly a guess about opex and carries no information, so this module measures the
surprise with the market's own reaction instead:

- **EAR**: market-adjusted cumulative abnormal return over days [0, +1] around the announcement
  (Brandt, Kishore, Santa-Clara and Venkatachalam 2008 show EAR-sorted drift is at least as strong
  as SUE-sorted drift and survives in samples where consensus is thin);
- **SEAR**: EAR divided by the pre-event abnormal-return volatility times sqrt(2), so a 20% move
  in a stock that routinely moves 10% a day is not called a surprise;
- **abnormal volume** over [0, +1] relative to days [-60, -11] (volume confirmation; Garfinkel and
  Sokobin 2006 link volume to opinion divergence and drift).

Drift is the buy-and-hold abnormal return (BHAR) from the close of day +1 to the close of day +k,
i.e. what an investor who acts after the reaction would earn relative to the benchmark. The same
machinery measures large moves with no logged announcement ("no-news shocks"), which Chan (2003)
finds tend to reverse rather than drift.

Pure functions over aligned daily series, oldest first. Point-in-time: the surprise uses days up
to +1 only; drift windows start after it. Volume-based event-day resolution only chooses between
sessions at or after the release (or within two sessions of an approximately dated one), which an
investor would have seen in real time.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date

EST_RET = (-120, -11)  # abnormal-return volatility window
EST_VOL = (-60, -11)  # volume baseline window
MIN_EST_DAYS = 30


@dataclass(frozen=True)
class Series:
    """A stock aligned with its benchmark on the stock's trading dates."""

    dates: list[date]
    close: list[float]
    volume: list[float]
    stock_ret: list[float | None]  # close-to-close; None on the first day
    bench_ret: list[float | None]

    @property
    def abnormal(self) -> list[float | None]:
        return [
            None if s is None or b is None else s - b for s, b in zip(self.stock_ret, self.bench_ret, strict=True)
        ]

    def index_on_or_after(self, d: date) -> int | None:
        for i, x in enumerate(self.dates):
            if x >= d:
                return i
        return None


def align(
    stock: Sequence[tuple[date, float, float]], bench: Mapping[date, float]
) -> Series:
    """Build a `Series` from (date, close, volume) rows and a benchmark daily-return map.

    Stock returns are close-to-close, so a missing snapshot folds two days into one return. The
    benchmark return on such a day is compounded over the skipped dates it has.
    """
    rows = sorted(stock)
    dates = [r[0] for r in rows]
    close = [r[1] for r in rows]
    volume = [r[2] for r in rows]
    bench_dates = sorted(bench)
    s_ret: list[float | None] = [None]
    b_ret: list[float | None] = [None]
    j = 0
    for i in range(1, len(rows)):
        s_ret.append(close[i] / close[i - 1] - 1.0 if close[i - 1] > 0 else None)
        prod, seen = 1.0, False
        while j < len(bench_dates) and bench_dates[j] <= dates[i]:
            if bench_dates[j] > dates[i - 1]:
                prod *= 1.0 + bench[bench_dates[j]]
                seen = True
            j += 1
        b_ret.append(prod - 1.0 if seen else None)
    return Series(dates, close, volume, s_ret, b_ret)


def _window(values: Sequence[float | None], i0: int, lo: int, hi: int) -> list[float]:
    a, b = max(0, i0 + lo), min(len(values) - 1, i0 + hi)
    return [v for v in values[a : b + 1] if v is not None]


def _sd(xs: Sequence[float]) -> float | None:
    if len(xs) < 2:
        return None
    m = sum(xs) / len(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def abnormal_volume(s: Series, i: int, est: tuple[int, int] = EST_VOL) -> float | None:
    """Volume on day i over the mean of the baseline window (1.0 = normal)."""
    base = _window(s.volume, i, *est)
    if len(base) < MIN_EST_DAYS // 2 or not sum(base):
        return None
    return s.volume[i] / (sum(base) / len(base))


def resolve_event_index(
    s: Series, release: date, timing: str = "unknown", precision: str = "day"
) -> tuple[int | None, bool]:
    """Index of the reaction day for an announcement released on `release`.

    - `bmo` or `intraday`: the release session; `amc`: the next session (timing taken as given).
    - `unknown`: the release session or the next one, whichever has clearly higher abnormal
      volume (1.25x). Aggregators often misreport before-open vs after-close; the volume spike is
      the market's own timestamp, the approach DellaVigna and Pollet (2009) use for uncertain
      announcement dates. Both candidates are at or after the release, so no look-ahead.
    - `precision == "approx"`: search two sessions either side of the dated release.

    Returns (index, moved), where `moved` is true when volume picked a day other than the
    default (the release session for `unknown`, the dated session for `approx`).
    """
    i_rel = s.index_on_or_after(release)
    if i_rel is None:
        return None, False
    if precision == "approx":
        candidates = [i_rel + k for k in (-2, -1, 0, 1, 2)]
        default = i_rel
    elif timing in {"bmo", "intraday"}:
        return i_rel, False
    elif timing == "amc":
        i = i_rel + 1 if s.dates[i_rel] == release else i_rel
        return (i, False) if i < len(s.dates) else (None, False)
    elif timing == "unknown":
        candidates = [i_rel, i_rel + 1]
        default = i_rel
    else:
        raise ValueError(f"unknown release timing: {timing}")
    best, best_av = default, abnormal_volume(s, default) or 0.0
    for i in candidates:
        if i == default or not 0 <= i < len(s.dates):
            continue
        av = abnormal_volume(s, i) or 0.0
        if av > best_av * 1.25:
            best, best_av = i, av
    return best, best != default


def bhar(s: Series, start: int, end: int) -> float | None:
    """Buy-and-hold abnormal return over return days start..end (indexes into the series)."""
    if start < 1 or end >= len(s.dates) or end < start:
        return None
    ps, pb = 1.0, 1.0
    for i in range(start, end + 1):
        if s.stock_ret[i] is None or s.bench_ret[i] is None:
            return None
        ps *= 1.0 + s.stock_ret[i]  # type: ignore[operator]
        pb *= 1.0 + s.bench_ret[i]  # type: ignore[operator]
    return ps - pb


@dataclass(frozen=True)
class EventStats:
    index: int
    day0: date
    moved: bool
    ear: float | None  # CAR over [0, +1]
    sear: float | None
    av01: float | None  # mean abnormal volume over [0, +1]
    pre_run: float | None  # BHAR over [-20, -2]
    drift: dict[int, float | None] = field(default_factory=dict)  # k -> BHAR over [+2, +k]

    def surprise(self, z: float = 2.0, av_min: float = 2.0) -> str:
        """`positive` / `negative` when |SEAR| >= z with volume confirmation, else `neutral`."""
        if self.sear is None or self.av01 is None:
            return "unknown"
        if abs(self.sear) >= z and self.av01 >= av_min:
            return "positive" if self.sear > 0 else "negative"
        return "neutral"


def event_stats(s: Series, i0: int, horizons: Sequence[int] = (5, 20, 60), moved: bool = False) -> EventStats:
    ar = s.abnormal
    r0 = [ar[i] for i in (i0, i0 + 1) if 0 <= i < len(ar)]
    ear = sum(r0) if len(r0) == 2 and all(v is not None for v in r0) else None  # type: ignore[misc]
    est = _window(ar, i0, *EST_RET)
    sd = _sd(est) if len(est) >= MIN_EST_DAYS else None
    sear = ear / (sd * math.sqrt(2.0)) if ear is not None and sd else None
    avs = [abnormal_volume(s, i) for i in (i0, i0 + 1) if 0 <= i < len(s.dates)]
    av01 = sum(avs) / len(avs) if avs and all(a is not None for a in avs) else None  # type: ignore[arg-type]
    drift = {k: bhar(s, i0 + 2, i0 + k) for k in horizons}
    return EventStats(i0, s.dates[i0], moved, ear, sear, av01, bhar(s, i0 - 20, i0 - 2), drift)


def no_news_shocks(
    s: Series, known: Sequence[int], z: float = 3.0, av_min: float = 3.0, exclusion: int = 2, gap: int = 5
) -> list[int]:
    """Days with |abnormal return| >= z pre-event sigmas on abnormal volume >= av_min, at least
    `exclusion` days from any logged event and `gap` days from the previous shock picked."""
    ar = s.abnormal
    out: list[int] = []
    for i in range(abs(EST_RET[0]), len(ar)):
        if ar[i] is None:
            continue
        if any(abs(i - k) <= exclusion for k in known):
            continue
        if out and i - out[-1] < gap:
            continue
        sd = _sd(_window(ar, i, *EST_RET))
        av = abnormal_volume(s, i)
        if sd and av and abs(ar[i]) >= z * sd and av >= av_min:  # type: ignore[arg-type]
            out.append(i)
    return out


@dataclass(frozen=True)
class DriftSummary:
    label: str
    n: int
    mean_ear: float | None
    mean_drift: float | None
    t_stat: float | None
    continuation: float | None  # share of events whose drift has the sign of the EAR
    median_drift: float | None = None


def summarize(label: str, events: Sequence[EventStats], horizon: int) -> DriftSummary:
    pairs = [(e.ear, e.drift.get(horizon)) for e in events if e.ear is not None and e.drift.get(horizon) is not None]
    if not pairs:
        return DriftSummary(label, 0, None, None, None, None, None)
    ears = [p[0] for p in pairs]
    drifts = [p[1] for p in pairs]
    m = sum(drifts) / len(drifts)  # type: ignore[arg-type]
    sd = _sd(drifts)  # type: ignore[arg-type]
    t = m / (sd / math.sqrt(len(drifts))) if sd else None
    same = [((a > 0) == (d > 0)) for a, d in pairs if a != 0 and d != 0]  # type: ignore[operator]
    return DriftSummary(
        label,
        len(pairs),
        sum(ears) / len(ears),  # type: ignore[arg-type]
        m,
        t,
        sum(same) / len(same) if same else None,
        _median(drifts),  # type: ignore[arg-type]
    )


def _median(xs: Sequence[float]) -> float | None:
    if not xs:
        return None
    v = sorted(xs)
    n = len(v)
    return v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2.0
