# Backtest Pre-Registration: H16 Phase 2 quality drift

Written 2026-10-08, before any readout list or price history for the test was pulled. Motivating
note: `docs/research/2026-10-08_takeout_database_and_phase2_gate.md` section 5 (D-035). Grading
rules: `src/biotech_divedeep/models/phase2.py` at the commit that adds this file; any later change
to the gates, weights or the 0.65 threshold is an amendment and is reported as such.

| Field | Entry |
|---|---|
| Hypothesis | H16 (`docs/BLUEPRINT.md` section 3) |
| Question | After a positive randomized Phase 2 topline, do readouts graded `clean` earn positive excess return vs XBI from a post-financing entry, and more than `positive_not_clean` readouts? |
| Universe | Survivorship-free US-listed biotech (SIC 2834, 2835, 2836, 8731), delisted and acquired names included, market cap USD 100M to 15B on the day before the readout. |
| Events | First public topline of a randomized, controlled Phase 2 or Phase 2b in which the sponsor reports the primary endpoint met. Source: 8-K item 7.01 or 8.01 and press releases (M1, M4), matched to the ctgov record (M3) as of the readout date. Single-arm and Phase 1b readouts are excluded from the primary test and kept as a secondary set. |
| Grading | Two graders score each event blind to post-event prices, from the release, the registry version at the readout date and any same-day presentation. Disagreements resolved by a third read; inter-rater kappa reported. Unknown items score 0. |
| Entry | Close of the day after the first equity offering priced within 30 trading days of the readout (424B5 or 8-K), or close of day +20 if none. A sensitivity variant enters at the close of day +1. |
| Exit | Day +126 and day +252 after entry; earlier exit at the deal price if the company announces a sale (the takeout is part of the return, not removed). |
| Period | In-sample 2008-01 to 2017-12; out-of-sample 2018-01 to 2023-12; untouched hold-out 2024-01 to 2026-09. |
| Costs | 50 bp round trip for market cap above USD 1B, 150 bp below; delisting returns from the last trade or the deal price. |
| Primary metric | Mean 252-day excess return vs XBI total return of `clean` events, equal-weighted per event. |
| Success threshold | Out of sample: mean 252-day excess of `clean` events above +10% with a bootstrap 90% interval excluding 0, and `clean` minus `positive_not_clean` above +10 points. |
| Variants planned | Entry rule {post-financing, day +1}; horizon {126, 252}; threshold {0.55, 0.65, 0.75}. 12 variants, Holm-adjusted on the primary metric. |
| Secondary questions | Does assurance (with a mechanism-class prior fitted only on in-sample pairs) add to the grade? Does the takeout score (`models/takeout.py`) predict which `clean` names are acquired within 24 months? How much of the 252-day excess comes from takeouts? |
| Known risks | Grader hindsight (mitigated by blinding and registry versions); small samples per year; deal waves concentrating returns in a few years. |

## Results (append after running)

| Run | Date | Variant | Primary metric | Notes |
|---|---|---|---|---|
