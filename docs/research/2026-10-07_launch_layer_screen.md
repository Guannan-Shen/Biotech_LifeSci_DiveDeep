# Launch and Commercial Layer Screen During the AI-Bio Break

Date: 2026-10-07. Investor request: the 10-06 case study set IOVA aside under the `launch`
playbook; explore the launch layer more widely, starting with HROW and ETON, for names that were
not overhyped and may offer opportunity in a sector downturn. IOVA stays out of the AI bucket.

Data: `data/reference/launch_commercial_snapshot_2026-10-06.csv` (FMP profiles after the 10-06
close, 17 names), `data/reference/revenue_baseline_2026.csv` (revenue bases with per-row sources
and evidence classes), `data/reference/launch_layer_ma_2026.csv` (2026 takeouts found while
screening). Tables: `python scripts/valuation_screen.py`. Research note, not investment advice.

Layers: `launch` = first major product approved within about 30 months, value set by the ramp
(H2). `commercial_pharma` = established or multi-product revenue (H6). Names whose approval status
could not be verified (VERA) are left out (Q-023).

---

## 0. Summary

1. **The launch layer did not take part in the theme selloff.** Median 10-06 return: launch +0.1%,
   commercial -1.7%, against -7.9% to -12.0% for the AI-bio layers. Run size was small (median
   close / 52-week low 1.2x to 1.4x vs 2.4x to 2.8x). So the downturn did not hand over discounts
   here; the discounts that exist are name-specific (a court ruling, a guidance cut, payer
   friction, a slow quarter).
2. **The layer is cheaper per unit of growth.** Median growth-adjusted P/S (PSG): launch 0.11,
   commercial 0.18, against 0.40 (clinical genomics) and 0.99 (data generators). TARS (4.6x sales,
   +69% growth), MDGL (7.9x, +71%), TVTX (8.1x, +70%) and ETON (10.3x, +99% mostly acquired) carry
   large positive growth gaps.
3. **Takeouts set a floor under approved-product names.** Three names a launch screen would have
   held this year were acquired: APLS (Biogen, USD 41 + CVR, about USD 5.6B), CPRX (Angelini,
   USD 31.50, USD 4.1B, 21% premium), CRNX (Vertex, USD 85, USD 10B). This is H8 evidence for the
   layer and a survivorship warning: a screen run today without them looks worse than the layer
   performed.
4. **Opportunity here is an H2 question, not a theme-rebound question.** The market punishes slow
   quarters and over-extrapolates them (framework section on `launch`). The candidates are names
   whose price fell on a fixable or temporary problem while the demand data kept rising.
5. **HROW** is the cleanest test of that idea and also the riskiest on credibility: 3.2x guided
   sales, 8% of the way up its 52-week range, but the guide needs second-half revenue about double
   the first half. **ETON** is a quality compounder priced as one (10.3x, adjusted EBITDA margin at
   least 35%), not a downturn bargain. **IOVA** is the one launch name with an AI-data-layer price
   profile (7.4x off its low, top 8% of its range) and fell the most in the layer (-8.4%).

## 1. The layer on 10-06

