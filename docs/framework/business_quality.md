# Business Quality Gate: Product, Moat, Business Model, People

Added 2026-10-08 (D-030 to D-033). Owner: Guannan Shen. Applies to every memo in the core and
adjacent sleeves. Evidence classes as everywhere: **F** fact, **G** management guidance, **A** own
assumption, **U** unverified.

## 0. Why this gate exists

The first three gates (framework section 3) ask whether the thesis has a dated test, whether the
company survives until the test, and what the price already assumes. None of them asks what the
company sells, whether anyone else can sell it, how good the money-making machine is, or whether
the people running it deliver what they say. The 2026-10-07 HROW memo shows the gap: it priced a
coin flip on management credibility without scoring management, and it modelled 2027 revenue
without separating VEVYE (a prescription drug fighting for pharmacy-benefit access) from IHEEZO (a
physician-administered drug whose economics depend on Medicare reimbursement). Those two products
fail in different ways, and the price gate cannot see that.

The gate sits between the survival gate and the price gate. Its output is a one-page **business
quality card** (section 7) that feeds the price gate in three explicit ways (section 6). It never
produces a buy signal by itself: a great business at a price that assumes greatness is a normal
investment.

## 1. Lens A: product and revenue map

One row per product or revenue line that is at least 5% of revenue, or that management names as a
growth driver. Pre-revenue companies map assets and programs instead, with expected revenue start.

| Field | Question | Typical primary source |
|---|---|---|
| Problem and user | Which problem, for which patient or customer, at which moment of care? | Label, 10-K business section |
| Payer and channel | Who pays (commercial plan via PBM, Medicare Part B buy-and-bill, Part D, facility budget, government program, cash) and through which channel (retail pharmacy, specialty pharmacy, distributor to clinic, direct)? | 10-K, payer policies, CMS files |
| Revenue and share of total | Latest quarter, trailing four quarters, share of company revenue | 10-Q, earnings release |
| Demand vs revenue | Units or prescriptions vs recognized revenue; is the gap explained by stocking, destocking or gross-to-net? | Earnings release KPIs, call |
| Net revenue per unit | Revenue / demand units, and its direction | Derived (A) |
| Economics shared | Royalty, transfer price, profit split, milestones owed to a licensor | License 8-K, 10-K notes |
| Protection end | Last Orange Book patent, regulatory exclusivity, biosimilar interchangeability, practical barriers (complex manufacturing) | Orange Book, Purple Book, 10-K |
| Substitutes | Branded competitors, generics, cheap off-label or compounded alternatives, procedures | Payer policies, guidelines |
| Kill question | What single change would make a prescriber stop using it? | Own analysis (A) |

Revenue quality checks across the map:

1. **Concentration.** Herfindahl index (HHI) of product revenue shares and the top product's
   share. HHI above 0.35 or a top product above 50% means single-product risk dominates the card.
2. **Sell-in vs sell-through.** When reported revenue diverges from demand units for two quarters
   in a row, the revenue line is channel-driven and the card marks it `channel_noise`.
3. **Gross-to-net trajectory.** Net revenue per unit falling while volume rises is volume bought
   with price (copay cards, high-deductible mix, rebates). It is a moat warning, not a growth signal.
4. **Licensor take.** The share of each product's net revenue that goes to a licensor. An
   in-licensed product with a low double-digit royalty is a different asset from an owned one.
5. **Protection-weighted revenue life.** Revenue-weighted average years until loss of
   exclusivity (`models/business_quality.py`). Short life plus high concentration is the classic
   specialty-pharma cliff.

## 2. Lens B: competitive advantage

A patent protects a molecule; a moat protects demand and price. Many specialty drugs hold patents
into the late 2030s and still have no moat, because a cheap generic or a habit does the same job.
Score each source that applies, product by product, then aggregate by revenue weight.

| Moat source | What it looks like in this universe | How to test it | How it dies |
|---|---|---|---|
| Legal exclusivity | Orange Book patents, NCE or orphan exclusivity, biologic data exclusivity, certification precedent (deep-tech) | Dates, litigation, Paragraph IV filings | Patent challenge, design-around, 505(b)(2) entrant |
| Clinical differentiation | Label claim others lack, head-to-head data, tolerability, onset | Label text, guideline position, head-to-head trials | A competitor matches the claim; payers treat the class as interchangeable |
| Reimbursement position | Product-specific J-code, pass-through, preferred formulary tier, Medicare ASP economics that pay the prescriber | CMS files, formulary lists, payer policies | Pass-through expiry, bundling, step edits, ASP erosion |
| Call-point scale | Sales force and relationships concentrated on a small prescriber base (eye care, dermatology), portfolio bundling | Reps per prescriber, share of prescribers writing two or more company products | A larger company enters the call point with more products |
| Workflow and switching cost | A product embedded in a procedure or clinic protocol; staff trained on it | Repeat order rates, account retention | A cheaper product that fits the same workflow |
| Manufacturing know-how | Biologics, sterile ophthalmics, cell therapy, complex generics; supply that others cannot easily copy | Supply interruptions, 483s, number of qualified suppliers | Contract manufacturers learn the process; licensor controls supply |
| Data and network | Installed base that generates data or consumable pull-through (tools, dx, AI) | Pull-through per system, data licensing renewals | Open data, competing platforms |
| Deal sourcing | Repeated ability to in-license approved assets cheaply from small developers | Upfront paid vs revenue two years later, across all deals | Competition for assets raises prices; licensors terminate |

