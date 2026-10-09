# M9 Event Prediction

Status: design. Phase 4 build target. Models are judged by calibration, not by
headline accuracy.

## 1. Model list (priority order)

| # | Target | Horizon | Key features | Label source |
|---|---|---|---|---|
| P1 | Equity financing within 90 days | 90 days | Runway, dilution pressure score, 20-day run-up, recent data event, shelf/ATM status, financing window index, specialist ownership | 424B5 / 8-K 1.01, 3.02 |
| P2 | Trial primary-completion slip beyond guided window | Per trial | Sponsor slip history, enrollment pace vs target, indication rarity, sites, phase, event-driven design | ctgov history (AACT) |
| P3 | FDA first-cycle action: approval vs CRL | Per application | Review priority, designations, AdCom outcome, modality and CMC complexity, site inspection history, prior CRLs, sponsor experience, endpoint type | Drugs@FDA, CBER lists, CRL collection, 8-Ks |
| P4 | Launch trajectory class (above / on / below analog band) | Quarters 3 to 8 | Early quarters revenue vs analogs, label breadth, modality, site-of-care, payer policy, gross-to-net | 10-Q product revenue (XBRL) |
| P5 | Takeout within 12 months | 12 months | Stage and data class, Phase 2 grade, therapeutic area vs acquirer LOE gaps, market cap band, specialist ownership, activist 13D or proxy contest, big-pharma equity or option, cash, deal-wave index | 8-K / DEFM14A / SC TO-T / SC 14D9; seed table `data/reference/biotech_takeouts.csv` |
| P6 | Readout outcome prior | Per readout | Phase/indication base rates, mechanism validation elsewhere, Phase 2 effect size and CI shrunk toward a mechanism-class prior, assurance, Phase 2 scorecard | Topline events (hand-labeled) |
| P7 | Price reaction distribution given event | Event window | Event type, market-implied move (when available), run-up, short interest, cash | Prices + events |

Interim tools (2026-10-08, D-034, D-035): `models/takeout.py` scores P5 with own-assumption
likelihood ratios from `config/takeout_priors.yaml` until the hazard model is fitted;
`models/phase2.py` gives P6 its shrinkage, assurance and scorecard. Both are described in
`docs/research/2026-10-08_takeout_database_and_phase2_gate.md`.

P6 stays mostly prior-driven; outcome prediction from public data is weak and the
framework says so. P1 and P2 are the most data-rich and likely the most useful.

## 2. Methodology

- Time-split validation only (train on years before, test on years after).
- Baselines: base rates by phase, indication and modality; any model must beat them on
  Brier score and log loss.
- Calibration curves and reliability tables published in each model card.
- Point-in-time features via `available_at`; feature snapshots stored per prediction
  date so the live model and the backtest see identical inputs.
- Interpretable models first (regularized logistic, gradient boosting with monotonic
  constraints); complexity only if it improves calibrated out-of-sample skill.
- Every model has a card in `docs/models/` (created when built): data, period, metrics,
  failure cases.

## 3. How predictions are used

They feed scenario probabilities in memos (as ranges), the event position cap, and
H1/H3 rules. A prediction never replaces reading the primary evidence for a held name.
