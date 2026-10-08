# MRLN Business Quality Card: Product, Moat, Business Model, People

Date: 2026-10-08. Second application of the business quality gate
(`docs/framework/business_quality.md`), for the adjacent-sleeve pilot. Complements
`docs/memos/MRLN.md`, which covered capital structure, runway and the bad-news register. Research
note, not investment advice. **F** fact, **G** guidance, **A** own assumption, **U** unverified.
Numbers reproduce with `python scripts/business_quality_card.py MRLN --as-of 2026-10-08`.

## 1. The one-paragraph answer

Merlin sells one product idea, the Merlin Pilot: autonomy software and hardware retrofitted to
existing aircraft. Today's revenue is not that product. It is about USD 2.2M a quarter of US
government development and integration work, delivered at or slightly below cost, almost all for
USSOCOM's C-130J program. The business the thesis needs (a certified system installed per
aircraft, paid for with an integration fee and a recurring licence) would be a great model if it
existed, because certification would be the moat. Merlin gave up its closest certification path
in September 2026, one month after reaching SOI 3 in New Zealand, for an undated large-aircraft
path. The model is **unproven**, the moat is **none to narrow and eroding on the civil side**, and
the people grade is **unknown**: the only resolvable guide (the merger-era 2026 revenue
projection) resolves in early 2027 and is on track to miss by a wide margin.

## 2. Product and revenue map (lens A)

| Line | Q2 2026 (USD M) | What it is, who pays | Moat, trend | Class |
|---|---|---|---|---|
| US government development and integration | 2.13 | C-130J autonomy for USSOCOM under a USD 105M-ceiling IDIQ (ordering period to 2029); KC-135 prototype work; funded task orders | Narrow (incumbency on the IDIQ), stable | U (10-Q) |
| Commercial and non-US government | 0.06 | Civil autonomy work | None, eroding | U |
| Merlin Pilot per-aircraft licence (target) | 0 | Integration fee plus recurring licence per tail; third-party summary of management comments: about USD 3M plus USD 2M a year | None today | A / U |

- **Concentration.** HHI 0.95; one customer family (US government) is about 97% of revenue.
  The 10-Q risk factors say customer contracts carry no material purchase obligations (U).
- **Unit economics.** AIN reports that delivering Q2's government work cost slightly more than it
  earned (U). Development revenue at or below cost says nothing yet about the licence model.
- **Program status.** Critical design review for the C-130J passed on 2026-06-04; the next phase is
  aircraft integration and ground test, but USSOCOM has not designated an airframe, citing
  operational demands (U). That designation is the first evidence node.
- **Kill question.** USSOCOM does not fund the integration phase within the IDIQ, or funds it with
  a competitor's autonomy stack.

## 3. Competitive advantage (lens B)

| Source | Status | Evidence |
|---|---|---|
| Certification precedent (the moat the thesis needs) | Abandoned on the closest path. New Zealand STC for the Cessna Caravan reached SOI 3 in August 2026 and was withdrawn on 2026-09-09 to pursue large-aircraft (Part 25) certification. The company has not explained how Part 23 work transfers to Part 25 (AIN, U) | Company release, trade press |
| Defense incumbency | Real but thin: prime on one IDIQ with a USD 105M ceiling; prototypes, not a program of record | Contract award 2024, CDR 2026 |
| Technology | "Aircraft-agnostic" claim; one autonomy researcher said the company "isn't doing anything new" (B7 in the memo, U) | Expert quote via search |
| Data and flight hours | Unknown; no disclosed metric | Gap |

Competitors with the same target: Reliable Robotics (Part 23 Caravan, FAA approval targeted for
2028 per press, funded mostly by non-dilutive government grants), Shield AI and Anduril on
military mission autonomy, Sikorsky's MATRIX kit, and Garmin Autoland as a narrow certified
precedent for emergency landing (U). If Reliable Robotics certifies first on the small-aircraft
path Merlin just left, the "first certified" moat belongs to someone else.

**Moat verdict: none to narrow; civil trend eroding, defense stable.** No source has passed a
price, share or returns test.

## 4. Business model grade (lens C): unproven

| # | Criterion | Score | Why | Class |
|---|---|---|---|---|
| C1 | Gross margin | 0 | Development work at or slightly below cost | U |
| C2 | Revenue recurrence | 0 | Funded task orders | U |
| C3 | Pricing power | not scorable | No product sold at a price | A |
| C4 | Capital intensity | 0 | SPAC proceeds and a ratcheting USD 120M preferred | U |
| C5 | Operating leverage | 0 | Adjusted EBITDA loss USD 27.8M in Q2 on USD 2.2M revenue | U |
| C6 | Reinvestment runway | 2 | Large fleets, pilot shortage, defense demand for reduced crew | A |
| C7 | Dependency | 0 | About 97% US government, concentrated in USSOCOM | U |
| C8 | Balance sheet fit | 1 | USD 183.9M cash, no debt, but a senior preferred and about 18 months of trailing runway | U |

Grade **unproven**: revenue is about 7% of the quarterly cost base, so the existing revenue is not
the model being valued. **Target model** (A, labelled separately as the framework requires):
certified software licensed per aircraft would score 2 on C1, C2 and C6 and could earn **great**,
because certification is a moat that takes competitors years to copy. The validation chain breaks
at the first link (a dated certification basis) and the third (paid recurring demand).

## 5. People (lens D)

