# Blueprint: Biotech & Life Sciences DiveDeep

Status: v0.6 (2026-10-09, listed universe, listing history, measured takeout hazard, case-study method; v0.5 2026-10-08, takeout database and Phase 2 gate; v0.4 2026-10-08; v0.3 2026-10-07; v0.2 2026-10-06; v0.1 2026-10-05). Owner: Guannan Shen. This is the north-star document.
Every session starts by re-reading it, and every material design change lands here
first (with an entry in `notes/decision_log.md`), then in code.

---

## 1. Mission

Build a research and decision system that helps a single investor hold a basket of
small and mid-cap biotech and life-science stocks that **beats XBI (total return) over
rolling windows of 6 months and longer**, after costs, with drawdowns the investor can
actually sit through.

Three jobs, in this order:

1. **Understand**: a point-in-time, source-cited record of what each company, asset
   and trial is doing (EDGAR, FDA, ClinicalTrials.gov, company news, prices).
2. **Insight**: where breakthroughs are most needed and which drug and tool types carry
   the largest economic potential; which business archetypes the market misprices.
3. **Predict**: probabilities for the events that move these stocks (readouts, FDA
   actions, financings, launch trajectories, takeouts), calibrated and backtested.

**Adjacent sleeve (added 2026-10-05, D-013).** The same framework applies to listed
companies outside biotech that share its economics: pre-revenue or early-revenue,
venture-like risk, a finite cash runway, and value unlocked by a regulatory or
customer gate (FAA certification, a defense program of record). First case: MRLN
(Merlin, AI autonomous flight). These names live in a capped adjacent sleeve; the
whole portfolio is still judged against XBI, and the sleeve also gets its own
diagnostic benchmark.

The wider motivation: AI-for-bio is compressing parts of discovery, and slow, expensive
drug development is the bottleneck between scientific progress and patients. Capital
that flows to the companies that actually remove that bottleneck is good for returns
and for medicine. The system should be able to tell real bottleneck removal from
narrative.

## 2. Objective function and success criteria

| Item | Definition |
|---|---|
| Benchmark | XBI total return (dividends reinvested). Diagnostics only: IBB, an equal-weight tools peer basket, and an equal-weight basket of the watchlist itself. |
| Primary metric | Rolling 126-trading-day (about 6 months) excess return vs XBI, measured weekly. Also 252-day. |
| Secondary | Information ratio, hit rate of rolling windows, max relative drawdown, left-tail frequency (positions losing more than 50%), turnover, slippage. |
| Validation standard | Out-of-sample, survivorship-free universe (delisted names included), point-in-time data, realistic costs. Then a 6-month paper portfolio before capital. |
| Phase gate to real money | Out-of-sample IR above 0.4 and positive excess return in at least 60% of rolling 6-month windows, plus a clean paper period. These thresholds are initial and live in `notes/decision_log.md`. |

Why XBI is a hard and specific benchmark: it is a modified equal-weight index of US
biotech, so it already tilts toward small and mid caps and carries their left tail
(failed readouts, dilution, cash-burn spirals). Beating it requires either selection
skill or systematic avoidance of that left tail. The system treats **left-tail
avoidance as alpha source number one** because it is the most testable and least
dependent on forecasting science.

## 3. Return hypotheses (each must be tested before it earns capital)

