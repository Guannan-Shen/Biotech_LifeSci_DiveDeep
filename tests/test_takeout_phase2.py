import csv
import math
from pathlib import Path

import pytest

from biotech_divedeep.models.phase2 import (
    GRADED_ITEMS,
    Posterior,
    assurance,
    exaggeration_ratio,
    grade_phase2,
    norm_cdf,
    norm_ppf,
    phase3_se_for_power,
    power,
    se_from_ci,
    shrink_effect,
)
from biotech_divedeep.models.takeout import (
    ACQUIRER_TYPES,
    CONSIDERATION,
    DEAL_KINDS,
    KEY_DATA,
    PRIOR_RELATIONSHIP,
    STAGES,
    basket_deal_distribution,
    expected_kicker,
    hazard_from_counts,
    load_deals,
    load_priors,
    market_cap_band,
    required_probability,
    score_takeout,
    summarize_deals,
)

ROOT = Path(__file__).resolve().parents[1]
DEALS = ROOT / "data" / "reference" / "biotech_takeouts.csv"
PRIORS = ROOT / "config" / "takeout_priors.yaml"
EVIDENCE = {"fact", "management_guidance", "own_assumption", "unverified"}


# --- Phase 2 statistics -----------------------------------------------------------------------


def test_normal_helpers():
    assert norm_ppf(0.975) == pytest.approx(1.959964, abs=1e-6)
    for p in (0.01, 0.3, 0.9):
        assert norm_cdf(norm_ppf(p)) == pytest.approx(p, abs=1e-10)
    assert se_from_ci(-1.96, 1.96) == pytest.approx(1.0, abs=1e-4)


def test_shrinkage_weights_by_precision():
    post = shrink_effect(10, 4, 2, 4)  # equal precision: halfway, variance halves
    assert post.mean == pytest.approx(6.0)
    assert post.sd == pytest.approx(math.sqrt(8))
    assert post.weight_on_data == pytest.approx(0.5)
    assert shrink_effect(10, 0.1, 2, 4).mean == pytest.approx(10, abs=0.01)  # precise data dominates


def test_power_and_assurance():
    se3 = phase3_se_for_power(10, 0.9)
    assert power(10, se3) == pytest.approx(0.9, abs=1e-9)
    # With no uncertainty on the effect, assurance equals power.
    assert assurance(Posterior(10, 1e-9, 1.0), se3) == pytest.approx(0.9, abs=1e-6)
    # Uncertainty pulls a well-powered trial's success probability toward one half.
    assert 0.5 < assurance(Posterior(10, 5, 0.5), se3) < 0.9
    # The documented example: z = 2.5 Phase 2, equal-precision prior at 3.
    assert assurance(shrink_effect(10, 4, 3, 4), se3) == pytest.approx(0.543, abs=0.005)


def test_exaggeration_ratio():
    assert exaggeration_ratio(6.5, 4) == pytest.approx(1.63, abs=0.01)
    assert exaggeration_ratio(40, 4) == pytest.approx(1.0, abs=1e-3)  # well powered: no inflation
    assert exaggeration_ratio(1, 4) > 3  # badly underpowered: a significant result exaggerates


def test_phase2_grade_labels():
    gates = {"randomized_controlled": True, "primary_endpoint_met": True, "no_new_safety_signal": True}
    assert grade_phase2(gates, {k: 2 for k in GRADED_ITEMS}).label == "clean"
    assert grade_phase2(gates, {"clinically_meaningful_effect": 2}).label == "positive_not_clean"
    single_arm = dict(gates, randomized_controlled=False)
    graded = grade_phase2(single_arm, {k: 2 for k in GRADED_ITEMS})
    assert graded.label == "not_clean" and graded.failed_gates == ("randomized_controlled",)
    assert sum(w for w, _ in GRADED_ITEMS.values()) == pytest.approx(1.0)
    with pytest.raises(ValueError):
        grade_phase2(gates, {"vibes": 2})
    with pytest.raises(ValueError):
        grade_phase2(gates, {"dose_response": 3})


# --- Takeout score and arithmetic ---------------------------------------------------------------


def test_priors_load_and_are_positive():
    priors = load_priors(PRIORS)
    assert 0 < priors.base_low < priors.base_mid < priors.base_high < priors.max_probability
    for table in (priors.stage, priors.market_cap, priors.traits):
        assert all(v > 0 for v in table.values())


