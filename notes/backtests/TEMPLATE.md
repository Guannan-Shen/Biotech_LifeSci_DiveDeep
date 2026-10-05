# Backtest Pre-Registration: <ID> <short name>

Copy to `notes/backtests/YYYY-MM-DD_<hypothesis>_<name>.md` and fill in **before** running.

| Field | Entry |
|---|---|
| Hypothesis | H? from `docs/BLUEPRINT.md` section 3 |
| Question | One sentence |
| Universe | Definition, filters, point-in-time membership source |
| Period | In-sample, out-of-sample, untouched hold-out |
| Rules | Entry, exit, rebalance cadence, sizing, constraints |
| Costs | Spread and impact model, delisting return assumptions |
| Primary metric | e.g., rolling 126-day excess vs XBI total return |
| Success threshold | Stated before running |
| Variants planned | List every parameter set to be tried (counts toward multiple testing) |

## Results (append after running)

| Run | Date | Variant | Primary metric | Notes |
|---|---|---|---|---|
