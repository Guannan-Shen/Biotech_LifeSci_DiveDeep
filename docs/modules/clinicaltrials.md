# M3 ClinicalTrials.gov Tracker

Status: design. Phase 1 build target.

## 1. Sources

| Use | Source | Notes |
|---|---|---|
| Current records | API v2 `https://clinicaltrials.gov/api/v2/studies` and `/studies/{NCT}` | JSON; query by sponsor, intervention, condition |
| Version history | Website record history (internal endpoints; unstable) | Use only with fallbacks; validate before relying on it |
| Point-in-time backfill | AACT (CTTI) database: daily PostgreSQL snapshots of ctgov; archived static copies | Best route to historical states for backtests (H7) |
| Ongoing history | Our own daily snapshots + diffs | From Phase 1 onward we own a clean history |
| Later | EU CTIS, WHO ICTRP, ChiCTR | Ex-US trials of tracked assets |

## 2. Trial card (schema)

Mirrors the framework's trial card. Fields marked (ctgov) come from the registry; the
rest come from filings, publications and press releases with evidence classes.

| Field | Source |
|---|---|
| nct_id, title, sponsor, collaborators | ctgov |
| asset_ids (entity master), interventions | ctgov + curation |
| condition(s), mapped indication (MeSH) | ctgov |
| phase, allocation, masking, comparator arms | ctgov |
| enrollment (ESTIMATED vs ACTUAL), sites, countries | ctgov |
| primary and secondary outcomes (text + time frame) | ctgov |
| overall_status, why_stopped | ctgov |
| start, primary_completion, completion dates (+ ESTIMATED/ACTUAL type) | ctgov |
| last_update_posted (point-in-time key) | ctgov |
| effect size, CI, safety, subgroups, follow-up maturity | publications / PR (evidence class) |
| expected readout window | company guidance (`management_guidance`) |
| source URLs, updated_at | system |

## 3. Change detection (H7 signals)

Each daily snapshot is diffed against the previous one. Flags:

| Flag | Rule (initial, tune in Phase 3) | Interpretation |
|---|---|---|
| pcd_slip | Estimated primary completion moved later by more than 90 days | Enrollment or event-accrual trouble; delays force financing |
| pcd_pull_in | Moved earlier | Faster accrual or design change |
| pcd_actual | Primary completion type switched to ACTUAL | **Readout window opens.** Topline usually follows within months; strong catalyst-calendar input |
| enrollment_cut | Target enrollment reduced | Possible futility, budget cut or redesign |
| enrollment_actual | Enrollment switched to ACTUAL | Enrollment complete; often press-released |
| status_negative | Status to SUSPENDED, TERMINATED or WITHDRAWN | Read `why_stopped` |
| endpoint_edit | Primary outcome text or time frame changed | Potential goalpost moving; high scrutiny |
| arm_change | Arms added or removed | Design change |
| site_drop | Sites removed in bulk | Operational trouble |

Every flag becomes an `Event` with `available_at = last_update_posted` (registry post
date). Companies sometimes update the registry later than reality; the lag is part of
the signal and is measured, not assumed.

## 4. Sponsor and asset matching

Registry sponsor strings vary ("Recursion Pharmaceuticals Inc.", subsidiaries,
partners as sponsors). Asset codes change (REC-4881, INN names). Matching goes through
the entity master: curated aliases, then suggestion queue for unmatched trials whose
interventions mention tracked asset codes.

## 5. Management credibility score

For each company: share of guided readouts (from PRs and filings) delivered within the
guided window, and the average slip in months. Computed from the catalyst ledger (M6)
joined with ctgov actual dates. Feeds position sizing and the trial-delay model.
