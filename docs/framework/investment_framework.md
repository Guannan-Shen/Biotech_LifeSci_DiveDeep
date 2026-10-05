# Small and Mid-Cap Biotech Investment Framework

Version: 2026-10-03 draft by the investor (originally written in Chinese), translated
and restructured 2026-10-05. Horizon: 6 to 24 months. Fundamentals lead; trend assists.

Purpose: improve decisions through better evidence, better entry prices and explicit
risk budgets. Neither the framework nor its trading parameters have been backtested,
so it makes no claim of higher returns yet. It is a research framework. It does not
contain current buy or sell rankings or price targets, because live prices, fully
diluted share counts and the latest events were not verified when it was written.

---

## 1. Name the path to profit first

Every position must state:

- What the current price implies the market expects.
- What evidence in the next 6 to 24 months would change that expectation.
- The per-share value after that change.
- How much cash will burn and how many shares will be issued while waiting.

Tag every record as **fact / management guidance / own assumption / unverified**.
Management timelines are never treated as facts.

## 2. Research grouping of the investor's list

These are analytical groupings and open questions, not valuation-ranked
recommendations. A company can span groups; value segments separately. Whether ILMN,
TEM, TXG and TWST fit the small/mid-cap mandate is decided by market cap on the research
date (see `config/universe.yaml` for the latest snapshot).

| Company | Research type | Key validation question | Valuation approach |
|---|---|---|---|
| PACB / Pacific Biosciences | Sequencing instruments + consumables; operating repair | Do active installed base and consumable pull-through per system rise together? | Normalized gross margin and cash-flow scenarios; EV/revenue only as a cross-check |
| DNA / Ginkgo Bioworks | Automated labs; R&D services platform in transition | Do paid usage, repeat purchase, utilization and unit contribution improve? | Conservative operating scenario plus cash burn; long-dated platform value separately |
| QSI / Quantum-Si | Early protein-sequencing tool | Does technical performance become reliable delivery, paid placements and consumable repeat orders? | Success / delay / failure scenarios with post-financing share count |
| RXRX / Recursion | Clinical pipeline plus discovery platform | Do human data and partner progress validate the platform? | Per-asset rNPV plus partnership economics |
| SDGR / Schrödinger | Computational software plus drug-discovery equity | What is the quality of software contracts and renewals? What are the drug assets worth? | Sum of parts: software, pipeline, equity stakes, cash |
| CERT / Certara | Biosimulation software and services | Can software growth, renewals and services margin improve? | Normalized FCF; software and services valued separately |
| TEM / Tempus AI | Clinical testing plus data business | Does test volume convert to collections? Is data licensing recurring? | Segment valuation of testing and data; strip acquisition effects |
| GRAL / GRAIL | Multi-cancer early detection | Do clinical utility, regulatory path and payer coverage support scale? | Billable tests x net ASP x contribution margin, layered with regulatory scenarios |
| ILMN / Illumina | Mature sequencing tools | How do consumable demand, product transitions and competition affect cash flow? | Normalized earnings and FCF |
| TXG / 10x Genomics | Single-cell and spatial biology tools | Can platform usage and consumable repeat orders offset competition and budget pressure? | Active installed base, consumable margin, cash-flow scenarios |
| EDSA / Edesa | Clinical event-driven | Do the specific trial, primary endpoint and funding support the next key readout? | Per-asset event tree; verify latest trial and financing status first |
| TWST / Twist | Synthetic DNA and life-science tools | Can revenue mix, gross margin and capacity utilization create operating leverage? | Segment gross margin and FCF path |

Additional names added 2026-10-05 (see `docs/framework/archetypes.md`): HROW and ETON
(commercial specialty / rare-disease pharma), SLS (phase 3 binary), REPL and IOVA
(post-approval launch execution).

## 3. Three gates before any buy discussion

### Evidence gate

- One sentence states which problem the product solves, for whom, and who pays.
- A defined future validation event exists and can plausibly occur within the horizon.
- At least two pieces of evidence that would break the thesis are written down.
- Undisclosed key data is marked unknown and never filled with story.

### Survival gate

- Usable cash = unrestricted cash and highly liquid investments. Unawarded grants,
  future milestones and unused ATM capacity are not cash.
