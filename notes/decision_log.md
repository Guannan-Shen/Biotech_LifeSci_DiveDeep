# Decision Log

Format: ID, date, decision, rationale, status. Newest at the bottom. Reversals get a new
entry that references the old one.

| ID | Date | Decision | Rationale | Status |
|---|---|---|---|---|
| D-001 | 2026-10-05 | English only; Python only. | Investor rule. One language for code and docs keeps the corpus searchable and agent-friendly. | Active |
| D-002 | 2026-10-05 | Repository `Guannan-Shen/Biotech_LifeSci_DiveDeep` is the project home. | It was created empty for this purpose and is the repo attached to the session. | Active |
| D-003 | 2026-10-05 | Event-centric data model with `available_at` and `observed_at`. | One stream feeds calendars, alerts, models and backtests; separating the two timestamps prevents look-ahead. | Active |
| D-004 | 2026-10-05 | Evidence classes: fact, management_guidance, own_assumption, unverified. | Carried over from the investor's framework; makes trust explicit in every table and report. | Active |
| D-005 | 2026-10-05 | Storage: raw immutable snapshots, then Parquet + DuckDB; local-first. | Free, fast, reproducible; no server to run. Revisit if multi-user access is needed. | Active |
| D-006 | 2026-10-05 | Primary benchmark XBI total return, rolling 126 and 252 trading days. Diagnostic benchmarks: IBB, tools peer basket, equal-weight watchlist. | Matches the investor's goal; sub-benchmarks stop tools and software names from being judged against clinical biotech. | Active |
| D-007 | 2026-10-05 | Seven archetypes decide the model per company. | Tools, software, diagnostics, launches and binaries have different value drivers; one model would mislead. | Active |
| D-008 | 2026-10-05 | Left-tail avoidance (H1) is the first hypothesis to test. | XBI's modified equal weighting carries the left tail of small caps; avoiding it is the most testable edge. | Active |
| D-009 | 2026-10-05 | Source priority: EDGAR > FDA > ctgov > company IR > aggregators. | Legal accountability and timestamp quality. | Active |
| D-010 | 2026-10-05 | Backtests are pre-registered in `notes/backtests/`. | Controls multiple-testing inflation; mirrors clinical-trial discipline. | Active |
| D-011 | 2026-10-05 | Phase gate to real capital: out-of-sample IR > 0.4, positive excess in at least 60% of rolling 6-month windows, then 6 months of paper trading. | Initial thresholds; to be confirmed by the investor (see open questions). | Proposed |
| D-012 | 2026-10-05 | Corrected prior: discovery speed is economically material. A stylized rNPV shows a 2-year discovery saving is worth about a 10-point Phase 2 success-rate gain for mid-value assets. | Computed in `docs/research/ai_drug_discovery_cycle_times.md`, reproduced in `tests/test_rnpv.py`. | Active |
| D-013 | 2026-10-05 | Add an adjacent sleeve for regulated deep-tech (archetype `regulated_deeptech`, `sleeve: adjacent`). Pilot: MRLN. | Investor request. Runway-bound, regulator-gated companies share biotech economics; survival and price gates transfer unchanged, evidence sources need extension (M14). | Active |
| D-014 | 2026-10-05 | Portfolio still judged vs XBI; adjacent sleeve capped (15% proposed) with its own diagnostic benchmark. | Keeps the mandate measurable while allowing the extension. | Proposed (Q-011) |
| D-015 | 2026-10-05 | Add M13 Social / X tracker with account tiers T1-T5; only Reg FD-designated channels can yield `fact`; crowd data used only as attention metrics. | X carries early disclosures for venture-like companies and fast expert critique in biotech; tiering contains manipulation risk. | Active |
| D-016 | 2026-10-05 | X data only via the official API; full text stored in a purgeable table, hashes and derived fields in the immutable store. | Terms of service and deletion obligations vs audit trail. | Active |
| D-017 | 2026-10-05 | `scripts/check_data_access.py` is stdlib-only and runs before install. | Lets the investor verify source access on a local machine with zero setup. | Active |
