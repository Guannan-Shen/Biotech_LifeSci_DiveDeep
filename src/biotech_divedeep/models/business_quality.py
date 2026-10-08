"""Business quality gate: product concentration, moat life, business model grade, people grade.

Specification: `docs/framework/business_quality.md` (D-030 to D-033). The functions here are the
arithmetic behind the business quality card; the judgments (scores, moat grades, ledger entries)
live in `data/reference/` with sources and evidence classes.

Two ledgers carry the people lens:

- `guidance_ledger.csv`: every quantitative guide and how it resolved. `guidance_credibility`
  turns it into a Beta-Binomial posterior hit rate with a credible interval, because three to six
  guides per company are too few for a raw hit rate to mean much.
- `costly_signal_ledger.csv`: actions that trade short-term results for a stated long-term
  payoff. Only `pre_committed` entries (announced before the cost, cost and payoff quantified, check
  date named) count toward the score; `unqualified`, `post_hoc` and `short_termist` entries are kept
  for the record.
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date

# --------------------------------------------------------------------------------------------
# Beta distribution helpers (stdlib only; scipy is not a dependency)
# --------------------------------------------------------------------------------------------


def _beta_continued_fraction(x: float, a: float, b: float) -> float:
    """Continued fraction for the regularized incomplete beta function (modified Lentz method)."""
    tiny = 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, 300):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-12:
            break
    return h


def beta_cdf(x: float, a: float, b: float) -> float:
    """Regularized incomplete beta function I_x(a, b), the CDF of Beta(a, b) at x."""
    if a <= 0 or b <= 0:
        raise ValueError("shape parameters must be positive")
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    log_front = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log1p(-x)
    front = math.exp(log_front)
    if x < (a + 1.0) / (a + b + 2.0):
        return front * _beta_continued_fraction(x, a, b) / a
    return 1.0 - front * _beta_continued_fraction(1.0 - x, b, a) / b


def beta_quantile(p: float, a: float, b: float) -> float:
    """Inverse CDF of Beta(a, b) by bisection (60 halvings, error below 1e-15)."""
    if not 0.0 <= p <= 1.0:
        raise ValueError("p must be in [0, 1]")
    lo, hi = 0.0, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2.0
        if beta_cdf(mid, a, b) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


@dataclass(frozen=True)
class BetaPosterior:
    successes: float
    trials: int
    prior_a: float
    prior_b: float
    ci: float = 0.8

    @property
    def a(self) -> float:
        return self.prior_a + self.successes

    @property
    def b(self) -> float:
        return self.prior_b + self.trials - self.successes

    @property
    def mean(self) -> float:
        return self.a / (self.a + self.b)

    @property
    def interval(self) -> tuple[float, float]:
        tail = (1.0 - self.ci) / 2.0
        return beta_quantile(tail, self.a, self.b), beta_quantile(1.0 - tail, self.a, self.b)


# --------------------------------------------------------------------------------------------
# D1: guidance credibility
# --------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Guide:
    """One quantitative guide. `kind` is `level` (revenue, EBITDA: hit if actual >= low) or
    `timeline` (launch, filing, certification: hit if actual_date <= deadline). Unresolved guides
    have no actual and are ignored by the score."""

    kind: str
    low: float | None = None
    high: float | None = None
    actual: float | None = None
    deadline: date | None = None
    actual_date: date | None = None

    @property
    def resolved(self) -> bool:
        if self.kind == "level":
            return self.actual is not None and self.low is not None
        if self.kind == "timeline":
            return self.actual_date is not None and self.deadline is not None
        raise ValueError(f"unknown guide kind: {self.kind}")

    @property
    def hit(self) -> bool:
        if not self.resolved:
            raise ValueError("unresolved guide has no outcome")
        if self.kind == "level":
            return self.actual >= self.low  # type: ignore[operator]
        return self.actual_date <= self.deadline  # type: ignore[operator]

    @property
    def signed_error(self) -> float | None:
        """(actual - guide midpoint) / midpoint for level guides; open-ended guides use the low end."""
        if self.kind != "level" or not self.resolved:
            return None
        mid = self.low if self.high is None else (self.low + self.high) / 2.0  # type: ignore[operator]
        if not mid:
            return None
        return (self.actual - mid) / abs(mid)  # type: ignore[operator]


@dataclass(frozen=True)
class Credibility:
    resolved: int
    hits: int
    pending: int
    posterior: BetaPosterior
    mean_signed_error: float | None

    @property
    def mean(self) -> float:
        return self.posterior.mean

    @property
    def interval(self) -> tuple[float, float]:
        return self.posterior.interval


def guidance_credibility(
    guides: Iterable[Guide], prior_a: float = 2.0, prior_b: float = 2.0, ci: float = 0.8
) -> Credibility:
    """Beta-Binomial posterior hit rate of management guidance (D-032).

    The Beta(2, 2) prior centres on a coin flip and is worth four pseudo-guides: enough to stop one
    hit from reading as certainty, weak enough that five resolved guides dominate it.
    """
    guides = list(guides)
    resolved = [g for g in guides if g.resolved]
    hits = sum(g.hit for g in resolved)
    errors = [e for g in resolved if (e := g.signed_error) is not None]
    mse = sum(errors) / len(errors) if errors else None
    post = BetaPosterior(successes=hits, trials=len(resolved), prior_a=prior_a, prior_b=prior_b, ci=ci)
    return Credibility(len(resolved), hits, len(guides) - len(resolved), post, mse)


# --------------------------------------------------------------------------------------------
# D4: costly-signal ledger
# --------------------------------------------------------------------------------------------

SIGNAL_TYPES = {"pre_committed", "unqualified", "post_hoc", "short_termist"}
SIGNAL_OUTCOMES = {"paid_off", "partial", "failed", "pending", "n/a"}
_OUTCOME_CREDIT = {"paid_off": 1.0, "partial": 0.5, "failed": 0.0}


@dataclass(frozen=True)
class CostlySignalScore:
    pre_committed: int
    resolved: int
    pending: int
    paid_off_credit: float
    unqualified: int
    post_hoc: int
    short_termist: int
    posterior: BetaPosterior


def costly_signal_score(
    entries: Iterable[tuple[str, str]], prior_a: float = 1.0, prior_b: float = 1.0
) -> CostlySignalScore:
    """Score (type, outcome) pairs from the costly-signal ledger (D-031).

    Partial payoffs earn half credit. The uniform prior reflects that most companies have zero or
    one resolved pre-committed sacrifice: the posterior should stay wide.
    """
    counts = dict.fromkeys(SIGNAL_TYPES, 0)
    credit, resolved, pending = 0.0, 0, 0
    for kind, outcome in entries:
        if kind not in SIGNAL_TYPES:
            raise ValueError(f"unknown signal type: {kind}")
        if outcome not in SIGNAL_OUTCOMES:
            raise ValueError(f"unknown outcome: {outcome}")
        counts[kind] += 1
        if kind != "pre_committed":
            continue
        if outcome == "pending":
            pending += 1
        elif outcome in _OUTCOME_CREDIT:
            resolved += 1
            credit += _OUTCOME_CREDIT[outcome]
    post = BetaPosterior(successes=credit, trials=resolved, prior_a=prior_a, prior_b=prior_b)
    return CostlySignalScore(
        counts["pre_committed"],
        resolved,
        pending,
        credit,
        counts["unqualified"],
        counts["post_hoc"],
        counts["short_termist"],
        post,
    )


# --------------------------------------------------------------------------------------------
# Lens A: revenue concentration and protection-weighted life
# --------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Concentration:
    hhi: float
    top_name: str
    top_share: float


def revenue_concentration(revenue_by_line: Mapping[str, float]) -> Concentration:
    """Herfindahl index of revenue shares; above 0.35 the top product dominates the card."""
    items = {k: v for k, v in revenue_by_line.items() if v > 0}
    total = sum(items.values())
    if total <= 0:
        raise ValueError("no positive revenue")
    shares = {k: v / total for k, v in items.items()}
    top = max(shares, key=shares.__getitem__)
    return Concentration(sum(s * s for s in shares.values()), top, shares[top])


def protection_weighted_life(lines: Sequence[tuple[float, date | None]], as_of: date) -> float:
    """Revenue-weighted years until loss of exclusivity. Lines without protection count as zero
    years: a compounded or long-generic product never had a cliff, but it also has no legal moat."""
    total = sum(r for r, _ in lines if r > 0)
    if total <= 0:
        raise ValueError("no positive revenue")
    years = 0.0
    for revenue, end in lines:
        if revenue <= 0 or end is None:
            continue
        years += revenue * max((end - as_of).days / 365.25, 0.0)
    return years / total


def deal_multiple(revenue_after: float, total_paid: float) -> float:
    """Revenue two or three years after a deal per dollar paid (upfront plus milestones paid).

    Ignores royalties, transfer prices and the sales force the product needed, so it flatters
    in-licensed products; use it to rank a company's own deals, not to compare with owned assets.
    """
    if total_paid <= 0:
        raise ValueError("total paid must be positive")
    return revenue_after / total_paid


# --------------------------------------------------------------------------------------------
# Lens C: business model grade
# --------------------------------------------------------------------------------------------

CRITERIA = ("C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8")
REPORTED = {"fact", "management_guidance", "unverified"}


@dataclass(frozen=True)
class Score:
    value: int | None
    evidence_class: str

    def __post_init__(self) -> None:
        if self.value is not None and self.value not in (0, 1, 2):
            raise ValueError("criterion scores are 0, 1 or 2")


@dataclass(frozen=True)
class ModelGrade:
    grade: str
    total: int
    scored: int
    zeros: int
    reasons: tuple[str, ...]


def business_model_grade(
    scores: Mapping[str, Score],
    wide_moat_revenue_share: float,
    revenue_to_opex: float | None = None,
) -> ModelGrade:
    """Normal / good / great / unproven with the gates of `business_quality.md` section 3.

    `unverified` evidence counts as reported data (it is a filing or release not yet re-read),
    `own_assumption` does not. Unscored criteria count as missing, not as zero.
    """
    unknown = set(scores) - set(CRITERIA)
    if unknown:
        raise ValueError(f"unknown criteria: {sorted(unknown)}")
    values = {k: s.value for k, s in scores.items() if s.value is not None}
    total = sum(values.values())
    zeros = sum(1 for v in values.values() if v == 0)
    reported = sum(1 for s in scores.values() if s.value is not None and s.evidence_class in REPORTED)
    reasons: list[str] = []

    if revenue_to_opex is not None and revenue_to_opex < 0.25:
        reasons.append(f"revenue is {revenue_to_opex:.0%} of operating expenses: not yet the target model")
    if reported < 4:
        reasons.append(f"only {reported} criteria scorable from reported data")
    if reasons:
        return ModelGrade("unproven", total, len(values), zeros, tuple(reasons))

    c5 = scores.get("C5")
    great_blockers = []
    if total < 12:
        great_blockers.append(f"sum {total} < 12")
    if zeros:
        great_blockers.append(f"{zeros} criterion at 0")
    if wide_moat_revenue_share < 0.5:
        great_blockers.append(f"wide moat on {wide_moat_revenue_share:.0%} of revenue < 50%")
    if not (c5 and c5.value == 2 and c5.evidence_class == "fact"):
        great_blockers.append("operating leverage (C5) not proven with fact evidence")
    if not great_blockers:
        return ModelGrade("great", total, len(values), zeros, ("all gates passed",))
    if total >= 8 and zeros <= 1:
        return ModelGrade("good", total, len(values), zeros, tuple(great_blockers))
    return ModelGrade("normal", total, len(values), zeros, tuple(great_blockers))


# --------------------------------------------------------------------------------------------
# Lens D: people grade
# --------------------------------------------------------------------------------------------


def people_grade(
    credibility: Credibility,
    candor_flags: int,
    aligned: bool | None,
    paid_off_sacrifices: float,
) -> str:
    """trust / verify / discount / unknown (section 4 of the specification)."""
    if credibility.resolved < 3:
        return "unknown"
    mse = credibility.mean_signed_error
    if (credibility.mean < 0.4 and mse is not None and mse < 0) or candor_flags >= 2:
        return "discount"
    if credibility.mean > 0.6 and candor_flags == 0 and aligned and paid_off_sacrifices >= 1:
        return "trust"
    return "verify"


def guidance_scenario_cap(credibility: Credibility) -> float:
    """Maximum probability for a scenario that assumes guidance is met (section 6, rule 1)."""
    return credibility.interval[1]


# --------------------------------------------------------------------------------------------
# Loaders for the reference ledgers in data/reference/
# --------------------------------------------------------------------------------------------


def _rows(path, ticker: str) -> list[dict[str, str]]:
    import csv

    with open(path, newline="") as fh:
        return [r for r in csv.DictReader(fh) if r["ticker"] == ticker]


def _num(text: str) -> float | None:
    return float(text) if text.strip() else None


def _day(text: str) -> date | None:
    return date.fromisoformat(text) if text.strip() else None


def load_guides(path, ticker: str) -> list[Guide]:
    return [
        Guide(
            kind=r["kind"],
            low=_num(r["low"]),
            high=_num(r["high"]),
            actual=_num(r["actual"]),
            deadline=_day(r["deadline"]),
            actual_date=_day(r["actual_date"]),
        )
        for r in _rows(path, ticker)
    ]


def load_signals(path, ticker: str) -> list[tuple[str, str]]:
    return [(r["type"], r["outcome"]) for r in _rows(path, ticker)]


def load_scorecard(path, ticker: str) -> dict[str, Score]:
    return {
        r["criterion"]: Score(int(r["score"]) if r["score"].strip() else None, r["evidence_class"])
        for r in _rows(path, ticker)
    }


def load_product_map(path, ticker: str) -> list[dict[str, str]]:
    return _rows(path, ticker)