| Ticker | Layer | 10-06 | RVOL | Close / low | Range pos. before | From high | P/S | Basis | Growth | PSG | Growth gap |
|---|---|---|---|---|---|---|---|---|---|---|---|
| IOVA* | launch | -8.4% | 1.1 | 7.4x | 0.92 | -15% | 13.9 | guide (G) | +66% | 0.21 | +43 pts |
| LQDA | launch | -6.3% | 2.3 | 1.2x | 0.08 | -72% | 3.4 | pre-ruling run rate | n/a | n/a | n/a |
| CYTK | launch | -2.2% | 1.6 | 1.1x | 0.25 | -31% | 75.4 | Q2 run rate (first year) | n/a | n/a | n/a |
| SPRY | launch | +0.1% | 0.7 | 1.1x | 0.03 | -67% | 3.2 | Q2 run rate | +115% | 0.03 | +124 pts |
| MDGL | launch | +0.6% | 1.0 | 1.3x | 0.45 | -19% | 7.9 | Q2 run rate | +71% | 0.11 | +61 pts |
| REPL | launch | +0.8% | 0.6 | 8.8x | 0.79 | -19% | n/a | approved 2026-08-06 | n/a | n/a | n/a |
| INSM | launch | +1.3% | 1.2 | 1.2x | 0.11 | -51% | 12.8 | guide (G) | n/a | n/a | n/a |
| TVTX | commercial | -2.9% | 1.8 | 2.5x | 0.76 | -19% | 8.1 | Q2 run rate | +70% | 0.12 | +60 pts |
| MIRM | commercial | -2.7% | 1.5 | 1.3x | 0.27 | -39% | 7.0 | guide (G) | +38% | 0.18 | +31 pts |
| KRYS | commercial | -2.4% | 0.9 | 1.8x | 0.77 | -15% | 20.2 | Q2 run rate | +24% | 0.84 | -8 pts |
| ARDX | commercial | -2.4% | 1.4 | 1.0x | 0.03 | -61% | 1.7 | guide (G) | +31% | 0.06 | +50 pts |
| RYTM | commercial | -1.8% | 1.4 | 1.2x | 0.38 | -26% | 21.8 | Q2 run rate | +47% | 0.46 | +13 pts |
| AXSM | commercial | -1.5% | 1.7 | 1.5x | 0.42 | -33% | 10.3 | Q2 run rate | +46% | 0.22 | +31 pts |
| ETON* | commercial | -1.5% | 0.9 | 3.8x | 0.79 | -17% | 10.3 | guide (G) | +99% | 0.10 | +83 pts |
| HROW* | commercial | -0.8% | 0.7 | 1.1x | 0.08 | -45% | 3.2 | guide (G) | +11% | 0.29 | +20 pts |
| TARS | commercial | -0.5% | 0.5 | 1.4x | 0.55 | -19% | 4.6 | guide (G) | +69% | 0.07 | +71 pts |
| ADMA | commercial | +0.7% | 0.7 | 1.4x | 0.22 | -50% | 4.3 | guide (G, cut) | n/a | n/a | n/a |

P/S uses market cap (no net cash or debt adjustment). Growth is the latest quarter year over year.
Growth gap is growth minus the revenue CAGR the price needs for a 0% return at 5x sales in five
years (A). `*` = named by the investor.

## 2. Why each discount exists (the first question before any price)

