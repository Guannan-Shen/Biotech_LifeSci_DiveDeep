import importlib.util
import math
import sys
from pathlib import Path

import pytest

from biotech_divedeep.signals.technical import (
    acceleration,
    bollinger,
    equal_weight_index,
    kdj,
    momentum_12_1,
    pct_from_sma,
    pearson,
    range_position,
    return_similarity,
    rsi,
    sma,
)


def test_sma_and_distance():
    assert sma([1, 2, 3, 4], 2) == [None, 1.5, 2.5, 3.5]
    assert pct_from_sma([1, 2, 3, 4], 2)[-1] == pytest.approx(4 / 3.5 - 1)


def test_rsi_extremes_and_balance():
    up = [float(i) for i in range(1, 30)]
    assert rsi(up)[-1] == 100.0
    assert rsi(up)[13] is None and rsi(up)[14] is not None
    zigzag = [10.0 + (i % 2) for i in range(30)]  # equal gains and losses
    assert rsi(zigzag)[14] == pytest.approx(50.0, abs=4.0)


def test_rsi_wilder_reference():
    # 15 closes: 7 gains of 1 and 7 losses of 0.5 in the first 14 changes -> RS = 7 / 3.5 = 2 -> RSI 66.67
    closes = [10.0]
    for i in range(14):
        closes.append(closes[-1] + (1.0 if i % 2 == 0 else -0.5))
    assert rsi(closes)[14] == pytest.approx(100 - 100 / 3)


def test_kdj_tracks_position_in_range():
    highs = [float(i) + 1 for i in range(20)]
    lows = [float(i) for i in range(20)]
    closes = [float(i) + 1 for i in range(20)]  # always closes at the high
    last = kdj(highs, lows, closes)[-1]
    assert last is not None
    assert last.k > 90 and last.j > last.k  # J overshoots K in a persistent trend
    assert kdj(highs, lows, closes)[7] is None
    with pytest.raises(ValueError):
        kdj([1.0], [1.0, 2.0], [1.0])


def test_bollinger_pct_b():
    closes = [10.0] * 19 + [12.0]
    band = bollinger(closes)[-1]
    assert band is not None
    assert band.mid == pytest.approx(10.1)
    assert band.pct_b(12.0) > 1.0  # a jump this size closes outside the upper band
    flat = bollinger([5.0] * 20)[-1]
    assert flat.pct_b(5.0) == 0.5 and flat.bandwidth == 0.0


def test_range_position():
    assert range_position(30.0, 20.0, 40.0) == 0.5
    assert range_position(40.0, 20.0, 40.0) == 1.0
    assert range_position(5.0, 5.0, 5.0) == 0.5


def test_momentum_and_acceleration():
    assert momentum_12_1([1.0] * 100) is None
    flat_then_vertical = [1.0] * 190 + [math.exp(i / 63) for i in range(63)]
    assert acceleration(flat_then_vertical) == pytest.approx(1.0, abs=0.02)
    steady = [math.exp(i / 252) for i in range(253)]
    assert acceleration(steady) == pytest.approx(0.25, abs=0.01)
    assert momentum_12_1(steady) == pytest.approx(math.exp(231 / 252) - 1, rel=1e-6)


def test_similarity_and_index():
    a = [100.0 * (1.01**i) * (1.0 + 0.02 * ((-1) ** i)) for i in range(80)]
    b = [x * 2 for x in a]
    assert return_similarity(a, b) == pytest.approx(1.0)
    assert return_similarity(a, b[:-1]) is None
    assert pearson([1, 2, 3], [3, 2, 1]) == pytest.approx(-1.0)
    idx = equal_weight_index([[1.0, 1.1], [1.0, 0.9]])
    assert idx == [1.0, pytest.approx(1.0)]


def _load_panel_script():
    path = Path(__file__).resolve().parents[1] / "scripts" / "technical_panel.py"
    spec = importlib.util.spec_from_file_location("technical_panel", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_technical_panel_runs_offline_on_synthetic_bars(tmp_path, monkeypatch, capsys):
    panel = _load_panel_script()
    syms = ["AAA", "BBB", "CCC", "DDD", "EEE", "FFF", "GGG", "HHH", "ARKG"]
    dates = [f"2025-{m:02d}-{d:02d}" for m in range(1, 13) for d in range(1, 29)][:300]
    dates[-1] = "2026-10-06"
    for k, sym in enumerate(syms):
        closes = [10.0 * (1.0 + 0.002 * (k + 1)) ** i * (1.0 + 0.01 * ((-1) ** (i + k))) for i in range(len(dates))]
        closes[-1] = closes[-2] * (1.0 - 0.02 * k)  # event-day loss grows with k
        lines = ["Date,Open,High,Low,Close,Volume"]
        lines += [
            f"{d},{c},{c * 1.01},{c * 0.99},{c},{1000 + 10 * i}"
            for i, (d, c) in enumerate(zip(dates, closes, strict=True))
        ]
        (tmp_path / f"{sym}.csv").write_text("\n".join(lines))
    monkeypatch.setattr(panel, "BARS", tmp_path)
    monkeypatch.setattr(panel, "tickers", lambda: syms)
    monkeypatch.setattr(panel, "EXTRA", ["ARKG"])
    monkeypatch.setattr(sys, "argv", ["technical_panel.py", "--event", "2026-10-06"])
    assert panel.main() == 0
    out = capsys.readouterr().out
    assert "Features at the" in out and "| rsi14 |" in out and "| sim_arkg_63 |" in out