| ID | Hypothesis | Primary data | Test style |
|---|---|---|---|
| H1 | Left-tail avoidance: excluding names with short runway, live dilution machinery (effective shelf + ATM + recent run-up) or going-concern language beats XBI with lower drawdown. | EDGAR XBRL, S-3/424B, 10-Q text | Cross-sectional backtest, monthly rebalance |
| H2 | Launch-execution drift: after approval, the market misprices launch trajectories; early prescription/revenue metrics vs analog curves predict 2-4 quarter returns (REPL, IOVA type). | 10-Q product revenue (XBRL), FDA approvals, analogs | Event study + analog regression |
| H3 | Catalyst run-up: stocks with a dated binary catalyst drift up into the event; owning the run-up and cutting before the binary has positive expectancy. | ctgov dates, 8-K/PR guidance, PDUFA dates | Event study with exit rules |
| H4 | Specialist conviction: concentration and changes in dedicated biotech fund ownership (13F, 13D/G) predict forward excess return, especially in small caps. | EDGAR 13F/13D/13G | Quintile sort, lag-aware (45-day 13F delay) |
| H5 | Trend and regime: XBI regime (vs 200-day MA, rates), stock relative strength and volume confirmation (breakouts on above-average volume, accumulation vs distribution) improve timing of fundamental entries. | Prices and Trading Volume | Overlay test on H1-H4 |
| H6 | Quality inside biotech: profitable or near-profitable specialty pharma (HROW, ETON type) is underfollowed and compounds vs XBI. | XBRL fundamentals | Factor sort |
| H7 | Trial-registry signals: primary-completion slippage, enrollment cuts, endpoint edits and status changes on ClinicalTrials.gov lead price and outcome. | ctgov version history | Event study |
| H8 | Takeout likelihood: acquirers buy de-risked mechanisms (randomized Phase 2, pivotal or commercial data) and approved products in acquirer-gap areas; a company-quarter hazard model with stage, Phase 2 grade, size, activist, partner and gap-area features beats stage base rates, and a top-decile basket that passes H1 beats XBI. The takeout is a kicker on a standalone thesis, never the thesis. Measured 2021-2026 base hazard by size (D-040): micro 0.6%, small 4.8%, mid 8.1% a year. Setup features come from case-control studies of each deal (D-041). | Deal table `data/reference/biotech_takeouts.csv` (2005-2026), listing panel, case-study tables, EDGAR SC TO-T / SC 14D9 / DEFM14A, 13D, ctgov, FDA | Discrete-time hazard model (P5), time-split Brier; basket test (pre-registration pending; priors in `config/takeout_priors.yaml` until fitted); case-control likelihood ratios after 20 cases |
| H9 | AI-for-bio value capture: in the current AI cycle, data generators and tools with recurring consumables convert AI demand into revenue earlier than AI-native drug pipelines. | Segment revenue, customer disclosures | Panel study, slow (multi-year) |
| H10 | Attention and disclosure on X: official-channel posts lead press releases and filings; abnormal cashtag attention spikes in small caps predict short-term reversal. | X API, EDGAR timestamps | Lead-lag study; event study on attention z-scores |
| H11 | De-SPAC overhang: PIPE resale registrations, warrant exercisability and lockup expiries predict negative drift; the stock bottoms after supply clears, and names trading below residual cash (after senior claims) with controlled burn re-rate. | EDGAR 424B3/S-1, 8-K, prices | Event study around supply dates |
| H12 | Credible dissent: public criticism from qualified insiders (former regulators or reviewers, trial investigators, ex-employees, domain experts) in long-form media precedes negative revisions; a dissent flag improves left-tail avoidance (H1). | Podcasts, YouTube, FDA review documents, petitions | Case studies first (Humacyte), then event study on a labeled dissent set |
| H13 | Crowded-theme blow-off reversal: when a theme cohort's leaders finish a large run (close several times the 52-week low) and print a heavy-distribution day while the broad market is flat or up, they underperform XBI and run-matched controls over the next 1-6 months; names whose validation gap is closed hold up better. | Prices and volume, thematic ETF holdings, fit matrix | Event study, pre-registered (`notes/backtests/2026-10-06_H13_theme_blowoff_reversal.md`; amendment A1 adds range position, RSI, KDJ, Bollinger, momentum, acceleration, similarity and growth gap as exploratory predictors) |
| H14 | Giant read-through: announcements by large pharma or AI labs that name a listed small or mid-cap counterparty move it; those without financial terms reverse within about a month, those with disclosed terms drift. | M16 event log, counterparties' filings, prices | Event study split by terms disclosed (`docs/modules/pharma_ai_watch.md` section 4) |
| H15 | Management credibility: a low posterior hit rate on management's own guidance predicts negative drift after a fresh miss and a wider discount to guided value; a strong costly-signal record (pre-announced, quantified, dated sacrifices that paid off) predicts better 12-month excess return among commercial names. | 8-K and earnings-release guidance history, `data/reference/guidance_ledger.csv`, `costly_signal_ledger.csv` | Event study after guidance misses; cross-sectional sort on credibility (pre-registration pending) |
| H16 | Phase 2 quality drift: positive randomized Phase 2 readouts graded `clean` (gates: randomized control, pre-specified primary met, no new safety signal; graded items in `models/phase2.py`) earn positive excess return vs XBI from an entry after the first post-data financing, and beat `positive_not_clean` readouts. Shrinkage and assurance, not the point estimate, measure how much of the effect survives to Phase 3. | 8-K and press-release toplines, ctgov versions, 424B5, prices | Event study, pre-registered (`notes/backtests/2026-10-08_H16_phase2_quality_drift.md`) |

