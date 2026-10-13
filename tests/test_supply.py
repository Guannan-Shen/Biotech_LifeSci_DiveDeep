from datetime import date, timedelta

from biotech_divedeep.signals.drift import align
from biotech_divedeep.signals.supply import (
    Segment,
    SupplyParams,
    _rolling_max,
    bhar_dates,
    block_bootstrap,
    cap_band,
    day_states,
    holm,
    match_events,
    pick_events,
    share_growth,
    split_adjust,
)

P = SupplyParams(lookback=20, vol_base=(-15, -3), dedupe=10)


def _calendar(n: int) -> list[date]:
    d, out = date(2022, 1, 3), []
    while len(out) < n:
        if d.weekday() < 5:
            out.append(d)
        d += timedelta(days=1)
    return out


def _segment(sym: str, closes: list[float], vols: list[float], cal: list[date], bench: dict, cap_shares: float = 3e7):
    s = align(list(zip(cal[: len(closes)], closes, vols, strict=True)), bench)
    caps = [c * cap_shares for c in closes]
    return Segment(sym, "therapeutics", s, caps, day_states(s, caps, P))


def test_rolling_max_and_cap_band():
    assert _rolling_max([1, 3, 2, 5, 4, 1], 3) == [None, None, 3, 5, 5, 5]
    assert cap_band(100e6) == "micro" and cap_band(5e8) == "small" and cap_band(3e9) == "mid"
    assert cap_band(30e6) is None and cap_band(None) is None


def test_supply_needs_run_down_close_and_volume():
    cal = _calendar(60)
    bench = {d: 0.0 for d in cal}
    closes = [2.0] * 5 + [2.0 + 0.15 * i for i in range(1, 26)]  # 2.0 -> 5.75 over 25 sessions
    closes += [5.0] * 30  # day 30: -13% on heavy volume
    vols = [1e6] * 30 + [5e6] + [1e6] * 29
    seg = _segment("RUN", closes, vols, cal, bench)
    st = seg.state
    assert st.in_run[30] and st.run_ratio[30] >= 2.0
    assert st.supply[30] and st.rel_volume[30] == 5.0
    assert pick_events(st, 10) == [30]
    # Same day without the volume spike is not supply.
    seg2 = _segment("QUIET", closes, [1e6] * 60, cal, bench)
    assert not any(seg2.state.supply)
    # Same volume spike on an up day is not supply.
    up = closes[:30] + [6.2] * 30
    assert not any(_segment("UP", up, vols, cal, bench).state.supply)


def test_bhar_dates_freezes_after_delisting():
    cal = _calendar(10)
    bench = {d: 0.01 for d in cal}
    s = align([(cal[i], 10.0 * 1.02**i, 1.0) for i in range(6)], bench)  # stops at day 5
    full = bhar_dates(s, bench, cal[2], cal[5])
    assert abs(full - (1.02**4 - 1.01**4)) < 1e-12
    after = bhar_dates(s, bench, cal[2], cal[9])
    assert abs(after - full * 1.01**4) < 1e-12
    assert bhar_dates(s, bench, cal[0] - timedelta(days=3), cal[5]) is None


def test_share_growth_from_caps():
    cal = _calendar(5)
    s = align([(d, 2.0, 1.0) for d in cal], {d: 0.0 for d in cal})
    caps = [200.0, 200.0, 200.0, 240.0, 240.0]
    assert abs(share_growth(s, caps, 1, 2) - 0.2) < 1e-12


def test_match_events_uses_same_date_run_controls():
    cal = _calendar(80)
    bench = {d: 0.0 for d in cal}
    run = [2.0] * 5 + [2.0 + 0.15 * i for i in range(1, 26)]
    ev = _segment("EVT", run + [5.0] * 50, [1e6] * 30 + [5e6] + [1e6] * 49, cal, bench)
    ctl_a = _segment("CTLA", run + [5.8] * 50, [1e6] * 80, cal, bench)  # same run, no supply
    ctl_b = _segment("CTLB", [2.0] * 80, [1e6] * 80, cal, bench)  # no run: never a control
    out = match_events([ev, ctl_a, ctl_b], cal, bench, P, horizons=(20,), n_controls=3)
    assert len(out) == 1
    m = out[0]
    assert m.symbol == "EVT" and m.controls == ("CTLA",) and m.band == "micro"
    assert m.event_bhar[20] == 0.0 and m.control_bhar[20] == 0.0 and m.diff(20) == 0.0


def test_block_bootstrap_interval_brackets_mean():
    vals = [-0.2, -0.1, 0.0, -0.3, 0.1, -0.15]
    months = ["2022-01", "2022-01", "2022-02", "2022-03", "2022-03", "2022-04"]
    s = block_bootstrap(vals, months, n_boot=500)
    assert s.n == 6 and s.n_clusters == 4
    assert s.lo <= s.mean <= s.hi
    assert abs(s.share_negative - 4 / 6) < 1e-12


def test_split_adjust_reverse_split_and_stale_close():
    # 1-for-10 reverse split on day 2: raw close jumps 10x while the screener's return says -5%.
    close = [1.0, 1.0, 9.5, 9.5]
    ret = [None, 0.0, -0.05, 0.0]
    adj_c, adj_v, splits = split_adjust(close, ret, [100.0, 100.0, 10.0, 10.0])
    assert splits == [2]
    assert [round(c, 6) for c in adj_c] == [10.0, 10.0, 9.5, 9.5]
    assert [round(v, 6) for v in adj_v] == [10.0, 10.0, 10.0, 10.0]
    # A stale lastsale on day 2 (price not updated, +100% reported) is caught up on day 3: no split.
    close2 = [1.0, 1.0, 1.0, 2.0]
    ret2 = [None, 0.0, 1.0, 0.0]
    assert split_adjust(close2, ret2, [1.0] * 4)[2] == []


def test_holm_adjustment():
    assert holm([0.01, 0.04, 0.03]) == [0.03, 0.06, 0.06]
