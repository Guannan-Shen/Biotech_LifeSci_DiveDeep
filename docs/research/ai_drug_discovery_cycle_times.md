# Research Note: AI-Enabled Drug Discovery Cycle Times (McKinsey chart)

Date: 2026-10-05. Source: chart shared by the investor, "Emerging trends in AI-enabled
drug discovery suggest accelerated discovery cycle time", McKinsey & Company; underlying
sources per the chart: company websites, Pharmaprojects, press search. Publication
date not shown on the image. Data transcribed to
`data/reference/ai_discovery_cycle_times.csv` (evidence class: `fact` as a transcription
of a third-party chart; the underlying company claims are `management_guidance`-grade
disclosures).

## 1. What the chart says

Nine publicly disclosed AI-enabled programs report discovery cycle times of 9 to 36
months, against a large-pharma median of 32 to 50 months from hit ID to preclinical
candidate (PCC) plus 16 to 20 months from PCC to first-in-human (FIH). Claimed speed-up
ranges from 15-45% (Insilico ISM3312) to 70-80% (Schrödinger SGR-1505, Exscientia
EXS21546).

## 2. Why it cannot be used as a statistic

The chart's own footnotes concede most of this:

1. **Selection bias**: a non-exhaustive set of publicized, mostly successful programs.
   Failed or quiet programs are absent.
2. **Mixed start and end points**: Target ID to IND, Hit ID to FIH, Hit ID to PCC,
   Target ID to PCC. Rows are not comparable to each other or fully to the benchmark.
3. **Fast followers dominate**: 6 of 9 programs address validated targets (HER2, TL1A,
   3CLpro, RBM39, MALT1, A2AR). Fast-follow chemistry is the easiest place to be fast.
4. **Stage at chart time**: phases shown were current when the chart was made; at
   least one program has since been discontinued (EXS21546 was deprioritized by
   Exscientia in 2023 per our recollection; mark `unverified`).
5. **Discovery speed is upstream of the expensive part**: clinical development
   dominates both time and cost.

## 3. What it does support

A testable hypothesis: AI-enabled teams can compress hit-to-candidate time on validated
targets. Two investment implications follow, both to be tested:

### 3a. Speed is worth real money, comparable to modest success-rate gains

Stylized rNPV using `src/biotech_divedeep/models/rnpv.py` (all inputs `own_assumption`):
discovery costs 10 per year, Phase 1 cost 20 / 1.5 years / 60% advance, Phase 2 cost 50 /
2.5 years / 30% advance, Phase 3 cost 150 / 3 years / 60% advance, filing 5 / 1 year / 90%
approval, discount rate 10%, base discovery 4 years.

| Commercial value at launch | Base rNPV | Discovery 2 years shorter | Phase 2 POS 30% to 40% | Phase 2 POS 30% to 45% |
|---|---|---|---|---|
| 1,000 | -48.1 | +13.0 | +6.1 | +9.1 |
| 3,000 | +13.8 | +26.0 | +26.7 | +40.1 |
| 6,000 | +106.8 | +45.5 | +57.7 | +86.5 |

Reading: a 2-year discovery saving is worth about the same as a 10-point Phase 2
success-rate gain for a mid-value asset. The speed benefit is relatively larger for
low-value assets (it mostly saves discounting and early spend) and the success-rate
benefit is larger for high-value assets. This corrects an earlier prior in this repo
that speed barely matters.

### 3b. Speed matters most in races

For fast-follow targets, arriving second instead of fourth changes peak market share,
which this rNPV sketch does not capture (it holds launch value fixed). Phase 5 work:
model launch value as a function of launch order using historical class launches.

## 4. What would make the AI claim investable

Evidence the chart lacks, and which the system should collect per platform company:

- Denominator: all programs started, including stopped ones.
- Like-for-like comparison: same target class and modality, same start and end points.
- Total R&D spend per candidate, not only elapsed months.
- Human outcomes: Phase 1 to Phase 2 transition and Phase 2 success rates of
  AI-derived assets vs base rates. This is the link in the validation chain that
  currently has the least evidence.

## 5. Uses in this repo

- Prior for the `ai_platform` archetype: cycle-time advantage plausible, success-rate
  advantage unproven.
- Feature idea for P5 (takeout model) and M10: crowded fast-follow targets reward speed.
- Ticker overlap with the universe: RXRX (REC-1245, EXS21546 via the Exscientia merger),
  SDGR (SGR-1505), ABSI (ABS-101). Insilico, Iambic, Generate and GV20 are private or
  listed outside the US (verify).
