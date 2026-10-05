# M6 Catalyst Calendar

Status: design. Phase 2 build target.

The calendar fuses M1 to M4 into one ledger of future events per company and asset.

## 1. Catalyst record

| Field | Meaning |
|---|---|
| catalyst_id | Stable id |
| ticker, asset_id, nct_id | Links to entity master |
| catalyst_type | topline_readout, pdufa, adcom, approval_decision, launch, label_expansion, conference_presentation, quarterly_results, financing_need, lockup_expiry, debt_maturity |
| window_start, window_end | Date range; a "Q4 2026" claim becomes 2026-10-01 to 2026-12-31 |
| precision | day, month, quarter, half, year |
| source_type, source_url, quote | Where the claim came from |
| evidence_class | `fact` (e.g., scheduled AdCom), `management_guidance` (PDUFA, readout windows), `own_assumption` (inferred from ctgov dates) |
| confidence | Probability that the event happens inside the window (from management credibility and ctgov state) |
| first_seen_at, history | Every revision of the window, for slippage tracking |
| binary_magnitude | Optional: stress move estimate for position sizing |

## 2. Inference rules (own_assumption class)

- ctgov `pcd_actual` with no guided date: topline window = PCD + 1 to 6 months
  (calibrate from history).
- Filing accepted with standard review: decision about 10 months after the 60-day filing
  date for NMEs under PDUFA program rules; priority review shorter. Company-stated date
  overrides.
- Runway end minus 12 months: `financing_need` pseudo-catalyst.

## 3. Outputs

- Next 90/180-day catalyst table per watchlist name (weekly report).
- Readout clustering view: portfolio exposure by week to binary events.
- ICS export for the investor's calendar (nice to have).
