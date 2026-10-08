# M16 Big Pharma and AI-Lab Watch

Status: design plus a seeded event log (added 2026-10-07, D-025). Phase 2 build target: weekly
manual log; Phase 3: automated newsroom and filing ingestion.

## 1. Why a small-cap system watches giants

Small and mid-cap life-science stocks are often priced on what a giant does next:

- **Demand signals.** Lilly paying outside labs to generate TuneLab training data (DNA, TWST,
  2026-09) or Novo adopting Claude Science (2026-09-16) is the closest thing to a purchase order
  the AI data layer has. H9 lives or dies on whether such deals become disclosed revenue.
- **Substitution signals.** An AI lab running its own wet lab (Anthropic, 2026-09-18) is both a
  customer of reagents and a competitor to outsourced data generation. The 2026-09-23 ART
  preprint moved gene-editing stocks without touching their fundamentals.
- **Exit prices.** Patent-cliff acquirers set the floor for approved-product companies (APLS,
  CPRX, CRNX in 2026; `data/reference/launch_layer_ma_2026.csv`).
- **Narrative fuel.** On 10-05, sell-side notes turned these announcements into "genomics is AI
  infrastructure" target hikes; on 10-06 the stocks reversed. Knowing which announcements carried
  money and which carried only words is the edge.

## 2. Actors

`config/watch_sources.yaml` lists each actor with its official channels. Tiers follow M13:
an actor's own release is `fact` for what the actor did; a counterparty's revenue from it stays
`unverified` until the counterparty files it.

| Group | Actors | Why |
|---|---|---|
| Trillion-dollar pharma | LLY | TuneLab, NVIDIA lab, the largest buyer of AI-bio services |
| Large pharma (USD 100B+) | NVO, JNJ, ABBV, MRK, AZN, NVS, RHHBY, AMGN, PFE, SNY, GSK, BMY, GILD, VRTX | AI partnerships and the M&A demand that sets launch-layer floors |
| AI labs and model makers | OpenAI, Anthropic, Google DeepMind and Isomorphic Labs, NVIDIA (BioNeMo, Clara), Microsoft Research | Model launches, wet labs, pharma alliances, data deals |
| Large tools | TMO, DHR, RVTY | Distribution partners for models (Revvity Signals hosts TuneLab) and acquirers of tools |

## 3. Event taxonomy

| event_type | Example | Expected read-through |
|---|---|---|
| `data_supply` | Ginkgo Datapoints and Twist join TuneLab | Revenue for the supplier only if terms or volumes are disclosed |
| `model_access` | TuneLab via Revvity Signals | Platform traffic; little revenue near term |
| `platform_partnership` | Novo and Anthropic | Signal of buyer intent; no listed small-cap counterparty |
| `compute_lab` | Lilly and NVIDIA, up to USD 1B over five years | Capital intensity of in-house AI; can crowd out outsourcing |
| `model_launch` | OpenAI GPT-Rosalind (2026-04-16) | Tool vendors named as partners (TMO) |
| `wet_lab` | Anthropic Bay Area lab | Ambiguous: customer and competitor |
| `discovery_claim` | ART preprint | Headline risk for modality incumbents; needs peer review |
| `financing` | Isomorphic USD 2.1B Series B | Private-market price for AI-bio; competition for partnerships |
| `acquisition` | Anthropic buys Coefficient Bio; Vertex buys Crinetics | Exit prices; vertical integration |
| `data_license` | Tempus and Recursion extension | Recurring data revenue (H9 evidence) |

Every row in `data/reference/pharma_ai_watch_events.csv` records `financial_terms_disclosed`,
the field H14 tests.

## 4. Hypothesis H14 (giant read-through)

Announcements by large pharma or AI labs that name a listed small or mid-cap counterparty move the
counterparty's price. **Announcements without financial terms reverse within about a month;
announcements with disclosed terms (upfront, minimums, revenue) drift in the same direction.**
This is Savor's (2012) information versus no-information split applied to partnership news.

Test design (to pre-register in `notes/backtests/` before data are pulled): event study on every
dated row with a listed counterparty, abnormal return vs XBI over days 0-1, 2-5, 6-21 and 22-63;
split by `financial_terms_disclosed` and by actor group; a placebo set of same-day announcements by
the same giant that name no listed company. Sources must give `available_at` to the minute where
possible (press-release timestamps; X post times for AI labs).

## 5. Sources and ingestion

| Source | What | Route | Status |
|---|---|---|---|
| Company newsrooms and IR pages | Releases with timestamps | RSS where offered; weekly manual check otherwise | URLs in `config/watch_sources.yaml`, to verify on the local machine |
| AI lab blogs | Model launches, partnerships, lab news | RSS (`/news`, `/blog`) | Same |
| Official X accounts | Often the first public post for AI labs | M13 (X API, Q-012); manual log meanwhile | Handles listed; T1 for the actor's own news |
| SEC EDGAR | 8-K and 6-K of listed actors and counterparties; full-text search for "TuneLab" and partner names | M1 connector (blocked here, Q-004) | Full-text search is the cheapest way to find which counterparties disclose terms |
| GDELT news volume | Coverage intensity of each announcement | `scripts/attention_proxies.py` | Local only |
| Sell-side target changes | Narrative amplification after an event | Press aggregators (U) | Count only; never a fact |

## 6. Weekly routine (Phase 2, manual)

1. Scan the newsroom and blog list in `config/watch_sources.yaml` and the official X accounts.
2. Log each relevant item as a row in `pharma_ai_watch_events.csv`; tag counterparties and
   whether financial terms were disclosed.
3. For rows with listed counterparties, note the counterparty's same-day and next-day moves in
   the weekly report and link the row to the fit matrix (`next_node`, `falsifier`).
4. Twice a year, compare logged events with counterparties' reported revenue: did any
   `data_supply` deal show up as a disclosed customer or revenue line? That is H9's scorecard.
