# HROW Business Quality Card: Products, Moat, Business Model, People

Date: 2026-10-08. First application of the business quality gate
(`docs/framework/business_quality.md`, D-030 to D-033). Complements the hold memo
(`docs/memos/HROW.md`), which priced the stock without looking inside the product lines. Research
note, not investment advice. **F** fact, **G** guidance, **A** own assumption, **U** unverified
(secondary summaries of the 8-K, 10-Q and 10-K; see `docs/research/business_quality_reference_data.md`).
Numbers reproduce with `python scripts/business_quality_card.py HROW --as-of 2026-10-08`.

## 1. The one-paragraph answer

Harrow is an eye-care roll-up that buys or licenses approved but neglected ophthalmic products
cheaply and pushes them through one sales and distribution chassis. Two products decide the
thesis. **VEVYE** is a chronic dry eye drop with a real formulation edge, rising share and
patents into the late 2030s, but it sells through pharmacy-benefit managers in a crowded class
anchored by generic cyclosporine, and in H1 2026 it bought volume with price. **IHEEZO** is a
single-use anesthetic gel whose economics come from Medicare reimbursement rather than from
clinical superiority over two-dollar generic drops; its best channel closed when pass-through
ended on 2026-04-01, and its 2025 revenue was inflated by channel loading. The deal-sourcing
engine is a genuine capability (VEVYE returned about 11 dollars of 2025 revenue per dollar paid),
which makes the model **good**, not great: no product has a wide moat and the lead product fails
the price test. Management's strategy is coherent; its guidance is not reliable (2 of 7 guides
hit, posterior 0.36). The 2026 plan is a genuine pre-committed sacrifice whose payoff is checked
by the FY2026 report, and simple arithmetic says the H2 guide needs the top of every plausible
range at once.

## 2. Product and revenue map (lens A)

Q2 2026 revenue USD 70.7M (U). Lines are as Harrow groups them; TRIESENCE is not broken out.

| Line | Q2 2026 (USD M) | Share | What it does, who pays | Protection | Economics shared | Moat, trend |
|---|---|---|---|---|---|---|
| VEVYE | 29.4 | 42% | Chronic dry eye drop (cyclosporine 0.1% in a water-free vehicle); commercial plans via PBM, Part D, copay card | Formulation patent to 2037-09; last listed patent to 2042 (U, aggregators) | Low double-digit royalty to Novaliq plus milestones | Narrow, stable |
| IHEEZO | 15.6 | 22% | Anesthetic gel before eye procedures, 82% of units in retina offices; Medicare Part B buy-and-bill (J2403, ASP plus 6%) | Orange Book patent "until 2038" per Harrow (U) | Per-unit transfer price and royalty to Sintetica | Narrow, eroding |
| ImprimisRx compounded | 14.6 | 21% | Compounded perioperative drops sold direct to surgeons | None (compounding) | None | Narrow, stable |
| TRIESENCE and specialty | 11.0 | 16% | TRIESENCE: preservative-free triamcinolone for vitrectomy visualization and ocular inflammation; plus older acquired brands | No patent assumed; sterile manufacturing and approved status are the barrier | None (bought from Novartis) | Narrow, widening |
| BYOOVIZ, later OPUVIZ | stocking only | 0% | Lucentis and Eylea biosimilars for retina practices | None against other biosimilars | Share of net sales to Samsung Bioepis | None |
| BYQLOVI | 0 | 0% | Post-operative steroid drop | Not checked | Undisclosed (Formosa) | None |
| TYRVAYA | 0 | 0% | Nasal spray for dry eye; closed H2 2026 | Not checked | None after purchase; up to USD 70M milestones | Narrow, stable |

Revenue quality (A, from the table): HHI 0.29 (below the 0.35 single-product flag), top line 42%,
protection-weighted life 7.0 years (36% of revenue has no patent at all). The portfolio is
organized, in effect, as **two franchises on one chassis**: an ocular surface franchise (VEVYE,
TYRVAYA, BYQLOVI, compounded drops) and a retina franchise (IHEEZO, BYOOVIZ, OPUVIZ from 2027,
TRIESENCE). That framing is ours (A), and it explains the deal pattern: each new product is
chosen to reuse a call point Harrow already pays for.

### 2.1 VEVYE: the product that decides the thesis

