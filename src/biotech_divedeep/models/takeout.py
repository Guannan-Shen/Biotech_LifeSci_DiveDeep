"""Takeout model: the deal database, a transparent hazard score, and the basket arithmetic (H8, P5).

Specification: `docs/research/2026-10-08_takeout_database_and_phase2_gate.md` (D-034).

Three pieces:

1. `load_deals` and `summarize_deals` read `data/reference/biotech_takeouts.csv` and describe the
   targets (stage, data before the deal, acquirer type, premium). This describes acquired companies
   only. Traits common to targets may be just as common among companies never bought, so the
   summary is a hypothesis generator, never a predictor (Palepu 1986: choice-based samples
   overstate accuracy).
2. `score_takeout` turns a company profile into an annual takeout probability band with the
   odds-times-likelihood-ratio priors in `config/takeout_priors.yaml` (`own_assumption`).
   P5 will replace the priors with a discrete-time hazard model fitted on company-quarters.
3. `expected_kicker` and `basket_deal_distribution` show what a takeout tilt is worth: a 5% annual
   hazard times a 45% premium adds about 2% a year to one name, so the takeout is a kicker on a
   thesis that already works standalone, and only a basket turns it into a likely event.
"""

from __future__ import annotations

import csv
import statistics
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from biotech_divedeep.models.business_quality import BetaPosterior

STAGES = {"approved", "filed", "phase3", "phase2", "phase1", "preclinical"}
KEY_DATA = {
    "commercial",
    "approval",
    "phase3_pivotal",
    "phase2_randomized",
    "phase2_single_arm",
    "phase1_poc",
    "none",
    "unknown",
}
ACQUIRER_TYPES = {
    "big_pharma", "mid_pharma", "large_generic", "biotech", "private_pharma", "royalty_or_shell", "private_equity",
}
CONSIDERATION = {"cash", "cash_cvr", "stock", "cash_stock"}
# strategic: a negotiated sale; contested: a hostile or competing public bid before signing; parent_buy_in:
# a controlling holder buys the minority; going_private: a management or financial consortium; distressed:
# a sale under financing pressure at a low price; cash_shell: a buyer of a cash-rich, failed company (D-042).
DEAL_KINDS = {"strategic", "contested", "parent_buy_in", "going_private", "distressed", "cash_shell"}
# Kinds that describe a full-value strategic takeout, the event H8 predicts.
STRATEGIC_KINDS = {"strategic", "contested"}
PRIOR_RELATIONSHIP = {"yes", "no", "unknown"}  # acquirer was a partner, licensee or holder before the deal


# --------------------------------------------------------------------------------------------
# Deal database
# --------------------------------------------------------------------------------------------


def _num(text: str) -> float | None:
    text = (text or "").strip()
    return float(text) if text else None


@dataclass(frozen=True)
class Deal:
    deal_id: str
    target_ticker: str
    acquirer: str
    acquirer_type: str
    announced_on: str
    price_per_share_usd: float | None
    cvr_max_per_share_usd: float | None
    equity_value_usd_b: float | None
    premium_last_close_pct: float | None
    premium_vwap_pct: float | None
    consideration: str
    stage_at_deal: str
    key_data_before_deal: str
    therapeutic_area: str
    modality: str
    activist_or_review: str
    evidence_class: str
    source_url: str
    deal_kind: str = "strategic"
    prior_relationship: str = "unknown"

    @property
    def year(self) -> int:
        return int(self.announced_on[:4])