def test_score_takeout_behaves():
    priors = load_priors(PRIORS)
    base = score_takeout(priors, "phase2_no_data", 1.0)
    clean = score_takeout(priors, "phase2_clean", 1.0)
    activist = score_takeout(priors, "phase2_clean", 1.0, ["activist_or_strategic_review"])
    assert base.p_mid < clean.p_mid < activist.p_mid
    assert clean.p_low < clean.p_mid < clean.p_high
    assert score_takeout(priors, "phase2_clean", 1.0, horizon_years=2).p_mid > clean.p_mid
    capped = score_takeout(priors, "filed", 5, list(priors.traits)[:4], horizon_years=50)
    assert capped.p_high == priors.max_probability
    with pytest.raises(ValueError):
        score_takeout(priors, "phase4", 1.0)
    with pytest.raises(ValueError):
        score_takeout(priors, "phase3", 1.0, ["rumour"])
    assert market_cap_band(0.29) == "micro_under_0.3" and market_cap_band(30) == "mega_over_25"


def test_kicker_and_basket():
    assert expected_kicker(0.05, 0.45) == pytest.approx(0.0225)
    assert required_probability(0.05, 0.4) == pytest.approx(0.125)
    pmf = basket_deal_distribution([0.08] * 15)
    assert sum(pmf) == pytest.approx(1.0)
    assert 1 - pmf[0] == pytest.approx(1 - 0.92**15)
    assert sum(k * m for k, m in enumerate(pmf)) == pytest.approx(1.2)
    with pytest.raises(ValueError):
        basket_deal_distribution([1.2])


def test_hazard_from_counts():
    post = hazard_from_counts(30, 800)
    assert post.mean == pytest.approx(31 / 826)  # Beta(1 + 30, 25 + 770)
    lo, hi = post.interval
    assert lo < post.mean < hi
    with pytest.raises(ValueError):
        hazard_from_counts(10, 5)


# --- Reference table --------------------------------------------------------------------------


def test_takeout_table_is_well_formed():
    with open(DEALS, newline="") as fh:
        rows = list(csv.DictReader(fh))
    ids = [r["deal_id"] for r in rows]
    assert len(ids) == len(set(ids))
    for r in rows:
        assert r["stage_at_deal"] in STAGES, r["deal_id"]
        assert r["key_data_before_deal"] in KEY_DATA, r["deal_id"]
        assert r["acquirer_type"] in ACQUIRER_TYPES, r["deal_id"]
        assert r["consideration"] in CONSIDERATION, r["deal_id"]
        assert r["activist_or_review"] in {"yes", "no", "unknown"}, r["deal_id"]
        assert r["date_precision"] in {"day", "approx"}, r["deal_id"]
        assert r["deal_kind"] in DEAL_KINDS, r["deal_id"]
        assert r["prior_relationship"] in PRIOR_RELATIONSHIP, r["deal_id"]
        assert r["evidence_class"] in EVIDENCE, r["deal_id"]
        assert len(r["announced_on"]) == 10, r["deal_id"]
        assert r["deal_id"][3:7] == r["announced_on"][:4], r["deal_id"]
        if r["source_url"]:
            assert r["source_url"].startswith("https://"), r["deal_id"]
        else:
            assert r["evidence_class"] == "unverified" and "Recall" in r["note"], r["deal_id"]
        if r["cvr_max_per_share_usd"]:
            assert r["consideration"] == "cash_cvr", r["deal_id"]


def test_takeout_table_matches_launch_layer_deals():
    # Tickers are reused (RNA was Prosensa, then Avidity), so key on ticker and announcement date.
    deals = {(d.target_ticker, d.announced_on): d for d in load_deals(DEALS)}
    with open(ROOT / "data" / "reference" / "launch_layer_ma_2026.csv", newline="") as fh:
        for row in csv.DictReader(fh):
            d = deals[(row["target"], row["announced"])]
            assert d.price_per_share_usd == pytest.approx(float(row["price_per_share_usd"]))
    assert any(t == "PCRX" for t, _ in deals)


def test_summary_counts():
    s = summarize_deals(load_deals(DEALS))
    assert sum(s.by_stage.values()) == s.n
    assert 0 < s.share_clinical < 1
    q1, med, q3 = s.premium_last_close
    assert q1 <= med <= q3
