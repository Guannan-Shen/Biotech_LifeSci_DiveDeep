# Case Study: The AI-Bio Theme Reversal of 2026-10-06

Date: 2026-10-06 (written after the close). Status: first pass, one-day data. Hypothesis
links: H9 (AI-for-bio value capture), H5 (trend, regime, volume), H4 (ownership), new H13
(crowded-theme blow-off reversal, pre-registered in
`notes/backtests/2026-10-06_H13_theme_blowoff_reversal.md`).

Data: `data/reference/ai_bio_cohort_snapshot_2026-10-06.csv` (FMP company profiles, 36
symbols, fetched 2026-10-06 23:46 UTC, after the close) and
`data/reference/ai_bio_fit_matrix.csv` (one row per asset). Every table in sections 3 and 4
is reproduced by `python scripts/cohort_snapshot.py`. Research note, not investment advice.

Evidence classes follow `AGENTS.md`: **F** fact, **G** management guidance, **A** own
assumption, **U** unverified (most press and aggregator items below are U until a filing
or company release confirms them).

---

## 0. Summary

1. **The investor's label needs one refinement.** The names that broke hardest were the
   *suppliers of data to AI models* (TWST, TXG, DNA: median -17%, 3x to 9x normal volume)
   and AI-branded clinical genomics (TEM, GRAL). The AI drug designers fell less (RXRX
   -3.1%, ABCL -4.6%). The market was trading our own H9 ("data generators capture AI-bio
   value first") before H9 had evidence. Call the set the **AI-bio data layer**.
2. **It was a two-day round trip.** Monday 10-05 was a melt-up on sell-side target hikes
   (DNA +21%, RXRX +16%, PACB +13%, TEM +9%, ILMN +7.6%). Tuesday 10-06 erased it:
   TWST printed a new 52-week high of 219.71 intraday and closed at 166.97, 24% below it.
3. **The selloff was sector-specific.** The S&P 500 and Nasdaq closed at records (SPY
   +0.5%, NVDA flat) while healthcare was the only falling sector. ARKG fell 8.8% on 3.8x
   volume; XBI fell 3.4%. Money left the AI-bio trade and stayed in megacap AI.
4. **Three forces stacked:** a narrative peak (Lilly TuneLab deals, Anthropic's wet lab,
   "genomics is AI infrastructure" target hikes), flows (ARK's 21st straight session
   selling TWST, insider Form 144s, call-option chasing in DNA) and macro (10-year
   Treasury near 5.25%, the highest since 2007, after a September Fed hike).
5. **Inside the cohort, run size predicted the damage.** How far a stock stood above its
   52-week low ranked with the day's loss (Spearman -0.45, n = 23). Beta (-0.19) and the
   composite crowding score fixed in advance (-0.10) did much worse. One day and 23 names
   cannot carry inference, so this becomes a pre-registered test (H13).
6. **Plan:** treat 10-06 as a *distribution* signal for the epicenter and an *evidence
   test* for everyone else. The next three to six weeks hold the deciding data: FOMC on
   10-28 and Q3 reports from late October to mid November. Decide per name with the fit
   matrix (section 5) and the pre-commitment rules (section 7), and keep the 52-week high
   out of the calculation.

---

## 1. Timeline

| Date | Event | Class | Source |
|---|---|---|---|
| 2026-09-15/16 | Ginkgo Datapoints (DNA) and Twist (TWST) join Lilly TuneLab as wet-lab data suppliers (ADME, antibody developability, antibody characterization) | F | [Ginkgo release](https://s28.q4cdn.com/823357996/files/doc_news/2026/Sep/16/Ginkgo-Datapoints-x-TuneLab-Announcement.pdf), [Twist release](https://investors.twistbioscience.com/news-releases/news-release-details/twist-bioscience-joins-lilly-tunelab-advance-antibody-drug) |
| 2026-09-16 | FOMC raises the policy rate 25 bp to 3.75-4.00% | U | [fedratecalc](https://fedratecalc.com/fomc-meeting-schedule/october-2026/) |
| 2026-09-21 | Tempus and Recursion extend their data license through November 2029 | F | [Tempus release](https://www.tempus.com/news/pr/tempus-and-recursion-extend-existing-data-license-agreement-and-enter-new-license-agreement-for-recursions-rna-foundation-model/) |
| 2026-09-23 | Anthropic announces a life-sciences group and wet lab; its agents found "ART", an enzyme system with CRISPR-like repeats, function unknown, preprint not peer reviewed. Gene-editing stocks fall (CRSP -5.5%, BEAM -6.0%, PRME -11.6%) | U | [The Scientist](https://www.the-scientist.com/anthropic-s-secretive-ai-powered-wet-lab-breaks-cover-and-makes-first-discovery-75037), [Seeking Alpha](https://seekingalpha.com/news/4646229-gene-editing-stocks-fall-anthropic-crispr-like-discovery) |
| 2026-09-23 | Flash composite PMI 58.4 (highest since July 2021); 10-year Treasury tops 5% for the first time since 2007 | U | [report](https://coinalertnews.com/news/2026/09/23/treasury-yield-tops-five-percent) |
| 2026-09-23 | FDA advisory panel on GRAIL's Galleri: 10-0 safety, 6-4 effectiveness, 7-2 (1 abstain) benefit-risk; final decision "in the coming months" | U | [ASCO Post](https://ascopost.com/news/september-2026/fda-advisory-committee-votes-in-favor-of-approval-of-multi-cancer-early-detection-test/) |
| 2026-09-29 | Iovance raises 2026 revenue guidance to USD 410-420M; stock +30% | G | [Benzinga](https://www.benzinga.com/markets/guidance/26/09/62059046/iovance-biotherapeutics-amtagvi-demand-drives-2026-revenue-guidance-bump-stock-soars) |
| 2026-10-02 | 10x Genomics starts Atera shipments, launches Sentira software | U | [report](https://www.timothysykes.com/news/10xgenomicsinc-txg-news-2026_10_02/) |
| 2026-10-05 (Mon) | Melt-up. RBC lifts ILMN target 230 to 310; Leerink lifts TWST to 190, Guggenheim 107 to 212; DNA +21% on heavy call volume; TEM +9.0% | U | [ILMN](https://www.ad-hoc-news.de/boerse/news/corporate-news/rbc-raises-target-for-illumina-stock-to-usd-310/70233455), [TWST](https://stockstotrade.com/news/twist-bioscience-corporation-twst-news-2026_10_05/), [DNA](https://www.gurufocus.com/news/9110384/ginkgo-bioworks-dna-surges-21-on-heavy-options-activity-following-lilly-tunelab-partnership), [TEM](https://www.tradingkey.com/news/market-movers/262200753-market-movers-tem-20261005) |
| 2026-10-06 (Tue) | S&P 500 and Nasdaq at records; healthcare the only falling sector; 48 of 428 Russell 2000 healthcare names up | U | [Yahoo live](https://finance.yahoo.com/markets/live/stock-market-today-tuesday-october-6-dow-sp-500-nasdaq-080526166.html), [Motley Fool](https://www.fool.com/coverage/stock-market-today/2026/10/06/stock-market-midday-oct-6-s-and-p-500-sets-new-high-nuclear-stocks-surge/) |
| 2026-10-06 | TWST: intraday high 219.71, close 166.97; ARK's 21st consecutive session of TWST sales (about USD 18M across ARKK and ARKG); CEO Form 144 for 4,548 shares; two other insiders sold on 10-02 | U | [Investing.com](https://www.investing.com/news/stock-market-news/why-is-twist-bioscience-stock-plunging-today-93CH-4935087), [Defense World](https://www.defenseworld.net/2026/10/06/twist-bioscience-nasdaqtwst-stock-falls-9-7-following-insider-selling.html) |
| 2026-10-06 | Cohort closes (36 symbols) | F | FMP profiles; prior closes cross-checked for TXG, ILMN, TEM and XBI against [heygotrade](https://www.heygotrade.com/en/us-stock/txg/) and the reports above |

Ahead: FOMC 2026-10-27/28 (hike odds quoted between about 36% and 73% by different
sources, U); Guardant Q3 on 10-29 (U); Schrodinger Q3 on 11-05 (U); Recursion REC-4881
Phase 2 data in November (G); GRAIL PMA decision undated (G).

---

## 2. Locating the set precisely

The investor's list (TWST, ILMN, GRAL, TEM, NTRA, GH, TXG, IOVA, ADPT, DNA) mixes four
businesses that the market grouped under one AI story. Splitting them by **where they sit
in the AI-bio value chain** shows where the trade was concentrated.

| Layer | What it sells | Names in the snapshot | AI link |
|---|---|---|---|
| `data_generator` | Wet-lab measurements and instruments that make training data | TWST, TXG, DNA, ILMN, PACB, QSI | Suppliers to AI models (TuneLab), "sequencing as AI infrastructure" |
| `clinical_genomics_dx` | Clinical tests; some license de-identified data | TEM, GRAL, NTRA, GH, ADPT, CDNA, VCYT | TEM licenses data; the rest carry an AI label on a testing business |
| `ai_drug_design` | Software, platforms and pipelines built on models | SDGR, ABSI, CERT, ABCL, RXRX | The literal "AI drug design" group |
| `genomic_medicine` | Gene-editing therapeutics | CRSP, BEAM, NTLA, PRME | Exposed to the Anthropic ART headline as a substitution story |
| `launch` | An approved therapy in commercial ramp | IOVA | None; a launch-execution story (H2) |

Controls: TMO, DHR, BRKR (large tools), LLY, MRNA, NVDA, and the ETFs SPY, QQQ, IWM, XBI,
IBB, ARKG, ARKK.

**Core cohort for follow-up (the epicenter):** TWST, TXG, DNA, TEM, GRAL, plus ILMN as the
profitable reference. **Extended cohort:** the rest of the dx layer and the AI-design
layer. IOVA leaves the theme and returns to the `launch` playbook.

---

## 3. The cohort as a whole

### 3.1 By layer (2026-10-06)

| Layer | n | Median day | $-vol weighted | Share down | Median RVOL | Median close / 52w low | Median from 52w high |
|---|---|---|---|---|---|---|---|
| data_generator | 6 | -12.0% | -14.0% | 100% | 3.7 | 2.8x | -22.8% |
| clinical_genomics_dx | 7 | -8.8% | -9.9% | 100% | 1.7 | 2.4x | -12.5% |
| launch | 1 | -8.4% | -8.4% | 100% | 1.1 | 7.4x | -15.3% |
| ai_drug_design | 5 | -7.9% | -6.1% | 100% | 1.4 | 2.6x | -14.8% |
| genomic_medicine | 4 | -2.3% | -2.5% | 75% | 1.7 | 1.4x | -41.8% |

Benchmarks the same day: ARKG -8.8% (RVOL 3.8), MRNA -7.8%, BRKR -5.3%, XBI -3.4%,
TMO -3.0%, DHR -2.6%, ARKK -2.5%, IBB -2.3%, IWM -0.7%, NVDA +0.1%, QQQ +0.5%, SPY +0.5%,
LLY +1.3%. RVOL is volume over the vendor's average volume; the averaging window is not
documented, so treat the level as approximate and the ranking as the signal.

### 3.2 Two-day path for watchlist names

Pre-spike closes come from the `config/universe.yaml` snapshot, which was fetched on
2026-10-05 before the open and therefore holds the 2026-10-02 close (D-022).

| Ticker | Mon 10-05 | Tue 10-06 | Net two days |
|---|---|---|---|
| DNA | +21.3% | -17.2% | +0.5% |
| RXRX | +16.0% | -3.1% | +12.4% |
| PACB | +13.0% | -5.9% | +6.3% |
| TEM | +9.0% | -13.8% | -6.1% |
| TWST | +8.7% | -18.6% | -11.5% |
| ILMN | +7.6% | -6.9% | +0.2% |
| SDGR | +7.6% | -11.3% | -4.7% |
| CERT | +7.6% | -7.9% | -1.0% |
| GRAL | +7.6% | -10.9% | -4.2% |
| TXG | +4.5% | -17.5% | -13.7% |
| IOVA | -0.5% | -8.4% | -8.8% |
| QSI | -17.4% | -4.7% | -21.3% |

QSI's Monday drop has no explanation in the sources searched; check for a financing or
filing before using it (Q-019). RXRX kept most of Monday's gain on 3.4x volume, which
reads as supply absorbed by buyers.

### 3.3 Mechanics: three stacked forces

**Narrative.** Three real events built the story within three weeks: Lilly paying outside
labs to generate data for TuneLab, Tempus extending a paid data license, and an AI lab
opening its own wet lab. Each is a legitimate H9 signal. The sell-side then wrote the
story into price targets on 10-05 ("valuation re-rating across the life sciences
ecosystem", "infrastructure for AI"). Target hikes that arrive *after* a 5x to 7x move follow
price, so they carry little new information.

A second reading of the Anthropic news cuts the other way: an AI lab that runs its own
wet lab is a customer of reagents and instruments, and also a possible competitor to
outsourced data generation. The market priced only the first reading.

**Flows.** Thematic money was leaving while the price peaked. ARK had sold TWST for 21
sessions; ARKG traded 3.8x normal volume; insiders filed sales into the spike; DNA's
Monday move came from call buying (9x normal volume on Tuesday). Thematic ETF and options
flow sit at the far end from the specialist conviction that H4 measures: fast,
momentum-driven and quick to reverse.

**Macro.** Most of these companies burn cash or earn little now and are valued on
profits years out. With the 10-year near 5.25% and the Fed hiking, those distant profits
are worth less each week rates stay high. Megacap AI, which earns cash today, kept rising
the same day. That split explains why the S&P 500 set a record while AI-bio broke.

### 3.4 What predicted the damage inside the cohort

Spearman rank correlation of each feature with the 10-06 return (23 cohort stocks):

| Feature | rho |
|---|---|
| Close / 52-week low | -0.45 |
| Market cap | -0.34 |
| Range multiple (52w high / low) | -0.23 |
| Relative volume | -0.22 |
| Beta | -0.19 |
| Crowding score (run size, beta, small size; fixed before the run) | -0.10 |

Readings, all `A` and hypothesis-generating only:

- The bigger and more intact the run, the harder the fall. TWST and TXG stood about 7x
  above their 52-week lows.
- Size worked against the prior. The epicenter sat in USD 5-15B names (TWST, TXG, TEM,
  GRAL), the institutional momentum leaders, so the "small floats amplify flows" term in
  the crowding score pointed the wrong way. The score stays unchanged for H13 so it is
  tested out of sample with no refit to this day.
- Leak to note: a 52-week high set intraday on the same day (TWST) enters the range
  multiple. Close / 52-week low has no such leak.

---

## 4. The names individually

Columns: first gap = the first link of the framework's AI validation chain (technical
performance, customer outcome, paid demand, margin and cash, per-share value) that lacks
evidence. Lens = the archetype model and hypotheses that fit. Full rows, falsifiers and
evidence classes are in `data/reference/ai_bio_fit_matrix.csv`.

| Ticker | 10-06 | RVOL | Close / low | AI link | First gap | Lens |
|---|---|---|---|---|---|---|
| TWST | -18.6% | 4.5 | 7.2x | TuneLab supplier (F); revenue size undisclosed | Paid demand | tools; H9, H13, H5, H4 |
| TXG | -17.5% | 2.9 | 7.2x | Narrative ("training data") | Paid demand (Atera pull-through) | tools; H9, H13 |
| DNA | -17.2% | 9.0 | 2.3x | TuneLab supplier (F); core revenue shrinking (U) | Paid demand at scale | ai_platform; H1, H9, H13 |
| TEM | -13.8% | 2.4 | 1.8x | Paid data licensing (F) | Margin and cash ex investment gains | dx_data; H9, H13 |
| SDGR | -11.3% | 3.3 | 2.6x | Software revenue (F) | Margin and cash | software + pipeline; H9, H13 |
| ABSI | -10.9% | 1.3 | 4.6x | Narrative until human data | Customer or clinical outcome | ai_platform; H3, H9 |
| GRAL | -10.9% | 2.3 | 3.3x | Narrative; value hinges on FDA and payers | Paid demand (coverage) | dx_data; H3, H13, H12 |
| ADPT | -9.9% | 0.9 | 2.2x | Partnership; core is MRD testing | Margin and cash (FCF breakeven target) | dx_data; H2, H6 |
| GH | -8.8% | 1.4 | 2.8x | Label only | Margin and cash | dx_data; H6, H5 |
| CDNA | -8.7% | 2.2 | 4.6x | None | Margin and cash | dx_data; H6, H13 |
| IOVA | -8.4% | 1.1 | 7.4x | None | Margin and cash | launch; H2, H5 |
| CERT | -7.9% | 1.1 | 2.1x | Software revenue | Paid demand | software; H6, H9 |
| ILMN | -6.9% | 1.8 | 3.1x | Narrative on a profitable base | Per-share value (price already high) | tools; H9, H5 |
| VCYT | -6.3% | 1.3 | 1.5x | None | None major | dx_data; H6 |
| PACB | -5.9% | 5.8 | 2.5x | Narrative | Paid demand | tools; H1, H9 |
| NTRA | -5.9% | 1.7 | 2.4x | Label only | None major | dx_data; H6, H5 |
| CRSP | -5.8% | 1.6 | 1.2x | Substitution headline | Paid demand (Casgevy ramp) | launch/binary; H2, H3 |
| QSI | -4.7% | 1.9 | 1.8x | Narrative | Technical (Proteus delayed to Q2 2027, G) | tools; H1, H11 |
| ABCL | -4.6% | 1.4 | 4.8x | Partnership | Clinical outcome | ai_platform; H3, H9 |
| RXRX | -3.1% | 3.4 | 1.7x | Paid partnerships | Clinical outcome (REC-4881, Nov) | ai_platform; H3, H9, H12 |
| NTLA | -3.0% | 1.7 | 1.6x | Substitution headline | Clinical outcome | clinical_binary; H3, H1 |
| BEAM | -1.7% | 1.2 | 1.2x | Substitution headline | Clinical outcome | clinical_binary; H3, H1 |
| PRME | +9.0% | 3.7 | 3.2x | Substitution headline | Clinical outcome; runway | clinical_binary; H1, H3 |

Notes on the core and on the outliers:

- **TWST.** The TuneLab agreement is real and the business has operating leverage, but
  the size of AI-linked revenue is undisclosed. At 7x off the low, the price assumes the
  paid-demand link is already proven. The intraday reversal from a new high on 4.5x
  volume, with the largest thematic holder selling for a month, is the textbook
  distribution pattern H13 describes. Next node: fiscal Q4 results (fiscal year ends
  September 30; report date U).
- **TXG.** The Atera launch is a real product cycle. The question is placements and
  consumable pull-through per active system, which no source quantifies yet. Monday's
  move was the smallest (+4.5%) and Tuesday's one of the largest, so holders sold into the
  first strength.
- **DNA.** Highest RVOL in the cohort (9.0) on a USD 0.8B company: speculative flow on top
  of a shrinking core (Q2 Cell Engineering revenue about USD 20M vs 39M a year earlier, U,
  framework section 7). H1 (runway, dilution) is the governing lens; H9 is secondary.
- **TEM.** The one name in the epicenter with paid, recurring data revenue. Its gap is
  profitability that excludes unrealized investment gains. Beta 3.7 makes it the most
  rate-sensitive name in the set.
- **GRAL.** A regulatory binary with a positive panel and a split effectiveness vote
  (6-4). Approval, label scope and Medicare coverage are three separate nodes. H3 (run-up
  into a dated catalyst) applies once the FDA date is known; today there is no date.
- **ILMN.** Profitable incumbent and the least narrative-dependent of the core. It fell
  about two points less than ARKG; it serves as the cohort's profitable reference.
- **NTRA, GH, ADPT, VCYT.** Diagnostics businesses with reported growth (NTRA Q2
  revenue +38% to USD 753M and 2026 guidance USD 2.85-2.91B, G) and an AI label that adds
  little. They fell with beta, on normal volume (ADPT RVOL 0.9). H6 (quality inside
  biotech) is the better lens; these are the names where a theme selloff may hand over
  quality at a lower price, subject to the price gate.
- **AI drug designers.** RXRX and ABCL fell least. Their value hinges on clinical data,
  which no AI-data narrative changes, so the theme money was never concentrated here.
  SDGR is the exception (-11.3%, RVOL 3.3): it had risen about 64% from 19.85 on 08-19
  (U) to 32.60 on 10-05 and behaved like the data layer.
- **Gene editing.** Relative winners on Tuesday (+3 to +18 points vs ARKG) after taking
  their AI hit on 09-23. PRME rose 9% on 3.7x volume with no identified news (U).
- **IOVA.** No AI exposure. It fell 8.4% on normal volume one week after a 30% guidance
  jump. It belongs under the `launch` playbook (H2): the test is Q3 revenue against the
  raised USD 410-420M run rate.

---

## 5. Which framework fits which asset

| Framework or hypothesis | Fits best | Why |
|---|---|---|
| H9 AI value capture (fundamental) | TEM, TWST, DNA, SDGR | They report or will report revenue that can be tied to AI customers; track it quarterly |
| H13 crowded-theme reversal (price) | TWST, TXG, TEM, GRAL, SDGR, CDNA, DNA | Large run, heavy-distribution day, flow selling |
| H1 left-tail avoidance | DNA, PACB, QSI, PRME, BEAM, NTLA | Cash burn and dilution risk dominate the outcome |
| H6 quality inside biotech | NTRA, GH, VCYT, ADPT, CERT | Revenue at scale, path to FCF; the AI label is incidental |
| H2 launch drift | IOVA, ADPT, CRSP (Casgevy) | Value set by the shape of the ramp vs analogs |
| H3 catalyst run-up | GRAL (PMA), RXRX (REC-4881), ABSI, ABCL | Dated binary or regulatory node |
| H5 trend and volume | Every name, as the timing overlay | Distribution days, MA breaks and volume confirmation decide entry timing |
| H4 ownership | TWST, TEM (ARK flows); later all via 13F | Thematic-fund exits as a negative signal |

The finding worth keeping: **the same AI story maps onto four different value engines**.
A rule that buys or sells "AI-bio" as one block would ignore the variable that decides
each name's outcome.

---

## 6. Scenarios for the epicenter (3 to 6 months)

Probabilities are `A`, written before any H13 evidence, as ranges.

| Scenario | Probability | What it looks like | Signposts that favor it |
|---|---|---|---|
| A. Shakeout, trend resumes | 20-30% | Core names reclaim the 10-06 highs within about 3 months | Q3 reports show AI-attributed revenue or raised guides **and** stocks rise on them; 10-year back under 5%; ARK selling stops; volume dries up on pullbacks |
| B. Topping range, dispersion | 40-50% | Cohort ranges 15-35% below highs; names with proof hold, narrative names drift lower | Mixed Q3s; stocks fall on good news for some names and hold for others; rates flat |
| C. Regime unwind | 25-35% | Core falls 40%+ from highs within 6 months, as ARKG did after February 2021 (U, needs price data) | FOMC hikes on 10-28 or 10-year above 5.5%; four or more heavy-distribution days in the core over the next 25 sessions; secondary offerings into the decline; good Q3 news sold |

The most informative single observation: **how the stocks react to their own Q3
reports.** Good news sold is the classic late-stage sign (scenario C); good news bought
argues for A.

---

## 7. Decision plan

### 7.1 Instinct traps and the process that replaces each

| Fast instinct | Why it misleads | Process |
|---|---|---|
| "It is 24% off the high, so it is cheap" | The 52-week high was set by flows on a peak day and carries no information about value | Price gate: three scenario values per share (framework section 3); compare to those |
| "Analysts just raised targets" | Target hikes after a 5x run follow price | Count only new facts: revenue, guidance, contracts, data |
| "AI news, so buy the group" | The group holds four different value engines | Use the fit matrix; act per name |
| "Sell everything after a -18% day" | One day is a weak predictor of a single name's next six months | Pre-set reduce rules (7.2), applied mechanically |
| "The dip will be bought, it always was" | Base rates after parabolic runs plus key reversals are still unmeasured for this cohort | Wait for H13 evidence; until then size as if scenario C is live |
| Ignoring who is selling | ARK, insiders and option holders supplied the stock | Track flows weekly (ARK daily trades, Form 4/144, 13F) |

### 7.2 Holders of the epicenter names (process rules for the investor to calibrate)

1. **Size first, view second.** A position that grew 5x to 7x is probably above its risk
   budget. Trimming to budget is risk management and needs no forecast (framework
   section 9: cap = acceptable loss / stress drawdown; use a 60-70% stress drawdown for
   this cohort, an `A` taken from the size of prior thematic unwinds).
2. **A give-back line.** Decide in advance the share of the open gain you accept to give
   back. Example: with a 30% give-back from the peak, TWST's line is
   0.70 x 219.71 = 153.80. Write the number down before the next session.
3. **Reduce on confirmation.** Under the framework's trend overlay
   (section 10) reduce after two weekly closes below the 200-day average. Parabolic names
   sit far above their 200-day lines, so add a faster rule for this cohort: reduce a
   further step on a second heavy-distribution day (down 10% or more on 2x volume) within
   25 sessions of 10-06.
4. **Re-underwrite at the next evidence node**, using the fit-matrix falsifier for the
   name. If the falsifier triggers, exit regardless of price.

### 7.3 Non-holders and watchers

1. **No entry in the epicenter while distribution continues.** Minimum conditions: the
   evidence gate passes (a defined validation event within the horizon), a base of at
   least four to seven weeks forms, and a volume-confirmed breakout appears (RVOL above
   1.5, D-018). Holding the 10-06 low through the Q3 report also counts as evidence.
2. **Prefer names whose first gap is closed or narrow.** NTRA and ILMN (fundamentals
   reported, AI incidental), TEM (paid data, profitability gap), ADPT (FCF target). Names
   whose first gap is paid demand or technical (DNA, QSI, PACB, ABSI) need new evidence
   before any price looks attractive.
3. **Set entry prices from scenario values**, built on post-financing share counts, never
   from the distance to the high.
4. **Keep IOVA out of the AI bucket.** Judge it on Q3 against the raised guide.

### 7.4 Calendar to watch

| Window | Node | Names |
|---|---|---|
| Weekly | ARK daily trades; Form 4 and 144; distribution-day count; % of cohort above 50-day MA | Core |
| 2026-10-27/28 | FOMC decision | All; TEM, GRAL most rate-sensitive (beta above 3) |
| 2026-10-29 | Guardant Q3 (U) | GH; read-through to dx layer |
| Late Oct to mid Nov | Q3 reports (dates U) | All; TWST fiscal Q4 |
| 2026-11-05 | Schrodinger Q3 (U) | SDGR |
| November | REC-4881 Phase 2 data (G) | RXRX |
| Undated | Galleri PMA decision | GRAL |

---

## 8. What this case changes in the system

1. **H13 added and pre-registered** (D-021): crowded-theme blow-off reversal.
2. **H9 split in two:** fundamental H9 (does AI revenue appear in the data layer first?)
   and the market's pricing of H9 (did the stocks run ahead of that revenue?). The second
   is an H13 question.
3. **Thematic flows** join H4 as a separate signal: thematic ETF and options flow vs
   specialist conviction.
4. **Cohort features** in M5 (`src/biotech_divedeep/signals/cohort.py`): day class,
   relative volume, run size, two-day path, layer summaries, rank tests.
5. **Fit matrix** per asset (`data/reference/ai_bio_fit_matrix.csv`) becomes the template
   for future theme events.

## 9. Limits

- One day of cross-section. No price history: the FMP plan allows only per-symbol
  profiles (Q-016, Q-017). Moving averages, distribution-day counts and the 2021 analog
  cannot be computed here.
- RVOL uses the vendor's average volume of undocumented length.
- Most event sources are press aggregators (`U`); company releases are linked where
  found. EDGAR is blocked in this environment (Q-004).
- Probabilities in section 6 are judgment, to be replaced by H13 base rates.

## Sources

- FMP company profiles, 36 symbols, fetched 2026-10-06 23:46 UTC.
- [Twist joins Lilly TuneLab](https://investors.twistbioscience.com/news-releases/news-release-details/twist-bioscience-joins-lilly-tunelab-advance-antibody-drug);
  [Ginkgo Datapoints x TuneLab](https://s28.q4cdn.com/823357996/files/doc_news/2026/Sep/16/Ginkgo-Datapoints-x-TuneLab-Announcement.pdf);
  [Tempus and Recursion extension](https://www.tempus.com/news/pr/tempus-and-recursion-extend-existing-data-license-agreement-and-enter-new-license-agreement-for-recursions-rna-foundation-model/)
- [Why is Twist stock plunging today (Investing.com)](https://www.investing.com/news/stock-market-news/why-is-twist-bioscience-stock-plunging-today-93CH-4935087);
  [TWST insider selling](https://www.defenseworld.net/2026/10/06/twist-bioscience-nasdaqtwst-stock-falls-9-7-following-insider-selling.html);
  [TWST 10-05 targets](https://stockstotrade.com/news/twist-bioscience-corporation-twst-news-2026_10_05/)
- [DNA +21% on options activity](https://www.gurufocus.com/news/9110384/ginkgo-bioworks-dna-surges-21-on-heavy-options-activity-following-lilly-tunelab-partnership);
  [ILMN RBC target](https://www.ad-hoc-news.de/boerse/news/corporate-news/rbc-raises-target-for-illumina-stock-to-usd-310/70233455);
  [ILMN +7.6%](https://www.gurufocus.com/news/9110217/illumina-inc-ilmn-shares-surge-76-what-gf-score-of-65-tells-investors);
  [TEM +9.03% on 10-05](https://www.tradingkey.com/news/market-movers/262200753-market-movers-tem-20261005);
  [ARK sells TEM](https://tradersunion.com/news/stocks/show/3611915-tempus-ai-slides-5-20percent-today/);
  [TXG Atera](https://www.timothysykes.com/news/10xgenomicsinc-txg-news-2026_10_02/);
  [TXG 10-05 close](https://www.heygotrade.com/en/us-stock/txg/);
  [XBI 10-05 close](https://www.heygotrade.com/en/us-stock/xbi/)
- [Anthropic wet lab (The Scientist)](https://www.the-scientist.com/anthropic-s-secretive-ai-powered-wet-lab-breaks-cover-and-makes-first-discovery-75037);
  [Gene-editing stocks fall (Seeking Alpha)](https://seekingalpha.com/news/4646229-gene-editing-stocks-fall-anthropic-crispr-like-discovery)
- [10-year above 5%](https://coinalertnews.com/news/2026/09/23/treasury-yield-tops-five-percent);
  [10-year at 19-year high](https://tradingeconomics.com/united-states/government-bond-yield/news/587067);
  [FOMC October schedule](https://fedratecalc.com/fomc-meeting-schedule/october-2026/);
  [October hike expectations](https://cryptobriefing.com/fed-expected-hike-interest-rates-october/)
- [Market on 10-06 (Yahoo)](https://finance.yahoo.com/markets/live/stock-market-today-tuesday-october-6-dow-sp-500-nasdaq-080526166.html);
  [Midday 10-06 (Motley Fool)](https://www.fool.com/coverage/stock-market-today/2026/10/06/stock-market-midday-oct-6-s-and-p-500-sets-new-high-nuclear-stocks-surge/);
  [GRAIL on 10-06 (CNBC)](https://www.cnbc.com/2026/10/06/cramer-grail-stock-galleri-fda-approval.html)
- [Galleri advisory panel (ASCO Post)](https://ascopost.com/news/september-2026/fda-advisory-committee-votes-in-favor-of-approval-of-multi-cancer-early-detection-test/);
  [IOVA guidance](https://www.benzinga.com/markets/guidance/26/09/62059046/iovance-biotherapeutics-amtagvi-demand-drives-2026-revenue-guidance-bump-stock-soars);
  [NTRA Q2](https://www.genomeweb.com/cancer/natera-prospective-study-readouts-accelerate-q2-revenue-climbs-38-percent);
  [ADPT guidance](https://www.360dx.com/sequencing/adaptive-biotechnologies-raises-2026-revenue-guidance-solid-q1-mrd-business-growth);
  [SDGR ACV outlook](https://seekingalpha.com/news/4586486-schrodinger-outlines-218m-228m-2026-acv-outlook-with-focus-on-hosted-transition-and-bunsen);
  [GH earnings date](https://beta.earningswhispers.com/go/x/GH)
