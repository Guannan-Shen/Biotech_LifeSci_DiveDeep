"""Attention proxies that need no X API budget (M13 fallback, H10).

The X API is the target source for cashtag attention (docs/modules/social_x.md), but it is paid and
undecided (Q-012). Two free, documented public APIs give a daily attention series in the meantime:

- Wikimedia pageviews (REST API, per-article daily views): retail and press curiosity about a
  company or a concept page ("Twist Bioscience", "Drug discovery").
- GDELT DOC 2.0 `timelinevol`: share of worldwide online news coverage matching a query.

Neither measures X directly. Both are timestamped, reproducible and cheap, which is enough to test
whether abnormal attention peaks coincide with theme tops (Da, Engelberg and Gao 2011 found that
search-volume spikes predict higher prices over about two weeks and a reversal within the year).
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from datetime import date, datetime
from statistics import mean, pstdev
from typing import Any


def parse_wikimedia_pageviews(payload: dict[str, Any]) -> list[tuple[date, int]]:
    """Daily views from a Wikimedia per-article pageviews response, oldest first."""
    rows = []
    for item in payload.get("items", []):
        ts = str(item["timestamp"])  # YYYYMMDDHH
        rows.append((date(int(ts[:4]), int(ts[4:6]), int(ts[6:8])), int(item["views"])))
    return sorted(rows)


def parse_gdelt_timeline(payload: dict[str, Any]) -> list[tuple[date, float]]:
    """Daily values from a GDELT DOC 2.0 timeline response (first series), oldest first."""
    timeline = payload.get("timeline") or []
    if not timeline:
        return []
    rows = []
    for point in timeline[0].get("data", []):
        stamp = datetime.strptime(point["date"][:8], "%Y%m%d").date()
        rows.append((stamp, float(point["value"])))
    return sorted(rows)


def abnormal_attention(values: Sequence[float], baseline: int = 60, min_periods: int = 20) -> list[float | None]:
    """z-score of log(1 + value) against the trailing `baseline` days, excluding the current day.

    The log tames the heavy right tail of attention data; excluding the current day keeps a spike
    from diluting its own baseline. None until `min_periods` prior days exist or when the baseline is
    flat.
    """
    logs = [math.log1p(max(v, 0.0)) for v in values]
    out: list[float | None] = [None] * len(values)
    for i in range(len(values)):
        window = logs[max(0, i - baseline) : i]
        if len(window) < min_periods:
            continue
        sd = pstdev(window)
        if sd == 0:
            continue
        out[i] = (logs[i] - mean(window)) / sd
    return out


def peak_lead_days(attention_dates: Sequence[date], z: Sequence[float | None], price_peak: date) -> int | None:
    """Days from the attention peak (max z) to a price peak; positive = attention peaked first."""
    scored = [(v, d) for d, v in zip(attention_dates, z, strict=True) if v is not None]
    if not scored:
        return None
    _, peak_day = max(scored)
    return (price_peak - peak_day).days
