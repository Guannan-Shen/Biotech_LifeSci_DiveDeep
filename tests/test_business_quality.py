import csv
import math
from datetime import date
from pathlib import Path

import pytest

from biotech_divedeep.models.business_quality import (
    SIGNAL_OUTCOMES,
    SIGNAL_TYPES,
    Guide,
    Score,
    beta_cdf,
    beta_quantile,
    business_model_grade,
    costly_signal_score,
    deal_multiple,
    guidance_credibility,
    guidance_scenario_cap,
    load_guides,
    load_scorecard,
    load_signals,
    people_grade,
    protection_weighted_life,
    revenue_concentration,
)

REF = Path(__file__).resolve().parents[1] / "data" / "reference"
EVIDENCE = {"fact", "management_guidance", "own_assumption", "unverified"}


# --- Beta helpers -----------------------------------------------------------------------------


def test_beta_cdf_closed_forms():
    assert beta_cdf(0.5, 2, 2) == pytest.approx(0.5)
    for x in (0.1, 0.37, 0.9):
        assert beta_cdf(x, 1, 1) == pytest.approx(x)  # uniform
        assert beta_cdf(x, 2, 1) == pytest.approx(x * x)
        assert beta_cdf(x, 1, 3) == pytest.approx(1 - (1 - x) ** 3)


def test_beta_quantile_inverts_cdf():
    for a, b in ((4, 7), (2.5, 9), (30, 3)):
        for p in (0.1, 0.5, 0.9):
            assert beta_cdf(beta_quantile(p, a, b), a, b) == pytest.approx(p, abs=1e-9)


# --- Guidance credibility -----------------------------------------------------------------------


def test_guide_hit_rules_and_signed_error():
    beat = Guide("level", low=180, actual=199.6)
    assert beat.hit and beat.signed_error == pytest.approx(19.6 / 180)
    miss = Guide("level", low=71, high=81, actual=70.7)
    assert not miss.hit and miss.signed_error == pytest.approx((70.7 - 76) / 76)
    late = Guide("timeline", deadline=date(2025, 12, 31), actual_date=date(2026, 6, 30))
    assert not late.hit and late.signed_error is None
    assert not Guide("level", low=350, high=365).resolved


def test_credibility_posterior_and_cap():
    guides = [Guide("level", low=1, actual=2)] * 2 + [Guide("level", low=1, actual=0.5)] * 5
    cred = guidance_credibility(guides)
    assert (cred.hits, cred.resolved) == (2, 7)
    assert cred.mean == pytest.approx(4 / 11)  # Beta(2 + 2, 2 + 5)
    lo, hi = cred.interval
    assert lo < cred.mean < hi
    assert guidance_scenario_cap(cred) == pytest.approx(hi)


def test_prior_dominates_tiny_samples():
    one_hit = guidance_credibility([Guide("level", low=1, actual=2)])
    assert one_hit.mean == pytest.approx(0.6)  # not 100%


# --- Costly signals -----------------------------------------------------------------------------


def test_only_pre_committed_entries_score():
    score = costly_signal_score(
        [
            ("pre_committed", "paid_off"),
            ("pre_committed", "partial"),
            ("pre_committed", "pending"),
            ("post_hoc", "n/a"),
            ("unqualified", "n/a"),
            ("short_termist", "n/a"),
        ]
    )
    assert score.resolved == 2 and score.pending == 1
    assert score.paid_off_credit == pytest.approx(1.5)
    assert score.posterior.mean == pytest.approx((1 + 1.5) / (2 + 2))
    with pytest.raises(ValueError):
        costly_signal_score([("excuse", "n/a")])


# --- Lens A -----------------------------------------------------------------------------------


def test_concentration_and_protection_life():
    conc = revenue_concentration({"a": 50, "b": 50, "c": 0})
    assert conc.hhi == pytest.approx(0.5) and conc.top_share == pytest.approx(0.5)
    life = protection_weighted_life([(60, date(2036, 10, 8)), (40, None)], date(2026, 10, 8))
    assert life == pytest.approx(0.6 * 3653 / 365.25)
    assert deal_multiple(88.7, 8) == pytest.approx(11.0875)


