"""Cross-sectional features for a theme cohort on one trading day.

Built for the 2026-10-06 AI-bio reversal case study (docs/research/2026-10-06_ai_bio_theme_reversal.md)
and for hypothesis H13 (crowded-theme blow-off reversal). Input is one row per symbol from a
vendor company profile: close, day change, volume, average volume, 52-week range, beta, market cap.

Everything here is a one-day snapshot. It describes how a cohort traded; it cannot say what comes
next. Thresholds are initial values to be tested in H13, not tuned parameters.
"""

from __future__ import annotations

import csv
import random
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from statistics import median

# Day classification thresholds (initial; H13 pre-registration fixes the tested variants).
DISTRIBUTION_RET = -0.04
DISTRIBUTION_RVOL = 1.5
HEAVY_RET = -0.10
HEAVY_RVOL = 2.0


@dataclass(frozen=True)
class DaySnapshot:
    ticker: str
    name: str
    layer: str
    investor_named: bool
    close: float
    change: float
    volume: float
    avg_volume: float
    low_52w: float
    high_52w: float
    beta: float
    market_cap_usd: float

    @property
    def prev_close(self) -> float:
        return self.close - self.change

    @property
    def ret(self) -> float:
        """Day return as a decimal, from close and absolute change."""
        return self.change / self.prev_close

    @property
    def rvol(self) -> float:
        """Volume over the vendor's average volume (FMP profile; window not documented)."""
        return self.volume / self.avg_volume

    @property
    def off_low(self) -> float:
        """Close as a multiple of the 52-week low: how far the run went and still stands."""
        return self.close / self.low_52w

    @property
    def range_multiple(self) -> float:
        """52-week high over 52-week low: the size of the run at its peak."""
        return self.high_52w / self.low_52w

    @property
    def from_high(self) -> float:
        """Close relative to the 52-week high (negative = below the high)."""
        return self.close / self.high_52w - 1.0

    @property
    def range_position(self) -> float:
        """Close within the 52-week range, 0 at the low and 1 at the high (252-day RSV)."""
        span = self.high_52w - self.low_52w
        return 0.5 if span == 0 else (self.close - self.low_52w) / span

    @property
    def prev_range_position(self) -> float:
        """The same for the prior close: how stretched the name was going into the day.

        The 52-week high can include the day's own intraday high (TWST on 2026-10-06), so this value
        is a slight understatement of the true prior-day position, never an overstatement.
        """
        span = self.high_52w - self.low_52w
        return 0.5 if span == 0 else (self.prev_close - self.low_52w) / span

    @property
    def dollar_volume(self) -> float:
        return self.volume * self.close


def load_snapshot(path: Path | str) -> list[DaySnapshot]:
    with open(path, newline="") as fh:
        rows = list(csv.DictReader(fh))
    return [
        DaySnapshot(
            ticker=r["ticker"],
            name=r["name"],
            layer=r["layer"],
            investor_named=r["investor_named"].strip().lower() == "true",
            close=float(r["close"]),
            change=float(r["change"]),
            volume=float(r["volume"]),
            avg_volume=float(r["avg_volume"]),
            low_52w=float(r["range_low_52w"]),
            high_52w=float(r["range_high_52w"]),
            beta=float(r["beta"]),
            market_cap_usd=float(r["market_cap_usd"]),
        )
        for r in rows
    ]


def classify_day(s: DaySnapshot) -> str:
    """Label the day: heavy_distribution, distribution, quiet_decline or up."""
    if s.ret >= 0:
        return "up"
    if s.ret <= HEAVY_RET and s.rvol >= HEAVY_RVOL:
        return "heavy_distribution"
    if s.ret <= DISTRIBUTION_RET and s.rvol >= DISTRIBUTION_RVOL:
        return "distribution"
    return "quiet_decline"


def two_day_path(prior_close: float, s: DaySnapshot) -> tuple[float, float, float]:
    """Returns (spike day, reversal day, net) for prior_close -> prev_close -> close."""
    spike = s.prev_close / prior_close - 1.0
    return spike, s.ret, s.close / prior_close - 1.0


