# Memo (draft): MRLN, Merlin, Inc.

Status: **draft, evidence incomplete**. Adjacent-sleeve pilot (D-013). Research date
2026-10-05 (revision 2: capital structure corrected, dissent scan added). Horizon 6 to
24 months. Template: framework section 11.

Evidence classes in brackets: [F] fact from a primary filing, [G] management guidance,
[A] own assumption, [U] unverified (secondary source, search snippet or vendor feed).
The SEC filings could not be opened from the cloud environment, so filing-derived
numbers below are [U] until checked on a machine with EDGAR access.

## Revision note

Revision 1 called MRLN a "trading below cash" setup with a cash floor of about USD 1.64
per share. That ignored the USD 120M Series A preferred stock issued in the PIPE, which
sits ahead of common shareholders. After the preference, residual cash for common is
about USD 0.32 per share and the market prices roughly USD 120M of option value into the
technology. The framework now requires a seniority check (D-019).

## 1. Identity

| Item | Value |
|---|---|
| Company | Merlin, Inc. (Merlin Labs), Boston; CIK 0002028707 [U] |
| Business | Aircraft-agnostic AI autonomy ("Merlin Pilot") for military and civil aircraft [U] |
| Listing | Nasdaq MRLN since 2026-03-17, via business combination with Inflection Point Acquisition Corp. IV; more than USD 200M gross proceeds including a USD 120M preferred PIPE [U] |
| Archetype | `regulated_deeptech`, sleeve `adjacent` |

## 2. Capital structure snapshot

| Item | Value | Date | Class |
|---|---|---|---|
| Price / market cap | USD 1.57 / USD 151.5M; 52-week range 1.57 to 17.00 | 2026-10-05 | [U: FMP] |
| Common shares | about 96.5M (market cap / price) | 2026-10-05 | [A] verify on 10-Q cover |
| Cash and short-term investments, no debt | USD 183.9M | 2026-06-30 | [U] |
| Operating cash outflow | USD 50.9M for H1 2026 | 2026-06-30 | [U] |
| **Series A preferred** | USD 120M PIPE; USD 12.00 stated value; dividends 10% cash or 12% in kind, cumulative and compounding; senior liquidation preference = greater of accrued value or as-converted value | issued 2026-03 | [U: 10-Q / 424B3 via search] |
| Preferred conversion price | Reset from USD 12.00 to USD 6.67 on 2026-05-01 (down-round adjustment triggered by a May 2026 PIPE) | 2026-05-01 | [U] |
| May 2026 PIPE | Common stock plus a warrant for up to 4.0M shares at USD 6.67 (down-round adjustable); 13.3M shares registered for resale by a PIPE investor | 2026-05 | [U] |
| Accounting impact | Preferred carried in mezzanine equity at USD 162.5M; USD 60.8M deemed dividend from the down-round adjustment plus USD 9.6M dividends and accretion reduce income to common | Q2 2026 | [U] |
| Short interest | 7.3M shares, 9.6% of float, up about 610% since March | recent | [U: finviz via search] |

## 3. Runway, three ways [A]

Trailing burn = 50.9 / 2 = USD 25.4M per quarter (H1 includes pre-listing months).
Adjusted EBITDA loss in Q2 was USD 27.8M, about triple a year earlier [U], so the
post-listing run rate may be above trailing.

| Case | Burn per quarter | Months from 2026-06-30 | Months from today |
|---|---|---|---|
| Trailing | 25.4 | 21.7 | 18.5 |
| Stress (x1.25) | 31.8 | 17.3 | 14.1 |
| Ramp (x1.5) | 38.2 | 14.5 | 11.3 |

Cash dividends on the preferred (10% of about USD 124M, about USD 12M a year) would
shorten runway further; paying in kind instead grows the preference. The investor's
15-month estimate sits between the stress and ramp cases.

## 4. Residual cash and option value [A]

| Item | Value |
|---|---|
| Projected cash 2026-09-30 (one more trailing quarter) | about USD 158.5M |
| Preferred accrued value (12% in kind, compounding since 2026-03) | about USD 128M |
| **Residual cash to common** | about USD 31M, **USD 0.32 per share** |
| Common option value = market cap - residual cash | about USD 121M |
| Preferred as-converted at USD 6.67 | about 19M shares; conversion is worth about USD 30M at USD 1.57, far below the preference, so holders keep the preference |
| Rough fully diluted share count | about 120M (common + as-converted preferred + 4M warrants), before options, RSUs and earnouts |

Reading: common shareholders own a call option on the technology, funded by cash that
the preferred holders get first. Every further down round can reset terms against
common holders again.