Hypotheses are ranked by data availability and testability. H1, H3, H5, H7 come
first because public data covers them well.

## 4. Universe and archetypes

The universe has two layers:

- **Watchlist** (`config/universe.yaml`): names the investor follows closely, each
  tagged with one or more archetypes and a thesis note.
- **Research universe**: all US-listed companies in biotech, pharma, diagnostics and
  life-science tools SIC codes (2834, 2835, 2836, 3826, 3841, 8731 and peers), including
  delisted names, used for backtests and screening. Built 2026-10-09 (D-038, D-039) from the
  Nasdaq screener in six layers (therapeutics, tools, services, diagnostics, software and data,
  medtech): 941 companies today in `data/reference/us_lifesci_universe.csv`, with XBI and IBB
  membership from the sponsor files when fetched locally. The point-in-time history since
  2021-01 comes from the git history of a public screener mirror (`scripts/listing_history.py`):
  monthly entries, exits, ticker changes and market caps, which give the hazard denominator and
  an audit of the deal table. Before 2021 the denominator still needs EDGAR (Q-032, Q-037).

Archetypes decide which model applies (details in `docs/framework/archetypes.md`):

| Code | Archetype | Examples | Valuation core |
|---|---|---|---|
| `clinical_binary` | Clinical-stage, value hinges on readouts | SLS, EDSA | Asset event tree, rNPV |
| `launch` | Recently approved, commercialization in progress | REPL, IOVA | Patient-cohort launch model vs analogs |
| `commercial_pharma` | Revenue-generating specialty or rare-disease pharma | HROW, ETON | Normalized FCF, product-level |
| `tools` | Instruments + consumables | PACB, ILMN, TXG, TWST, QSI | Active installed base x pull-through |
| `software` | Simulation and discovery software | SDGR, CERT | ACV, retention, FCF |
| `dx_data` | Diagnostics and clinical data | TEM, GRAL | Billable volume x ASP, coverage |
| `ai_platform` | AI-native discovery or automated labs | RXRX, DNA, SDGR (pipeline) | Platform validation chain + asset rNPV |
| `regulated_deeptech` | Adjacent sleeve: venture-like, runway-bound, regulatory or program gate | MRLN | Milestone event tree (certification, contracts) + runway + cash floor |

**Theme cohorts (added 2026-10-06, D-021).** A narrative can make names from different
archetypes trade as one block (the AI-bio data layer of 2026-10-06 joined tools,
diagnostics, software and gene editing). A theme event gets a case study in
`docs/research/`: a layer taxonomy by position in the value chain, a one-day or multi-day
cohort snapshot (`src/biotech_divedeep/signals/cohort.py`), and a **fit matrix** that
assigns each asset its archetype lens, the hypotheses that apply, the first missing link
in the validation chain, a falsifier and the next evidence node
(`data/reference/ai_bio_fit_matrix.csv` is the template). The archetype still decides the
valuation model; the theme only explains the correlated price action.

**Business quality (added 2026-10-08, D-030).** Before the price gate, every memo answers four questions in `docs/framework/business_quality.md`: what each product does and earns (product and revenue map), whether that is defensible (moat grade and trend), whether the way the company makes money is normal, good or great (business model grade), and whether the people can deliver (guidance credibility, capital allocation returns, alignment, costly-signal ledger). The archetype picks the valuation model; the business quality card decides how much of the modelled value to trust and which scenario weights to use.

Each company also carries a `sleeve`: `core` (biotech and life sciences) or `adjacent`
(see `docs/framework/adjacent_deeptech.md`).

## 5. System architecture

```
 Sources                Raw store          Normalized (silver)      Features (gold)      Decisions
 ------------------     ---------------    --------------------     ----------------     --------------
 SEC EDGAR        -->                      filings, xbrl_facts,     runway, dilution,    gates (evidence,
 openFDA / FDA    -->   immutable          holdings, events         catalyst calendar,   survival, price)
 ClinicalTrials   -->   snapshots    -->   trials, trial_versions   trial-change flags,  scenario values
 Company IR / PR  -->   (json, html,       approvals, labels,       ownership scores,    position sizing
 Prices / ETFs    -->    parquet)          news items, prices       RS / regime          weekly report
                                   \______ entity master (company / asset / trial / target / indication) ______/
```

