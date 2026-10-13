# Backtest Pre-Registration: H18 Insider and holder flow

Written 2026-10-12, before any event list or forward return for this test was computed. The price
panel (`data/silver/prices/mirror_daily_lifesci.csv.gz`, D-044) was rebuilt the same day; only
the QSI and NAUT series had been looked at before (H17 case study). Method code:
`src/biotech_divedeep/signals/supply.py` (part A) and `signals/insider.py`, `signals/fund_flow.py`
(part B) at the commit that adds this file. Any later change to a definition, threshold or window
is an amendment and is reported as one.

## Why two parts

The investor's prior: insider buying does not reliably lift a biotech stock, while block selling
after a big rally marks the stock as somewhat overvalued even if it does not fall at once. The
literature agrees on the first half only in part and is thin on the second:

- Purchases carry information on average (Jeng, Metrick and Zeckhauser 2003: more than 6% a year
  of abnormal return on purchases, none on sales), but most of it sits in *opportunistic* trades:
  insiders whose trade timing has no calendar pattern (Cohen, Malloy and Pomorski 2012: about 82 bp
  a month value-weighted; routine trades about zero).
- Sales are mostly noise (diversification, taxes, plans) unless the discretionary part is
  isolated (Form 4 footnotes on plans and tax withholding).
- In small biotech a large share of "insider purchases" are 10%-owner funds buying in the
  company's own financing (Form 4 code P at the offering price). That is a financing, not a
  signal, and it pollutes any screen that counts code P. We separate it.

The rally-and-block-sale claim has two rival explanations that a naive test cannot separate:
(1) the seller knows something (information), and (2) every big rally mean-reverts and sales just
happen to occur after rallies (H13, the run itself). So every test compares against **run-matched
controls**: stocks in the same run state on the same date that printed no supply event.

Part A needs no seller identity and runs today on the listing mirror. Part B adds identity (who
sold or bought, under a plan or not, fund skill) and runs on the local machine from the SEC
insider-transaction and 13F data sets (sec.gov does not resolve from the cloud sandbox).

## Part A: supply after a run (identity-free)

