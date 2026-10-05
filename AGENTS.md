# AGENTS.md

Operating rules for any agent (Claude Code or otherwise) working in this repository.

## Non-negotiable rules

1. **English only.** Code, comments, docs, notes, commit messages. Source material in
   other languages is translated before it is committed.
2. **Python only** for code (3.11+). Notebooks are allowed for exploration but logic
   that matters moves into `src/`.
3. **Blueprint first.** Before executing any task:
   - Re-read `docs/BLUEPRINT.md` (mission, hypotheses, architecture, roadmap).
   - Check that the task fits the current phase and a named module or hypothesis.
   - If it does not fit, or it changes the design, update the blueprint and add an
     entry to `notes/decision_log.md` **before** writing code.
   - Double-check the big-picture direction once more after the plan is drafted, then
     execute.
4. **Always keep notes.** Every working session adds or updates
   `notes/sessions/YYYY-MM-DD.md` with: goal, what was done, decisions, open items,
   next steps. Durable decisions go to `notes/decision_log.md`; unanswered questions
   go to `notes/open_questions.md`; research ideas go to `notes/research_backlog.md`.
5. **Evidence discipline.** Every factual claim about a company, asset, trial or
   regulator carries a source and an evidence class (`fact`, `management_guidance`,
   `own_assumption`, `unverified`). Never fill unknowns with narrative.
6. **Point-in-time discipline.** Anything that can feed a backtest records
   `available_at`. No look-ahead joins, no survivorship-filtered universes.

## Repository map

| Path | Content |
|---|---|
| `docs/BLUEPRINT.md` | North star: mission, objective, hypotheses, architecture, roadmap |
| `docs/framework/` | Investment framework and archetype playbooks |
| `docs/modules/` | Design doc per module (EDGAR, FDA, ctgov, news, market, ...) |
| `docs/research/` | Research notes on external material (charts, papers, reports) |
| `config/` | Watchlist universe, data-source settings |
| `data/reference/` | Small curated reference tables committed to git (CSV) |
| `data/raw`, `data/silver`, `data/gold` | Local data store, git-ignored |
| `notes/` | Session logs, decision log, open questions, research backlog |
| `src/biotech_divedeep/` | Python package |
| `tests/` | Pytest suite |

## Development conventions

- Install: `pip install -e ".[dev]"`. Test: `python -m pytest`. Lint: `ruff check .`.
- Network clients must send a descriptive User-Agent; SEC requires a contact email,
  read from the `SEC_USER_AGENT` environment variable. Never hard-code personal emails.
- Respect rate limits (SEC: 10 requests/second max; openFDA: 240/minute without key).
- Connectors write raw payloads to `data/raw/<source>/<date>/` before parsing.
- Tests for connectors use recorded fixtures in `tests/fixtures/`; no live network in CI.
- Keep reference data small and sourced; each CSV in `data/reference/` has a sibling
  note in `docs/research/` describing provenance and caveats.

## Writing style for docs and notes

Direct sentences, no em dashes, no filler. State the claim, the source and the
uncertainty.
