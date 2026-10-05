# Biotech & Life Sciences DiveDeep

A point-in-time research and decision system for investing in small and mid-cap
biotech and life-science companies, with one measurable goal: a basket that beats
**XBI over rolling 6-month and longer windows**, after costs.

It tracks four primary sources (SEC EDGAR, FDA, ClinicalTrials.gov, company news),
turns them into a single timestamped event stream, and uses that stream to:

- **Understand** each company through archetype-specific models (clinical binary,
  launch, commercial pharma, tools, software, diagnostics, AI platforms).
- **Find insight** on where breakthroughs are most needed and which modalities carry
  the most economic potential.
- **Predict** the events that move these stocks: financings, trial delays, FDA actions,
  launch trajectories, takeouts.

## Start here

| Document | Why |
|---|---|
| [`docs/BLUEPRINT.md`](docs/BLUEPRINT.md) | Mission, objective, return hypotheses, architecture, roadmap. The north star |
| [`AGENTS.md`](AGENTS.md) | Rules for anyone (human or agent) working here |
| [`docs/framework/investment_framework.md`](docs/framework/investment_framework.md) | Evidence, survival and price gates; scenarios; trend overlay; memo template |
| [`docs/framework/archetypes.md`](docs/framework/archetypes.md) | Playbook per business type, event taxonomy |
| [`docs/modules/`](docs/modules/) | One design doc per module |
| [`docs/research/`](docs/research/) | Notes on external material (AI discovery cycle times, specialist ownership) |
| [`notes/`](notes/) | Session log, decision log, open questions, research backlog |
| [`config/universe.yaml`](config/universe.yaml) | Watchlist, screen candidates, benchmarks |

## Status

Phase 0 (blueprint) complete. Phase 1 (data foundation: entity master, EDGAR, ctgov and
openFDA connectors) is next. See the roadmap in the blueprint.

## Setup

```bash
pip install -e ".[dev]"          # add ".[data]" for pandas / pyarrow / duckdb
python -m pytest
ruff check .
export SEC_USER_AGENT="Your Name your@email"   # required by SEC for EDGAR access
```

## Disclaimer

Research software. Nothing here is investment advice. Company statements in this
repository carry evidence classes; anything marked `unverified` has not been checked
against a primary source.
