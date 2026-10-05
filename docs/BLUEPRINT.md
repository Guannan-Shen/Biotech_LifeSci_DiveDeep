# Blueprint: Biotech & Life Sciences DiveDeep

Status: v0.1 (2026-10-05). Owner: Guannan Shen. This is the north-star document.
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
| H5 | Trend and regime: XBI regime (vs 200-day MA, rates) and stock relative strength improve timing of fundamental entries. | Prices | Overlay test on H1-H4 |
| H6 | Quality inside biotech: profitable or near-profitable specialty pharma (HROW, ETON type) is underfollowed and compounds vs XBI. | XBRL fundamentals | Factor sort |
| H7 | Trial-registry signals: primary-completion slippage, enrollment cuts, endpoint edits and status changes on ClinicalTrials.gov lead price and outcome. | ctgov version history | Event study |
| H8 | Takeout likelihood: patent-cliff-driven M&A favors late-stage assets in acquirer-gap therapeutic areas; a takeout probability score adds return. | EDGAR, ctgov, FDA, M&A history | Classifier + portfolio tilt |
| H9 | AI-for-bio value capture: in the current AI cycle, data generators and tools with recurring consumables convert AI demand into revenue earlier than AI-native drug pipelines. | Segment revenue, customer disclosures | Panel study, slow (multi-year) |

Hypotheses are ranked by data availability and testability. H1, H3, H5, H7 come
first because public data covers them well.

## 4. Universe and archetypes

The universe has two layers:

- **Watchlist** (`config/universe.yaml`): names the investor follows closely, each
  tagged with one or more archetypes and a thesis note.
- **Research universe**: all US-listed companies in biotech, pharma, diagnostics and
  life-science tools SIC codes (2834, 2835, 2836, 3826, 3841, 8731 and peers), including
  delisted names, used for backtests and screening.

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
| M5 | Market & trend | Prices, XBI/IBB benchmarks, relative strength, regime, liquidity | `docs/modules/market_trend.md` |
| M6 | Catalyst calendar | Fuses M1-M4 into dated, sourced, confidence-scored catalysts | `docs/modules/catalyst_calendar.md` |
| M7 | Fundamentals, runway & dilution | Cash, burn, debt, share count, financing capacity, stress runway | `docs/modules/edgar.md` (section 5) |
| M8 | Thesis & valuation | One-page memo, three scenarios, per-share value, evidence log | `docs/framework/investment_framework.md` |
| M9 | Event prediction | Financing, FDA action, trial-delay, launch-curve, takeout models | `docs/modules/event_prediction.md` |
| M10 | Opportunity map | Unmet need x economics x crowding by indication and modality | `docs/modules/opportunity_map.md` |
| M11 | Portfolio & backtest | Point-in-time backtest vs XBI, sizing, risk budget, paper trading | `docs/modules/portfolio_backtest.md` |
| M12 | Reporting | Weekly review, alerts, memo rendering | `docs/modules/portfolio_backtest.md` (section 6) |

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
This is a research order, not a buy order.

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
