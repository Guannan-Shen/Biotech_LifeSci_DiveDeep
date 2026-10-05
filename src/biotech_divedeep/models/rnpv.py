"""Staged risk-adjusted NPV (rNPV) for a single development asset.

Implements the framework definition (docs/framework/investment_framework.md, section 4):
commercial value weighted by cumulative probability of success, minus each stage's cost
weighted by the probability of reaching that stage, all discounted to today.

Deliberately simple: one lump of commercial value at launch, stage costs paid at stage
start. Good enough for sensitivity work; full launch curves live in the launch model.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Stage:
    """One development stage. `cost` is paid at stage start; `pos` is P(advance)."""

    name: str
    cost: float
    years: float
    pos: float

    def __post_init__(self) -> None:
        if not 0.0 <= self.pos <= 1.0:
            raise ValueError(f"{self.name}: pos must be in [0, 1], got {self.pos}")
        if self.years < 0 or self.cost < 0:
            raise ValueError(f"{self.name}: cost and years must be non-negative")


@dataclass(frozen=True)
class RnpvResult:
    rnpv: float
    cumulative_pos: float
    years_to_launch: float


def rnpv(
    stages: list[Stage],
    launch_value: float,
    discount_rate: float,
    start_year: float = 0.0,
) -> RnpvResult:
    """Return rNPV of an asset whose first stage begins `start_year` years from today.

    `launch_value` is the net present value of commercial cash flows measured at the
    launch date (i.e., already discounted back to launch, not to today).
    """
    if discount_rate <= -1.0:
        raise ValueError("discount_rate must be greater than -1")

    def df(t: float) -> float:
        return (1.0 + discount_rate) ** -t

    t = start_year
    p_reach = 1.0
    value = 0.0
    for stage in stages:
        value -= p_reach * stage.cost * df(t)
        t += stage.years
        p_reach *= stage.pos
    value += p_reach * launch_value * df(t)
    return RnpvResult(rnpv=value, cumulative_pos=p_reach, years_to_launch=t)