| Field | Entry |
|---|---|
| Hypothesis | H18-A (`docs/BLUEPRINT.md` section 3) |
| Question | After a life-science stock doubles, does a heavy-volume down day (a block sale, secondary, or distribution by holders) predict lower returns than the same run without one? |
| Universe | Point-in-time therapeutics, tools and diagnostics layers from the listing mirror (`connectors/listings.py`), day -1 market cap USD 50M to 20B, close at least USD 1. Delisted and acquired names kept: after the last snapshot the position earns the benchmark (abnormal return 0), so a takeout keeps its last price. Symbol series are split at gaps of more than 10 sessions (ticker reuse). |
| Run state on day t | R126 = close(t-1) / close(t-127) >= 2.0 and close(t-1) >= 0.75 x max close over [t-127, t-1] (still near the top). |
| Supply event | A day t in run state with stock return <= -3%, abnormal return vs benchmark <= -3%, and volume >= 3x the mean over [-60, -11]. One event per symbol per 60 sessions (the first one counts). |
| Controls | Up to 3 symbols in run state on the same date, same cap band (50-300M, 300M-2B, 2B-20B), no supply event in [t-20, t], nearest log R126. Controls use only information up to day t. |
| Entry and windows | Measure from the close of day +1. BHAR over [+2, +k], k in {20, 60, 126, 252}, vs `EW_LIFESCI_200M`. Matched difference = event BHAR minus the mean of its controls' BHAR over the same dates. |
| Period | In-sample: events 2021-06 to 2023-12. Out-of-sample: 2024-01 to 2025-09. Hold-out: 2025-10 onward (short horizons only, read after the OOS run). |
| Costs | The long-only use is an exit: sell the name on day +1 instead of holding it. The exit is worth the matched difference less a 150 bp (above USD 300M) or 300 bp (below) round trip; sensitivity at double. |
| Primary metric | Mean matched difference at k = 126, equal-weighted per event, 90% interval from a calendar-month block bootstrap (2,000 draws). |
| Success threshold | Out of sample: mean matched difference at k = 126 at or below -5 points, interval excludes 0, and the exit beats holding after costs. |
| Secondary predictions (Holm-adjusted) | A2 slow bleed: the k = 20 matched difference is less than half the k = 126 one in absolute value (the "not immediately" part of the investor's claim). A3 financing follows: implied share count (market cap / close) rises at least 10% within 120 sessions more often after events than for controls. A4 run alone: run-state controls themselves have negative BHAR at 126 (H13 mean reversion, context only). A5 drawdown: share of events with a drawdown of at least 40% from the day +1 close within 252 sessions, events vs controls. |
| Variants planned | Run threshold R126 in {1.75, 2.0, 3.0}; volume multiple in {2.5, 3, 4}; return threshold in {-3%, -6%}, applied to both the raw and the abnormal return: 18 cells on the primary metric, Holm-adjusted. A2 to A5 at the base cell only. |
| Known risks | The mirror holds closes only (no intraday range), so a supply day is approximated by a down close on heavy volume; it mixes holder blocks, company offerings and plain distribution, which part B separates. About 1% of snapshots have a stale field (windows use close-to-close returns, which telescope). Market caps lag filings, so A3 undercounts and dates late. 2021-2022 is a biotech bear market in which most runs reversed; controls absorb the level, not necessarily the interaction. |

## Part B: who traded (identity, local machine)

Data: the SEC **Insider Transactions Data Sets**
(quarterly ZIPs of Forms 3, 4, 5 as TSV tables) and **Form 13F Data Sets**, parsed by
`connectors/sec_ownership.py`; Form 144 notices from EDGAR (electronic since 2023). `available_at`
is the filing date (Form 4, 144) or the 13F filing date, never the transaction date or quarter end.

| ID | Prediction | Event definition | Metric and threshold (out of sample) |
|---|---|---|---|
| B1 (primary) | Discretionary sales by officers, directors or 10% owners in run state underperform run-matched controls. | Code S, not flagged as a 10b5-1 plan, not F (tax). Lines cluster per issuer until 14 calendar days pass without a filing; the event fires on the filing date at which the cluster reaches USD 250k and one seller has sold at least 5% of the holding. Run state as in part A on the first session on or after that date. | Matched difference at 126 at or below -5 points, interval excludes 0. |
| B2 | Opportunistic open-market purchases by officers and directors earn positive BHAR; routine ones and offering participation do not. | Code P outside any financing window (no 424B or 8-K item 3.02 within 5 sessions, price not equal to the offering price); routine = the insider traded in the same calendar month in each of the 3 prior years (Cohen, Malloy and Pomorski 2012). | Opportunistic BHAR[+2,+126] at least +5 points; opportunistic minus routine at least +5. |
| B3 | Cluster buys (3 or more distinct insiders in 30 days, opportunistic) beat single buys. | As B2. | Difference at 126 at least +5 points. |
| B4 | Form 144 notices by 10% owners in run state lead the Form 4 sale and carry the same sign. | Form 144, approximate sale date and size. | Median lead at least 2 sessions; matched difference at 126 at or below -3 points. |
| B5 | Fund skill: new positions by specialist funds in the top tercile of point-in-time skill beat those of the bottom tercile. | Skill = shrunk mean of the 2-quarter BHAR of each fund's prior new positions, using only quarters fully realized before the 13F filing date (`signals/fund_flow.py`). | Top minus bottom BHAR over the 2 quarters after the filing date at least +3 points. |
| B6 | Specialist exits and trims of at least 50% after a run precede equity financing (424B5 within 90 days) and negative drift (H4 x H1). | 13F change against the prior quarter, run state at the filing date. | Financing rate at least 1.5x controls; matched difference at 126 at or below -5 points. |

Variants for part B are fixed now: sale size floor {USD 250k, USD 1M}; plan flag {exclude, include};
stake floor {5%, 20%};
horizons {60, 126, 252}. Counts toward the Holm adjustment with part A.

## What would change the investor's rule

- If A1 and B1 pass but A2 fails (the drop is immediate), the rule becomes "sell on the print"
  rather than "trim over the next quarter".
- If A1 fails and A4 holds, the run alone explains it and the block sale adds nothing: the exit rule
  then belongs to H13 (stretch), not to flow.
- If B2 fails for opportunistic buys, insider buying leaves the entry checklist entirely.

## Amendments

A0 (2026-10-12, before any Form 4 data was read): the B1 size rule was written as "USD 250k or
1% of the holding", which nearly every sale passes; it now reads "USD 250k and one seller at
least 5% of the holding" with a 20% variant, and the clustering rule matches `signals/insider.py`.

A1 (2026-10-12, data correction after the first in-sample run, part A): the mirror's `lastsale`
is not split-adjusted while its one-day return is, so reverse splits read as 14x to 20x runs.
Closes and volumes are now back-adjusted by `signals.supply.split_adjust` (585 split days). No
threshold, window or metric changed. Both runs are reported below.

## Results (append after running)

| Run | Date | Variant | Primary metric | Notes |
|---|---|---|---|---|
| A-IS-1 | 2026-10-12 | Part A base cell, in sample, raw closes | Matched diff at 126: -12.6% (90%: -18.7% to -6.0%), n 157 | Superseded by A-IS-2: reverse splits counted as runs |
| A-IS-2 | 2026-10-12 | Part A base cell, in sample, split-adjusted | Matched diff at 126: **-12.2%** (90%: -19.3% to -6.0%; bootstrap p < 0.001; Holm over 18 cells < 0.01), n 141 events in 21 months; median -19.5% | k = 20: +0.9%, 60: -2.1%, 252: -24.1% (-36.2% to -13.6%). A2 slow bleed holds; A3 share count +10% in 48% of events vs 38% of controls; A4 controls +1.4% at 126; A5 62% of events drew down 40% or more. Micro -20.2%, small -6.8%, mid -10.2% |
| A-IS-2v | 2026-10-12 | Part A, 18 cells, in sample | Base cell is the only one significant on the mean after Holm; all 18 medians and trimmed means negative (-4% to -20%) | Means at a 1.75x run are positive (+1% to +2%), driven by a right tail of later winners (ALPN, APLT, ARDX, CBAY). Table in `docs/research/2026-10-12_insider_holder_flow.md` |

Out-of-sample (2024-01 to 2025-09) not run. Part B not run (needs SEC data on the local machine).
