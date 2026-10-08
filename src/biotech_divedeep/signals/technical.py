"""Price-path features for the trend overlay (H5) and the H13 blow-off test.

Pure functions over daily series (oldest first). Each returns a list aligned with the input, with
None where the window is not yet full, so callers never mix warm-up values into a cross-section.
Point-in-time: a value at index t uses data up to and including t only.

Conventions:
- RSI: Wilder smoothing (alpha = 1/n), the textbook 14-day version.
- KDJ: the stochastic variant common in Asian charting. RSV_t = 100 * (C_t - L_n) / (H_n - L_n),
  K_t = (2/3) K_{t-1} + (1/3) RSV_t, D_t = (2/3) D_{t-1} + (1/3) K_t, J = 3K - 2D, seeded at 50.
- Bollinger: 20-day mean +/- 2 population standard deviations; %b = (C - lower) / (upper - lower).
- Acceleration: share of the trailing 252-day log return earned in the last 63 days, an own
  definition inspired by the "price path" attribute in Greenwood, Shleifer and You (2019).

Thresholds such as RSI 70 or %b 1.0 are conventions, not tested edges; H13 treats every feature
here as a candidate predictor to be measured, never as a rule.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

Series = Sequence[float]


def sma(values: Series, n: int) -> list[float | None]:
    out: list[float | None] = [None] * len(values)
    run = 0.0
    for i, v in enumerate(values):
        run += v
        if i >= n:
            run -= values[i - n]
        if i >= n - 1:
            out[i] = run / n
    return out


def pct_from_sma(closes: Series, n: int) -> list[float | None]:
    """Close relative to its n-day simple moving average (0.45 = 45% above)."""
    return [None if m is None else c / m - 1.0 for c, m in zip(closes, sma(closes, n), strict=True)]


def rsi(closes: Series, n: int = 14) -> list[float | None]:
    """Wilder RSI. First value at index n (needs n price changes)."""
    out: list[float | None] = [None] * len(closes)
    if len(closes) <= n:
        return out
    gains = [max(closes[i] - closes[i - 1], 0.0) for i in range(1, len(closes))]
    losses = [max(closes[i - 1] - closes[i], 0.0) for i in range(1, len(closes))]
    avg_g = sum(gains[:n]) / n
    avg_l = sum(losses[:n]) / n
    for i in range(n, len(closes)):
        if i > n:
            avg_g = (avg_g * (n - 1) + gains[i - 1]) / n
            avg_l = (avg_l * (n - 1) + losses[i - 1]) / n
        if avg_l == 0.0:
            out[i] = 100.0 if avg_g > 0 else 50.0
        else:
            out[i] = 100.0 - 100.0 / (1.0 + avg_g / avg_l)
    return out


@dataclass(frozen=True)
class KDJ:
    k: float
    d: float
    j: float


def kdj(highs: Series, lows: Series, closes: Series, n: int = 9) -> list[KDJ | None]:
    if not len(highs) == len(lows) == len(closes):
        raise ValueError("highs, lows and closes must have equal length")
    out: list[KDJ | None] = [None] * len(closes)
    k = d = 50.0
    for i in range(len(closes)):
        if i < n - 1:
            continue
        hi = max(highs[i - n + 1 : i + 1])
        lo = min(lows[i - n + 1 : i + 1])
        rsv = 50.0 if hi == lo else 100.0 * (closes[i] - lo) / (hi - lo)
        k = (2.0 * k + rsv) / 3.0
        d = (2.0 * d + k) / 3.0
        out[i] = KDJ(k, d, 3.0 * k - 2.0 * d)
    return out


@dataclass(frozen=True)
class Band:
    mid: float
    upper: float
    lower: float

    def pct_b(self, close: float) -> float:
        width = self.upper - self.lower
        return 0.5 if width == 0 else (close - self.lower) / width

    @property
    def bandwidth(self) -> float:
        return 0.0 if self.mid == 0 else (self.upper - self.lower) / self.mid


def bollinger(closes: Series, n: int = 20, k: float = 2.0) -> list[Band | None]:
    out: list[Band | None] = [None] * len(closes)
    for i in range(n - 1, len(closes)):
        window = closes[i - n + 1 : i + 1]
        mean = sum(window) / n
        sd = math.sqrt(sum((x - mean) ** 2 for x in window) / n)
        out[i] = Band(mean, mean + k * sd, mean - k * sd)
    return out


def range_position(close: float, low: float, high: float) -> float:
    """Where the close sits in a trailing range, 0 at the low and 1 at the high.

    With a 52-week range this is the 252-day RSV of the KDJ family, computable from a vendor
    profile with no price history.
    """
    return 0.5 if high == low else (close - low) / (high - low)


def log_returns(closes: Series) -> list[float]:
    return [math.log(closes[i] / closes[i - 1]) for i in range(1, len(closes))]


def momentum_12_1(closes: Series) -> float | None:
    """Return from t-252 to t-21: the standard momentum factor that skips the last month."""
    if len(closes) < 253:
        return None
    return closes[-22] / closes[-253] - 1.0


def acceleration(closes: Series, window: int = 252, recent: int = 63) -> float | None:
    """Share of the trailing window's log return earned in the last `recent` days.

    1.0 means the whole year's gain came in the last quarter (a vertical path); values above 1
    mean the stock was down over the earlier part. Undefined when the window return is near zero.
    """
    if len(closes) < window + 1:
        return None
    total = math.log(closes[-1] / closes[-1 - window])
    if abs(total) < 1e-9:
        return None
    return math.log(closes[-1] / closes[-1 - recent]) / total


def pearson(x: Series, y: Series) -> float:
    if len(x) != len(y) or len(x) < 3:
        raise ValueError("need two sequences of equal length >= 3")
    mx, my = sum(x) / len(x), sum(y) / len(y)
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y, strict=True))
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    return sxy / math.sqrt(sxx * syy)


def return_similarity(closes_a: Series, closes_b: Series, window: int = 63) -> float | None:
    """Correlation of daily log returns over the last `window` days: how much A trades like B.

    Used two ways: a name vs the theme ETF (ARKG) measures how much of its price is theme flow;
    a name vs the equal-weight cohort basket feeds the correlation-cluster cohort in H13.
    """
    if len(closes_a) != len(closes_b) or len(closes_a) < window + 1:
        return None
    ra = log_returns(closes_a[-window - 1 :])
    rb = log_returns(closes_b[-window - 1 :])
    return pearson(ra, rb)


def equal_weight_index(series: Sequence[Series]) -> list[float]:
    """Equal-weight, daily-rebalanced index (base 1.0) from aligned close series."""
    if not series:
        raise ValueError("need at least one series")
    length = len(series[0])
    if any(len(s) != length for s in series):
        raise ValueError("series must be aligned to the same dates")
    level = [1.0]
    for t in range(1, length):
        level.append(level[-1] * (1.0 + sum(s[t] / s[t - 1] - 1.0 for s in series) / len(series)))
    return level
