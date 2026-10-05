# M11 Portfolio & Backtest (+ M12 Reporting)

Status: design. Phase 3 (harness), Phase 6 (paper portfolio).

## 1. Pre-registration

Borrowed from clinical trials: before running a backtest, write a short analysis plan
in `notes/backtests/` (hypothesis id, universe, period, rules, primary metric, success
threshold). Every variant run is logged, so the number of trials is known and
multiple-testing inflation can be corrected (deflated Sharpe, hold-out period untouched
until final). A result without a pre-registration is exploratory.

## 2. Universe

- Point-in-time membership: US-listed companies in target SIC codes, active on the
  rebalance date, including those later delisted or acquired.
- Filters at each date: price above 1 USD, 20-day median dollar volume above a floor
  set by capital size (open question), market cap band per mandate.
- Delisting returns: acquisitions use deal consideration; failure delistings use last
  price with a conservative haircut (sensitivity: 0%, -30%, -100%).

## 3. Strategy stack

```
universe -> H1 survival screen -> scores (H4 specialist, H6 quality, H8 takeout, archetype models)
         -> H5 trend overlay -> H3 event rules -> sizing -> constraints -> orders (simulated)
```

Sizing: equal risk contribution baseline; event names capped by
`loss budget / stress drawdown`. Constraints: max per name, per archetype, per theme
(AI, obesity, oncology), per payer exposure, binary events per week.

## 4. Metrics

Primary: rolling 126 and 252-day excess return vs XBI total return. Secondary:
information ratio, hit rate of windows, max relative drawdown, left-tail frequency,
turnover, cost drag, capacity (performance vs assumed capital size).

## 5. Costs

Commission (near zero), spread proxy by liquidity bucket, market impact as a function
of trade size over ADV, borrow costs if shorts are allowed.

## 6. M12 Reporting

Weekly review (Markdown in `reports/weekly/YYYY-MM-DD.md`, git-ignored or committed by
choice):

1. Regime: XBI vs 200-day, financing window index, rates.
2. Watchlist table: price, market cap, archetype, runway, dilution score, trend state,
   memo status, action state.
3. Changes this week: filings, trial diffs, FDA items, guidance changes.
4. Catalysts next 90 days, with confidence and binary magnitude.
5. Alerts: survival-gate failures, thesis falsifiers triggered.
6. Paper portfolio vs XBI (Phase 6).
