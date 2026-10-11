"""US equity trading calendar, 2021 onwards (NYSE and Nasdaq share holidays).

Only what the event-study code needs: is a date a trading day, the previous and next trading day,
and the trading date a screener snapshot refers to. The holiday list is written out by hand from
the NYSE schedule, including the 2025-01-09 closure for the national day of mourning (President
Carter). Half days count as trading days. Extend the table before using dates past 2026.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

NEW_YORK = ZoneInfo("America/New_York")

NYSE_HOLIDAYS: frozenset[date] = frozenset(
    date.fromisoformat(d)
    for d in (
        # 2021
        "2021-01-01", "2021-01-18", "2021-02-15", "2021-04-02", "2021-05-31", "2021-07-05",
        "2021-09-06", "2021-11-25", "2021-12-24",
        # 2022 (New Year's Day fell on a Saturday; no observed closure)
        "2022-01-17", "2022-02-21", "2022-04-15", "2022-05-30", "2022-06-20", "2022-07-04",
        "2022-09-05", "2022-11-24", "2022-12-26",
        # 2023
        "2023-01-02", "2023-01-16", "2023-02-20", "2023-04-07", "2023-05-29", "2023-06-19",
        "2023-07-04", "2023-09-04", "2023-11-23", "2023-12-25",
        # 2024
        "2024-01-01", "2024-01-15", "2024-02-19", "2024-03-29", "2024-05-27", "2024-06-19",
        "2024-07-04", "2024-09-02", "2024-11-28", "2024-12-25",
        # 2025
        "2025-01-01", "2025-01-09", "2025-01-20", "2025-02-17", "2025-04-18", "2025-05-26",
        "2025-06-19", "2025-07-04", "2025-09-01", "2025-11-27", "2025-12-25",
        # 2026 (Independence Day on a Saturday; observed Friday 07-03)
        "2026-01-01", "2026-01-19", "2026-02-16", "2026-04-03", "2026-05-25", "2026-06-19",
        "2026-07-03", "2026-09-07", "2026-11-26", "2026-12-25",
    )
)
LAST_COVERED = date(2026, 12, 31)


def is_trading_day(d: date) -> bool:
    if d > LAST_COVERED:
        raise ValueError(f"holiday table ends {LAST_COVERED}; extend NYSE_HOLIDAYS before using {d}")
    return d.weekday() < 5 and d not in NYSE_HOLIDAYS


def previous_trading_day(d: date) -> date:
    """Last trading day strictly before `d`."""
    d -= timedelta(days=1)
    while not is_trading_day(d):
        d -= timedelta(days=1)
    return d


def next_trading_day(d: date) -> date:
    """First trading day strictly after `d`."""
    d += timedelta(days=1)
    while not is_trading_day(d):
        d += timedelta(days=1)
    return d


MIRROR_LAG_START = date(2026, 9, 24)


def snapshot_trade_date(committed_at: datetime) -> date:
    """Trading date whose close a screener-mirror snapshot holds.

    The mirror (`rreichel3/US-Stock-Symbols`) commits on weekday evenings New York time (about
    19:20 to 21:00, sometimes a little later). Two regimes, found from repeated snapshots and
    checked against dated price moves (`docs/research/mirror_price_reference_data.md`):

    - Before 2026-09-24: the snapshot holds the close of its own New York date; a weekend or
      holiday commit holds the previous trading day. Anchors: QSI +67% to 3.60 on 2024-12-27,
      NAUT -28% on 2026-07-28 (Q2 release that morning).
    - From 2026-09-24: the screener lags one trading day, so the snapshot holds the close of the
      trading day before its New York date. The 2026-09-24 snapshot repeats 2026-09-23 exactly.
      Anchors: QSI 0.795 on Monday 2026-09-28 then +20% on 09-29 (HUPO data); NAUT +12.7% to
      about 1.77 intraday on 2026-10-02 from a 1.57 close; TXG 93.50 on 2026-10-02 (D-022).

    Callers must still drop snapshots that repeat the previous one.
    """
    if committed_at.tzinfo is None:
        raise ValueError("committed_at must be timezone-aware")
    ny = committed_at.astimezone(NEW_YORK)
    ny_date = ny.date()
    if ny_date >= MIRROR_LAG_START:
        return previous_trading_day(ny_date)
    if is_trading_day(ny_date) and ny.hour >= 16:
        return ny_date
    return previous_trading_day(ny_date)


def event_day_zero(release: date, timing: str) -> date:
    """First trading session that can react to a release.

    `timing`: `bmo` (before the open) or `intraday` -> the release date if it is a trading day;
    `amc` (after the close) -> the next trading day; `unknown` -> treated like `bmo` and left for
    volume-based resolution (`signals.drift.resolve_event_index`).
    """
    if timing not in {"bmo", "amc", "intraday", "unknown"}:
        raise ValueError(f"unknown release timing: {timing}")
    if timing == "amc" or not is_trading_day(release):
        return next_trading_day(release)
    return release