## 5. Bad-news register (dissent scan, 2026-10-05)

| # | Item | Severity | Source tier | Class |
|---|---|---|---|---|
| B1 | **Certification path abandoned.** On 2026-09-09 Merlin withdrew its small-aircraft (Cessna Caravan) supplemental type certificate application with the New Zealand CAA, pursued since 2021 and recently at SOI 3, to pursue a large-aircraft civil certification strategy. The nearest civil certification catalyst is gone; the new path is longer and undated. New Zealand stays a test center. | High | Company release (T1) | [F per release] |
| B2 | **Revenue far below the deal projections.** IPO coverage cited 2025 revenue of USD 8.5M and a 2026 projection of USD 32M. H1 2026 revenue was USD 3.2M (Q1 1.0M, Q2 2.2M, Q2 down 29% year over year). Reaching 32M needs about 28.8M in H2. | High | Press + company results | [U] |
| B3 | **Preferred stock with ratchet.** Senior USD 120M preference, 10-12% dividends, conversion price already cut from 12.00 to 6.67 after one quarter; warrants with down-round adjustment. Common holders bear the first loss and further resets. | High | Filings via search | [U] |
| B4 | **Share supply.** 13.3M PIPE shares registered for resale in May; price down about 83% from the April level near USD 9.94. | Medium | Filings / market data | [U] |
| B5 | **Short interest rising.** 9.6% of float, up about 610% since March; borrow reported tight after listing. No published short report found. | Medium | Market data / retail commentary (D5) | [U] |
| B6 | **Governance and culture complaints.** Anonymous Glassdoor reviews describe abusive management, a revolving door of C-suite executives (most turned over twice in three years) and talent loss. Anonymous and unverifiable; check executive turnover against 8-K Item 5.02 filings and the S-4/proxy. | Medium (if corroborated) | Anonymous reviews (D5) | [U] |
| B7 | **Technical novelty questioned.** Autonomy researcher Missy Cummings: "Merlin isn't doing anything new," adding "Maybe they'll do it better." General skepticism about AI-pilot certification, no specific allegation. Quote found via search summary; the original article is still to be located. | Low | Domain expert (D3) | [U] |
| B8 | **Military programs are prototypes.** KC-135 (with SNC, test flights since 2024) and C-130J (CDR completed 2026-06-04) are development efforts; no program of record found. Government interest is real but not yet recurring revenue. | Medium | Company and trade press | [U] |

Not found: lawsuits, SEC or DOJ investigations, crashes or test incidents, a short-seller
report, or a whistleblower comparable to the Humacyte case. Absence in web search is weak
evidence; the EDGAR full-text search for "litigation", "subpoena", "material weakness"
and "going concern" in Merlin filings is the next check.

## 6. Core view: which variables matter in the next 2 to 4 quarters

1. **Contracted revenue**: does H2 2026 revenue close any of the gap to the USD 32M
   projection, and do military prototype programs convert to funded follow-ons?
2. **Burn and financing terms**: quarterly burn vs the stress case, and whether any new
   raise triggers another ratchet against common holders.
3. **The new certification plan**: a dated, regulator-acknowledged large-aircraft
   certification basis, or only intent.

## 7. Variant perception

Market view implied by price: about USD 120M of value for the technology after the
preferred, with heavy skepticism after the certification pivot and revenue gap. A
differing bullish view needs evidence of contracted revenue or a program of record; a
differing bearish view says the option value is still too high given B1-B3 and a likely
dilutive raise within 12 to 18 months.

## 8. Key metrics to track

| Metric | Definition | Current | Frequency |
|---|---|---|---|
| Quarterly operating cash burn | 10-Q cash flow, de-cumulated | about 25M (H1 average) [U] | Quarterly |
| Revenue vs projection | Quarterly revenue vs USD 32M FY2026 deal projection | 3.2M H1 [U] | Quarterly |
| Preferred accrued value and conversion price | 10-Q mezzanine equity note | about 128M; 6.67 [A]/[U] | Quarterly |
| Funded obligations | 10-Q remaining performance obligations; USAspending | Unknown | Quarterly / monthly |
| Certification basis | Large-aircraft certification plan status with FAA or other authority | Announced intent only [F per release] | Event-driven |
| Volume and supply | Relative volume and turnover around resale and lockup dates (M5, section 2a) | High turnover [U] | Weekly |

## 9. Catalysts

| Window | Event | Class |
|---|---|---|
| Q3 results, likely November 2026 | Revenue vs projection, burn, any guidance change | [G] |
| Next few quarters | C-130J aircraft integration and ground test | [G] |
| Unknown | Large-aircraft certification basis announcement | [G] |
| Unknown | Further resale registrations, warrant and earnout dates | [U] |