| Sub-score | Evidence | Reading |
|---|---|---|
| D1 Guidance credibility | One entry: USD 32M FY2026 revenue (merger-era projection, as reported by press). H1 actual USD 3.2M. Resolves with the FY2026 report. Search results conflict on whether management gave an H2 guide (USD 4-6M per one summary, none per another) | `unknown` (fewer than three resolved). If the projection misses, the posterior is Beta(2, 3) = 0.40 on one data point |
| D2 Capital allocation | USD 120M preferred PIPE at 10% cash or 12% in kind, conversion reset from 12.00 to 6.67 two months after listing; May 2026 PIPE with down-round warrants; 13.3M shares registered for resale | Survival financing on terms that transfer value from common holders |
| D3 Alignment | Founder-CEO and chairman Matt George holds about 11.5% (about 15M shares, about USD 23M at 1.57; Simply Wall St and Form 4 feeds disagree slightly, U) | Strongly aligned in ownership |
| D4 Costly signals | One `unqualified` entry: the New Zealand withdrawal, framed as long-term (7,000 large US aircraft, pilot shortage) with no certification basis, budget or date. It becomes `pre_committed` once those are named | No pre-committed sacrifice on record |
| D5 Candor | Anonymous culture complaints and C-suite turnover claims (B6 in the memo, U); minimal KPI disclosure | One provisional flag |
| D6 Bench | CFO Ryan Carrithers (November 2025; previously Ginkgo Bioworks and Astra), CRO Mark Brunner (April 2026); board with defense and aerospace names (U) | New team, little shared history |

The founder's previous company, Bridj (on-demand shuttles, Boston), shut down in April 2017 after
a funding deal with a car maker fell through (WBUR, Xconomy). One prior venture is not a pattern,
but it names the failure mode to watch here as well: a capital-hungry plan that depends on one
external party saying yes. At Bridj that party was an investor; at Merlin it is a regulator and
one military customer.

**People grade: unknown.** Size MRLN as an event position, as the memo already does.

## 6. So what for the memo

The card does not change the memo's stance (no entry under the trend overlay; common is an option
on technology after a senior preferred). It sharpens what the option is on. Two evidence nodes now
lead the watch list:

1. **Certification basis with a date**: a regulator-acknowledged Part 25 project (FAA or another
   authority) with a named aircraft type and launch operator. This moves the NZ withdrawal from
   `unqualified` to `pre_committed` and gives the moat a path.
2. **C-130J airframe designation and the first funded integration task order**: the first sign
   that defense incumbency converts to production revenue.

Add one falsifier to the memo: FY2026 revenue below USD 10M confirms the projection miss and moves
D1 toward discount once two more guides resolve.

## Sources

[Q2 2026 10-Q](https://www.sec.gov/Archives/edgar/data/0002028707/000162828026056882/mrln-20260630.htm);
[Q2 2026 results 8-K exhibit](https://www.sec.gov/Archives/edgar/data/0002028707/000162828026056712/merlininc8-kxex99181326.htm);
[Earlier 10-Q with preferred terms](https://www.sec.gov/Archives/edgar/data/0002028707/000121390026057138/ea0289176-10q_merlin.htm);
[PIPE resale prospectus supplement](https://www.sec.gov/Archives/edgar/data/0002028707/000162828026058115/merlinpipeprospectussupple.htm);
[Large-aircraft certification strategy (GlobeNewswire, 2026-09-09)](https://www.globenewswire.com/news-release/2026/09/09/3358555/0/en/merlin-announces-plans-to-pursue-a-civil-certification-strategy-for-large-aircraft.html);
[SOI 3 in New Zealand (Leeham News)](https://leehamnews.com/2026/08/17/merlin-clears-ai-certification-hurdle-in-new-zealand/);
[AIN on SOI 3 and Q2 economics](https://backend.ainonline.com/aviation-news/futureflight/2026-08-14/merlin-clears-certification-hurdle-ai-cockpit);
[C-130J CDR (AIN)](https://backend.ainonline.com/aviation-news/defense/2026-06-05/merlins-autonomous-c-130j-passes-critical-design-review);
[USD 105M USSOCOM IDIQ (Business Wire, 2024)](https://www.businesswire.com/news/home/20240611723182/en);
[Per-tail economics (Crossroads Capital)](https://www.crossroadscap.io/insights/the-long-duration-case-for-merlin-labs);
[Listing and 2026 projection (Washington Technology)](https://www.washingtontechnology.com/companies/2026/03/merlin-labs-public-offering-collects-200m-build-ai-autopilot-any-aircraft/412209/);
[Reliable Robotics profile](https://www.robotics.press/companies/reliable-robotics/);
[Shield AI Hivemind (2026-02-19)](https://shield.ai/shield-ai-demonstrates-ai-enabled-autonomy-for-future-collaborative-combat-aircraft/);
[CFO appointment (Business Wire)](https://www.businesswire.com/news/home/20251104781512/en);
[CRO appointment (GlobeNewswire)](https://www.globenewswire.com/news-release/2026/04/13/3272577/0/en/Merlin-Further-Expands-Executive-Team-Appointing-Mark-Brunner-as-Chief-Revenue-Officer.html);
[Ownership (Simply Wall St)](https://simplywall.st/stocks/us/capital-goods/nasdaq-mrln/merlin/ownership);
[Bridj shutdown (WBUR)](https://www.wbur.org/news/2017/05/01/bridj-shuts-down);
[Bridj and the car-company deal (Xconomy)](https://legacy.xconomy.com/?p=344615).