Design rules:

1. **Event-centric.** Every source is normalized into `Event` records
   (`src/biotech_divedeep/core/events.py`). Catalyst calendars, alerts and backtests
   all read the same event stream.
2. **Point-in-time.** Each event carries `available_at` (earliest moment the
   information was public: EDGAR acceptance time, ctgov version post date, press
   release timestamp) and `observed_at` (when we fetched it). Backtests filter on
   `available_at` only; where it is uncertain, a conservative lag is added.
3. **Evidence classes.** Every extracted claim is tagged `fact`, `management_guidance`,
   `own_assumption` or `unverified`. Models may weight them differently; reports always
   show them.
4. **Raw first, immutable.** Fetched payloads are stored unmodified with a hash, so
   parsing can be re-run and audited. Storage: Parquet files + DuckDB, local-first.
5. **Entity master is the hard part.** Linking "RP1" to "vusolimogene oderparepvec",
   its BLA, its NCT trials and Replimune's CIK is curated in YAML, assisted by
   automatic suggestions, never silently guessed.
6. **Source priority** for conflicting facts: EDGAR filing > FDA record > ctgov record
   > company IR page > news aggregator.
7. **LLM-assisted extraction with citations.** Language models may extract structured
   fields (runway guidance, catalyst windows, launch metrics) from filings and press
   releases, but each field stores its source URL and quoted span, and stays
   `unverified` until checked.

## 6. Modules

| # | Module | Purpose | Design doc |
|---|---|---|---|
| M1 | EDGAR tracker | Filings feed, 8-K items, XBRL financials, shelf/ATM/424B dilution, Form 4, 13F/13D/13G | `docs/modules/edgar.md` |
| M2 | FDA tracker | Approvals, labels, CRLs, AdComs, safety (FAERS), manufacturing (483/warning letters), exclusivity | `docs/modules/fda.md` |
| M3 | ClinicalTrials.gov tracker | Trial cards, version diffs, date slippage, enrollment, endpoint changes | `docs/modules/clinicaltrials.md` |
| M4 | Company news tracker | IR press releases, events/presentations, conference calendar | `docs/modules/company_news.md` |
| M5 | Market & trend | Prices, XBI/IBB benchmarks, relative strength, regime, liquidity, theme-cohort features | `docs/modules/market_trend.md` |
| M6 | Catalyst calendar | Fuses M1-M4 into dated, sourced, confidence-scored catalysts | `docs/modules/catalyst_calendar.md` |
| M7 | Fundamentals, runway & dilution | Cash, burn, debt, share count, financing capacity, stress runway | `docs/modules/edgar.md` (section 5) |
| M8 | Thesis & valuation | One-page memo, business quality card, three scenarios, per-share value, evidence log | `docs/framework/investment_framework.md`, `docs/framework/business_quality.md` |
| M9 | Event prediction | Financing, FDA action, trial-delay, launch-curve, takeout models; Phase 2 quality grade and assurance; takeout case studies (case-control) | `docs/modules/event_prediction.md`, `docs/research/2026-10-08_takeout_database_and_phase2_gate.md`, `docs/framework/takeout_case_study.md` |
| M10 | Opportunity map | Unmet need x economics x crowding by indication and modality | `docs/modules/opportunity_map.md` |
| M11 | Portfolio & backtest | Point-in-time backtest vs XBI, sizing, risk budget, paper trading | `docs/modules/portfolio_backtest.md` |
| M12 | Reporting | Weekly review, alerts, memo rendering | `docs/modules/portfolio_backtest.md` (section 6) |
| M13 | Social / X tracker | Official-channel disclosures, expert and press accounts, cashtag attention | `docs/modules/social_x.md` |
| M14 | Government contracts & non-FDA regulators | USAspending, SAM.gov, DoD contract announcements, FAA records (adjacent sleeve) | `docs/framework/adjacent_deeptech.md` (section 3) |
| M15 | Long-form media & dissent tracker | Podcasts, YouTube, conference talks, investigative press; dissent register per company | `docs/modules/long_form_media.md` |
| M16 | Big pharma & AI-lab watch | Announcements by the trillion-dollar and large pharma, AI labs and compute vendors; counterparties, terms disclosed, M&A floors | `docs/modules/pharma_ai_watch.md` |

