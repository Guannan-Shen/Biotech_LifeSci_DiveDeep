# Provenance: Listing Universe, Exits, Base Rates and Case-Study Tables

Written 2026-10-09 (D-038 to D-041). One entry per reference file added or changed that day.

## Listing-derived tables

Source for all four: the Nasdaq stock screener as committed daily to the public repository
https://github.com/rreichel3/US-Stock-Symbols (files `<exchange>/<exchange>_full_tickers.json`),
sampled once a month from 2021-01-30 to 2026-10-09 by `scripts/listing_history.py`. The screener's
market cap is Nasdaq's figure on the commit day (shares outstanding times last sale); it is not
float-adjusted and can lag share-count changes. Classification is `own_assumption`
(`connectors/listings.py`). Regenerate with:

    python scripts/listing_history.py --repo /path/to/US-Stock-Symbols
    python scripts/build_lifesci_universe.py
    python scripts/takeout_base_rate.py

| File | Content | Caveats |
|---|---|---|
| `us_lifesci_universe.csv` | 941 listed companies on 2026-10-09 in six layers, with cap band, exchange, country, ADR flag, XBI and IBB columns, watchlist and AI-fit flags, first sighting in the history | XBI and IBB membership columns are empty until `scripts/fetch_etf_holdings.py` runs on a machine that reaches the sponsors; the `*_rule_proxy` columns over-include (325 vs about 250 for IBB, 192 vs about 140 for XBI) |
| `lifesci_layer_overrides.csv` | 119 ticker overrides with a reason each | Keyed by ticker: a reused ticker inherits the override (accepted; reuse is rare among overridden names) |
| `lifesci_listing_counts_monthly.csv` | Companies per month, stable layer and cap band (the hazard denominator) | Layer is the company's most frequent layer across its history; a company counts if at least a third of its snapshots place it in the universe |
| `lifesci_listing_exits.csv` | Every universe company that stopped appearing: first and last sighting, last and peak market cap, exit size class, ticker-change successor, matched `deal_id`, curated resolution | Monthly sampling: dates are accurate to a month. 330 small and mid therapeutics exits are `unresolved` |
| `lifesci_exit_resolutions.csv` | Curated outcomes for exits that are not deals (renames, delistings, bankruptcy, halt, wind-down, SPAC) | Mostly recall (U); three rows sourced |
| `takeout_base_rates_2021_2026.csv` | Annual strategic takeout hazard per cap band with an 80% interval | Numerator limited to the deal table, so the micro band in particular is a floor (Q-037); one deal cycle |

Known data problems handled in code: industry labels that flicker for a few months (stable
layers), ticker reuse (spell split when a symbol returns after a gap under another name), fresh
IPOs with no industry (name rescue), blank-check shells and theme-park or crypto companies filed
under health-care labels (name exclusion).

## Deal table changes (`biotech_takeouts.csv`)

- 141 rows added (88 to 229): 9 sourced 2025-2026 deals found through listing exits (URL per row),
  48 recall rows for 2019-2025 deals found through exits or missed on 10-08, and 84 recall rows for
  2005-2018. Recall rows have `date_precision = approx`, no URL, and a note starting
  "Recall"; equity values and prices are approximate and several prices are left blank where
  memory was not reliable (EUR or SEK prices, cash-plus-stock terms).
- New columns: `deal_kind` (strategic, contested, parent_buy_in, going_private, distressed,
  cash_shell) and `prior_relationship` (yes, no, unknown). Existing rows default to `strategic`
  and `unknown` except where the 10-08 notes already said otherwise.
- New acquirer type `private_equity`.
- Sorted by announcement date, newest first.

## Case-study tables

| File | Content | Caveats |
|---|---|---|
| `takeout_case_signals.csv` | Public pre-deal signals for four 2026 cases, coded with `config/takeout_signals.yaml` | From search summaries and recall; every row U; controls not yet coded |
| `takeout_case_process.csv` | Private process from background sections for the same four deals | Crinetics from a BioPharma Dive account of the proxy; Ventyx from summaries of the proxy supplement; Soleno and Pacira not yet coded |
| `takeout_case_controls.csv` | Two stage-matched controls per case, picked from a size-ranked pool 90 days before the deal | All censored: their 365-day windows end after 2026-10-09 |
