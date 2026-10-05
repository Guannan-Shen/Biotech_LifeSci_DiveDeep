# Research Note: Specialist Concentration Table (Breakthrough)

Date: 2026-10-05. Source: screenshot shared by the investor, "Highest specialist
concentration, smallest third of companies", branded Breakthrough. Snapshot date and
scoring method are not shown. Market cap is labeled "dilution-adjusted". Transcribed to
`data/reference/specialist_concentration_snapshot.csv`.

## 1. Reading the columns

| Column | Our interpretation | Confidence |
|---|---|---|
| Held | Percent of shares held by specialist funds | Plausible, unverified |
| Holders | Number of specialist funds holding (equals the numerator in the next column on every row) | High |
| Specialists / total institutions | Specialist count over all institutional holders | High |
| Score | Composite percentile-like score, method unknown | Unknown |

## 2. Caveats

- Likely built from 13F filings: about 45 days of lag, long positions only, no short or
  hedge visibility, and options reported coarsely. It cannot show current net exposure.
  [SEC 13F FAQ](https://www.sec.gov/rules-regulations/staff-guidance/frequently-asked-questions-about-form-13f)
- Very high "Held" in a micro cap (e.g., 61-64% for LONA and KLRS) also means a thin
  float and heavy overhang if those funds exit; concentration cuts both ways.
- Several names are post-failure shells or reverse-merger vehicles where specialists
  hold residual cash claims. High specialist ownership there signals a cash-value or
  restructuring play, not scientific conviction.
- No date: the table may be stale relative to the current 13F cycle.

## 3. How the system uses it

1. **Candidate pool** today: add the 20 tickers to the research universe as
   `screen_only` entries so M1 can resolve CIKs and pull filings.
2. **Rebuild the signal ourselves** (M1 section 6, H4): own specialist fund list, own
   method, every quarter point-in-time. Then test whether level, change, or new
   positions predict 6 and 12-month excess returns vs XBI, split by market-cap band and
   by "cash shell" vs "operating" status.
3. **Combine with 13D/13G** for timelier changes in large holders.

## 4. Questions to answer once data flows

- Does specialist concentration predict returns after controlling for cash/market-cap
  (many high-concentration micro caps trade near cash)?
- Is the change in specialist count more predictive than the level?
- Do specialist exits precede financings or failures (left-tail signal for H1)?
