# M5 Market & Trend

Status: design. Phase 3 build target (price store needed for backtests); a light
version for the weekly report arrives in Phase 2.

## 1. Data

| Need | Candidate source | Caveat |
|---|---|---|
| Daily adjusted prices, watchlist | FMP (connected; current plan blocks batch endpoints) | Per-symbol calls only on current plan |
| XBI, IBB total return | FMP or ETF provider history | Use adjusted close with dividends |
| Delisted price history | Requires a vendor that keeps delisted names (FMP higher tier, Sharadar, Norgate, CRSP) | **Decision pending**; without it backtests carry survivorship bias |
| Short interest | FINRA semi-monthly short interest files | Lagged |
| Implied volatility around events | Options data vendor | Later; implied move = market-priced binary size |

## 2. Features

- 50 and 200-day moving averages, slope of the 200-day.
- 13-week relative strength vs XBI and vs the archetype peer basket (tools names are
  compared to tools peers).
- XBI regime: price vs 200-day MA; drawdown from high; 10-year Treasury yield change
  (biotech is long-duration and rate sensitive).
- **Financing window index** (own construct): weekly count and dollar volume of
  biotech follow-ons and IPOs from EDGAR 424B filings. Open windows help weak balance
  sheets survive; closed windows punish them. Expected to interact strongly with H1.
- Liquidity: 20-day median dollar volume, spread proxy, days to cover.

### 2a. Volume features (added 2026-10-05, D-018, investor edit to H5)

| Feature | Definition | Reading |
|---|---|---|
| Relative volume (RVOL) | Daily volume / 50-day median volume | Above 2 marks an information day; tie it to an event before trusting it |
| Breakout confirmation | Close above the 50 or 200-day MA (or a 13-week high) with RVOL above 1.5 | Confirmed breakouts are the candidate-buy trigger in the trend overlay; unconfirmed ones wait |
| Up/down volume ratio | 50-day sum of volume on up days / volume on down days | Above 1.2 suggests accumulation; below 0.8 suggests distribution |
| On-balance volume (OBV) slope | 13-week slope of cumulative signed volume, scaled by float | Divergence from price (price up, OBV down) is a warning |
| Event-day volume | RVOL and gap on catalyst and filing days | Separates news the market absorbed from news it ignored; feeds P7 in M9 |
| Supply-day volume | RVOL around lockup expiries, resale registrations, warrant exercisability | Measures overhang absorption for H11 |
| Turnover | Daily volume / float | Very high turnover in micro caps means crowding (pairs with M13 attention z-score) |

Caveats: volume is raw (not split-adjusted in some feeds); use share counts from the same
date as the volume. Micro-cap volume is noisy, so features use medians and require a
dollar-volume floor. Off-exchange and short-volume data (FINRA daily short volume) are a
later addition.

## 3. Rules under test (framework section 10)

Weekly snapshot, candidate-buy conditions, one-third initial sizing, 200-day exit rule,
event gap-risk recalculation. Every parameter is versioned in config so backtests and
the live report use identical definitions.