# --- Lens C -----------------------------------------------------------------------------------


def _scores(values, evidence="unverified"):
    return {f"C{i + 1}": Score(v, evidence) for i, v in enumerate(values)}


def test_model_grade_gates():
    great = _scores([2, 2, 2, 2, 2, 2, 1, 1], "fact")
    assert business_model_grade(great, wide_moat_revenue_share=0.6).grade == "great"
    # Same scores but the moat is narrow: a high sum cannot buy greatness.
    assert business_model_grade(great, wide_moat_revenue_share=0.2).grade == "good"
    assert business_model_grade(_scores([2, 1, 0, 1, 1, 2, 1, 1]), 0.0).grade == "good"
    assert business_model_grade(_scores([2, 1, 0, 1, 0, 2, 1, 1]), 0.0).grade == "normal"
    assert business_model_grade(_scores([2] * 8), 1.0, revenue_to_opex=0.1).grade == "unproven"
    assert (
        business_model_grade(_scores([2, 2, 2, 2, None, None, None, None], "own_assumption"), 1.0).grade == "unproven"
    )
    with pytest.raises(ValueError):
        Score(3, "fact")


def test_people_grade_rules():
    good = guidance_credibility([Guide("level", low=1, actual=2)] * 6)
    bad = guidance_credibility([Guide("level", low=1, actual=0.5)] * 6)
    assert people_grade(good, 0, True, 1) == "trust"
    assert people_grade(good, 0, True, 0) == "verify"
    assert people_grade(good, 2, True, 1) == "discount"
    assert people_grade(bad, 0, True, 1) == "discount"
    assert people_grade(guidance_credibility([]), 0, True, 1) == "unknown"


# --- Reference ledgers --------------------------------------------------------------------------


def _read(name):
    with open(REF / name, newline="") as fh:
        return list(csv.DictReader(fh))


def test_ledgers_are_well_formed():
    for name, key in (
        ("product_revenue_map.csv", "line"),
        ("guidance_ledger.csv", "guide_id"),
        ("costly_signal_ledger.csv", "signal_id"),
        ("deal_ledger.csv", "deal_id"),
        ("business_quality_scorecard.csv", "criterion"),
    ):
        rows = _read(name)
        assert rows, name
        for r in rows:
            assert r["evidence_class"] in EVIDENCE, (name, r[key])
            if r.get("source_url"):
                assert r["source_url"].startswith("https://"), (name, r[key])
    for r in _read("product_revenue_map.csv"):
        assert r["moat_grade"] in {"none", "narrow", "wide"} and r["moat_trend"] in {"widening", "stable", "eroding"}
    for r in _read("costly_signal_ledger.csv"):
        assert r["type"] in SIGNAL_TYPES and r["outcome"] in SIGNAL_OUTCOMES, r["signal_id"]
    for r in _read("guidance_ledger.csv"):
        assert r["kind"] in {"level", "timeline"}, r["guide_id"]
    ids = [r["guide_id"] for r in _read("guidance_ledger.csv")]
    assert len(ids) == len(set(ids))


def test_hrow_card_numbers_match_the_memo():
    cred = guidance_credibility(load_guides(REF / "guidance_ledger.csv", "HROW"))
    assert (cred.hits, cred.resolved) == (2, 7)
    assert cred.mean == pytest.approx(4 / 11)
    assert math.isclose(cred.interval[1], 0.55, abs_tol=0.01)
    grade = business_model_grade(load_scorecard(REF / "business_quality_scorecard.csv", "HROW"), 0.0)
    assert grade.grade == "good" and grade.total == 9
    sig = costly_signal_score(load_signals(REF / "costly_signal_ledger.csv", "HROW"))
    assert sig.pre_committed == 1 and sig.pending == 1
    mrln = business_model_grade(load_scorecard(REF / "business_quality_scorecard.csv", "MRLN"), 0.0, 2.2 / 30)
    assert mrln.grade == "unproven"
