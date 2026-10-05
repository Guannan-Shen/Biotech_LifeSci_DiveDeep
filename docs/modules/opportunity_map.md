# M10 Opportunity Map

Status: design. Phase 5 build target. This module answers the "insight" questions:
which areas most need breakthroughs, and which drug and tool types carry the largest
economic potential.

## 1. Grid

Rows: indications (MeSH-mapped). Columns: modalities (small molecule, mAb, bispecific,
ADC, radiopharmaceutical, siRNA/ASO, mRNA, autologous cell therapy, allogeneic and in
vivo cell therapy, gene therapy, gene editing, peptide incl. GLP-1 class, molecular
glue / degrader, vaccine, diagnostic, tool). Each cell carries component scores, never
a single opaque number.

## 2. Components and sources

| Component | Question | Sources |
|---|---|---|
| Burden | How much disease? | IHME Global Burden of Disease (DALYs, prevalence), CDC/SEER for US |
| Unmet need | How well is it treated today? | Approved therapies per indication (FDA labels), standard-of-care response rates from guidelines and pivotal trials |
| Economic pool | How much is spent and at what price tolerance? | CMS Part D and Part B spending dashboards, list price data, ICER value reports |
| Policy exposure | How do pricing rules hit this modality? | IRA negotiation timelines (small molecules earlier than biologics under current law; verify any amendments), Medicare coverage rules for diagnostics |
| Crowding | How many shots on goal? | ctgov active industry trials per indication x modality x target; number of Phase 2+ competitors per target |
| Acquirer demand | Who must buy? | Big pharma loss-of-exclusivity schedules (Orange/Purple Book, 10-Ks), therapeutic-area focus statements |
| Science momentum | Is the field moving? | PubMed and bioRxiv publication velocity, first-in-class approvals, AI-for-bio relevance (data availability, assay throughput) |
| Execution friction | How hard is delivery? | Modality COGS, manufacturing complexity, site-of-care requirements (IOVA lesson), REMS |

## 3. Outputs

- "White space" list: high burden and unmet need, manageable crowding, workable
  economics. This is where breakthroughs are most needed and most rewarded.
- "Crowded trades": popular targets with many Phase 2+ entrants (e.g., TL1A appears in
  the McKinsey chart as a fast-follow target), where late entrants face share
  compression.
- Modality economics table with launch friction and pricing-policy exposure.
- Point-in-time replay: run the map as of past dates to see whether it would have
  flagged known waves (GLP-1 obesity, ADCs, radiopharma) before the market did. This is
  the Phase 5 gate.

## 4. Initial qualitative priors (`own_assumption`, to be replaced by data)

- In a stylized rNPV model, a 2-year discovery saving is worth roughly as much as a
  10-point gain in Phase 2 success probability, and speed matters most in fast-follow
  races where launch order sets market share. The evidence for speed gains is public;
  the evidence for success-rate gains is still thin. See
  `docs/research/ai_drug_discovery_cycle_times.md`.
- Autologous cell therapy carries high delivery friction regardless of efficacy.
- Oral small molecules face earlier Medicare negotiation under the IRA as enacted;
  any legislative change here shifts modality economics and should be tracked as a
  regime event.
- Tools that produce training data for biological AI models may monetize AI demand
  before AI-native drugs do (H9).
