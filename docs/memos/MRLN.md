# Memo (draft): MRLN, Merlin, Inc.

Status: **draft, evidence incomplete**. Adjacent-sleeve pilot (D-013). Research date
2026-10-05. Horizon 6 to 24 months. Template: framework section 11.

Evidence classes in brackets: [F] fact from a primary filing, [G] management guidance,
[A] own assumption, [U] unverified (secondary source or derived from a vendor feed).

## 1. Identity

| Item | Value |
|---|---|
| Company | Merlin, Inc. (Merlin Labs), Boston; CIK 0002028707 [U: FMP profile] |
| Business | Aircraft-agnostic AI autonomy ("Merlin Pilot") for military and civil aircraft, takeoff to touchdown [U] |
| Listing | Nasdaq MRLN since 2026-03-17, via business combination with Inflection Point Acquisition Corp. IV; deal described as more than USD 200M gross proceeds [U: press coverage] |
| Archetype | `regulated_deeptech`, sleeve `adjacent` |

## 2. Capital snapshot

| Item | Value | Date | Class |
|---|---|---|---|
| Price | USD 1.57 (52-week range 1.57 to 17.00; first-day close reported at 9.03) | 2026-10-05 | [U: FMP] |
| Market cap | USD 151.5M | 2026-10-05 | [U: FMP] |
| Implied shares | about 96.5M (market cap / price); excludes any warrants, earnouts, unvested awards | 2026-10-05 | [A] verify on 10-Q cover |
| Cash, equivalents, short-term investments | USD 183.9M, no debt | 2026-06-30 | [U: Q2 release, to confirm in 10-Q] |
| Operating cash outflow, 6 months | USD 50.9M | H1 2026 | [U: 10-Q via search snippet] |
| Q2 revenue | USD 2.2M (Q1: 1.0M) | Q2 2026 | [U] |
| Q2 GAAP net loss | USD 58.4M (Q1: 90.4M); likely includes non-cash SPAC-related charges | Q2 2026 | [U]; split cash vs non-cash in 10-Q |
| Runway guidance | Resources expected to fund growth "into fiscal 2028" | Q2 release | [G] |

## 3. Runway, three ways [A]

Trailing quarterly burn = 50.9 / 2 = USD 25.4M. H1 includes pre-merger months, so the
post-listing run rate may be higher; the stress cases cover that.

| Case | Burn per quarter | Months from 2026-06-30 | Months from today |
|---|---|---|---|
| Trailing | 25.4 | 21.7 | 18.5 |
| Stress (x1.25) | 31.8 | 17.3 | 14.1 |
| Ramp (x1.5) | 38.2 | 14.5 | 11.3 |

The investor's estimate of about 15 months sits between the stress and ramp cases. The
company's "into fiscal 2028" matches the trailing case. Survival gate verdict:
**passes only if** the next value-creating milestone lands within about 12 months;
otherwise a raise near current prices becomes likely and heavily dilutive.

## 4. Cash floor and option value [A]

| Item | Value |
|---|---|
| Projected cash at 2026-09-30 (one more trailing quarter of burn) | about USD 158.5M |
| Cash floor per share (on about 96.5M shares) | about USD 1.64 (USD 1.91 at June 30) |
| Option value = market cap - projected cash | about USD -7M |

The market values the technology at roughly zero or below: it expects the cash to be
burned without a return, or it is still absorbing de-SPAC share supply (PIPE resale
prospectuses were filed as 424B3s [U]). This is the classic biotech "trading below
cash" setup, where outcomes split sharply on burn discipline and the next milestone.

## 5. Core view: which two variables matter in the next 2 to 4 quarters

1. **Conversion of military prototype work into funded production or program-of-record
   money.** Reported: C-130J autonomy program Critical Design Review completed
   2026-06-04 for USSOCOM; next phase is aircraft integration and ground test [U].
   Verify KC-135 program status separately [U].
2. **Quarterly burn vs revenue ramp.** Revenue of USD 2.2M against about 25M of burn
   per quarter; the gap must close or the runway clock dominates.