| Ticker | What hit the price | Class | Fixable or structural? | Next evidence node |
|---|---|---|---|---|
| LQDA | 2026-09-30 Delaware ruling: YUTREPIA infringes two valid claims of UTHR's '327 patent (PH-ILD); stock -57% that day; appeal and label carve-out planned ([MarketBeat](https://www.marketbeat.com/instant-alerts/price-liquidia-nasdaq-lqda-stock-falls-58-whats-next-2026-09-29/), [TIKR](https://www.tikr.com/blog/liquidia-stock-crashed-57-in-a-day-after-a-delaware-court-ruling-an-appeal-could-decide-whether-shares-rebound)) | U | Legal binary: injunction scope decides the PH-ILD share of revenue | Proposed judgment and injunction terms |
| INSM | Q1 BRINSUPRI miss, early discontinuations, Nasdaq-100 exit; Q2 then beat and guide rose to USD 1.25-1.4B, peak sales above USD 7B (G) | U | Looks temporary if Q3 holds the sequential ramp | Q3 BRINSUPRI revenue and persistence |
| ADMA | 2026 guide cut from above USD 635M to 530-560M on immunoglobulin pricing and channel inventory | G | Partly structural (pricing) | Q3 ASCENIV growth vs BIVIGAM erosion |
| ARDX | Payer utilization management slowed IBSRELA; guide revised to USD 350-370M; USD 1B long-term goal kept but timing under review | G | Payer friction can ease or persist | Q3 IBSRELA net price and volume |
| SPRY | neffy share 5% of US epinephrine; strategy narrowed, costs cut | U | Structural adoption question | Q3 share and cash burn |
| HROW | H1 revenue about USD 115M, below plan, on VEVYE net revenue; full-year guide kept at USD 350-365M | G | Test arrives with Q3 | Q3 revenue vs the H2 run rate the guide implies |
| MIRM | Volixibat regulatory delay; revenue guide raised to USD 680-700M | G | Pipeline delay, base business intact | Volixibat timeline |
| AXSM | Off its high while revenue grows 46%; AUVELITY agitation launch June 2026 | U | Unclear; check for a specific event | Q3 agitation uptake |

Mechanism (A): every discount above is either a legal or payer event or a slow quarter. H2 says
the market over-extrapolates slow quarters for launches whose demand metrics keep rising and is
right about structural problems. The screen therefore has to separate demand (prescriptions,
patients, start forms) from net revenue (price, channel, payer). HROW and ARDX are the two names
where demand reportedly rose while net revenue disappointed.

## 3. HROW and ETON

### HROW (Harrow)

| Item | Value | Class | Source |
|---|---|---|---|
| Price, 52-week range | 30.35; 28.54 to 54.85; 8% up the range, -45% from the high | F | FMP profile |
| 2026 guide | Revenue USD 350-365M; adjusted EBITDA USD 80-100M (reiterated August) | G | [MarketBeat Q2 call](https://www.marketbeat.com/instant-alerts/harrow-q2-earnings-call-highlights-2026-08-11/) |
| H1 2026 revenue | About USD 115M; Q2 USD 70.7M (+60% sequential, +11% yoy) | U | [allinvestview](https://www.allinvestview.com/earnings/HROW/q2-2026/) |
| Implied H2 | USD 235-250M, roughly 2x H1 | A (arithmetic on G) | |
| VEVYE | Prescriptions +21% sequential; revised business rules improve economics in H2 | G | Q2 call |
| P/S | 3.2x on the guide midpoint; growth gap +20 pts | A | `valuation_screen.py` |
| Beta, RVOL on 10-06 | 0.24; 0.67 | F | FMP profile |

Reading: the price assumes management misses again. The Q3 report is a clean falsification
test because the guide forces a large step-up. **Falsifier (A): Q3 revenue below about USD 100M
or a guidance cut** (on-track Q3 is roughly USD 110-125M if H2 is split evenly). Two checks before
any position: (1) debt maturities and covenants under H1 (Harrow has carried senior notes; terms
not verified here, Q-024); (2) how much of the H2 step-up is price versus volume (VEVYE
business rules). Lens: H6 (quality) plus H2 (VEVYE ramp). The low beta and quiet volume mean no
crowding; the risk is credibility, not flows.

### ETON (Eton Pharmaceuticals)

| Item | Value | Class | Source |
|---|---|---|---|
| Price, 52-week range | 54.77; 14.27 to 66.37; 79% up the range, 3.8x off the low | F | FMP profile |
| Q2 2026 | Revenue USD 37.6M (+99% yoy, HEMANGEOL acquisition included); GAAP EPS 0.35; adjusted EBITDA USD 16.2M | U | [Barchart release](https://www.barchart.com/story/news/3837934/eton-pharmaceuticals-reports-second-quarter-2026-financial-results) |
| 2026 guide | Revenue above USD 145M (raised from above 120M); adjusted EBITDA margin at least 35% | G | same |
| Pipeline | ASN-001 (infantile hemangioma) acquired; NDA targeted 2027 | G | same |
| P/S, EV / adjusted EBITDA | 10.3x; about 29x on 35% of USD 145M, before net cash or debt | A | |

Reading: ETON ran 3.8x off its low on earnings, not narrative, and still trades like a
compounder. It is a quality name to own at the right price rather than a downturn discount. The
open question from the universe note stands: how much growth is organic. **Falsifier (A):
organic growth (excluding HEMANGEOL and other acquired products) below about 20%, or the adjusted
EBITDA margin below 35%.**

### IOVA (kept in `launch`, out of the AI bucket)

Two facts from this screen. First, IOVA's price profile matches the AI data layer even though its
business does not: 7.4x off the 52-week low, 92% up the range, and the largest 10-06 loss in the
launch layer (-8.4%, on normal volume). Stretch made it vulnerable on a theme day regardless of
its story. Second, the multiple is supported: 13.9x the raised USD 410-420M guide, +66% growth,
gross margin 56%, cash USD 304M with runway into 2H 2028 (G). H1 revenue was about USD 170M
(Q1 about 71M, Q2 99.3M), so the guide needs USD 240-250M in H2, about USD 120-125M a quarter;
a Q3 print near or above USD 115M keeps the ramp on that path (A). The fit-matrix falsifier is unchanged.

### REPL (correction to the universe note)

The universe note said approval was unverified (Q-007). FDA granted accelerated approval to
vusolimogene oderparepvec-wtpg (TUDRIQEV) plus nivolumab for anti-PD-1-failed melanoma on
2026-08-06 ([FDA](https://www.fda.gov/drugs/resources-information-approved-drugs/fda-grants-accelerated-approval-vusolimogene-oderparepvec-wtpg-combination-nivolumab-melanoma)),
after a 10-3 advisory vote. The stock is 8.8x off its 52-week low: like IOVA, a launch name with
a crowded-name price profile. Runway was guided into late Q1 2027 before approval, with up to
USD 120M of Hercules debt tied to milestones (G), so H1 (financing risk) applies alongside H2.

## 4. Takeouts in the layer (H8)

| Target | Acquirer | Announced | Terms | Lead product (approval) |
|---|---|---|---|---|
| APLS | Biogen | 2026-03-31 | USD 41.00 cash + CVR (two USD 2 payments on SYFOVRE sales), about USD 5.6B; closed 2026-05-14 | SYFOVRE, EMPAVELI |
| CPRX | Angelini Pharma | 2026-05-07 | USD 31.50, USD 4.1B, 21% over the unaffected close; closed mid-July | FIRDAPSE, AGAMREE, FYCOMPA |
| CRNX | Vertex | 2026-07-06 | USD 85.00, USD 10.0B (8.8B net of cash); closing expected Q3 2026 | PALSONIFY (2025-09) |

All `U` (press and law-firm summaries; 8-Ks to check). Two lessons: acquirers are paying for
approved, growing assets (patent-cliff demand, H8), and the premiums were moderate (about 20-30%),
so the floor is real but not a lottery ticket. **Correction 2026-10-08:** only Catalyst fits that
range (21% to its unaffected close); Apellis was 140% to its 2026-03-30 close and Crinetics 102%
(`docs/research/2026-10-08_takeout_database_and_phase2_gate.md` section 2). The research universe must keep these names with
their deal prices (no survivorship filter), which is why they sit in a separate table rather than
being dropped.

## 5. Where opportunity may sit (process, not picks)

| Bucket | Names | Test before any price work |
|---|---|---|
| Demand up, net revenue lagging | HROW, ARDX | Q3 shows net price stabilizing while volume keeps rising |
| Large positive growth gap, low stretch | TARS, MDGL, MIRM, AXSM | Profitability and cash (not yet collected); payer and competitive risk per product |
| Supported multiple, crowded price | IOVA, REPL, ETON | Size for theme-day drawdowns even though the business is sound |
| Binary, not drift | LQDA (legal), ADMA (pricing) | Treat as event trees, outside H2 |
| Early ramp, run rate misleading | CYTK, RYTM | Use patient counts and start forms, not annualized revenue |

Rule carried from the case study: set entry prices from scenario values, never from the
distance to the 52-week high.

## 6. Limits

- Profiles and revenue bases only; no cash, debt, margins or share counts for most names yet
  (needs EDGAR XBRL, blocked here, Q-004).
- Growth from one quarter; launch ramps distort year-over-year rates.
- 10-06 is one day; the claim that this layer is uncorrelated with the AI theme needs return
  correlations from daily bars (`scripts/technical_panel.py`, `sim_arkg_63`).

## Provenance of the new reference tables

| File | Content | Source and caveats |
|---|---|---|
| `launch_commercial_snapshot_2026-10-06.csv` | FMP profile fields, same schema as the AI cohort snapshot | Fetched 2026-10-07 before the open; values are the 2026-10-06 close. Vendor average-volume window undocumented. CRNX, CPRX, APLS excluded (inactive symbols) |
| `revenue_baseline_2026.csv` | Guidance or Q2 run rate per ticker, growth, release date, evidence class | Figures from search summaries of company releases; `verified_against_primary` is false for every row until the linked 8-K exhibits are read |
| `launch_layer_ma_2026.csv` | 2026 takeouts of approved-product companies found while screening | Press and law-firm summaries (U); not a complete M&A list |
| `pharma_ai_watch_events.csv` | Dated announcements by large pharma, AI labs and compute vendors (M16) | Company releases where linked (`fact` for what the actor did), press otherwise (U); month-precision rows flagged in `date_precision`; seeded, not exhaustive |
