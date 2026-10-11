# Provenance: daily prices from the listing mirror

Covers `data/reference/qsi_naut_daily_2021_2026.csv` and the git-ignored
`data/silver/prices/mirror_daily_lifesci.csv.gz`, both written by `scripts/mirror_daily_prices.py`
(D-044). Also `data/reference/announcement_events.csv` and
`data/reference/announcement_drift_qsi_naut.csv` (H17 case study).

## Source

The public repository `rreichel3/US-Stock-Symbols` commits the full Nasdaq stock screener (NASDAQ,
NYSE, NYSE American) on weekday evenings New York time, daily since 2021-01-30 (D-039). Each row
carries `lastsale`, `netchange`, `pctchange`, `volume` and `marketCap`. Cloned bare (about 490 MB)
on 2026-10-11; last commit used 2026-10-10 00:42 UTC.

## Date mapping (the hard part)

The screener's timing changed once:

| Period (New York date of commit) | Snapshot holds | Evidence |
|---|---|---|
| Up to 2026-09-23 | That day's close; weekend or holiday commits hold the previous trading day | QSI +67% to 3.60 on Friday 2024-12-27 (StockInvest: +66.5% to 3.58 that day); NAUT -28% on 2026-07-28, the morning of its Q2 release (RTTNews: about -27%); half-day volumes on 2025-11-28 and 2025-12-24 sit on those dates |
| From 2026-09-24 | The close of the trading day before | The 2026-09-24 snapshot repeats 2026-09-23 exactly (every lastsale and pctchange equal); QSI closed 0.795 on Monday 2026-09-28 and rose about 24% on Tuesday 09-29 (Benzinga); NAUT traded about 12.7% up at about 1.77 on 2026-10-02 from a 1.57 close (Stockstotrade); TXG 93.50 on 2026-10-02 (D-022) |

`core/calendar.snapshot_trade_date` encodes both regimes; `MIRROR_LAG_START` must move if the
screener changes again. Snapshots that repeat the previous one are dropped (six in 2021-06 to
2026-10). Five sessions have no commit at all (2022-12-21, 2022-12-28, 2026-02-04, 2026-02-19,
2026-02-24).

## Fields and caveats

- `close`: `lastsale`. `ret_1d`: `netchange / (lastsale - netchange)`, the screener's own return
  against the previous close.
- About 1% of snapshots show a close that disagrees with the one-day return by more than 2 points
  (the same dates across tickers: 2025-03-28, 2025-04-03, 2025-05-14, 2025-06-16, 2025-07-11,
  2025-10-06, 2025-10-31, 2026-09-23 among them), so one of the two fields was stale. Event windows
  therefore use close-to-close returns, which telescope over the window, and the benchmarks use
  `ret_1d` averaged over hundreds of names.
- No split or dividend adjustment beyond what the screener's return applies. QSI and NAUT had no
  splits in the period (A; check before reuse on other names).
- `EW_LIFESCI_200M`: equal-weight `ret_1d` of point-in-time therapeutics and tools names (layer from
  `connectors/listings.py` per snapshot) with prior-day market cap of at least USD 200M, winsorized at
  -60% and +150%; median 370 names. Its cumulative path matches XBI's well (0.49 at the June 2022 low,
  0.46 in October 2023, 0.45 in April 2025) but it is a proxy (Q-049).
- `EW_TOOLS`: the same for the tools layer; median 27 names, so noisy.
- Market caps use the screener's share counts, which lag filings.

## Event log

`announcement_events.csv`: one row per announcement with `available_at` (release date), `timing`
(`bmo`, `amc`, `intraday`, `unknown`), `date_precision` (`day` or `approx`), event type, timeline
effect (`slip`, `extend`, `reaffirm`, `cut`, `none`) coded from the text, evidence class and source.
Most dates come from earnings aggregators and press summaries (evidence `unverified`; Q-043).
`announcement_drift_qsi_naut.csv` is derived and can be regenerated with
`python scripts/announcement_drift.py QSI NAUT`.