- **What is different.** Cyclosporine dissolved in perfluorobutylpentane (Novaliq's EyeSol):
  no water, no preservative, no emulsion. Labelled for signs and symptoms of dry eye; Restasis and
  Cequa are labelled for tear production. The label difference is mostly a marketing point (U,
  physician comment); the tolerability and onset story is what drives switching.
- **Demand.** 2025 revenue USD 88.7M, up 216% (U). Share of branded dry eye prescriptions 14.6%
  at end of June 2026 vs 7.8% a year earlier, while the branded category fell about 18% in Q1
  (company, IQVIA; U). Company says VEVYE passed Xiidra on monthly prescriptions. NRx +25% and
  TRx +11% in Q1; TRx +21% in Q2.
- **Revenue per script.** Q1 2026 revenue was cut by about USD 8M of gross-to-net (high-deductible
  patients using copay cards at a rate the model did not expect). Business rules changed at the
  end of April; Q2 revenue rose 40% sequentially on 21% TRx growth, which implies revenue per
  script rose about 16% from a depressed Q1 (A). The H2 promise is further ASP recovery as
  deductibles are met plus a top-three PBM coverage win from 2026-08-01 (G).
- **Competition.** Generic cyclosporine 0.05% since 2022 anchors payer step edits; branded
  Restasis, Cequa, Xiidra, Miebo (also Novaliq technology, sold by Bausch), Tyrvaya (now Harrow's)
  and Tryptyr (Alcon, launched 2025 with a free first fill). Alcon names Tryptyr as a growth
  driver in 2026 (U).
- **Kill question.** A PBM that moves VEVYE behind generic cyclosporine in a step edit, or loses
  the August 2026 coverage, would cut new starts faster than any competitor launch.
- **Moat verdict: narrow, stable.** Sources: formulation patents, tolerability, and from Q4 2026 a
  two-product dry eye bag (VEVYE plus TYRVAYA). Share test: passing. Price test: failed in H1
  2026; Q3 is the retest.

### 2.2 IHEEZO: a reimbursement product, not a clinical franchise

- **What it is.** Chloroprocaine 3% gel for ocular surface anesthesia, approved 2022-09-27, the
  first chloroprocaine approval in US ophthalmology. Licensed from Sintetica in 2021 for up to
  USD 18M plus per-unit transfer price and royalty (U).
- **Where the money comes from.** Medicare paid it separately at ASP plus 6% under a
  product-specific J-code (J2403) and, in ambulatory surgery centers, under transitional
  pass-through from 2023-04-01 to 2026-04-01. After pass-through ended, ASC use is packaged into
  the facility payment, and management says the ASC channel is now at zero (U). What remains is
  the retina office, where the gel is applied before intravitreal injections and billed separately.
- **Channel distortion.** 2025 revenue USD 81.3M with USD 35.9M in Q4 2025, then USD 1.9M in Q1
  2026 and USD 15.6M in Q2 (mostly stocking of a new five-pack) against record demand of 65,477
  units (+34% year over year) (U). Revenue and demand have not matched for three quarters, so the
  card marks this line `channel_noise`: 2025 revenue is not a run rate.
- **Substitutes.** Proparacaine and tetracaine drops cost a few dollars a bottle; lidocaine gel
  (Akten) about USD 25-34 a unit; IHEEZO lists around USD 590 a unit (cash price sites, U). The
  pivotal trial was in cataract surgery, not retina injections. Physicians use it because it works
  as a gel and because the office is paid for it.
- **Price test, live.** An approximately 25% net price increase took effect 2026-07-01 (G). Under
  ASP plus 6%, a higher ASP raises the physician's add-on too (with a two-quarter ASP lag), so the
  increase may not cost volume. Q3 and Q4 revenue per demand unit is the test.
- **Kill question.** CMS packaging topical anesthetics into the intravitreal injection payment, or
  a payer policy treating it as a supply. Either would remove the reason to choose a USD 590 gel
  over a USD 3 drop.
- **Moat verdict: narrow, eroding.** The moat is a reimbursement position, which is a policy
  option rather than a franchise. One leg (pass-through) already expired.

### 2.3 The smaller lines, briefly

- **TRIESENCE** is the quiet best moat per dollar: owned outright (no licensor take), the only
  FDA-approved preservative-free triamcinolone for intraocular use, and supply that was absent for
  years before Harrow, which is itself the evidence that manufacturing is the barrier. Units +162%
  in Q2; 2025 revenue USD 9.9M against a long-run ambition of USD 100M a year (G, undated).
- **ImprimisRx** gives surgeon relationships and cash flow with no exclusivity and some
  regulatory exposure (compounding rules). Guided USD 60-65M for 2026 (G).
- **Biosimilars** are commodity products whose value to Harrow is the retina call point it
  already pays for through IHEEZO. OPUVIZ (aflibercept) may launch in the US from January 2027
  under the Samsung Bioepis-Regeneron settlement; it is a 2027 driver, not an H2 2026 one (U).
- **TYRVAYA** was bought for USD 30M upfront plus up to USD 70M in sales milestones; Harrow
  expects over USD 30M of revenue in 2027 (G).

## 3. The H2 2026 bridge: what the guide needs from each line

The company guides FY2026 revenue of USD 350-365M after H1 of USD 114.9M, so H2 must deliver
USD 235-250M against a Q2 run rate of about USD 141M for a half. Holding the smaller lines at our
mid estimates (TRIESENCE and specialty 25, compounded 34 from the guide less H1, new launches
including one quarter of TYRVAYA 8; total 67, all A), full-year revenue by VEVYE and IHEEZO H2
revenue is:

| FY2026 revenue (USD M) | IHEEZO H2 35 | IHEEZO H2 50 | IHEEZO H2 65 |
|---|---|---|---|
| VEVYE H2 70 (1.4x H1) | 287 | 302 | 317 |
| VEVYE H2 85 (1.7x H1) | 302 | 317 | 332 |
| VEVYE H2 100 (2.0x H1) | 317 | 332 | 347 |

No cell reaches the USD 350M low end. Reaching it needs VEVYE to double H1 and IHEEZO to roughly
quadruple H1 **and** about USD 3M or more of upside in the small lines. With IHEEZO at 50, VEVYE
would need about USD 118M in H2, 2.3 times H1. This is our arithmetic on secondary numbers, and
the small lines could surprise (the compounded guide alone spans 5M), but the shape is robust: the
guide is a top-of-every-range outcome, not a central one. The adjusted EBITDA guide (USD 80-100M
after about USD -14M in H1) is more sensitive still, since biosimilar and new-launch revenue
carries lower margins.

## 4. Business model grade (lens C): good, at the bottom edge

| # | Criterion | Score | Why | Class |
|---|---|---|---|---|
| C1 | Gross margin | 2 | 71% in Q2 2026; high-70s targeted for H2 | U / G |
| C2 | Revenue recurrence | 1 | VEVYE is chronic; the rest is procedure-driven repeat buying | U |
| C3 | Pricing power | 0 | Lead product failed the price test in H1; IHEEZO lost pass-through | U |
| C4 | Capital intensity | 1 | Operating cash flow (USD 43.9M in 2025) plus 8.625% notes; no recent equity | U |
| C5 | Operating leverage | 1 | Strong in 2025 (adjusted EBITDA USD 61.9M), reversed in H1 2026 by a pre-committed sales build | U |
| C6 | Reinvestment runway | 2 | Large generic-treated dry eye pool, retina buy-and-bill, repeatable in-licensing into one call point | A |
| C7 | Dependency | 1 | VEVYE 42% and PBM-gated; IHEEZO Medicare-gated; three licensors on top lines | U |
| C8 | Balance sheet fit | 1 | Net debt about USD 216M: 2.4x guided 2026 adjusted EBITDA, 3.5x 2025 actual; no maturity before 2030 | U |

Sum 9 of 16, one zero: **good**. What blocks **great**: no wide moat on any revenue, pricing
power at zero, operating leverage not proven with audited numbers. What would drop it to
**normal**: a second zero, most plausibly C5 if H2 EBITDA misses badly, or C8 if the TYRVAYA
cash outlay and a weak H2 push leverage above about 4x.

What is genuinely good about the model is the **deal-sourcing engine** (deal ledger, U): VEVYE
returned about 11 dollars of 2025 revenue per dollar paid upfront, IHEEZO about 4.5 (flattered
by channel loading), and TYRVAYA was bought for USD 30M upfront from a big-pharma owner that had
stopped prioritizing it. The weak spot in the record is the 2023 Novartis package (USD 130M plus
up to USD 45M): TRIESENCE alone returned 0.06 dollars of 2025 revenue per dollar paid, and the
other four products are not disclosed. Licensing cheaply has a cost that the multiple hides:
licensors keep a royalty or transfer price on VEVYE, IHEEZO and the biosimilars, so Harrow owns
the selling cost and shares the margin.

## 5. People (lens D): trust the strategy, discount the guidance

| Sub-score | Evidence | Reading |
|---|---|---|
| D1 Guidance credibility | 2 of 7 resolved guides hit (FY2023 miss, FY2024 beat, FY2025 original miss, FY2025 cut guide hit, H1 2026 miss, Q2 2026 miss, BYQLOVI launch late). Posterior 0.36, 80% interval 0.19-0.55; mean signed error -4.3% | Habitual mild optimist. The CEO has called the company's guidance "directional" (2025 letter, U): read guides as targets |
| D2 Capital allocation | Deal multiples above; refinanced 11.875% notes and an Oaktree facility into 8.625% notes (2025); prefers debt to equity | Strong sourcing, leverage as the price of avoiding dilution |
| D3 Alignment | CEO open-market purchase of about USD 302K at USD 30.20 (U); say-on-pay about 86% support; 10.6% of votes withheld on the CEO's re-election (2026 meeting, U) | Aligned; some shareholder dissent |
| D4 Costly signals | One pre-committed sacrifice (2026 sales build: about 100 roles, SG&A USD 185-205M, payoff H2 revenue and FY EBITDA, checked by the FY2026 report): pending. One post-hoc (VEVYE gross-to-net explanation), one unqualified (2022 pure-play pivot), one provisional short-termist (IHEEZO Q4 2025 loading ahead of pass-through expiry) | Long-term intent is real and unproven; 2026 is the test |
| D5 Candor | Auditor change and a late FY2024 10-K (one flag). Product disclosure shifts between groupings (TRIESENCE inside specialty, IHEEZO swings explained after the fact) | Watch for KPI drift in Q3 |
| D6 Bench | Commercial leadership disclosed (CCO Patrick Sullivan on calls); 40 Viatris staff join in Q4 2026 | Not scored yet |

**People grade: discount**, by the rule (posterior below 0.4 with negative signed error), and
close to the boundary: dropping the overlapping Q2 guide moves the posterior to exactly 0.40.
Resolution in March 2027: if the three FY2026 guides (revenue, adjusted EBITDA, VEVYE over 100M)
all hit, the posterior rises to 0.50 (verify); if all miss, it falls to 0.29.

The useful split: the **strategy** (cheap in-licensing into two call points, accepting a weak
year to double the sales force) is coherent and has worked before; the **calendar** (when
revenue arrives and how much) has repeatedly been late. Sacrificing H1 2026 for H2 was announced
in advance and quantified, which is exactly what a long-term operator does. Whether it was a
sacrifice or an overreach is decided by numbers in March 2027, not by tone on a call.

## 6. So what for the hold memo

1. **Scenario weights.** The memo's base (low end of the guide) and bull (guide met) both assume
   the revenue guide is met; together they carry 65%. The card caps guidance-dependent scenarios
   at the upper credible bound, 55%, and the bridge in section 3 says even that is generous.
   Moving 5 points each from base and bull to bear (45 / 40 / 15) lowers the
   probability-weighted value from about 32 to about 29 against a 2026-10-06 price of 30.35.
   The small positive edge in the memo disappears. Probabilities are A.
2. **Exit multiple.** A good, not great, model supports the memo's 2.5-4.5x EV/sales range; it
   does not support re-rating to a premium multiple on growth alone.
3. **Size.** The discount people grade supports the memo's rule: hold only at a size whose bear
   case is absorbable, no adds before Q3.
4. **Two new Q3 checks that grade the products rather than the total:**
   - VEVYE price test: Q3 VEVYE revenue grows faster than TRx (revenue per script up). Pass moves
     C3 from 0 to 1.
   - IHEEZO price test: Q3 IHEEZO revenue per demand unit at least 1.2x the Q2-implied level with
     units not falling. Fail moves the IHEEZO moat to `none`.

## 7. Falsifiers for the grades

- Business model drops to normal: H2 2026 adjusted EBITDA below about USD 40M (C5 to 0).
- Moat on VEVYE drops to none: loss of the top-three PBM coverage or a step edit behind generic
  cyclosporine at a major PBM.
- People grade rises to verify: FY2026 revenue at or above USD 350M with positive H2 EBITDA.

## Sources

[Q2 2026 release (Nasdaq copy)](https://www.nasdaq.com/press-release/harrow-announces-second-quarter-2026-financial-results-2026-08-10);
[Q2 call highlights (MarketBeat)](https://www.marketbeat.com/instant-alerts/harrow-q2-earnings-call-highlights-2026-08-11/);
[Q2 slides (Investing.com)](https://www.investing.com/news/company-news/harrow-q2-2026-slides-strong-demand-growth-amid-profitability-push-93CH-4851874);
[Q2 8-K exhibit 99.1](https://www.sec.gov/Archives/edgar/data/0001360214/000149315226036865/ex99-1.htm);
[Q1 2026 release (GlobeNewswire)](https://www.globenewswire.com/news-release/2026/05/11/3292306/0/en/index.html);
[Q1 gross-to-net detail](https://insights.munich-startup.de/news/feed/harrow-reports-44-2m-q1-revenue-amid-8m-gross-to-net-modelling-hit-reaffirms-350m-365m-2026-guidance);
[Q4 2025 release and 2026 guidance](https://www.globenewswire.com/news-release/2026/03/02/3247864/0/en/Harrow-Announces-Q4-and-Full-Year-2025-Financial-Results-and-2026-Financial-Guidance.html);
[Q4 2025 call highlights (Yahoo)](https://finance.yahoo.com/news/harrow-q4-earnings-call-highlights-161826840.html);
[FY2025 10-K](https://www.sec.gov/Archives/edgar/data/1360214/000149315226008562/form10-k.htm);
[2025 letter to stockholders](https://www.harrow.com/static-files/5c3f6f53-c5ec-456f-b360-af2e2179b9ff);
[FY2025 guidance cut (Seeking Alpha)](https://seekingalpha.com/news/4520142-harrow-updates-2025-revenue-guidance-to-270m-280m-as-vevye-and-iheezo-drive-growth-with-major);
[2024 guidance (TipRanks)](https://www.tipranks.com/news/the-fly/harrow-health-backs-2024-revenue-guidance-of-at-least-180m-consensus-184-91m);
[Novaliq VEVYE license (Business Wire)](https://www.businesswire.com/news/home/20230718821365/en);
[VEVYE patents (Pharsight)](https://pharsight.greyb.com/drug/vevye-patent-expiration);
[VEVYE patents (DrugPatentWatch)](https://www.drugpatentwatch.com/p/tradename/VEVYE);
[Sintetica IHEEZO license (Business Wire)](https://www.businesswire.com/news/home/20210727005107/en);
[IHEEZO J-code](https://ophthalmologytimes.com/view/harrow-announces-permanent-product-specific-j-code-for-chloroprocaine-hydrochloride-ophthalmic-gel-for-ocular-surface-anesthesia);
[IHEEZO pass-through status (BioSpace)](https://www.biospace.com/harrow-announces-transitional-pass-through-reimbursement-status-for-iheezo-chloroprocaine-hydrochloride-ophthalmic-gel-3-percent);
[IHEEZO price (Drugs.com)](https://www.drugs.com/price-guide/iheezo); [Akten price (Drugs.com)](https://drugs.com/price-guide/akten);
[Novartis portfolio deal (BioSpace)](https://www.biospace.com/harrow-enters-into-agreement-to-acquire-exclusive-u-s-rights-to-ilevro-nevanac-vigamox-maxidex-and-triesence);
[Samsung Bioepis partnership (Business Wire)](https://www.businesswire.com/news/home/20250717437977/en);
[BYOOVIZ relaunch (Business Wire)](https://www.businesswire.com/news/home/20260701576499/en);
[OPUVIZ settlement, US launch from January 2027 (Ophthalmology Times)](https://www.ophthalmologytimes.com/view/samsung-bioepis-reaches-settlement-agreement-for-eylea-aflibercept-biosimilar);
[BYQLOVI license (Business Wire)](https://www.businesswire.com/news/home/20250609515264/en/harrow-acquires-u.s.-commercial-rights-to-byqlovi%e2%84%a2-clobetasol-propionate-ophthalmic-suspension-0.05-from-formosa-pharmaceuticals);
[TYRVAYA acquisition 8-K](https://www.sec.gov/Archives/edgar/data/0001360214/000149315226036256/form8-k.htm);
[TYRVAYA (Ophthalmology Times)](https://www.ophthalmologytimes.com/view/harrow-acquires-global-rights-to-tyrvaya);
[Tryptyr launch (Optometry Times)](https://www.optometrytimes.com/view/alcon-commercially-launches-tryptyr-for-signs-and-symptoms-of-dry-eye-disease-in-the-us);
[Harrow history and spin-outs (Wikipedia)](https://en.wikipedia.org/wiki/Harrow_Health);
[2026 annual meeting vote results (8-K)](https://www.boardroomalpha.com/sec/hrow-8-k-2026-06-22-0001493152-26-029486).
