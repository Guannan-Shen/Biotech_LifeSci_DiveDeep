# Stretch, Valuation and Reversal Odds After the 2026-10-06 AI-Bio Break

Date: 2026-10-07. Follow-up to `docs/research/2026-10-06_ai_bio_theme_reversal.md`. Answers two
investor questions: (1) the run-size finding (rho -0.45, n = 23) is weak, so do RSI, KDJ, Bollinger
bands, forward P/S or momentum and similarity measures do better, and is 20x forward sales too
expensive? (2) Large intraday reversals have preceded month-long selloffs before; is this a
short-term turning point, and is there a small short opportunity?

Reproduce: `python scripts/valuation_screen.py` (sections 2 and 3). Daily-bar indicators need the
local price pull (Q-017): `python scripts/technical_panel.py --fetch --event 2026-10-06`.
Research note, not investment advice. Evidence classes: **F** fact, **G** management guidance,
**A** own assumption, **U** unverified.

---

## 0. Answers in brief

1. **A KDJ-type measure beats run size, and it survives a multiple-testing correction.** Where the
   prior close sat inside the 52-week range (the 252-day RSV, the raw input of a slow KDJ) ranks
   with the 10-06 loss at rho -0.60 (n = 23, 90% bootstrap interval -0.79 to -0.26, permutation
   p = 0.004). Run size gives -0.45 (p = 0.033), which fails a Holm correction across the four
   features tested (adjusted p = 0.093). The range position does not (adjusted p = 0.024).
2. **Stretch only mattered inside the crowded theme.** In the 17-name launch and commercial layer
   the same measure explains nothing (rho -0.15, interval -0.56 to +0.32). Stretch is a hazard
   when a theme's holders are leaving, which is what H13 claims, and a neutral fact otherwise.
3. **Sales multiples alone did not predict the day** (P/S rho -0.16, n = 15 in the AI cohort). They
   answer a slower question: what the price requires. At a 5x exit multiple, **20x sales needs
   about 32% revenue growth a year for five years just to return 0%, and about 45% to return
   10% a year.** Fewer than one company in five sustains even 20% a year for a decade (base rates
   in section 3). TXG is the extreme: 16.5x guided sales on 2-5% growth.
4. **The academic base rates split by horizon.** Over 1 month, a large drop with no firm-specific
   news tends to partly reverse (Savor 2012; the short-term reversal effect). Over 6 to 24
   months, a sector that has doubled carries crash odds near 50%, rising to about 80% after a
   150% run (Greenwood, Shleifer and You 2019), yet its *average* forward return is not reliably
   negative. Both facts argue against a naked one-month short and for patience plus confirmation.
5. **Turning point: not yet confirmed.** One heavy-distribution day is a candidate top. Section 5
   lists the confirmations to count over the next 25 sessions (to about 2026-11-10), which
   include FOMC (10-28) and the first Q3 reports.
6. **Shorts are outside the current mandate** until Q-002 is answered. If allowed, the
   structure that fits the evidence is small, defined-risk and confirmation-triggered: an ARKG
   versus XBI relative position (the H13 outcome itself), or put spreads through a Q3 report on
   the name with the widest growth gap. Section 6 gives the sizing arithmetic and the reasons to
   avoid squeeze-prone names.

---

## 1. What one-day snapshots can and cannot measure

The FMP plan returns profiles only (close, change, volume, average volume, 52-week range, beta,
market cap); charts, quotes, technical indicators, statements and estimates return "requires a
higher plan" (checked 2026-10-07), and price sites are blocked from this sandbox. So:

| Feature the investor proposed | Computable now? | How |
|---|---|---|
| KDJ | Partly | The 252-day RSV (range position) comes from the 52-week range. The 9-day K, D, J need bars: `signals/technical.py::kdj` |
| RSI(14) | No | `signals/technical.py::rsi` (Wilder), runs on local bars |
| Bollinger %b and bandwidth | No | `signals/technical.py::bollinger` |
| Forward P/S | Yes, with guidance as the forward base | `data/reference/revenue_baseline_2026.csv`, `models/multiples.py` |
| Momentum (12-1) and path acceleration | No | `momentum_12_1`, `acceleration` |
| Movement similarity | No | `return_similarity` vs ARKG and vs the equal-weight cohort |

All the daily-bar features are now pre-registered as exploratory secondary predictors in H13
amendment A1 (`notes/backtests/2026-10-06_H13_theme_blowoff_reversal.md`), fixed before any
history is pulled.

## 2. Rank tests against the 10-06 return

Spearman rho with the day return. Interval: 90% percentile bootstrap. p: two-sided permutation.

