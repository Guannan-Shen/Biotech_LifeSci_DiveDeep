# Backtest Pre-Registration: H13 Crowded-theme blow-off reversal

Written 2026-10-06, before any price history for the test was pulled. Motivating case:
`docs/research/2026-10-06_ai_bio_theme_reversal.md`. The 2026-10-06 event is excluded from
every sample below; it served to form the hypothesis.

| Field | Entry |
|---|---|
| Hypothesis | H13 (`docs/BLUEPRINT.md` section 3) |
| Question | After a theme cohort's leaders complete a large run and print a heavy-distribution day on a day the broad market is flat or up, do they underperform XBI and a run-matched control over the next 21, 63 and 126 trading days? |
| Universe | Survivorship-free US biotech, diagnostics and life-science tools (SIC 2834, 2835, 2836, 3826, 3841, 8071, 8731), delisted names included, market cap above USD 300M at the event date. |
| Cohorts | Two point-in-time definitions, both tested: (a) holdings of thematic ETFs on the event date (ARKG from its 2014 launch; other genomics or AI-health ETFs if daily holdings exist); (b) correlation clusters from trailing 126-day returns, rebuilt monthly with data up to the prior month end only. |
| Name-level trigger | All on day t: close / 252-day low >= 3.0; close within 10% of the 252-day high in the prior 5 sessions; day return <= -10%; volume / 50-day median volume >= 2.0; SPY return >= -0.25%. |
| Cohort-level trigger | At least 30% of a cohort's members (minimum 3 names) hit the name-level trigger within 3 sessions. |
| Controls | For each triggered name, up to 3 names from the same universe with close / 252-day low within +/-25% of the triggered name and no trigger in the prior 63 sessions, matched on date and size bucket. |
| Period | In-sample 2005-01 to 2018-12; out-of-sample 2019-01 to 2023-12; untouched hold-out 2024-01 to 2026-09. |
| Outcomes | Excess return vs XBI total return and vs controls at t+21, t+63, t+126 (entry at close t+1); max drawdown to t+126; share of names down 40% or more from the 252-day high by t+126. |
| Costs | Not a trading rule in the first pass, so no costs; a follow-on test of a reduce-and-avoid overlay on H1 uses the M11 cost model. |
| Primary metric | Median 126-day excess return vs XBI of triggered names (cohort-level events weighted equally). |
| Success threshold | Out of sample: median 126-day excess vs XBI <= -10% and vs controls <= -5%, with at least 60% of events negative vs XBI; bootstrap 90% interval for the median excess excludes 0. |
| Variants planned | Run-size threshold {2.0, 3.0, 5.0}; day-return threshold {-8%, -10%, -15%}; RVOL threshold {1.5, 2.0, 3.0}; cohort definition {ETF, cluster}. 3 x 3 x 3 x 2 = 54 variants; report all, with a Bonferroni or Holm adjustment on the primary metric. The crowding score in `src/biotech_divedeep/signals/cohort.py` is tested unchanged as a secondary sort. |
| Secondary questions | Does a second heavy-distribution day within 25 sessions raise the hit rate? Does the 10-year yield change over the prior 21 days interact with the outcome? Do names with closed validation gaps (fit matrix `first_gap` in {none_major, per_share_value}) underperform less? |
| Known analogs to check after the run (not tuning inputs) | Genomics after March 2000; biotech after July 2015; ARKG holdings after February 2021; COVID vaccine names in 2020-2021. |

## Amendment A1 (2026-10-07, before any price history was pulled)

Added after the investor asked whether RSI, KDJ, Bollinger bands, forward sales multiples or
momentum and similarity measures explain the damage better than run size. The primary metric,
triggers, periods and success threshold above are unchanged. The features below are
**exploratory secondary predictors**, each measured at the close before the trigger day
(`src/biotech_divedeep/signals/technical.py`, `src/biotech_divedeep/models/multiples.py`):

| Feature | Definition | Expected sign vs forward excess return |
|---|---|---|
| range_pos_252 | (close - 252-day low) / (252-day high - 252-day low) | Negative (motivated in-sample: rho -0.60 on 2026-10-06, so not independent evidence) |
| rsi14 | Wilder RSI(14) | Negative |
| kdj_j | KDJ(9) J line | Negative |
| boll_pct_b, boll_bw | Bollinger(20, 2) %b and bandwidth | Negative, negative |
| from_sma50, from_sma200 | Close / moving average - 1 | Negative |
| mom_12_1 | Return t-252 to t-21 | Negative within triggered names (crash odds, GSY 2019) |
| accel | Share of the 252-day log return earned in the last 63 days | Negative |
| sim_theme_63 | 63-day return correlation with the theme ETF or cluster | Negative (more theme flow, more unwind) |
| growth_gap | Latest yoy revenue growth minus the CAGR the price needs for a 0% return at 5x sales in 5 years | Positive (names whose growth covers the multiple hold up) |
| new_issuance | Follow-on, ATM or convertible within 63 days before the trigger | Negative (GSY issuance attribute) |

Reporting: one table of Spearman rho with bootstrap intervals for all features, Holm-adjusted;
no feature is promoted to a rule unless it holds in the out-of-sample period. The cross-layer
pooling trap seen on 2026-10-06 (both-layer rho inflated by layer membership) is avoided by
testing within cohorts only.

## Results (append after running)

| Run | Date | Variant | Primary metric | Notes |
|---|---|---|---|---|
