# Archetype Playbooks

Each company in the universe carries one or more archetype codes
(`config/universe.yaml`). The archetype picks the valuation model, the key metrics,
the event types to watch and the typical failure mode. Company-specific statements
below are `unverified` unless a source is linked; the investor's own descriptions are
recorded as such.

---

## `clinical_binary`: value hinges on readouts

Examples: SLS (SELLAS; investor note: phase 3 "powerball"), EDSA (Edesa).

| Item | Content |
|---|---|
| Value driver | Probability-weighted asset value after the next readout, minus dilution to get there |
| Key metrics | Cash vs months to readout, trial design quality, effect size needed vs observed in Phase 2, enrollment and event accrual pace |
| Watch events | ctgov status, enrollment complete, interim analysis, DSMB recommendations, topline, S-3/ATM activity |
| Failure modes | Underpowered or poorly controlled trial; endpoint drift; readout delays that force financing at the low; event-driven trials where accrual is slower than guided |
| Position rule | Sized as an event: cap = loss budget / stress drop (assume 70-90% gap). Consider H3 run-up rule: own into the event, cut before the binary unless the edge is in the outcome itself |
| Moat and people prompts | Differentiated mechanism and IP life; management's record of trials reading out on time and on the guided endpoint (`business_quality.md` section 5) |
| Prediction hooks | Trial-delay model (ctgov slippage), financing model (raise after data or before runway hits 12 months), outcome prior from phase/indication base rates |

SLS specific research questions: what event count triggers the final analysis, how
accrual compares to guidance over time, and what the statistical design implies for
the minimum detectable hazard ratio. All `unverified` until pulled from the registry
and filings.

## `launch`: approved, commercialization in progress

Examples: REPL (investor note: recently approved, launch slower than hoped), IOVA
(Amtagvi, an autologous TIL cell therapy; accelerated approval February 2024; launch
took longer than many expected).

| Item | Content |
|---|---|
| Value driver | Shape of the first 8 to 12 quarters of patient starts and net revenue vs analogs; time to cash-flow breakeven |
| Key metrics | Treating sites activated, patients infused or started per quarter, script-to-treatment time, manufacturing success rate and turnaround (for cell therapy), gross-to-net, inventory, SG&A per patient |
| Watch events | Quarterly product revenue (XBRL), label expansions, confirmatory trial status (accelerated approvals), payer policies, FAERS signals, manufacturing 483s |
| Failure modes | Site-of-care friction (cell and oncolytic therapies need authorized treatment centers); manufacturing capacity; reimbursement lag; confirmatory trial risk; overhead built for a faster ramp |
| Model | Patient-cohort model (framework section 5); one-time therapies use a site-activation x throughput model |
| Moat and people prompts | Site-of-care economics and reimbursement; launch guidance vs analogs, candor about slow quarters |
| Prediction hooks | Launch-analog library: normalize quarterly revenue since approval for comparable launches (modality, setting, pricing) and score where each launch sits vs the analog band |

Insight to test (H2): the market tends to price approval as the finish line, then
over-punishes slow quarters. A launch that is slow but on an analog-consistent
trajectory for its modality may be mispriced; one with deteriorating unit metrics is
correctly punished. The analog library separates the two.

## `commercial_pharma`: revenue-generating specialty or rare-disease pharma

Examples: HROW (Harrow; ophthalmic portfolio), ETON (Eton; rare-disease portfolio).
Investor description: "platform-like" life-science companies.

| Item | Content |
|---|---|
| Value driver | Product-level revenue growth x gross margin, operating leverage, capital allocation (in-licensing, acquisitions) |
| Key metrics | Revenue by product, gross margin, SG&A ratio, adjusted EBITDA vs FCF gap, debt and covenants, acquisition cadence and payback |
| Watch events | Product approvals and acquisitions, debt refinancing, quarterly revenue, generic or 505(b)(2) competition, Orange Book exclusivity changes |
| Failure modes | Acquisition-driven growth hiding organic decline; leverage; single-product concentration; reimbursement changes |
| Model | Normalized FCF, product-level DCF, exclusivity-aware terminal values |
| Moat and people prompts | Exclusivity, call-point scale, reimbursement position, deal sourcing (deal multiple = revenue in year two or three / total paid); guidance credibility ledger |

