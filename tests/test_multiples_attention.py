import json
from datetime import date
from pathlib import Path

import pytest

from biotech_divedeep.models.multiples import (
    growth_adjusted_ps,
    price_to_sales,
    required_cagr,
    required_revenue,
    years_to_multiple,
)
from biotech_divedeep.signals.attention import (
    abnormal_attention,
    parse_gdelt_timeline,
    parse_wikimedia_pageviews,
    peak_lead_days,
)
from biotech_divedeep.signals.cohort import (
    DaySnapshot,
    spearman,
    spearman_bootstrap_ci,
    spearman_permutation_p,
)

FIX = Path(__file__).resolve().parent / "fixtures" / "attention"


def test_twenty_times_sales_needs_about_32_percent_growth():
    # 20x sales, 5x exit, 5 years: revenue must quadruple for a 0% return.
    assert required_cagr(20.0, 1.0, terminal_ps=5.0, years=5.0) == pytest.approx(4**0.2 - 1)
    assert required_cagr(20.0, 1.0, 5.0, 5.0, annual_return=0.10) == pytest.approx((4 * 1.1**5) ** 0.2 - 1)
    # Dilution raises the hurdle like a higher required return.
    assert required_cagr(20.0, 1.0, 5.0, 5.0, annual_dilution=0.05) > required_cagr(20.0, 1.0, 5.0, 5.0)
    assert required_revenue(10.0, 5.0, 1.0) == pytest.approx(2.0)
    with pytest.raises(ValueError):
        price_to_sales(1.0, 0.0)


def test_growth_adjusted_ps_and_years_to_multiple():
    assert growth_adjusted_ps(20.0, 0.40) == pytest.approx(0.5)
    assert growth_adjusted_ps(10.0, -0.1) is None
    assert years_to_multiple(20.0, 5.0, 0.0) is None
    assert years_to_multiple(4.0, 5.0, 0.2) == 0.0
    assert years_to_multiple(20.0, 5.0, 0.3195) == pytest.approx(5.0, abs=0.01)


def test_attention_parsers_sort_and_convert():
    wiki = parse_wikimedia_pageviews(json.loads((FIX / "wikimedia_pageviews_sample.json").read_text()))
    assert wiki == [(date(2026, 10, 1), 120), (date(2026, 10, 2), 150), (date(2026, 10, 3), 410)]
    gdelt = parse_gdelt_timeline(json.loads((FIX / "gdelt_timelinevol_sample.json").read_text()))
    assert [d for d, _ in gdelt] == [date(2026, 10, 1), date(2026, 10, 2), date(2026, 10, 3)]
    assert parse_gdelt_timeline({"timeline": []}) == []


def test_abnormal_attention_flags_a_spike_and_its_lead():
    base = [100.0 + (i % 5) for i in range(40)]
    series = base + [1000.0]
    z = abnormal_attention(series)
    assert z[10] is None  # fewer than 20 prior days
    assert z[-1] is not None and z[-1] > 10
    days = [date(2026, 8, 1).fromordinal(date(2026, 8, 1).toordinal() + i) for i in range(len(series))]
    assert peak_lead_days(days, z, price_peak=date(2026, 9, 12)) == (date(2026, 9, 12) - days[-1]).days


def test_range_position_before_the_day():
    s = DaySnapshot(
        "X",
        "X",
        "l",
        False,
        close=90.0,
        change=-10.0,
        volume=1,
        avg_volume=1,
        low_52w=20.0,
        high_52w=120.0,
        beta=1.0,
        market_cap_usd=1e9,
    )
    assert s.range_position == pytest.approx(0.7)
    assert s.prev_range_position == pytest.approx(0.8)


def test_spearman_inference_helpers():
    x = list(range(20))
    y = [v + (3 if v % 4 == 0 else 0) for v in x]
    lo, hi = spearman_bootstrap_ci(x, y, n_boot=500)
    assert lo <= spearman(x, y) <= hi
    assert spearman_permutation_p(x, y, n_perm=500) < 0.01
    noise = [5, 1, 4, 2, 3, 0, 6, 9, 7, 8]
    assert spearman_permutation_p(list(range(10)), noise, n_perm=500) > 0.001
