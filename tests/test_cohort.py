import csv
from pathlib import Path

import pytest

from biotech_divedeep.signals.cohort import (
    DaySnapshot,
    classify_day,
    crowding_score,
    load_snapshot,
    spearman,
    summarize,
    two_day_path,
)
from biotech_divedeep.universe import Archetype

REF = Path(__file__).resolve().parents[1] / "data" / "reference"
SNAPSHOT = REF / "ai_bio_cohort_snapshot_2026-10-06.csv"
FIT = REF / "ai_bio_fit_matrix.csv"


def snap(ticker="X", change=-10.0, close=90.0, volume=300.0, avg=100.0, low=30.0, high=120.0, beta=2.0, cap=1e9):
    return DaySnapshot(ticker, ticker, "layer", False, close, change, volume, avg, low, high, beta, cap)


def test_features_from_close_and_change():
    s = snap()
    assert s.prev_close == 100.0
    assert s.ret == pytest.approx(-0.10)
    assert s.rvol == 3.0
    assert s.off_low == 3.0
    assert s.range_multiple == 4.0
    assert s.from_high == pytest.approx(-0.25)


@pytest.mark.parametrize(
    ("change", "volume", "label"),
    [
        (-10.0, 300.0, "heavy_distribution"),
        (-5.0, 200.0, "distribution"),
        (-5.0, 100.0, "quiet_decline"),
        (1.0, 500.0, "up"),
    ],
)
def test_classify_day(change, volume, label):
    assert classify_day(snap(change=change, close=100.0 + change, volume=volume)) == label


def test_two_day_path_round_trip():
    spike, rev, net = two_day_path(80.0, snap())  # 80 -> 100 -> 90
    assert spike == pytest.approx(0.25)
    assert rev == pytest.approx(-0.10)
    assert net == pytest.approx(0.125)


def test_spearman_handles_ties_and_sign():
    assert spearman([1, 2, 3, 4], [10, 20, 30, 40]) == pytest.approx(1.0)
    assert spearman([1, 2, 3, 4], [4, 3, 2, 1]) == pytest.approx(-1.0)
    assert -1.0 <= spearman([1, 1, 2, 3], [3, 1, 2, 2]) <= 1.0


def test_crowding_score_ranks_in_unit_interval():
    scores = crowding_score([snap("A", high=300.0), snap("B", beta=1.0, cap=5e10), snap("C")])
    assert all(0 < v <= 1 for v in scores.values())
    assert scores["A"] > scores["B"]


def test_reference_snapshot_matches_case_study():
    snaps = load_snapshot(SNAPSHOT)
    by = {s.ticker: s for s in snaps}
    assert len(snaps) == 36 and len(by) == 36
    assert by["TWST"].ret == pytest.approx(-0.1855, abs=1e-4)
    assert by["TWST"].prev_close == pytest.approx(205.0)
    data_layer = next(g for g in summarize(snaps, key=lambda s: s.layer) if g.group == "data_generator")
    assert data_layer.n == 6 and data_layer.median_ret == pytest.approx(-0.120, abs=1e-3)


def test_fit_matrix_is_well_formed():
    with open(FIT, newline="") as fh:
        rows = list(csv.DictReader(fh))
    layers = {s.ticker: s.layer for s in load_snapshot(SNAPSHOT)}
    valid_archetypes = {a.value for a in Archetype}
    valid_hypotheses = {f"H{i}" for i in range(1, 14)}
    gaps = {"technical", "outcome", "paid_demand", "margin_and_cash", "per_share_value", "none_major"}
    classes = {"fact", "management_guidance", "own_assumption", "unverified"}
    assert len({r["ticker"] for r in rows}) == len(rows) == 23
    for r in rows:
        assert layers[r["ticker"]] == r["layer"], r["ticker"]
        assert set(r["archetype"].split(";")) <= valid_archetypes, r["ticker"]
        assert set(r["hypotheses"].split(";")) <= valid_hypotheses, r["ticker"]
        assert r["first_gap"] in gaps, r["ticker"]
        assert r["evidence_class"] in classes, r["ticker"]
        assert r["falsifier"] and r["next_node"], r["ticker"]