def load_deals(path: str | Path) -> list[Deal]:
    with open(path, newline="") as fh:
        rows = list(csv.DictReader(fh))
    return [
        Deal(
            deal_id=r["deal_id"],
            target_ticker=r["target_ticker"],
            acquirer=r["acquirer"],
            acquirer_type=r["acquirer_type"],
            announced_on=r["announced_on"],
            price_per_share_usd=_num(r["price_per_share_usd"]),
            cvr_max_per_share_usd=_num(r["cvr_max_per_share_usd"]),
            equity_value_usd_b=_num(r["equity_value_usd_b"]),
            premium_last_close_pct=_num(r["premium_last_close_pct"]),
            premium_vwap_pct=_num(r["premium_vwap_pct"]),
            consideration=r["consideration"],
            stage_at_deal=r["stage_at_deal"],
            key_data_before_deal=r["key_data_before_deal"],
            therapeutic_area=r["therapeutic_area"],
            modality=r["modality"],
            activist_or_review=r["activist_or_review"],
            evidence_class=r["evidence_class"],
            source_url=r["source_url"],
            deal_kind=r.get("deal_kind") or "strategic",
            prior_relationship=r.get("prior_relationship") or "unknown",
        )
        for r in rows
    ]


@dataclass(frozen=True)
class DealSummary:
    n: int
    by_stage: dict[str, int]
    by_key_data: dict[str, int]
    by_acquirer_type: dict[str, int]
    by_area: dict[str, int]
    by_consideration: dict[str, int]
    by_deal_kind: dict[str, int]
    share_clinical: float  # lead asset not yet approved
    share_with_phase2_plus_data: float  # randomized Phase 2, pivotal or approval data before the deal
    premium_last_close: tuple[float, float, float] | None  # quartiles (25th, median, 75th)
    premium_n: int
    leakage_gap_median: float | None  # median of (VWAP premium - last-close premium), both known
    equity_value_median_usd_b: float | None


def _quartiles(values: Sequence[float]) -> tuple[float, float, float] | None:
    if len(values) < 2:
        return None
    q = statistics.quantiles(values, n=4, method="inclusive")
    return q[0], q[1], q[2]


def summarize_deals(deals: Iterable[Deal]) -> DealSummary:
    deals = list(deals)
    n = len(deals)
    if not n:
        raise ValueError("no deals")
    count = lambda attr: dict(Counter(getattr(d, attr) for d in deals).most_common())  # noqa: E731
    premiums = [d.premium_last_close_pct for d in deals if d.premium_last_close_pct is not None]
    gaps = [
        d.premium_vwap_pct - d.premium_last_close_pct
        for d in deals
        if d.premium_vwap_pct is not None and d.premium_last_close_pct is not None
    ]
    values = [d.equity_value_usd_b for d in deals if d.equity_value_usd_b is not None]
    strong = {"phase2_randomized", "phase3_pivotal", "approval", "commercial"}
    return DealSummary(
        n=n,
        by_stage=count("stage_at_deal"),
        by_key_data=count("key_data_before_deal"),
        by_acquirer_type=count("acquirer_type"),
        by_area=count("therapeutic_area"),
        by_consideration=count("consideration"),
        by_deal_kind=count("deal_kind"),
        share_clinical=sum(d.stage_at_deal not in {"approved"} for d in deals) / n,
        share_with_phase2_plus_data=sum(d.key_data_before_deal in strong for d in deals) / n,
        premium_last_close=_quartiles(premiums),
        premium_n=len(premiums),
        leakage_gap_median=statistics.median(gaps) if gaps else None,
        equity_value_median_usd_b=statistics.median(values) if values else None,
    )


def hazard_from_counts(deals: int, company_years: float, prior_a: float = 1.0, prior_b: float = 25.0) -> BetaPosterior:
    """Annual takeout hazard with a Beta prior (default mean about 4%), once the denominator exists.

    `company_years` is the number of listed small and mid-cap biotech company-years at risk in the
    same window and universe as `deals` (Q-032). Rounded to whole trials for the Beta-Binomial.
    """
    if deals < 0 or company_years < deals:
        raise ValueError("need 0 <= deals <= company_years")
    return BetaPosterior(successes=deals, trials=round(company_years), prior_a=prior_a, prior_b=prior_b)


# --------------------------------------------------------------------------------------------
# Hazard score
# --------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class TakeoutPriors:
    base_low: float
    base_mid: float
    base_high: float
    max_probability: float
    stage: Mapping[str, float]
    market_cap: Mapping[str, float]
    traits: Mapping[str, float]


