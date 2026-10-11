import csv
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pytest

from biotech_divedeep.core.calendar import (
    event_day_zero,
    is_trading_day,
    next_trading_day,
    previous_trading_day,
    snapshot_trade_date,
)
from biotech_divedeep.signals.drift import (
    align,
    bhar,
    event_stats,
    no_news_shocks,
    resolve_event_index,
    summarize,
)

REF = Path(__file__).resolve().parents[1] / "data" / "reference"


def test_trading_calendar_holidays_and_weekends():
    assert not is_trading_day(date(2026, 7, 3))  # Independence Day observed
    assert not is_trading_day(date(2025, 1, 9))  # national day of mourning
    assert not is_trading_day(date(2026, 10, 10))  # Saturday
    assert previous_trading_day(date(2026, 9, 8)) == date(2026, 9, 4)  # across Labor Day
    assert next_trading_day(date(2026, 11, 25)) == date(2026, 11, 27)
    with pytest.raises(ValueError):
        is_trading_day(date(2027, 1, 4))


def test_snapshot_trade_date_regimes():
    # Before 2026-09-24 the evening snapshot holds its own day's close (NAUT -28% on 2026-07-28).
    assert snapshot_trade_date(datetime(2026, 7, 29, 0, 38, tzinfo=UTC)) == date(2026, 7, 28)
    # A Saturday-evening commit holds Friday.
    assert snapshot_trade_date(datetime(2025, 7, 13, 0, 30, tzinfo=UTC)) == date(2025, 7, 11)
    # From 2026-09-24 the screener lags a day: Monday evening holds Friday (TXG 93.50 on 10-02).
    assert snapshot_trade_date(datetime(2026, 10, 6, 0, 41, tzinfo=UTC)) == date(2026, 10, 2)
    with pytest.raises(ValueError):
        snapshot_trade_date(datetime(2026, 10, 6, 0, 41))


def test_event_day_zero():
    assert event_day_zero(date(2026, 8, 13), "amc") == date(2026, 8, 14)
    assert event_day_zero(date(2026, 7, 28), "bmo") == date(2026, 7, 28)
    assert event_day_zero(date(2026, 7, 3), "bmo") == date(2026, 7, 6)  # holiday release


def _synthetic(n=200, shock_at=150, shock=0.30, drift=0.002, spike_at=None):
    """Flat benchmark; stock flat with small alternating noise, a shock day and an optional drift."""
    d0 = date(2025, 1, 2)
    days, closes, vols, bench = [], [], [], {}
    px, d = 10.0, d0
    for i in range(n):
        while not is_trading_day(d):
            d += timedelta(days=1)
        if i > 0:
            r = 0.01 if i % 2 else -0.0099
            if i == shock_at:
                r = shock
            elif i > shock_at + 1:
                r += drift
            px *= 1 + r
        days.append(d)
        closes.append(px)
        vols.append(5e6 if i in (shock_at, shock_at + 1) else 2e6 if i == spike_at else 1e6)
        bench[d] = 0.0
        d += timedelta(days=1)
    return align(list(zip(days, closes, vols, strict=True)), bench), days


def test_event_stats_measure_reaction_and_drift():
    s, days = _synthetic()
    i0, moved = resolve_event_index(s, days[150], "bmo")
    assert i0 == 150 and not moved
    st = event_stats(s, i0, horizons=(5, 20))
    assert st.ear == pytest.approx(0.30 - 0.0099, abs=0.02)
    assert st.sear > 10 and st.av01 == pytest.approx(5.0)
    assert st.surprise() == "positive"
    assert st.drift[20] > 0.02  # about 0.2% a day built into the series
    assert bhar(s, 0, 5) is None  # day 0 has no return


def test_resolution_uses_volume_only_at_or_after_release():
    s, days = _synthetic(spike_at=149)
    i, moved = resolve_event_index(s, days[149], "unknown")
    assert (i, moved) == (150, True)  # day-after spike is larger than the release-day spike
    i, moved = resolve_event_index(s, days[150], "unknown")
    assert i == 150  # never moves before the release
    i, _ = resolve_event_index(s, days[149], "amc")
    assert i == 150


def test_no_news_shock_detection_skips_logged_events():
    s, _ = _synthetic()
    assert 150 in no_news_shocks(s, known=[])
    assert 150 not in no_news_shocks(s, known=[150])


def test_summary_continuation():
    s, days = _synthetic()
    st = event_stats(s, 150, horizons=(20,))
    sm = summarize("x", [st, st], 20)
    assert sm.n == 2 and sm.continuation == 1.0 and sm.median_drift == pytest.approx(sm.mean_drift)


def test_event_log_and_price_reference_are_well_formed():
    with open(REF / "announcement_events.csv", newline="") as fh:
        events = list(csv.DictReader(fh))
    ids = [e["event_id"] for e in events]
    assert len(ids) == len(set(ids))
    for e in events:
        date.fromisoformat(e["available_at"])
        assert e["timing"] in {"bmo", "amc", "intraday", "unknown"}, e["event_id"]
        assert e["date_precision"] in {"day", "approx"}, e["event_id"]
        assert e["guidance_effect"] in {"none", "slip", "extend", "reaffirm", "cut"}, e["event_id"]
        assert e["evidence_class"] in {"fact", "management_guidance", "own_assumption", "unverified"}
        assert e["source_url"].startswith("https://"), e["event_id"]
    with open(REF / "qsi_naut_daily_2021_2026.csv", newline="") as fh:
        prices = list(csv.DictReader(fh))
    by = {(r["symbol"], r["date"]): r for r in prices}
    assert float(by[("NAUT", "2026-07-28")]["ret_1d"]) < -0.25  # Q2 2026 broadscale miss
    assert float(by[("QSI", "2026-09-28")]["close"]) == pytest.approx(0.795)  # Benzinga anchor
    assert {"QSI", "NAUT", "EW_LIFESCI_200M", "EW_TOOLS"} <= {r["symbol"] for r in prices}