- Forecast R&D, launch preparation, capex, working capital and debt maturities by
  quarter. Never compute runway from the last quarter's net loss alone.
- Initial screening rule: cash covers the next key event plus at least 12 months of
  buffer. This is a conservative screen and is adjusted by business type.
- Net cash is not a value floor, because it may keep burning.
- **Seniority check (added 2026-10-05, D-019).** Cash belongs to common shareholders
  only after senior claims: debt, convertible notes, preferred stock liquidation
  preference with accrued dividends, and any royalty or revenue-interest financing.
  Compute `residual cash = usable cash - senior claims` before calling a stock "below
  cash". Also list ratchet (down-round) terms, because they transfer value from common
  holders whenever the company raises at a lower price. Lesson from the MRLN memo,
  where a USD 120M preferred turned an apparent below-cash stock into one priced well
  above its residual cash.

### Price gate

- At least three scenarios (bear, base, bull) on the same valuation date.
- Each scenario includes financing, delays and share-count changes.
- State how much success the market already prices in, beyond future market size.

## 4. Clinical-stage companies: update probabilities item by item

| Stage | Core questions | Common misreading |
|---|---|---|
| Preclinical / Phase 1 | Target rationale, exposure, target engagement, tolerability, achievable dose | Treating human safety or mechanism signals as efficacy proof |
| Phase 2 | Randomized control, effect size, confidence interval, clinical relevance, durability | Treating small samples, post-hoc subgroups or cross-trial comparisons as confirmation |
| Phase 3 | Primary endpoint, statistical analysis plan, dropout, changing standard of care, overall benefit-risk | Reading only the p-value or the press-release headline |
| Filing / review | Label scope, manufacturing quality, extra trial requirements, regulator communication | Treating filing acceptance or an AdCom vote as approval |

Each core program gets a **trial card**: drug, indication, target, registry ID, phase,
enrollment, comparator, primary endpoint, effect size, confidence interval, safety,
prespecified subgroups, follow-up maturity, expected readout window, source and update
time. (Schema: `docs/modules/clinicaltrials.md`.)

Probabilities are ranges. Start from historical priors for the same indication and
phase, then update with program evidence. An AI label never raises the probability of
success by itself. Assets within one platform can share mechanism and technology risk;
do not assume independence.

**Asset rNPV**: future commercial cash flows weighted by cumulative stage-success
probability, minus future R&D and launch spend weighted by the probability of reaching
each stage, discounted. Corporate overhead, debt and cash are handled at company level
to avoid double counting.

## 5. Post-approval execution: from label to cash

Model at least 8 quarters after approval.

Patient funnel: label-eligible patients -> diagnosed -> physician willing to prescribe
-> payer approves -> therapy starts -> therapy continues.

Revenue model: quarterly new-patient cohorts, each with retention, treatment duration
and net price; sum all active cohorts. One-time therapies (cell and gene therapy) get a
separate model; never apply chronic-therapy persistence logic to them.

| Dimension | Track each quarter | Signal to re-underwrite |
|---|---|---|
| Physician adoption | Active prescribers, new prescribers, repeat prescribing | Prescriber count grows while therapy starts stall |
| Payer coverage | Covered lives, prior auth, denial rate, out-of-pocket burden | High nominal coverage but patients cannot access drug |
| Patient conversion | New patients, script-to-therapy time, abandonment | Scripts rise without matching therapy starts |
| Persistence | Discontinuation, adherence, duration on therapy | Efficacy or tolerability pushes refills below model |
| Revenue quality | Gross-to-net, channel inventory, returns, collections | Strong initial stocking, weak end demand |
| Unit economics | Contribution per patient, SG&A, gross margin | Revenue growth needs faster-growing sales spend |
| Supply and competition | Yield, supply, treatment guidelines, competitor labels | Supply disruption or a competitor resets standard of care |

**Commercial inflection** (working rule, to be validated): two consecutive quarters of
improving patient starts and net revenue, explainable gross margin, and cash burn on
plan.

## 6. Tools, software, diagnostics and automated labs need their own models

- **Tools**: new-placement revenue + active installed base x consumable revenue per
  system + service revenue. Total installed base differs from active installed base;
  product transitions can double count. Watch for price cuts buying shipments, and
  whether consumable margin offsets them.