Package layout mirrors the modules:

```
src/biotech_divedeep/
  core/         events, evidence classes, entity master, storage helpers
  connectors/   edgar, fda, ctgov, company_news, market  (fetch + raw snapshot)
  signals/      runway, dilution, trial changes, ownership, trend
  models/       valuation, event prediction, opportunity map
  portfolio/    construction, risk budget, backtest
  reporting/    weekly review, memo rendering
```

## 7. Roadmap with phase gates

| Phase | Deliverable | Gate to next phase |
|---|---|---|
| 0. Blueprint (done in this commit) | Blueprint, framework, module designs, universe, notes, core contracts | Investor reviews and confirms direction and open questions (section 9) |
| 1. Data foundation | Entity master; EDGAR, ctgov, openFDA connectors with raw store and recorded test fixtures | Watchlist fully resolved (CIK, assets, NCT ids); daily refresh runs clean |
| 2. Watchlist intelligence | Catalyst calendar, runway/dilution panel, trial-change alerts, weekly report | Three full memos (PACB, SDGR, RXRX) built from system output |
| 3. Backtest harness | Survivorship-free universe, price store, H1/H3/H5/H7 tests | At least one hypothesis passes out-of-sample |
| 4. Prediction | Financing, FDA-action, trial-delay, launch-analog models with calibration | Brier score beats naive base rates out-of-sample |
| 5. Insight | Opportunity map; AI-for-bio validation scorecard | Map reproduces known history (e.g., GLP-1, ADC waves) when run point-in-time |
| 6. Paper portfolio | Live paper basket vs XBI with full logging | 6 months; criteria in section 2 |

Research order for memos (calibrating one model per archetype): PACB (tools), SDGR
(software + pipeline), RXRX (AI platform), then TEM/GRAL (dx), QSI/DNA (early product,
turnaround), REPL/IOVA (launch), SLS/EDSA (binary), HROW/ETON (commercial pharma).
Theme case studies run alongside the memos whenever a cohort moves as a block (first:
`docs/research/2026-10-06_ai_bio_theme_reversal.md`). Each theme study also screens the layers
that did *not* move with the theme (first: `docs/research/2026-10-07_launch_layer_screen.md`),
because a theme selloff can hide or create discounts elsewhere. A takeout and Phase 2 screen (`scripts/takeout_screen.py`, H8 and H16) runs alongside: every positive randomized Phase 2 in the research universe gets a scorecard, and takeout scores break ties inside baskets that already pass the gates. MRLN runs in parallel as the adjacent-sleeve pilot (`docs/memos/MRLN.md`) to test
whether the framework transfers outside biotech. This is a research order, not a buy
order.

## 8. Guardrails

- Research tool, not investment advice; no automated order routing.
- No look-ahead: every backtest join goes through `available_at`.
- No survivorship: delisted and acquired names stay in the research universe.
- Management timelines are `management_guidance` until they happen.
- "AI-enabled" never raises a probability of success by itself; the validation chain
  in the framework decides.
- Probabilities are ranges with sensitivity analysis; no false precision.
- Concentration is measured across shared targets, modalities, payers, funding
  climate, AI theme and clustered readout dates; ticker count is not diversification.

## 9. Open questions for the investor

Tracked with status in `notes/open_questions.md`. The ones that change the design:

1. Capital scale and minimum liquidity (sets the micro-cap floor and max position size).
2. Long-only, or are shorts, options or pair hedges (e.g., short XBI) allowed?
3. Data budget: the current FMP plan blocks batch endpoints. Are paid sources
   (FMP upgrade, Polygon, BioPharmCatalyst, Evaluate) on the table?
4. Where will connectors run? This cloud environment's network policy currently
   blocks sec.gov, api.fda.gov and clinicaltrials.gov.
5. Target number of holdings and rebalance cadence (weekly review assumed).
6. Maximum weight of the adjacent sleeve (15% proposed) and its diagnostic benchmark.
7. Budget for X API access, and the list of accounts worth following per company.
8. Price-history route for the local machine (Stooq script ready) and whether paid consensus
   estimates are worth buying for forward multiples (Q-017, Q-025).
