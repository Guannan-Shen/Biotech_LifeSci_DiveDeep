# Insider and holder flow: what follows a block sale after a run (H18), first results

Date: 2026-10-12. Hypothesis H18, module M17 (`docs/modules/ownership_flow.md`). Pre-registration
`notes/backtests/2026-10-12_H18_insider_and_holder_flow.md`, written before any event or forward
return was computed. Only the **in-sample** period (events 2021-12 to 2023-12) has been run; the
out-of-sample and hold-out periods are untouched.

## 1. The investor's two claims, restated as tests

1. "Insiders buying does not always mean the stock goes up." True of the average trade, and the
   literature says where the information hides (section 2). Tested in part B (B2, B3) once Form 4
   data is parsed on the local machine.
2. "Block selling after a big rally means the stock is a bit overvalued, even though it does not
   fall immediately." Two rival readings: the seller knows something, or every big biotech rally
   mean-reverts anyway (H13). The test separates them by comparing each event with **stocks in
   the same run state on the same date that printed no supply day** (run-matched controls). Part A
   runs today on price and volume alone.

## 2. What the literature says (secondary summaries; check originals before citing outside)

| Finding | Source | Evidence class |
|---|---|---|
| Insider purchases earn more than 6% a year of abnormal return for the insiders; sales earn none that is significant | Jeng, Metrick and Zeckhauser (2003), [Harvard copy](https://scholar.harvard.edu/sites/scholar.harvard.edu/files/rzeckhauser/files/insider_trading.pdf), [Wharton working paper](https://rodneywhitecenter.wharton.upenn.edu/wp-content/uploads/2014/04/9919.pdf) | unverified (secondary summary) |
| Splitting insiders into routine (same calendar month every year) and opportunistic: opportunistic trades earn about 82 bp a month value-weighted, routine about zero; opportunistic trades predict firm news | Cohen, Malloy and Pomorski (2012), [NBER w16454](https://www.nber.org/papers/w16454.pdf), [HLS forum](https://corpgov.law.harvard.edu/2012/02/03/decoding-inside-information) | unverified (secondary summary) |
| Discretionary sales, separated from plan and tax sales using Form 4 footnotes, predict negative returns and investors under-react | Amel-Zadeh et al., [Form 4 footnotes paper](https://cms-cdn.lmu.de/media/04-som/iuc/downloads/2019_amel-zadeh.pdf) | unverified |
| Form 144 notices move prices and volume, more so in small caps; notices are not binding and a large share are never executed | [Colorado College thesis record](https://digitalcc.coloradocollege.edu/record/6650), [MIT thesis (Voelcker 2024)](https://dspace.mit.edu/handle/1721.1/155852?show=full), [arXiv 2602.17890](https://arxiv.org/abs/2602.17890v1) | unverified |
| Stocks with the highest specialist concentration earned about 20% a year, those with none about -2% (paper not named in the summary) | [Swedroe summary](https://larryswedroe.substack.com/p/cracking-the-code-a-quantitative) | unverified |
| Names held by 12 or more of about 45 specialist funds beat the 13F biotech average by about 5 points a quarter (just short of significance, no costs); names held by one or two funds reliably underperformed | [BiopharmaWatch Q2 2026 report](https://www.biopharmawatch.com/blog/biotech-stocks-hedge-funds-are-buying-q2-2026) | unverified (vendor) |
| Joint changes in hedge fund 13F holdings and short interest predict abnormal returns | Jiao, Massa and Zhang (2015), via [CXO Advisory](https://www.cxoadvisory.com/investing-expertise/exploiting-interaction-of-hedge-fund-holdings-and-short-interest/) | unverified |
| Trial-data leaks before negative readouts show up as sales by people with access (SEC cases: Catabasis -71%, Neuralstem about -50%, Xoma -42%) | [SEC 2021-94](https://www.sec.gov/news/press-release/2021-94), [SEC LR 17684](https://www.sec.gov/litigation/litreleases/lr17684.htm) | fact (enforcement record), anecdotal for prediction |

What none of these test: sales by insiders and holders **conditioned on a prior run**, against a
run-matched control. That is the gap part A fills.

## 3. Part A in sample: supply days after a doubling

Data: listing mirror daily panel (D-044), therapeutics, tools and diagnostics, USD 50M to 20B,
split-adjusted closes, benchmark `EW_LIFESCI_200M`. Base cell: 144 events in 125 symbols
(2 in 2021, 46 in 2022, 96 in 2023), 141 with at least one control (129 with three). Median event:
the stock had risen 2.6x over 126 sessions, fell 9.3% on the supply day on 5.2x normal volume.
Events: `data/reference/h18a_supply_events_in_sample.csv`.

**Matched difference** = event BHAR minus the mean BHAR of its controls over the same dates, entry
at the close of day +1. Interval: 90% calendar-month block bootstrap (21 months).

| Horizon (sessions) | Event BHAR | Control BHAR | Matched diff, mean | Median | 10% trimmed | 90% interval | Share of events below controls |
|---|---|---|---|---|---|---|---|
| 20 | -0.2% | -1.1% | +0.9% | -0.2% | -0.5% | -3.2% to +5.4% | 51% |
| 60 | -5.1% | -3.0% | -2.1% | -3.7% | -3.2% | -7.1% to +2.8% | 55% |
| 126 (primary) | -10.8% | +1.4% | **-12.2%** | -19.5% | -16.5% | -19.3% to -6.0% | 66% |
| 252 | -12.6% | +11.6% | **-24.1%** | -29.3% | -28.6% | -36.2% to -13.6% | 69% |

The path in finer steps (exploratory, same events):

| Sessions after | 5 | 10 | 20 | 40 | 60 | 90 | 126 | 189 | 252 |
|---|---|---|---|---|---|---|---|---|---|
| Matched diff, mean | -0.2% | +3.0% | +0.9% | -0.5% | -2.1% | -2.8% | -12.2% | -17.5% | -24.1% |
| Matched diff, median | +1.5% | +1.1% | -0.2% | -3.4% | -3.7% | -13.1% | -19.5% | -26.6% | -29.3% |

Secondary predictions (base cell):

- **A2 slow bleed: holds.** Nothing in the first month (a small bounce in the first ten sessions),
  then a steady slide from about day 60. The 20-session difference (+0.9%) is far below half the
  126-session one. This is the investor's "not immediately falling", now measured.
- **A3 financing follows: direction holds, size modest.** Implied share count rose at least 10%
  within 120 sessions after 48% of events vs 38% of controls. Market caps lag filings, so this
  undercounts and dates late.
- **A4 the run alone:** controls earned +1.4% at 126 and +11.6% at 252 against the benchmark. In
  this sample a doubling without supply did *not* mean-revert; the underperformance sits in the
  names that printed supply.
- **A5 drawdown:** 62% of events fell at least 40% from the day +1 close within a year; mean worst
  drawdown -51% for events vs -40% for controls.
- **By size (k = 126):** micro caps -20.2% (90%: -34.7% to -6.3%, n 53), small -6.8% (-21.0% to
  +4.1%, n 74), mid -10.2% (-28.1% to +12.2%, n 14). The effect is concentrated where float is thin.
- **Supply-day severity does not matter** (exploratory): drops of 15% or more and milder ones give
  the same 126-session difference (-11.4% vs -12.4%); volume of 8x or more gives -19.4% vs -9.1%.

### Robustness across the 18 pre-registered cells (k = 126)

| Run x | Volume x | Drop | n | Mean diff | Median diff | Trimmed | 90% interval | Holm p |
|---|---|---|---|---|---|---|---|---|
| 1.75 | 2.5 | -3% | 239 | +1.5% | -12.9% | -6.9% | -5.9% to +9.4% | 1.00 |
| 1.75 | 2.5 | -6% | 176 | +1.2% | -9.0% | -5.3% | -6.6% to +9.6% | 1.00 |
| 1.75 | 3 | -3% | 207 | -1.8% | -16.1% | -8.7% | -7.1% to +3.8% | 1.00 |
| 1.75 | 3 | -6% | 155 | +2.3% | -8.1% | -4.8% | -5.7% to +11.1% | 1.00 |
| 1.75 | 4 | -3% | 158 | +1.7% | -12.1% | -7.0% | -7.2% to +10.8% | 1.00 |
| 1.75 | 4 | -6% | 119 | -1.0% | -12.2% | -10.6% | -11.1% to +10.9% | 1.00 |
| 2.0 | 2.5 | -3% | 166 | -2.6% | -19.0% | -12.1% | -13.6% to +10.5% | 1.00 |
| 2.0 | 2.5 | -6% | 122 | -5.5% | -19.5% | -12.1% | -15.4% to +4.3% | 1.00 |
| **2.0** | **3** | **-3%** | **141** | **-12.2%** | **-19.5%** | **-16.5%** | **-19.3% to -6.0%** | **<0.01** |
| 2.0 | 3 | -6% | 104 | -10.4% | -19.5% | -14.7% | -19.6% to -1.6% | 0.90 |
| 2.0 | 4 | -3% | 110 | -8.7% | -15.0% | -12.7% | -17.9% to -0.7% | 1.00 |
| 2.0 | 4 | -6% | 81 | -14.3% | -19.8% | -19.7% | -25.6% to -3.0% | 0.65 |
| 3.0 | 2.5 | -3% | 54 | -7.2% | -8.8% | -7.4% | -20.8% to +3.9% | 1.00 |
| 3.0 | 2.5 | -6% | 36 | -8.5% | -11.4% | -9.0% | -18.4% to +3.3% | 1.00 |
| 3.0 | 3 | -3% | 46 | -12.9% | -16.6% | -14.9% | -27.9% to -0.7% | 1.00 |
| 3.0 | 3 | -6% | 33 | -14.0% | -18.9% | -15.8% | -25.7% to -2.0% | 1.00 |
| 3.0 | 4 | -3% | 38 | -2.5% | -4.8% | -3.9% | -20.7% to +11.3% | 1.00 |
| 3.0 | 4 | -6% | 27 | -8.3% | -13.6% | -11.6% | -23.9% to +8.3% | 1.00 |

Reading: **every cell has a negative median and a negative trimmed mean** (-4% to -20%), so the
typical event underperforms its controls whatever the thresholds. The **mean** is fragile: only
the base cell survives the Holm adjustment, and at a 1.75x run the mean turns positive. The cause
is a right tail of winners. In the 1.75x cell the events that the 2.0x cell does not contain have
a median difference of +3.8% and a mean of +16.2%, driven by ALPN (+394% BHAR), APLT (+309%),
ARDX and CBAY. In the base cell, six events still beat the benchmark by more than 160% over a year
(RETA, VKTX, CBAY, NPCE, ETNB, APLT); **three of them (RETA, CBAY, ETNB) were later acquired**
(Biogen 2023, Gilead 2024, Roche 2025 per `biotech_takeouts.csv`, recall rows still to verify).
Only RETA's takeout fell inside the year measured; CBAY and ETNB first re-rated on trial data and
were bought afterwards.

That is the practical pattern: the rule wins most of the time and loses big occasionally, and the
big losses are names whose assets turned out to be real, the same names acquirers later pay for. A long-only exit rule therefore needs the takeout
screen (H8, D-036 do-not-sell-cheap flag) as an override, and a trim rather than a full exit is
the natural sizing (section 5).

### Data correction made after the first run

The first run (same day) used the mirror's raw closes. Its most extreme events (run ratios of
14x to 20x in ADMP, LIXT, HARP, ASLN) were reverse splits, because the screener's `lastsale` is
not split-adjusted while its one-day return is. `split_adjust` now detects splits from that
disagreement (factor outside 0.55 to 1.8, confirmed by the next session) and back-adjusts closes
and volumes: 585 split days across the panel. The base cell moved from -12.6% (158 events) to
-12.2% (144 events); the 1.75x cells moved most, because their means had been driven by split
artifacts. Both runs are logged in the pre-registration results table.

## 4. What this does and does not show

- It shows that **identity-free supply after a doubling** marks names that lag otherwise similar
  rallies by about 12 points over six months and 24 over a year, in 2021-2023, mostly in micro
  caps, with the damage arriving after the first two to three months.
- It does not show **who** sold. A supply day mixes holder blocks, company offerings priced
  overnight and plain distribution. Part B (Form 4, 144, 13F) splits them; the A3 share-count
  result suggests a good part is the company itself raising.
- In-sample only, one regime: 2022-2023 was a biotech bear market and its recovery. The
  out-of-sample period (2024-01 to 2025-09) decides whether the rule is real.
- Closes only: no intraday range, so a block trade that opened down and closed flat is missed.
- Delisted names keep their last price and then earn the benchmark; a bankruptcy after the last
  snapshot is not charged its full loss, which biases event BHARs **up** (against the finding).

## 5. Proposed use (advisory until the out-of-sample run, D-050)

1. `supply_after_run` fires on a held name: do not sell on the print. Review within 20 sessions;
   trim by default (half), exit if the H1 dilution score is high (live shelf or ATM, runway under
   18 months), keep if the takeout score is in the top decile (H8) or a dated catalyst sits
   inside 60 sessions (H3).
2. On a candidate name: wait. The in-sample path says the better entry comes three to twelve
   months later, after the financing the supply often precedes.
3. Insider buying stays off the buy list until B2 says otherwise; offering participation never
   counts as insider buying.

## 6. Provenance of `data/reference/h18a_supply_events_in_sample.csv`

Written by `python scripts/supply_after_run.py --period in_sample --events-out ...` on
2026-10-12 from `data/silver/prices/mirror_daily_lifesci.csv.gz` (rebuilt the same day from the
mirror's git history up to the 2026-10-10 commit) and the `EW_LIFESCI_200M` series in
`data/reference/qsi_naut_daily_2021_2026.csv`. One row per base-cell event with its controls,
BHARs at 20, 60, 126 and 252 sessions, matched differences, worst drawdown and implied share
growth. Derived data (evidence class `fact` for prices as reported by the screener, method
`own_assumption`). Caveats as in `docs/research/mirror_price_reference_data.md` plus the split
adjustment above.

## 7. Next

1. Investor review of the in-sample result and the proposed use; then one out-of-sample run of
   the 18 cells (Q-056), unchanged.
2. Local machine: fetch the insider data sets 2020q1 to 2026q2, resolve the fund CIKs, run part B
   in sample (Q-050 to Q-053).
3. Add a 424B5 financing list (M1) so offering participation is labelled from filings, not
   inferred from group buys.
4. Parse Item 408(a) 10b5-1 plan adoptions: a plan adopted right after a run is a delayed
   discretionary sale (Q-054).