## 6. Variant perception (to be filled after the evidence pass)

Market view implied by price: the cash will be consumed and further dilution is
likely. A differing view needs evidence of either (a) contracted revenue that shortens
the path to self-funding, or (b) a burn cut that extends runway past certification.

## 7. Key metrics to track

| Metric | Definition | Current | Frequency |
|---|---|---|---|
| Quarterly operating cash burn | 10-Q cash flow, de-cumulated | about 25M (H1 average) [U] | Quarterly |
| Contracted backlog / funded obligations | 10-Q remaining performance obligations; USAspending obligations | Unknown | Quarterly / monthly |
| Certification progress | SOI stage reached per authority | SOI 3 with CAANZ, coordinated with FAA under a bilateral agreement [U] | Event-driven |
| Diluted share count | Shares + warrants + earnouts + awards | Unknown | Quarterly |

## 8. Catalysts (calendar entries, all [G] or [U] until verified)

| Window | Event | Source to verify |
|---|---|---|
| Next few quarters | C-130J aircraft integration and ground testing | Q2 release, DoD records |
| Unknown | SOI 4 / certification credit (CAANZ, then FAA validation) | Company guidance |
| Q3 results (likely November) | Burn, revenue, backlog update | 8-K |
| Unknown | PIPE resale, warrant and earnout supply dates | 424B3, S-1, merger agreement |
| 2026-07-17 (past) | First fully autonomous landing at EAA AirVenture Oshkosh, Cessna 208B [U] | Already public |

## 9. Scenarios (structure only; probabilities after the evidence pass)

| Scenario | What must be true | Financing | Value anchor |
|---|---|---|---|
| Bear | Milestones slip, burn rises, raise at or below cash in 2027 | Large dilutive raise | Below cash floor after dilution |
| Base | Programs progress on prototype money; burn steady; certification slow | Modest raise or ATM in 2027 | Near cash floor plus small option value |
| Bull | Production contract or program of record; certification step on time; burn falls | Raise from strength, or none | Option value turns clearly positive |

## 10. Falsifiers (written before any position)

- A guided certification or program milestone slips by more than two quarters.
- Quarterly operating burn above USD 32M (stress case) with no matching revenue.
- An equity raise priced below the cash floor per share.
- Departure of the CEO, CFO or the head of certification within the horizon.

## 11. Trend and supply

Price at the 52-week low on 2026-10-05, down about 83% from the first-day close [U].
Trend overlay says no entry until the price recovers above a rising 200-day average,
which a stock this new does not yet have; use a 50-day reference and the H11 supply
calendar instead.

## 12. Evidence log and next research steps

1. Pull the Q2 10-Q (EDGAR, accession 0001628280-26-056882 per search result [U]):
   share count, warrants, earnouts, quarterly burn, remaining performance obligations,
   restricted cash, going-concern language.
2. Read the PIPE resale 424B3s: number of shares registered and holders.
3. USAspending.gov: obligations to Merlin's UEI by program.
4. Check whether Merlin designates X or LinkedIn accounts as disclosure channels; build
   the T1/T2 list for `config/x_accounts.yaml`.
5. Collect the de-SPAC base rate (H11) and the eVTOL certification-delay reference class.

Sources used: [Q2 2026 results, SEC 8-K exhibit](https://www.sec.gov/Archives/edgar/data/0002028707/000162828026056712/merlininc8-kxex99181326.htm),
[Q2 10-Q](https://www.sec.gov/Archives/edgar/data/0002028707/000162828026056882/mrln-20260630.htm),
[closing announcement](https://www.barchart.com/story/news/778641/merlin-and-inflection-point-acquisition-corp-iv-announce-closing-of-business-combination),
[listing coverage](https://hoodline.com/2026/03/merlin-s-nasdaq-liftoff-ends-boston-tech-ipo-dry-spell/).
These pages were found by web search; the filings themselves could not be opened from
this environment (network policy), so figures stay [U] until checked.