- **Software**: track contract value (ACV), renewals, customer expansion, cash
  collections, deferred revenue and recognized revenue separately. License-model
  changes can shift recognition. Separate one-time milestones and equity gains from
  the recurring software business.
- **Automated labs**: sellable machine hours x paid utilization x net price, minus
  reagents, operators, maintenance and depreciation. Customer counts and partnership
  announcements do not substitute for utilization and contribution margin. Separate
  lab-build project revenue from recurring services.
- **Diagnostics**: billable tests x realized net collection; plus sensitivity,
  specificity, PPV, downstream diagnostic burden and clinical utility. Volume growth
  can be offset by price or payer mix.

**AI value validation chain**: better technical performance -> better customer or
clinical outcome -> paid demand -> gross margin and cash flow -> per-share value after
financing. Discount at the first link that lacks evidence.

## 7. How recent disclosures reshape the research questions

Targeted examples, not a full event audit. All figures are as reported in the
investor's 2026-10-03 draft and have **not** been re-verified in this repository yet
(evidence class: `unverified` until a connector or reviewer confirms them).

- **PACB**: Q2 2026 revenue USD 39.0M vs 39.8M a year earlier; consumables 20.1M vs
  18.9M; Revio annualized pull-through about 202K vs 219K. Consumables total improved,
  per-system economics still need tracking; this alone does not prove AI-driven recovery.
  [Company release](https://www.pacb.com/press_releases/pacbio-announces-second-quarter-2026-financial-results/)
- **DNA**: Q2 continuing Cell Engineering revenue about USD 20.16M vs 39.13M; Nebula
  expansion and lab-build projects disclosed. Model business contraction, project
  delivery and recurring services separately. The OpenAI / Lilly / Novo revenue
  contributions mentioned by the investor were not verified and are excluded from
  booked revenue. [SEC exhibit](https://www.sec.gov/Archives/edgar/data/1830214/000162828026053319/ex991earningspr.htm)
- **QSI**: August 2026 update moved expected Proteus launch to Q2 2027; quarterly
  revenue USD 344K; company expects funding into Q4 2028 (management guidance). Focus
  on engineering, manufacturing, delivery and funding pressure after the delay.
  [Company update](https://www.quantum-si.com/press-releases/quantum-si-reports-second-quarter-2026-financial-results-and-provides-proteus-development-update/)
- **SDGR**: Q2 ACV +27%, software recognized revenue -10%, attributed to a hosted
  license transition. Read contract demand and accounting recognition together.
  [Company release](https://ir.schrodinger.com/press-releases/news-details/2026/Schrdinger-Reports-Second-Quarter-2026-Financial-Results/)
- **RXRX**: August disclosure of additional Phase 2 REC-4881 data expected November
  2026 (management guidance). Check for changes before the event and return to primary
  trial data. [Company release](https://ir.recursion.com/news-releases/news-release-details/recursion-reports-second-quarter-financial-results-genentech)
- **TEM**: Q2 revenue in both testing and data; net income includes unrealized gains
  on securities, so separate operating performance from investment gains.
  [Company release](https://www.tempus.com/news/pr/tempus-reports-second-quarter-2026-results/)
- **GRAL**: Q2 Galleri volume +35%, revenue +24%, which invites a price and customer
  mix study; investor site lists a 23 September advisory committee announcement
  supporting approval. Treat AdCom opinion, formal approval and payer coverage as
  three separate nodes.
  [Quarterly release](https://investors.grail.com/news-releases/news-release-details/grail-reports-second-quarter-2026-financial-results)

Initial sources for the rest: [CERT Q2](https://www.sec.gov/Archives/edgar/data/1827090/000182709026000026/q22026earningsreleaseex99.htm),
[ILMN results](https://investor.illumina.com/financial-information/quarterly-results),
[TXG Q2](https://www.sec.gov/Archives/edgar/data/1770787/000162828026054273/txg-20260806xexx991.htm),
[TWST investors](https://investors.twistbioscience.com/), [EDSA news](https://www.edesabiotech.com/news/).
EDSA's lead program status, financing and registry entries are unverified; no
probability of success is assigned yet.

## 8. Limits on the two reference charts

See `docs/research/ai_drug_discovery_cycle_times.md` and
`docs/research/specialist_concentration.md`. In short: the McKinsey cycle-time chart
supports a hypothesis that discovery may be faster, but mixes start and end points and
is selected toward visible successes, so it cannot yield industry success rates,
clinical-time savings or stock returns. The specialist-concentration table is a
candidate pool; its date, scoring method and 13F lag must be known before it becomes
a signal.

## 9. Expected per-share return and risk budget

For each scenario s at the same horizon T:

```
P_s(T) = [business equity value_s(T) + net cash not already in business value_s(T)]
         / fully diluted shares_s(T)

E[R_T] = sum_s p_s * (P_s(T) / current price - 1),   sum_s p_s = 1
```

Be explicit whether value already includes cash, debt, R&D spend and financing
proceeds. Convertibles: in the conversion scenario add shares and remove the debt; in
the non-conversion scenario keep the debt. Never both.

Worked example (hypothetical): price 10; 12-month bull/base/bear prices 20/11/2 with
probabilities 25%/45%/30%. Expected price 10.55, expected return 5.5%. The bull case
doubles, yet the 80% downside tail makes the odds unattractive. Run sensitivity on the
probabilities; decimals do not create precision.

Single-event position cap = acceptable portfolio loss / stress-case drawdown. Example:
accept 0.5% portfolio loss on one event, stress drawdown 80%, cap about 0.625%. Also test
a 100% loss case. Actual budgets depend on existing holdings and tolerable drawdown.

Aggregate concentration across shared targets, funding climate, research budgets,
payers, AI theme and adjacent readout dates.

## 10. Trend overlay: initial, testable rules

Starting parameters, not claimed to be optimal (tested in Phase 3, H5).

- Weekly at a fixed time: adjusted close, 200-day and 50-day moving averages, 13-week
  relative strength.
- Candidate buy: fundamentals pass the three gates, price above a rising 200-day MA,
  relative strength vs the peer benchmark improving, and the move confirmed by volume
  (breakout day relative volume above 1.5, up/down volume ratio above 1; definitions in
  `docs/modules/market_trend.md`, section 2a).
- Start with one third of the planned position; add only on new evidence that improves
  value or on further trend confirmation, within the total risk budget.
- Relative benchmark: the matching sub-industry first. XBI fits clinical biotech; it
  does not represent tools and software.
- Two consecutive weekly closes below the 200-day MA: reduce per the pre-agreed rule.
  If a key fundamental assumption breaks, re-underwrite immediately without waiting for
  the moving average.
- Before key clinical or regulatory events, recompute gap-risk loss; stop orders do not
  guarantee fill prices.
- After an event, update probabilities and per-share value before restoring a position.
  A falling price never lowers the evidence bar.

Validation: historical universe with delisted names; financials enter on actual
publication dates; adjust for splits, dilution and costs; compare fundamentals-only,
trend-only, combined and benchmarks; check out-of-sample performance, max drawdown,
turnover, slippage and missed rebounds.

## 11. One-page memo template

1. Company / ticker / business archetype / research date / horizon.
2. Price, shares, market cap, debt, restricted and unrestricted cash, each with its date.
3. Core view: which two variables improve over the next 2 to 4 quarters?
4. Variant perception: what does the price assume, and how does our view differ?
5. Three key metrics: definition, current value, target range, disclosure frequency.
6. Catalysts: date window, source, certainty, delay scenario.
7. Three scenarios: probability ranges, financing, share count, business value, per-share value.
8. Falsifiers: specific data or dates. "Long-term thesis intact" is not a falsifier.
9. Runway: base and stress cases, cash remaining after the key event.
10. Trend: moving averages, relative strength, liquidity, event risk.
11. Action: watch / candidate / hold / reduce; triggers and risk budget.
12. Evidence log: facts, guidance, assumptions, unknowns, with source links.

## 12. Execution order

Build complete memos for PACB, SDGR and RXRX first to calibrate the tools, software +
pipeline, and clinical platform models. Then TEM/GRAL for payer and diagnostics models,
QSI/DNA for early products and turnarounds. Research order, not buy order.

Weekly: trend and event calendar. Quarterly: rebuild metrics, cash and dilution
scenarios. After clinical or regulatory events: re-examine evidence. A thesis with no
verifiable node inside the horizon moves to the long-term watch pool.