| Feature | Set | n | rho | 90% interval | p |
|---|---|---|---|---|---|
| Range position before the day (252-day RSV) | AI cohort incl. IOVA | 23 | -0.60 | [-0.79, -0.26] | 0.004 |
| Close / 52-week low (run size, the 10-06 finding) | AI cohort incl. IOVA | 23 | -0.45 | [-0.71, -0.08] | 0.033 |
| Range position after the day | AI cohort incl. IOVA | 23 | -0.40 | [-0.69, +0.04] | 0.060 |
| Distance from the 52-week high | AI cohort incl. IOVA | 23 | -0.36 | [-0.65, +0.07] | 0.096 |
| P/S on the revenue base | AI cohort | 15 | -0.16 | [-0.70, +0.37] | 0.55 |
| Growth-adjusted P/S (PSG) | AI cohort | 12 | -0.27 | [-0.67, +0.27] | 0.39 |
| Range position before the day | Launch and commercial layer | 17 | -0.15 | [-0.56, +0.32] | 0.55 |
| Close / 52-week low | Launch and commercial layer | 17 | -0.08 | [-0.52, +0.39] | 0.76 |
| Range position before the day | Both layers | 39 | -0.64 | [-0.75, -0.45] | <0.001 |
| Growth-adjusted P/S | Both layers | 24 | -0.69 | [-0.83, -0.45] | <0.001 |

How to read it:

- **Range position is the better stretch measure** because it normalizes by the name's own
  range: a stock pinned at its high (GH 0.97, NTRA 0.96, SDGR 0.95, TXG 0.94) had the most
  holders with fresh gains to protect. Run size mixes stretch with the depth of last year's low.
  The prior-day version also avoids most of the intraday-high leak noted in the case study.
- **The both-layer results are mostly a layer effect.** The launch layer barely moved (median
  -1.6%) and also has low range positions and low PSG, so pooling manufactures a strong rho. The
  within-layer numbers are the honest ones.
- **Selection caution.** Range position was chosen after seeing the day (the investor's KDJ
  suggestion, tested by me the same day). The Holm adjustment treats it as one of four tests, but
  the honest status is still "hypothesis from one day". A1 fixes it for out-of-sample testing.

## 3. Is 20x forward sales too expensive?

A sales multiple is a claim about future revenue. `models/multiples.py::required_cagr` turns it
into the revenue growth the price needs:

`revenue CAGR = (market cap x (1 + r)^T x (1 + dilution)^T / exit multiple / revenue_today)^(1/T) - 1`

With a 5x exit multiple (A: roughly where large profitable tools companies such as TMO and DHR
trade on their reported revenue), T = 5 years and no dilution:

| Today's P/S | CAGR for 0% a year | CAGR for 10% a year | Exit at 3x, 0% | Exit at 8x, 0% |
|---|---|---|---|---|
| 10x | 15% | 26% | 27% | 5% |
| 15x | 25% | 37% | 38% | 13% |
| 20x | 32% | 45% | 46% | 20% |
| 30x | 43% | 57% | 58% | 30% |

