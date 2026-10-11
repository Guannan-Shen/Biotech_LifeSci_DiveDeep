# Backtest Pre-Registration: H17 Post-announcement drift

Written 2026-10-11, before any universe-wide event list or price panel for the test was pulled.
The only prices seen are QSI and NAUT (case study in
`docs/research/2026-10-11_qsi_naut_protein_platforms_and_drift.md`); both tickers are excluded from
the in-sample and out-of-sample sets so the case study cannot leak into the test. Method:
`src/biotech_divedeep/signals/drift.py` at the commit that adds this file; any later change to the
surprise definition, thresholds or windows is an amendment and is reported as such.

## Why a reaction-based surprise

Classic PEAD sorts on standardized unexpected earnings (Ball and Brown 1968; Bernard and Thomas
1989, 1990). Three facts make that the wrong tool here:

1. For pre-revenue tools and clinical names, consensus EPS is a forecast of operating expenses.
   Beating it says little about value.
2. Most of the information arrives outside earnings, or bundled with them: launch dates, trial and
   product data, runway changes, financings.
3. PEAD measured with SUE has shrunk in liquid US stocks since the mid-2000s (Chordia, Goyal,
   Sadka, Sadka and Shivakumar 2009; Martineau 2022) and survives mainly where trading is costly,
   which is exactly the small-cap life-science universe. That cuts both ways: the drift may exist
   and still be uncapturable after costs.

So the surprise is the market's own reaction: the two-day market-adjusted return (EAR, Brandt,
Kishore, Santa-Clara and Venkatachalam 2008), standardized by the stock's pre-event abnormal
volatility (SEAR), with abnormal volume as confirmation (Garfinkel and Sokobin 2006). Moves with no
logged announcement are measured with the same machinery because Chan (2003) finds they reverse.

| Field | Entry |
|---|---|
| Hypothesis | H17 (`docs/BLUEPRINT.md` section 3) |
| Question | After a company announcement, does the sign and size of the standardized two-day reaction predict the abnormal return over the next 20 and 60 trading days in US-listed small-cap life-science stocks? |
| Universe | Point-in-time research universe (therapeutics, tools, diagnostics layers of `us_lifesci_universe` rebuilt per month from the listing mirror), market cap USD 50M to 5B on day -2, close above USD 1 on day -2, delisted and acquired names kept. QSI and NAUT excluded. |
| Events | (a) Earnings releases (8-K item 2.02); (b) timeline changes stated in any release (launch, filing, readout or certification date moved, cut or reaffirmed), coded `slip`, `extend`, `reaffirm`, `cut` from the text before looking at prices; (c) product or trial data releases (8-K 7.01 or 8.01); (d) financings (424B5 pricing, registered direct, ATM prospectus); (e) no-news shocks: abs abnormal return of at least 3 pre-event sigmas on at least 3x abnormal volume, more than 2 sessions from any logged event. Release times from EDGAR acceptance timestamps (Q-043); session chosen by the rule in `resolve_event_index`. |
| Surprise | SEAR = CAR[0,+1] / (sd of daily abnormal return over [-120,-11] x sqrt 2). Classes: `positive` if SEAR >= 2 and mean abnormal volume over [0,+1] >= 2; `negative` if SEAR <= -2 with the same volume test; otherwise `neutral`. |
| Benchmark | XBI total return (Q-049); until it is available, `EW_LIFESCI_200M` (point-in-time equal-weight therapeutics and tools, prior-day cap at least USD 200M, daily returns winsorized at -60% and +150%). The final test reports both. |
| Entry and exit | Enter at the close of day +1 (after the reaction is known). Exit at the close of day +20 and day +60. Overlapping events in one name: the later event starts a new observation and the earlier one is truncated at its day -1. |
| Period | In-sample 2021-06 to 2023-12; out-of-sample 2024-01 to 2025-12; untouched hold-out 2026-01 onward. (The listing mirror starts 2021-01; earlier periods need EDGAR and a paid price source, Q-003.) |
| Costs | Round trip 150 bp above USD 300M market cap, 300 bp from USD 50M to 300M; sensitivity at double. Delisting return from the last trade or deal price. |
| Primary metric | Mean BHAR[+2,+60] of `negative` announcement events (the long-only exit and avoid use), equal-weighted per event, with standard errors clustered by calendar month. |
| Success threshold | Out of sample: mean BHAR[+2,+60] of `negative` events below -5% after costs of a hypothetical exit-versus-hold comparison, with a 90% cluster-bootstrap interval excluding 0, and `negative` minus `neutral` below -5 points. |
| Secondary predictions (each tested, Holm-adjusted) | P2: `slip` events drift more negatively than `negative` earnings events without a timeline change. P3: `positive` events drift less (or reverse) when an ATM or effective shelf is live at day 0 or a financing prices within 20 sessions (dilution truncation; interacts with H1). P4: positive no-news shocks have negative BHAR[+2,+60] (reversal), stronger for names with a top-decile attention spike (H10). P5: calendar-time long-only portfolio that holds `positive` non-financing-truncated events for 60 days beats the benchmark net of costs. |
| Variants planned | SEAR threshold {1.5, 2, 2.5}; volume threshold {1.5, 2, 3}; horizon {20, 60}; benchmark {XBI, EW proxy}. 36 cells on the primary metric, Holm-adjusted; P2-P5 at the base cell only. |
| Known risks | Event-date errors from aggregators (mitigated by EDGAR timestamps and the volume rule); bad snapshots in the mirror (about 1% of days show a stale close vs one-day return; the drift uses close-to-close returns over windows, which telescope); micro-cap costs swamp drift; clustering of events in theme waves (cluster by month); look-ahead in timeline coding (code from text before pulling prices). |

## Case-study observations that motivated it (not evidence for the test)

QSI and NAUT, 2021-06 to 2026-10, 39 earnings events, 6 other announcements, 23 detected no-news
shocks (`data/reference/announcement_drift_qsi_naut.csv`):

- 38 of 45 announcements were `neutral` (median absolute EAR on earnings 6%, median abnormal
  volume 1.05x): for pre-revenue platforms, earnings days carry little news.
- The two largest negative announcement reactions came with bad technical or timeline news: QSI in
  August 2023 (EAR -41%) and NAUT on 2026-07-28 (broadscale probes miss 2027 specifications, EAR
  -40%, then a further -29% over days +2 to +20 against a -4% median baseline).
- QSI's eleven positive no-news shocks (median EAR +27%; the late-2024 "quantum" name rally among
  them) returned a median BHAR[+2,+60] of -29% against a -16% unconditional median for the stock;
  nine of eleven were negative. NAUT's seven positive shocks split: the late-2025 run kept going.

## Results (append after running)

| Run | Date | Variant | Primary metric | Notes |
|---|---|---|---|---|