def load_priors(path: str | Path) -> TakeoutPriors:
    with open(path) as fh:
        raw = yaml.safe_load(fh)
    base = raw["base_annual_hazard"]
    return TakeoutPriors(
        base_low=float(base["low"]),
        base_mid=float(base["mid"]),
        base_high=float(base["high"]),
        max_probability=float(raw["max_probability"]),
        stage={str(k): float(v) for k, v in raw["stage"].items()},
        market_cap={str(k): float(v) for k, v in raw["market_cap"].items()},
        traits={str(k): float(v) for k, v in raw["traits"].items()},
    )


def market_cap_band(market_cap_usd_b: float) -> str:
    if market_cap_usd_b < 0.3:
        return "micro_under_0.3"
    if market_cap_usd_b < 2:
        return "small_0.3_to_2"
    if market_cap_usd_b < 10:
        return "mid_2_to_10"
    if market_cap_usd_b < 25:
        return "large_10_to_25"
    return "mega_over_25"


@dataclass(frozen=True)
class TakeoutScore:
    p_low: float
    p_mid: float
    p_high: float
    likelihood_ratio: float
    factors: tuple[tuple[str, float], ...] = field(default_factory=tuple)


def _odds_to_p(odds: float, cap: float) -> float:
    return min(odds / (1.0 + odds), cap)


def score_takeout(
    priors: TakeoutPriors,
    stage: str,
    market_cap_usd_b: float,
    traits: Iterable[str] = (),
    horizon_years: float = 1.0,
) -> TakeoutScore:
    """Probability band of a definitive sale within `horizon_years` (own_assumption priors)."""
    if stage not in priors.stage:
        raise ValueError(f"unknown stage {stage!r}; expected one of {sorted(priors.stage)}")
    traits = list(dict.fromkeys(traits))
    unknown = [t for t in traits if t not in priors.traits]
    if unknown:
        raise ValueError(f"unknown traits {unknown}")
    if horizon_years <= 0:
        raise ValueError("horizon must be positive")
    band = market_cap_band(market_cap_usd_b)
    factors = [(f"stage:{stage}", priors.stage[stage]), (f"market_cap:{band}", priors.market_cap[band])]
    factors += [(f"trait:{t}", priors.traits[t]) for t in traits]
    lr = 1.0
    for _, ratio in factors:
        lr *= ratio

    def p(base_annual: float) -> float:
        base = 1.0 - (1.0 - base_annual) ** horizon_years
        return round(_odds_to_p(base / (1.0 - base) * lr, priors.max_probability), 4)

    return TakeoutScore(
        p_low=p(priors.base_low),
        p_mid=p(priors.base_mid),
        p_high=p(priors.base_high),
        likelihood_ratio=round(lr, 4),
        factors=tuple(factors),
    )


# --------------------------------------------------------------------------------------------
# What a takeout tilt is worth
# --------------------------------------------------------------------------------------------


def expected_kicker(probability: float, premium: float) -> float:
    """Expected return added by a possible takeout: p x premium over the current price.

    Use the premium to the price you pay, not to the unaffected price: a stock that already ran
    up on rumours keeps less of the headline premium.
    """
    if not 0.0 <= probability <= 1.0:
        raise ValueError("probability must be in [0, 1]")
    return probability * premium


def required_probability(target_kicker: float, premium: float) -> float:
    """Takeout probability needed for the kicker alone to reach `target_kicker`."""
    if premium <= 0:
        raise ValueError("premium must be positive")
    return target_kicker / premium


def basket_deal_distribution(probabilities: Sequence[float]) -> list[float]:
    """Poisson-binomial distribution of the number of takeouts in a basket (independent names).

    Returns pmf[k] = P(exactly k deals). Independence is optimistic: deal waves cluster with rates,
    big-pharma cash and patent cliffs, so the real spread is wider.
    """
    pmf = [1.0]
    for p in probabilities:
        if not 0.0 <= p <= 1.0:
            raise ValueError("probabilities must be in [0, 1]")
        nxt = [0.0] * (len(pmf) + 1)
        for k, mass in enumerate(pmf):
            nxt[k] += mass * (1.0 - p)
            nxt[k + 1] += mass * p
        pmf = nxt
    return pmf