## 10. Scenarios (structure; probabilities after the evidence pass)

| Scenario | What must be true | Financing | Value to common |
|---|---|---|---|
| Bear | Revenue stays near current run rate, burn rises, raise in 2027 at a discount with another ratchet | Dilutive raise plus preferred terms reset | Near residual cash (about 0.3) or below after dilution |
| Base | Prototype revenue grows slowly, burn steady, no new certification date | Raise or ATM in 2027 | Some option value survives; dilution caps upside |
| Bull | Program of record or large production contract; credible certification basis | Raise from strength | Option value expands; preferred converts |

## 11. Falsifiers

- Q3 or Q4 2026 revenue does not move materially toward the projection.
- Quarterly operating burn above USD 32M with no matching revenue.
- Any equity raise below USD 6.67 that resets preferred or warrant terms again.
- Corroborated executive departures (8-K Item 5.02) in the CFO, certification or
  engineering leadership roles.

## 12. Trend and supply

Price at the 52-week low on 2026-10-05. No entry under the trend overlay. Use relative
volume and turnover around supply dates (H11) to judge when overhang has cleared.

## 13. Next research steps

1. On a machine with EDGAR access: Q2 10-Q (accession 0001628280-26-056882) for share
   count, preferred note, warrants, earnouts, restricted cash, remaining performance
   obligations, litigation and risk-factor changes.
2. Read the 2026-09-09 release and any 8-K for the certification pivot: cost savings,
   headcount, revised timelines.
3. Pull the merger proxy/S-4 for the original projections and compare line by line.
4. EDGAR full-text search on Merlin filings for "going concern", "material weakness",
   "subpoena", "litigation".
5. Check 8-K Item 5.02 filings for executive turnover (tests B6).
6. Search podcasts and YouTube (M15) for former Merlin engineers, Air Force program staff
   and certification experts; log findings in `data/reference/dissent_register.csv`.

## Sources

- [Q2 2026 results, SEC 8-K exhibit](https://www.sec.gov/Archives/edgar/data/0002028707/000162828026056712/merlininc8-kxex99181326.htm)
- [Q2 2026 10-Q](https://www.sec.gov/Archives/edgar/data/0002028707/000162828026056882/mrln-20260630.htm)
- [Earlier 10-Q with preferred terms](https://www.sec.gov/Archives/edgar/data/0002028707/000121390026057138/ea0289176-10q_merlin.htm)
- [PIPE resale prospectus supplement](https://www.sec.gov/Archives/edgar/data/0002028707/000162828026058115/merlinpipeprospectussupple.htm)
- [13.3M shares registered for resale (Stock Titan)](https://www.stocktitan.net/sec-filings/MRLN/424b3-merlin-inc-prospectus-filed-pursuant-to-rule-424-b-3-7bbe4f07ce84.html)
- [Closing 8-K summary, PIPE preferred (Stock Titan)](https://www.stocktitan.net/sec-filings/BACQ/8-k-inflection-point-acquisition-corp-iv-reports-material-event-d2a782a0f167.html)
- [Large-aircraft certification strategy, withdrawal of NZ STC (GlobeNewswire, 2026-09-09)](https://www.globenewswire.com/news-release/2026/09/09/3358555/0/en/merlin-announces-plans-to-pursue-a-civil-certification-strategy-for-large-aircraft.html)
- [Simple Flying on the New Zealand withdrawal](https://simpleflying.com/merlin-abandon-new-zealand-automony-plan-chase-7000-us-airline-cockpits/)
- [Washington Technology on the listing](https://www.washingtontechnology.com/companies/2026/03/merlin-labs-public-offering-collects-200m-build-ai-autopilot-any-aircraft/412209/)
- [MarketBeat price history](https://www.marketbeat.com/stocks/NASDAQ/MRLN/)
- [Finviz short interest](https://finviz.com/stock?t=MRLN&ty=si)
- [Glassdoor reviews](https://www.glassdoor.com.au/Reviews/Merlin-Labs-Reviews-E3324504.htm)
- [Investing.com Q2 call transcript](https://www.investing.com/news/transcripts/earnings-call-transcript-merlin-labs-posts-q2-2026-loss-as-shares-fall-after-hours-93CH-4859356)
- [KC-135 test flights with SNC (Business Wire, 2024)](https://www.businesswire.com/news/home/20240806976637/en/CORRECTING-and-REPLACING-Merlin-Kicks-Off-KC-135-Test-Flight-Campaign-with-SNC-to-Progress-Autonomous-Capabilities-for-the-United-States-Air-Force)