Base rates (Mauboussin and Callahan, "The Base Rate Book", 2016, via
[summary](https://thesmartinvestor.com.sg/a-new-world-of-accelerating-growth); U on exact
figures): of companies that started below USD 325M of revenue, 18.1% compounded sales above 20% a
year for ten years; only about 1.5% of 2,548 firms compounded above 45% over three years. **So 20x
sales requires a top-decile growth path to merely hold value, and a top-few-percent path to earn
a normal return.** For a biotech launch that path is plausible for a few years (launch curves
grow 50-100%+ early), for a tools company growing 4% it is not.

Growth gap = latest year-over-year growth minus the CAGR the price needs for a 0% return (5x exit,
5 years). Negative means the price needs more growth than the company is producing now.

| Ticker | P/S | Basis | Growth | Required CAGR | Growth gap | Reading |
|---|---|---|---|---|---|---|
| TXG | 16.5 | 2026 guide 610-630M (G) | +4% | +27% | **-23 pts** | Largest gap in the table; Atera must re-accelerate growth by about 7x |
| GRAL | 33.0 | Q2 run rate (F, U source) | +26% | +46% | -20 pts | Priced for approval plus coverage; a regulatory option, not a sales multiple |
| TWST | 22.8 | FY26 guide 456-457M (G) | +23% | +35% | -12 pts | Needs AI demand to lift growth by half again |
| DNA | 10.1 | Q2 run rate | -48% | +15% | -63 pts | Shrinking base; H1 (runway) governs |
| ILMN | 9.0 | 2026 guide (G) | +10% | +12% | -2 pts | Roughly priced for what it reports |
| NTRA | 19.9 | 2026 guide (G) | +38% | +32% | +6 pts | 20x, but earned by growth; thin margin of safety |
| GH | 17.0 | 2026 guide (G) | +44% | +28% | +16 pts | High multiple with growth support |
| TEM | 7.9 | 2026 guide (G) | +22% | +10% | +12 pts | Not stretched on sales; its gap is profitability |
| IOVA | 13.9 | 2026 guide 410-420M (G) | +66% | +23% | +43 pts | Launch growth supports the multiple if Q3 holds the raised guide |

So the investor's 20x rule of thumb is right for the data layer and wrong for fast launches: the
multiple is too expensive when the growth gap is negative. TXG and TWST fail; NTRA and GH pass
narrowly; IOVA passes with room.

Caveats (A): current growth decays; dilution adds to the hurdle (`annual_dilution`); net cash
lowers it (GRAL holds USD 862M); run-rate bases understate fast ramps (CYTK, RYTM) and overstate
lumpy milestone revenue (SDGR, RXRX).

## 4. What follows a day like 10-06: base rates

| Evidence | Finding | Bearing on the next month | Bearing on 6-24 months |
|---|---|---|---|
| Savor (2012, JFE), [abstract](https://repository.upenn.edu/handle/20.500.14332/34495) | Large price shocks without information (no analyst report) reverse; shocks with information drift | 10-06 had no firm-specific fundamental news (flows, ARK, options), so the base rate is a partial bounce | Silent |
| Short-term reversal (Jegadeesh 1990; Lehmann 1990) | Last month's losers tend to outperform next month | Against a one-month short | Silent |
| Greenwood, Shleifer and You (2019, JFE), [paper](https://www.nber.org/system/files/working_papers/w23191/w23191.pdf) | US industries up 100% net of market over two years: crash (40% drawdown within two years) probability about 54% vs 19% at 50%, about 81% at 150%; unconditional about 14%. Average forward returns are *not* reliably low. Volatility, turnover, new issuance and an accelerating price path raise crash odds and lower returns | Silent | Elevated crash odds; TWST and TXG are up about 5x year to date (U), far beyond the paper's thresholds |
| Da, Engelberg and Gao (2011, JF) | Abnormal search attention predicts higher prices for about two weeks and a reversal within the year | A fading attention spike removes a support | Reversal of attention-driven gains |
| Genomics, 2000-03-14 | One headline (Clinton-Blair genome statement) knocked about USD 10.4B off genomics stocks; the Nasdaq Biotech index fell 12.5% that day ([CNN](https://money.cnn.com/2000/03/14/companies/biotech/), [BioCentury](https://www.biocentury.com/article/57468/10-4b-knocked-off-genomics-stocks)) | Partial recovery after the clarification | The theme peaked that month (U, needs prices) |
| ARKG after early 2021 | Drawdown from the January 2021 peak: -38% in 2021, -57% in 2022, about -84% at the trough in 2025 ([totalrealreturns](https://totalrealreturns.com/s/ARKG), U) | The decline was not immediate in a straight line | Regime unwind |

Synthesis (A): the investor's pattern memory is about the right *direction* at the wrong
*speed*. A key reversal on heavy volume in a parabolic theme raises the odds of a large decline
over the following quarters; it does not make the next month a reliable short, because the
no-news shock and short-term reversal evidence both point to a bounce first. GSY's attribute
list is the useful checklist: turnover (RVOL 3-9 on 10-06), volatility (betas 2-3.7),
acceleration (most of the run came in 2026) are already lit; **new issuance is the missing
flag**. A follow-on offering by TWST, TXG or TEM into a bounce would be the strongest single
top signal in that paper's framework.

Signal from 10-07 so far: one aggregator page showed TWST at 177.76 (+6.5%) on 10-07
([pluang](https://pluang.com/en/asset/usstock/TWST/10549), U, time of quote unknown). A bounce is
what the base rates predict; it is not evidence either way.

## 5. Turning-point scoreboard (count over the next 25 sessions, to about 2026-11-10)

| # | Confirmation | Why it matters | Status 2026-10-07 |
|---|---|---|---|
| 1 | A bounce retraces 38-62% of the 10-06 range on lower volume, then fails | Lower high on light demand: the classic distribution sequence | Pending |
| 2 | A second heavy-distribution day (<= -10% on >= 2x volume) in any core name | Case-study rule 7.2.3; H13 secondary question | 1 so far (10-06) |
| 3 | Core names close below their 50-day averages and stay there a week | Trend overlay (D-018) | Pending; needs bars |
| 4 | New issuance: follow-on, ATM usage or convertible in TWST, TXG, TEM, GRAL | GSY issuance attribute | None seen |
| 5 | ARK selling continues; insiders keep filing Form 144 | Flow supply | ARK sold TWST 21 sessions to 10-06 (U) |
| 6 | Good Q3 news is sold (first prints: GH 10-29, U) | Scenario C signpost | Pending |
| 7 | FOMC hikes on 10-28 or the 10-year rises above 5.5% | Duration pressure on long-dated cash flows | Pending |

Three or more by 2026-11-10: treat 10-06 as the turning point and move scenario C (case study
section 6) up. Zero or one with Q3 news bought: scenario A or B.

## 6. If shorts become allowed (Q-002): structure and sizing

The mandate is long-only until the investor answers Q-002. The analysis below is for that
decision, not a recommendation.

**What the evidence supports**

- **Relative, not absolute.** The H13 outcome is underperformance versus XBI, so the cleanest
  expression is ARKG (or an equal-weight TWST/TXG/TEM basket) against XBI. It strips out the
  sector beta and the FOMC risk that hits both legs. ARKG's beta (2.38) is about twice XBI's
  (1.10), so a beta-matched pair holds about USD 2.2 of XBI per USD 1 of ARKG; a dollar-matched
  pair keeps a net short-beta tilt.
- **Defined risk on single names.** Put spreads dated after the Q3 report, on the name with the
  widest growth gap and the weakest catalyst support: TXG (16.5x sales, 2-5% guided growth,
  gap -23 points).
- **Avoid:** DNA (9x RVOL on call buying, small cap, partnership headlines squeeze shorts; its
  lens is H1 avoidance, not a short), TWST outright (short interest about 23% of float in
  mid-September, [Benzinga](https://www.benzinga.com/quote/TWST/short-interest), U; crowded
  shorts plus a 52.8% gross margin and rising guidance make squeezes likely), TEM outright
  (short interest reported between 18% and 31% of float, U; beta 3.7).

**When.** The base rates favor a bounce first, so a confirmation trigger beats an immediate
entry: scoreboard items 1 or 2. Invalidation: a close above the 10-06 intraday high (TWST
219.71, TXG 102.81) or Q3 good news bought.

**How much.** With one day of evidence the right size is the size that makes being wrong
cheap: risk per idea of 0.25-0.5% of portfolio value at the invalidation level (A). Example:
on a USD 100k portfolio, a 0.5% risk budget is USD 500; a TXG put spread costing USD 4 that can
lose its full premium allows about 1.25 contracts, so one contract.

## 7. Limits

- One day of cross-section; within-layer n of 15 to 23.
- Revenue bases mix guidance (G) and run rates (F from aggregator summaries, U until checked
  against the 8-K exhibits linked in the CSV).
- Base-rate studies use industry portfolios (GSY) or broad samples; transferring them to a
  23-name cohort is an assumption.
- No borrow-cost or options-pricing data in this environment.

## Sources

- FMP profiles (two snapshots, 2026-10-06 close): `data/reference/ai_bio_cohort_snapshot_2026-10-06.csv`,
  `data/reference/launch_commercial_snapshot_2026-10-06.csv`.
- Revenue bases with per-row sources: `data/reference/revenue_baseline_2026.csv`.
- [Greenwood, Shleifer and You, "Bubbles for Fama"](https://www.nber.org/system/files/working_papers/w23191/w23191.pdf);
  [summary of crash probabilities](https://www.advisorperspectives.com/articles/2017/05/29/is-it-possible-to-identify-bubbles-can-investors-profit-from-this).
- [Savor, "Stock returns after major price shocks: the impact of information"](https://repository.upenn.edu/handle/20.500.14332/34495).
- [Base Rate Book summary](https://thesmartinvestor.com.sg/a-new-world-of-accelerating-growth); [hedgefundalpha](https://hedgefundalpha.com/education/michael-mauboussin-the-base-rate-book/).
- [ARKG drawdown](https://totalrealreturns.com/s/ARKG); [ARK sells TWST (MoneyCheck)](https://moneycheck.com/ark-invest-offloads-17m-in-twist-bioscience-twst-adds-recursion-rxrx-and-intellia-ntla/).
- [2000-03-14 genomics selloff (CNN)](https://money.cnn.com/2000/03/14/companies/biotech/).
- [TWST short interest (Benzinga)](https://www.benzinga.com/quote/TWST/short-interest); [TEM short interest (Benzinga)](https://www.benzinga.com/quote/TEM/sentiment).
- [TWST and TXG year-to-date gains (Stocktwits)](https://stocktwits.com/news-articles/markets/equity/cathie-wood-loads-up-on-these-biotech-stocks-after-strong-rallies-unloads-18-m-worth-of-twst-shares/cZDt2hdRBkH).
