# M1 EDGAR Tracker (+ M7 Fundamentals, Runway & Dilution)

Status: design. Phase 1 build target.

EDGAR is the backbone source: it is timestamped to the second (`acceptanceDateTime`),
legally binding, free, and covers financials, financing, ownership and material news
(8-K exhibits carry most press releases). When sources disagree, EDGAR wins.

## 1. Endpoints

| Use | Endpoint | Notes |
|---|---|---|
| Ticker to CIK | `https://www.sec.gov/files/company_tickers.json` | Refresh daily; keep history, tickers get reused |
| Filing list per company | `https://data.sec.gov/submissions/CIK##########.json` | Recent filings + pointers to older pages |
| XBRL facts per company | `https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json` | All tagged facts with `filed` date (point-in-time key) |
| Cross-sectional facts | `https://data.sec.gov/api/xbrl/frames/us-gaap/{tag}/USD/CY2026Q2I.json` | One tag across all filers; ideal for universe-wide runway screens |
| Live feed | `https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=8-K&output=atom` | Poll every few minutes for watchlist CIKs |
| Daily index | `https://www.sec.gov/Archives/edgar/daily-index/` | Backfill and completeness check |
| Full-text search | `https://efts.sec.gov/LATEST/search-index?q=...` | Phrases like "going concern", "at the market offering" |
| 13F structured data | SEC Form 13F data sets (quarterly) | Specialist ownership (H4) |
| Insider data | Form 4 XML in filing index; SEC insider transaction data sets | Insider buys and sells |

Rules: User-Agent from `SEC_USER_AGENT` (name + email), at most 10 requests per
second, exponential backoff on 429/503. Raw JSON and documents saved to
`data/raw/edgar/YYYY-MM-DD/` before parsing.

## 2. Filing types and what they mean here

| Form / item | Event type | Why it matters |
|---|---|---|
| 8-K 1.01 / 1.02 | partnership, licensing (entry / termination) | Partner opt-ins and terminations validate or erode platforms |
| 8-K 2.02 | quarterly_results | Earnings release (Ex-99.1) |
| 8-K 2.03 | convertible_issued, debt | New obligations |
| 8-K 3.01 | delisting notice | Bid-price deficiency precedes reverse splits |
| 8-K 3.02 | pipe | Unregistered equity sales |
| 8-K 5.02 | executive_change | CMO/CFO departures before readouts are a signal |
| 8-K 5.03 | reverse_split | Charter amendment |
| 8-K 7.01 / 8.01 | topline_readout, regulatory events, other | Most clinical and FDA news lands here |
| S-3, S-3ASR, EFFECT | shelf_filed | Financing capacity becomes live |
| 424B5 / 424B3 | offering_priced, atm_established | Actual dilution; ATM sales agreements |
| 10-Q / 10-K | quarterly_results, going_concern | XBRL financials; going-concern language; ATM usage in notes |
| SC 13D / 13G (and amendments) | ownership_13d_13g | Timely large-holder changes |
| 13F-HR | ownership_13f | Quarterly fund holdings, about 45-day lag |
| Form 4 | insider_trade | Open-market purchases are rarer and more informative than sales |
| DEF 14A | share authorization votes | Authorized-share increases foreshadow dilution |

## 3. Point-in-time keys

- Filing events: `available_at = acceptanceDateTime` (Eastern time, converted to UTC).
- XBRL facts: `available_at = filed` date of the filing that first reported the value;
  later restatements are separate records, never overwrites.
- 13F: `available_at` = filing date, never the quarter-end report date.

## 4. Parsing plan

1. Submissions JSON -> `filings` table (cik, accession, form, items, filed, accepted,
   primary_doc, url).
2. 8-K items -> event types per the table above; Ex-99.1 text stored for M4 extraction.
3. companyfacts -> `xbrl_facts` (cik, taxonomy, tag, unit, period_start, period_end,
   value, form, filed, accession, frame).
4. 424B/S-3 -> financing events with offering size, price, warrants (LLM-assisted
   extraction with quoted spans, `unverified` until checked).

## 5. M7 Runway and dilution model

Usable cash (framework survival gate):

```
usable_cash = CashAndCashEquivalentsAtCarryingValue
            + ShortTermInvestments | MarketableSecuritiesCurrent
              | AvailableForSaleSecuritiesDebtSecuritiesCurrent
            (+ long-term marketable securities, flagged)
            - restricted cash (if tagged separately)
```

Burn: `NetCashProvidedByUsedInOperatingActivities` is reported year-to-date in 10-Qs;
de-cumulate to quarterly values before averaging. Add capex
(`PaymentsToAcquirePropertyPlantAndEquipment`) and scheduled debt maturities.

Runway outputs (months), each with `available_at`:

| Variant | Burn assumption |
|---|---|
| Trailing | Average of last 2 de-cumulated quarters |
| Guided | Management runway statement (`management_guidance`, extracted from 10-Q/PR) |
| Stress | Trailing burn x 1.25, no new revenue |
| Event-adjusted | Months of cash left after the next catalyst date (from M6) |

Dilution pressure score inputs: effective shelf capacity, active ATM, recent 424B
activity, warrants in the money, convertibles, authorized-but-unissued shares, price
run-up over 20 days (companies raise into strength), runway under 18 months, going
concern flag. This score is the main H1 screen and a feature of the financing model in
M9.

## 6. Specialist ownership (H4)

- Curated list of dedicated biotech funds with CIKs in `config/specialist_funds.yaml`
  (Phase 1). Examples to verify: RA Capital, Baker Bros, Perceptive, EcoR1, BVF, RTW,
  Deep Track, Avoro, Commodore, Cormorant, Logos, Fairmount, Frazier Life Sciences,
  OrbiMed, Venrock HCP, Vivo, TCG Crossover, Janus life-science sleeve (needs care).
- Metrics per company and quarter: number of specialist holders, specialist share of
  institutional holders, percent of shares held, quarter-over-quarter change, new
  positions. This reproduces and extends the Breakthrough-style table in
  `docs/research/specialist_concentration.md` with a documented method.
- 13F excludes shorts and options detail is coarse; 13D/G give earlier signals for
  holders above 5%.

## 7. Tests

Recorded fixtures for one large filer (ILMN), one small clinical filer (EDSA, foreign
private issuer check: Edesa is Canadian but files 10-K/10-Q, verify) and one ATM-heavy
filer. Tests cover YTD de-cumulation, restatement handling and timestamp conversion.