**Grade.** `none`, `narrow` (protects some demand or price for a few years; one source, or several
weak ones), `wide` (two or more independent sources, at least one tested by the price or share
test, durable beyond five years). Add a **trend**: `widening`, `stable`, `eroding`.

**Three tests that turn claims into evidence:**

- **Price test.** Can the company raise net price (not list price) without losing volume? Net
  revenue per unit is the evidence; a list-price increase eaten by rebates fails the test.
- **Share test.** Does share hold or grow against cheaper substitutes after the launch push ends
  and the product stops getting free samples or copay support?
- **Returns test.** Do gross margin and returns on the capital spent to acquire or build the
  product exceed what a competitor would earn copying it? Deal multiple = revenue in year two or
  three / total paid to acquire or license.

## 3. Lens C: business model grade

Grades describe the machine, not the stock. Each criterion scores 0, 1 or 2 with evidence.

| # | Criterion | 0 | 1 | 2 |
|---|---|---|---|---|
| C1 | Gross margin | Below 40% or negative | 40-70% | Above 70% and stable |
| C2 | Revenue recurrence | One-time, project or development revenue | Repeat but discretionary (procedural, cash-pay) | Chronic therapy, consumables or contracted subscriptions |
| C3 | Pricing power | Net price falling | Flat net price | Net price rising with stable volume (passes the price test) |
| C4 | Capital intensity | Growth needs equity or heavy capex | Growth funded by debt or partners | Growth funded from operating cash flow |
| C5 | Operating leverage (evidence) | Opex grows faster than gross profit | Mixed | Gross profit grows faster than opex for four or more quarters |
| C6 | Reinvestment runway | Market saturated or shrinking | Growth from share gains in a flat market | Large untreated or underpenetrated market, plus a repeatable way to add products |
| C7 | Dependency | One payer, customer, licensor or regulator decides most of the value | Moderate | Diversified across products, payers and customers |
| C8 | Balance sheet fit | Leverage or burn that a bad year can break | Adequate | Net cash or leverage under 2x through-cycle cash EBITDA |

**Grading rules.** Sum the scores (maximum 16), then apply gates so a high sum cannot hide a fatal
flaw:

- **Great**: sum 12 or more, no criterion at 0, moat `wide` on at least half of revenue, and C5
  scored 2 with **F** evidence.
- **Good**: sum 8 or more and at most one criterion at 0.
- **Normal**: everything else with revenue.
- **Unproven**: the revenue that exists is not the revenue the thesis needs (trailing revenue
  below 25% of operating expenses), or fewer than four criteria can be scored from reported data
  (F, G, or U pending re-reading; A does not count). Grade the target model separately and label
  it as such.

## 4. Lens D: people

The question is whether this team can carry out this plan, including the hard version of the
plan: accepting a worse quarter for a better decade. Six sub-scores, each with a ledger behind it.

### D1. Guidance credibility (ledger, D-032)

Every quantitative guide (revenue, EBITDA, cash runway, launch date, readout window, certification
date, merger-proxy or SPAC projection) goes into `data/reference/guidance_ledger.csv` with the date
given, the date resolved, the guided range and the actual. A guide counts as **hit** if the actual
lands at or above the low end (for revenue and EBITDA) or on or before the date (for timelines).
The posterior hit rate under a Beta(2, 2) prior, its 80% credible interval and the mean signed
error (actual minus guide midpoint, relative) are computed by `guidance_credibility()`.

Read the two numbers together: a low hit rate with a large negative signed error is a habitual
optimist; a low hit rate with a near-zero mean error is a noisy forecaster. Only the first
justifies a systematic haircut. Mid-period cuts count: a guide cut before the period ends
resolves the original guide as a miss and opens a new entry for the cut guide.

### D2. Capital allocation returns

A deal ledger with every acquisition, license, financing and spin-out: what was paid (upfront plus
milestones), what it produced two and three years later (revenue, contribution if disclosed), and
what it cost shareholders (dilution, interest). The deal multiple from section 2 is the core
number. Patterns matter more than any single deal: repeated cheap in-licensing that grows is a
capability; one great deal is luck until repeated.

### D3. Alignment

Insider ownership value relative to annual cash compensation; open-market purchases and sales
(Form 4, excluding grants and tax withholding); what the bonus pays for (revenue and adjusted
EBITDA reward growth at any cost; per-share cash flow or return on capital reward discipline);
say-on-pay and director vote dissent.

### D4. Long-term orientation: the costly-signal ledger (D-031)

