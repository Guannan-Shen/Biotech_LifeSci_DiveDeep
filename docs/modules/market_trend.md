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

## 3. Rules under test (framework section 10)

Weekly snapshot, candidate-buy conditions, one-third initial sizing, 200-day exit rule,
event gap-risk recalculation. Every parameter is versioned in config so backtests and
the live report use identical definitions.