These names test H6 (quality inside biotech). They also act as a ballast within a
basket that otherwise carries binary risk.

## `tools`: instruments plus consumables

Examples: PACB, ILMN, TXG, TWST, QSI.

| Item | Content |
|---|---|
| Value driver | Active installed base x consumable pull-through; new-product adoption; gross margin path |
| Key metrics | Placements, active vs total installed base, pull-through per system, consumable share of revenue, gross margin, opex trajectory, customer mix (academic vs biopharma vs clinical) |
| Watch events | Quarterly results, product launches, NIH and academic budget news, China exposure, large pharma or AI-lab data-generation deals |
| Failure modes | Placements bought with price cuts; academic funding shocks; competitive platform transitions |
| AI angle (H9) | Data generators may be the earliest beneficiaries of AI-for-bio demand. Track disclosed AI or foundation-model customers and their consumable volume |
| Moat and people prompts | Installed-base pull-through and workflow lock-in; product-transition execution and pricing discipline |

## `software`: simulation and discovery software

Examples: SDGR, CERT.

| Item | Content |
|---|---|
| Value driver | Recurring contract value, retention, expansion, FCF |
| Key metrics | ACV, number of customers above thresholds, net retention, deferred revenue, services margin, milestone income (non-recurring) |
| Failure modes | License-model transitions masking or faking growth; services dilution; pharma R&D budget cuts |
| Model | Software multiple on normalized FCF plus separate pipeline rNPV or equity stakes |
| Moat and people prompts | Switching cost and data; honesty through license-model transitions |

## `dx_data`: diagnostics and clinical data

Examples: TEM, GRAL.

| Item | Content |
|---|---|
| Value driver | Billable volume x realized ASP, coverage expansion, data licensing |
| Key metrics | Test volume, ASP, collections, gross margin per test, coverage decisions (CMS NCD/LCD, commercial), data-licensing backlog |
| Watch events | FDA decisions (PMA), AdComs, CMS coverage, guideline inclusion, legislation affecting screening coverage |
| Failure modes | Volume growth with falling ASP; regulatory approval without reimbursement; data revenue lumpiness |
| Moat and people prompts | Coverage decisions and guideline inclusion; coverage-timeline guidance vs outcomes |

## `ai_platform`: AI-native discovery and automated labs

Examples: RXRX, DNA, SDGR (pipeline side).

| Item | Content |
|---|---|
| Value driver | Validated assets and partnership economics; platform value only after the validation chain holds |
| Key metrics | Clinical readouts of platform-derived assets, partner milestones received in cash, cost per development candidate, cycle time (point-in-time disclosed), cash burn |
| Watch events | Phase 2 data, partner opt-ins or terminations, restructurings, compute and data deals |
| Failure modes | Platform narrative without human proof; partner attrition; burn above revenue scaling |
| Note | AI does not raise priors by itself (framework section 4). See `docs/research/ai_drug_discovery_cycle_times.md` for the rNPV trade-off between faster discovery and higher clinical success rates |
| Moat and people prompts | Proprietary data and validated predictions; partner milestone guidance vs cash received |

---

## Cross-archetype event taxonomy (feeds `Event.event_type`)

| Group | Event types |
|---|---|
| Clinical | trial_registered, trial_status_change, enrollment_change, primary_completion_change, endpoint_change, topline_readout, interim_analysis, dsmb_recommendation |
| Regulatory | filing_submitted, filing_accepted, priority_review, breakthrough_designation, adcom_scheduled, adcom_vote, approval, crl, label_update, safety_communication, manufacturing_inspection |
| Financing | shelf_filed, atm_established, offering_priced, pipe, convertible_issued, debt_refinanced, reverse_split, going_concern |
| Corporate | partnership, licensing, acquisition_announced, restructuring, executive_change, insider_trade, ownership_13d_13g, ownership_13f |
| Commercial | quarterly_results, guidance_change, product_launch, coverage_decision |
| Market | price_regime_change, relative_strength_signal |
