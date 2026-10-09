"""Phase 2 quality gate: how much of a "clean" Phase 2 result survives into Phase 3.

Specification: `docs/research/2026-10-08_takeout_database_and_phase2_gate.md` section 5 (D-035).

Two problems with reading a positive Phase 2 at face value:

1. **Selection inflates the estimate.** Programs advance because their Phase 2 estimate came out
   high. Conditioning on significance in a small trial exaggerates the effect (Gelman and Carlin
   2014, "type M error"), so the Phase 3 effect is expected to be smaller. `shrink_effect` applies
   a normal-normal empirical Bayes shrinkage toward a class prior; `exaggeration_ratio` shows how
   large the inflation is for a given true effect and standard error.
2. **Phase 3 power is computed at the wrong effect.** Sponsors power Phase 3 on the Phase 2 point
   estimate. `assurance` (O'Hagan, Stevens and Campbell 2005) integrates power over the posterior
   of the effect, which gives the probability that Phase 3 is statistically positive.

`Phase2Scorecard` is the qualitative half: a checklist with gate items (randomized control, the
pre-specified primary endpoint met, no new safety signal) and graded items. A result is `clean`
only when every gate passes and the graded share is high; the numbers here never replace reading
the data release and the trial registration.

Stdlib only. Effects are on any scale where larger is better (difference in means, log hazard
ratio with the sign flipped, risk difference); keep the prior on the same scale.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass

_SQRT2 = math.sqrt(2.0)


def norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / _SQRT2))


def norm_pdf(x: float) -> float:
    return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


def norm_ppf(p: float) -> float:
    """Inverse standard normal CDF by bisection (accurate to about 1e-12 on (1e-12, 1 - 1e-12))."""
    if not 0.0 < p < 1.0:
        raise ValueError("p must be in (0, 1)")
    lo, hi = -40.0, 40.0
    for _ in range(100):
        mid = (lo + hi) / 2.0
        if norm_cdf(mid) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def se_from_ci(lower: float, upper: float, level: float = 0.95) -> float:
    """Standard error implied by a symmetric confidence interval (use log scale for ratios)."""
    if upper <= lower:
        raise ValueError("upper must exceed lower")
    return (upper - lower) / (2.0 * norm_ppf(0.5 + level / 2.0))


@dataclass(frozen=True)
class Posterior:
    mean: float
    sd: float
    weight_on_data: float  # share of the posterior mean that comes from the Phase 2 estimate


def shrink_effect(estimate: float, se: float, prior_mean: float, prior_sd: float) -> Posterior:
    """Normal-normal posterior for the true effect given a Phase 2 estimate and a class prior.

    The prior describes true effects of comparable programs (same mechanism class or indication),
    for example the distribution of Phase 3 effects of drugs that cleared Phase 2. It is an
    `own_assumption` until calibrated from a labelled readout set (P6).
    """
    if se <= 0 or prior_sd <= 0:
        raise ValueError("standard errors must be positive")
    w_data, w_prior = 1.0 / se**2, 1.0 / prior_sd**2
    mean = (w_data * estimate + w_prior * prior_mean) / (w_data + w_prior)
    return Posterior(mean=mean, sd=math.sqrt(1.0 / (w_data + w_prior)), weight_on_data=w_data / (w_data + w_prior))


def phase3_se_for_power(design_effect: float, power: float = 0.9, alpha_one_sided: float = 0.025) -> float:
    """Standard error a Phase 3 needs so that `design_effect` is detected with `power`."""
    if design_effect <= 0:
        raise ValueError("design effect must be positive")
    return design_effect / (norm_ppf(1.0 - alpha_one_sided) + norm_ppf(power))


def power(true_effect: float, se: float, alpha_one_sided: float = 0.025) -> float:
    """Conventional power of a one-sided z test at a fixed true effect."""
    return norm_cdf(true_effect / se - norm_ppf(1.0 - alpha_one_sided))


def assurance(posterior: Posterior, phase3_se: float, alpha_one_sided: float = 0.025) -> float:
    """Probability that Phase 3 is significant, averaging power over the posterior of the effect.

    With theta ~ N(m, s^2) and the Phase 3 estimate ~ N(theta, se3^2), the estimate is marginally
    N(m, s^2 + se3^2); success means estimate > z * se3.
    """
    z = norm_ppf(1.0 - alpha_one_sided)
    return norm_cdf((posterior.mean - z * phase3_se) / math.sqrt(posterior.sd**2 + phase3_se**2))


def exaggeration_ratio(true_effect: float, se: float, alpha_two_sided: float = 0.05) -> float:
    """Expected |estimate| / true effect given a significant result (Gelman and Carlin type M).

    Closed form: for X ~ N(mu, se^2) and the region |X| > c, E[|X|; region] is the sum of the
    upper-tail and lower-tail partial expectations.
    """
    if true_effect <= 0 or se <= 0:
        raise ValueError("true effect and se must be positive")
    c = norm_ppf(1.0 - alpha_two_sided / 2.0) * se
    a_up, a_low = (c - true_effect) / se, (-c - true_effect) / se
    p_up, p_low = 1.0 - norm_cdf(a_up), norm_cdf(a_low)
    e_up = true_effect * p_up + se * norm_pdf(a_up)  # E[X; X > c]
    e_low = true_effect * p_low - se * norm_pdf(a_low)  # E[X; X < -c], negative
    return (e_up - e_low) / (p_up + p_low) / true_effect


# --------------------------------------------------------------------------------------------
# Qualitative scorecard
# --------------------------------------------------------------------------------------------

# Gate items: one failure means the readout is not clean, whatever else it shows.
GATE_ITEMS = {
    "randomized_controlled": "Randomized with a concurrent placebo or active control arm",
    "primary_endpoint_met": "Pre-specified primary endpoint met at the pre-specified alpha (registry matches release)",
    "no_new_safety_signal": "No new or dose-limiting safety signal; adverse-event discontinuations similar to control",
}

# Graded items: 0 (no or unknown), 1 (partly), 2 (yes). Weights sum to 1.
GRADED_ITEMS = {
    "clinically_meaningful_effect": (
        0.15,
        "Effect clears the minimal clinically important difference and the standard of care",
    ),
    "dose_response": (0.10, "Monotone dose or exposure response across at least two active arms"),
    "consistent_secondaries": (0.10, "Key secondary endpoints and pre-specified subgroups point the same way"),
    "registrational_endpoint": (0.15, "Primary endpoint and population are the ones regulators accept for approval"),
    "adequate_size": (0.10, "Enough patients that the confidence interval excludes a trivial effect"),
    "durability": (0.10, "Effect maintained at the latest time point, or durable off treatment"),
    "best_in_class_evidence": (
        0.10,
        "Head-to-head data, or cross-trial comparison with matched populations and endpoints",
    ),
    "mechanism_validated": (0.10, "Target or pathway already validated in humans by another program"),
    "independent_confirmation": (
        0.10,
        "Second trial, independent investigators, or peer-reviewed full data with registry results",
    ),
}

CLEAN_THRESHOLD = 0.65


@dataclass(frozen=True)
class Phase2Grade:
    gates_passed: bool
    failed_gates: tuple[str, ...]
    graded_share: float  # 0..1, weighted share of the maximum graded score
    missing: tuple[str, ...]

    @property
    def label(self) -> str:
        if not self.gates_passed:
            return "not_clean"
        return "clean" if self.graded_share >= CLEAN_THRESHOLD else "positive_not_clean"


def grade_phase2(gates: Mapping[str, bool], graded: Mapping[str, int]) -> Phase2Grade:
    """Grade one readout. Unknown items count as failed (gates) or zero (graded)."""
    unknown = set(gates) - set(GATE_ITEMS) | set(graded) - set(GRADED_ITEMS)
    if unknown:
        raise ValueError(f"unknown items: {sorted(unknown)}")
    for key, value in graded.items():
        if value not in (0, 1, 2):
            raise ValueError(f"{key} must be 0, 1 or 2")
    failed = tuple(k for k in GATE_ITEMS if not gates.get(k, False))
    share = sum(w * graded.get(k, 0) / 2.0 for k, (w, _) in GRADED_ITEMS.items())
    missing = tuple(k for k in (*GATE_ITEMS, *GRADED_ITEMS) if k not in gates and k not in graded)
    return Phase2Grade(gates_passed=not failed, failed_gates=failed, graded_share=round(share, 4), missing=missing)