def _ranks(values: Sequence[float]) -> list[float]:
    """Average ranks (1-based), ties share the mean rank."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        for k in range(i, j + 1):
            ranks[order[k]] = (i + j) / 2.0 + 1.0
        i = j + 1
    return ranks


def spearman(x: Sequence[float], y: Sequence[float]) -> float:
    if len(x) != len(y) or len(x) < 3:
        raise ValueError("need two sequences of equal length >= 3")
    rx, ry = _ranks(x), _ranks(y)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    cov = sum((a - mx) * (b - my) for a, b in zip(rx, ry, strict=True))
    vx = sum((a - mx) ** 2 for a in rx)
    vy = sum((b - my) ** 2 for b in ry)
    return cov / (vx * vy) ** 0.5


def spearman_bootstrap_ci(
    x: Sequence[float], y: Sequence[float], n_boot: int = 4000, level: float = 0.90, seed: int = 7
) -> tuple[float, float]:
    """Percentile bootstrap interval for Spearman rho (pairs resampled with replacement).

    With n near 20 the interval is wide; that width is the point. Resamples with a constant column
    (possible with heavy ties) are skipped.
    """
    if len(set(x)) < 3 or len(set(y)) < 3:
        raise ValueError("need at least three distinct values in each sequence")
    rng = random.Random(seed)
    n = len(x)
    stats: list[float] = []
    attempts = 0
    while len(stats) < n_boot:
        attempts += 1
        if attempts > 50 * n_boot:
            raise ValueError("too many degenerate resamples; data are nearly constant")
        idx = [rng.randrange(n) for _ in range(n)]
        bx, by = [x[i] for i in idx], [y[i] for i in idx]
        if len(set(bx)) < 3 or len(set(by)) < 3:
            continue
        stats.append(spearman(bx, by))
    stats.sort()
    tail = (1.0 - level) / 2.0
    return stats[int(tail * n_boot)], stats[int((1.0 - tail) * n_boot) - 1]


def spearman_permutation_p(
    x: Sequence[float], y: Sequence[float], n_perm: int = 10000, seed: int = 11
) -> float:
    """Two-sided permutation p-value for Spearman rho (y shuffled against x)."""
    rng = random.Random(seed)
    observed = abs(spearman(x, y))
    ys = list(y)
    hits = 0
    for _ in range(n_perm):
        rng.shuffle(ys)
        if abs(spearman(x, ys)) >= observed - 1e-12:
            hits += 1
    return (hits + 1) / (n_perm + 1)


def crowding_score(snaps: Sequence[DaySnapshot]) -> dict[str, float]:
    """Mean percentile rank of run size (range multiple), beta and log market cap inverted.

    Uses only information available before the day's move (52-week range and beta are mostly
    set before the day; the range high can include the same day's intraday high, a known leak
    noted in the case study). Small size counts as more crowded because thin floats amplify flows.

    Pre-specified before the 2026-10-06 run. On that day it explained little (Spearman -0.10 vs the
    day return, n = 23) because the epicenter sat in 5-15B names; run size alone did better (-0.45).
    Kept unchanged so H13 tests it out of sample instead of a version fitted to one day.
    """
    n = len(snaps)
    run = _ranks([s.range_multiple for s in snaps])
    beta = _ranks([s.beta for s in snaps])
    small = _ranks([-s.market_cap_usd for s in snaps])
    return {s.ticker: (run[i] + beta[i] + small[i]) / (3.0 * n) for i, s in enumerate(snaps)}


@dataclass(frozen=True)
class GroupSummary:
    group: str
    n: int
    median_ret: float
    dollar_weighted_ret: float
    breadth_down: float
    median_rvol: float
    median_off_low: float
    median_from_high: float


def summarize(snaps: Iterable[DaySnapshot], key: Callable[[DaySnapshot], str]) -> list[GroupSummary]:
    groups: dict[str, list[DaySnapshot]] = {}
    for s in snaps:
        groups.setdefault(key(s), []).append(s)
    out = []
    for name, members in groups.items():
        dv = sum(m.dollar_volume for m in members)
        out.append(
            GroupSummary(
                group=name,
                n=len(members),
                median_ret=median(m.ret for m in members),
                dollar_weighted_ret=sum(m.ret * m.dollar_volume for m in members) / dv,
                breadth_down=sum(m.ret < 0 for m in members) / len(members),
                median_rvol=median(m.rvol for m in members),
                median_off_low=median(m.off_low for m in members),
                median_from_high=median(m.from_high for m in members),
            )
        )
    return sorted(out, key=lambda g: g.median_ret)
