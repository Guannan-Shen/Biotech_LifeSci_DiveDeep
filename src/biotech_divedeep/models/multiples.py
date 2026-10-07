"""Sales multiples turned into the growth they require.

A price-to-sales multiple is not cheap or expensive by itself; it is a claim about future revenue.
`required_cagr` makes the claim explicit: given today's market value, the revenue base, a terminal
multiple the business could plausibly hold when mature, a horizon and the return an owner wants,
how fast must revenue compound? Comparing that number with base rates of corporate growth
(Mauboussin and Callahan, "The Base Rate Book", 2016) is the test.

All inputs are scenario inputs. The terminal multiple and dilution are `own_assumption`; revenue
bases carry their own evidence class in `data/reference/revenue_baseline_2026.csv`.
"""

from __future__ import annotations

import math


def price_to_sales(market_cap_usd: float, revenue_usd: float) -> float:
    if revenue_usd <= 0:
        raise ValueError("revenue must be positive")
    return market_cap_usd / revenue_usd


def required_revenue(
    market_cap_usd: float,
    terminal_ps: float,
    years: float,
    annual_return: float = 0.0,
    annual_dilution: float = 0.0,
) -> float:
    """Revenue needed in `years` so that a holder earns `annual_return` per year.

    Equity value must grow by (1 + r)^T for the holder, and by a further (1 + dilution)^T because new
    shares take a slice of the same company. Equity value at T = terminal_ps x revenue_T (cash and
    debt are ignored, which flatters cash-rich names slightly and debt-heavy names more).
    """
    if terminal_ps <= 0 or years <= 0:
        raise ValueError("terminal multiple and horizon must be positive")
    growth = ((1.0 + annual_return) * (1.0 + annual_dilution)) ** years
    return market_cap_usd * growth / terminal_ps


def required_cagr(
    market_cap_usd: float,
    revenue_usd: float,
    terminal_ps: float = 5.0,
    years: float = 5.0,
    annual_return: float = 0.0,
    annual_dilution: float = 0.0,
) -> float:
    """Revenue CAGR needed over `years` to deliver `annual_return` at a `terminal_ps` exit multiple."""
    target = required_revenue(market_cap_usd, terminal_ps, years, annual_return, annual_dilution)
    return (target / revenue_usd) ** (1.0 / years) - 1.0


def growth_adjusted_ps(ps: float, growth: float) -> float | None:
    """P/S per point of revenue growth (PSG, the sales analog of the PEG ratio).

    None when growth is zero or negative: a multiple on a shrinking base has no growth to divide by,
    and the honest reading is 'no growth support' rather than a large number.
    """
    if growth <= 0:
        return None
    return ps / (growth * 100.0)


def years_to_multiple(current_ps: float, target_ps: float, growth: float) -> float | None:
    """Years of constant-rate growth at a flat market value until the multiple falls to target."""
    if growth <= 0:
        return None
    if current_ps <= target_ps:
        return 0.0
    return math.log(current_ps / target_ps) / math.log(1.0 + growth)