"Willing to sacrifice the short term for the long term" is easy to claim and impossible to see
in one quarter. The ledger makes it observable. An entry is a **pre-committed sacrifice** only if
all four hold:

1. It was announced before the cost appeared in results.
2. The short-term cost was quantified or plainly visible (lower EBITDA, lower near-term revenue, a
   catalyst given up).
3. The expected payoff was stated in measurable terms.
4. A check date or window was given.

Entries that fail the test are logged anyway and never count toward the score: `unqualified`
(a move framed as long-term with no measurable payoff or no date) or `post_hoc` (an explanation
or corrective action offered after a miss). When the check date arrives, each pre-committed entry
resolves to `paid_off`, `partial` or `failed`. The score is the Beta posterior of paid-off share
among resolved pre-committed entries, plus the count still pending. A management team with three
pre-committed sacrifices that paid off has shown long-term orientation; a team with ten post-hoc
explanations has shown fluency.

Opposite signals go into the same ledger as `short_termist`: channel stuffing ahead of a quarter
end, cutting R&D or sales support to hit EBITDA, pulling guidance forward, swapping a key
metric for a friendlier one.

### D5. Candor and disclosure consistency

- **KPI drift**: a metric disclosed for several quarters disappears or is redefined when it turns
  down. Each drop is a negative entry.
- **Adjusted-metric creep**: the gap between adjusted EBITDA and operating cash flow widens.
- **Filing hygiene**: late 10-K or 10-Q, auditor change, material weakness, restatement.
- **Bad news first**: does management pre-announce misses, or does the market learn on the call?

### D6. Bench and stability

Executive turnover in finance, commercial, regulatory and engineering roles (8-K Item 5.02), key
person dependence, board independence and relevant expertise.

**People grade.** `trust` (credibility posterior above 0.6, no candor flags, aligned, at least one
paid-off pre-committed sacrifice), `verify` (mixed record), `discount` (credibility posterior below
0.4 with negative signed error, or two or more candor flags). `unknown` when the ledger has fewer
than three resolved guides; a short history is a reason to size smaller, not a neutral score.

## 5. Archetype prompts

| Archetype | Product map unit | Moat sources that usually matter | People question that usually matters |
|---|---|---|---|
| `clinical_binary` | Asset and indication | Differentiated mechanism, IP life, label they could plausibly win | Trial design record: did past trials read out on time and on the guided endpoint? |
| `launch` | Product by setting of care | Label, site-of-care economics, reimbursement | Launch guidance vs analogs; honesty about slow quarters |
| `commercial_pharma` | Product and revenue line | Exclusivity, call-point scale, reimbursement, deal sourcing | Guidance credibility and deal multiples |
| `tools` | Instrument and consumable | Installed base pull-through, workflow lock-in | Product transition execution, pricing discipline |
| `software` | Product and contract type | Switching cost, data, regulatory acceptance | Honesty through license-model transitions |
| `dx_data` | Test and data product | Coverage decisions, guideline inclusion, data network | Coverage timeline guidance vs outcomes |
| `ai_platform` | Asset, partnership, platform service | Proprietary data, validated predictions | Partner milestone guidance vs cash received |
| `regulated_deeptech` | Program and contract | Certification precedent, program-of-record position | Certification and revenue projections vs delivery |

## 6. How the card changes the price gate

1. **Scenario weights.** When the base case rests on management guidance, its probability cannot
   exceed the upper bound of the 80% credible interval of the guidance hit rate. The released
   weight moves to the scenario that assumes the historical signed error.
2. **Terminal multiple.** The business model grade picks the range used for exit multiples; a
   `normal` model does not get a `great` model's multiple because its current growth is high.
   Ranges are **A** and live in the memo.
3. **Position size.** `unproven` or `unknown` people grades cap the position as an event position
   (framework section 9) even for a revenue-generating company.

## 7. Business quality card template

| Block | Content |
|---|---|
| Product map | Table from section 1, sorted by revenue; the one product that decides the thesis named first |
| Revenue quality | HHI, top product share, demand vs revenue gap, net revenue per unit trend, licensor take, protection-weighted life |
| Moat | Grade and trend per major product; which of the three tests passed, failed or is untested |
| Business model | C1-C8 scores with evidence class; grade after gates |
| People | D1-D6 with the ledger numbers; grade |
| So what for the price | How the card changes scenario weights, exit multiple and size |
| Falsifiers | The two observations that would change a grade, with dates |

## 8. Failure modes of this gate

- **Halo.** A rising stock makes management look visionary. Score the card before looking at the
  price chart, and score the ledger from documents, not from narrative.
- **Survivorship in deal ledgers.** Companies publicize the deals that worked. Pull every license
  and acquisition 8-K, including those quietly dropped.
- **Moat by assertion.** A patent date is not a moat. Every `wide` grade needs a passed price or
  share test.
- **Small samples.** Three guides cannot prove credibility. That is why the ledger uses a
  posterior with an interval and why `unknown` exists.
- **Grade drift.** Re-score every quarter and keep the history; a grade that changes should be
  explainable by a dated observation.
