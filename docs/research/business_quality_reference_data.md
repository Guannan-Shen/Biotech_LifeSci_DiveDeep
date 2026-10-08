# Business Quality Reference Data: Provenance and Caveats

Created 2026-10-08 (D-030 to D-033). Covers five tables in `data/reference/` that feed
`models/business_quality.py` and `scripts/business_quality_card.py`. First companies: HROW, MRLN.

## Tables

| File | One row per | Key fields | Consumer |
|---|---|---|---|
| `product_revenue_map.csv` | Product or revenue line | revenue in the period, demand units, protection end, licensor and take, substitutes, moat grade and trend | Lens A and B |
| `guidance_ledger.csv` | Quantitative guide | kind (`level` or `timeline`), guided range or deadline, actual, given and resolved dates | Lens D1, `guidance_credibility()` |
| `costly_signal_ledger.csv` | Action framed as long-term | type (`pre_committed`, `unqualified`, `post_hoc`, `short_termist`), cost, payoff, check date, outcome | Lens D4, `costly_signal_score()` |
| `deal_ledger.csv` | License, acquisition or financing | paid upfront, maximum milestones, ongoing terms, revenue two or three years later | Lens D2, `deal_multiple()` |
| `business_quality_scorecard.csv` | Company x criterion C1-C8 | score 0/1/2 (blank = not scorable), evidence class, rationale | Lens C, `business_model_grade()` |

## Sources and how they were gathered

All rows were built on 2026-10-08 from web search results. This cloud environment cannot open
sec.gov, harrow.com or fool.com directly (WebFetch DNS failures), so filing-derived numbers carry
`unverified` until the linked 8-K, 10-Q or 10-K is read on a machine with EDGAR access. Guidance
rows that are still pending carry `management_guidance`; resolved rows carry `unverified` because
the actual comes from a secondary summary.

Main sources: Harrow Q2 2026 release (Nasdaq copy) and call summaries (MarketBeat, Investing.com,
Yahoo); Q1 2026 release (GlobeNewswire) and gross-to-net coverage; Q4 2025 release and call
summary; FY2025 10-K excerpts quoted in search results (Samsung Bioepis terms, 2030 notes, BYQLOVI
timing); original deal releases (Sintetica 2021, Novartis 2022, Novaliq 2023, Formosa 2025,
Samsung Bioepis 2025); patent aggregators (Pharsight/GreyB, DrugPatentWatch) for VEVYE patents;
Merlin Q2 2026 10-Q and 8-K as quoted in search results, AIN and Leeham coverage of the
certification pivot, Crossroads Capital for per-tail economics, WBUR and Xconomy for Bridj.

## Caveats that change numbers

1. **Overlapping guides.** HROW-G05 (H1 2026) and HROW-G06 (Q2 2026) overlap: Q2 sits inside H1.
   Both are kept because management made two separate statements. Dropping G06 moves the HROW
   posterior from 0.36 to 0.40, exactly on the `discount` boundary.
2. **Open-ended guides.** "At least 180M" and "over 280M" are stored with a low end and no high
   end; the signed error then uses the low end, which flatters beats and is exact for misses.
3. **The FY2025 cut.** The original "over 280M" guide resolves as a miss and the cut guide (270-280M)
   as a hit, following the rule in `business_quality.md` section 4 D1. The cut's date is approximate.
4. **BYQLOVI timeline.** The actual date is the revised expectation (mid-2026), not a confirmed
   launch. If the launch slipped further, the entry is still a miss.
5. **IHEEZO protection end.** Harrow says an Orange Book patent runs "until 2038"; the month is
   not verified, so 2038-01-01 is used. VEVYE uses the 2037-09-22 formulation patent rather than the
   last listed patent (2042), because later patents in a family are easier to design around (A).
6. **Deal multiples ignore royalties and selling costs.** VEVYE's 11x revenue per dollar paid is
   an upper bound (milestones undisclosed, low double-digit royalty). The Novartis multiple (0.06x)
   is understated because only TRIESENCE revenue is disclosed.
7. **Debt amount.** The September 2025 notes priced at USD 250M; the 2026-06-30 10-Q reportedly
   shows USD 300M. An add-on issue would explain it but is not confirmed (Q-028).
8. **MRLN guidance.** One search summary reported H2 2026 revenue guidance of USD 4-6M; another
   says management gives no financial guidance. Neither is entered until the Q2 transcript is
   read. The USD 32M FY2026 figure is a merger-era projection as reported by press; the S-4 table
   is the primary source to check.
9. **Revenue-to-opex for MRLN** (`scripts/business_quality_card.py`) uses an approximate quarterly
   cash cost base of USD 30M (adjusted EBITDA loss of 27.8M plus revenue of 2.2M) (A).

## Update rule

Re-score every quarter and keep the old rows by adding a new `as_of` date to the scorecard; append
to the ledgers instead of editing resolved rows, except to correct an error (note it in `note`).
