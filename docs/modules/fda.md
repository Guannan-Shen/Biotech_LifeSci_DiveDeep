# M2 FDA Tracker

Status: design. Phase 1 build target.

## 1. Sources

| Use | Source | Notes |
|---|---|---|
| Drug approvals and submissions (CDER) | openFDA `https://api.fda.gov/drug/drugsfda.json` | Application number, submission type (ORIG, SUPPL), status dates, review priority |
| Labels | openFDA `/drug/label.json` | Indications text, boxed warnings, label revisions |
| Adverse events | openFDA `/drug/event.json` (FAERS) | Post-launch safety signals; report counts as a noisy utilization proxy |
| Recalls / enforcement | openFDA `/drug/enforcement.json` | Supply and quality issues |
| Devices and diagnostics | openFDA `/device/pma.json`, `/device/510k.json` | For dx and tools (GRAL, QSI, PACB clinical products) |
| Biologics under CBER | FDA CBER approval lists, "Approved Cellular and Gene Therapy Products" page | **Not in Drugs@FDA.** Cell and gene therapies (e.g., Amtagvi; RP1 if approved) live here |
| Novel approvals | CDER "Novel Drug Approvals" yearly pages | Clean NME/BLA list |
| Complete response letters | FDA's published CRL collection (began 2025) | Verify current location and whether openFDA exposes it as an endpoint |
| Advisory committees | FDA Advisory Committee Calendar | HTML scrape; meeting date, product, questions, later the vote |
| Patents and exclusivity | Orange Book data files; Purple Book downloads | Loss-of-exclusivity timelines; acquirer demand (H8) |
| Inspections, 483s, warning letters | FDA Data Dashboard; warning letter pages | Manufacturing risk for CDMO-dependent sponsors |
| Shortages | openFDA drug shortages endpoint (verify) | Demand shocks for generics and specialty pharma |
| Policy | Federal Register, FDA press announcements | Regime changes (review staffing, priority voucher programs, pricing policy); evidence class `unverified` until read in full |

Rules: openFDA API key from `OPENFDA_API_KEY` (optional; raises limits), raw payloads
saved before parsing.

## 2. What FDA does not publish

- **PDUFA goal dates** come from company disclosures only, so they enter the catalyst
  calendar as `management_guidance`.
- Pending applications are not public; filing acceptance comes from the sponsor.
- CRL reasons historically came only from sponsors (selectively). The newer published
  CRL collection allows comparing sponsor spin with the letter itself, a useful
  management-credibility input.

## 3. Entities and linking

`application_number` (NDA/BLA/PMA) <-> asset (entity master) <-> sponsor company
(CIK). Sponsor names in FDA data are legal entity names and subsidiaries; mapping is
curated in the entity master with automatic suggestions by fuzzy match.

## 4. Derived events

approval, label_update (new indication, boxed warning), crl, adcom_scheduled,
adcom_vote, safety_communication, recall, manufacturing_inspection (483 / warning letter
at a site used by a tracked sponsor), exclusivity_expiry.

## 5. Features for M9 models

- FDA action model: review priority, designations (BTD, Fast Track, Orphan, accelerated
  approval), AdCom held and vote split, prior CRL, modality and CMC complexity,
  manufacturing site history, sponsor's prior approvals, surrogate vs clinical endpoint.
- Launch model: label breadth vs trial population, boxed warning or REMS, competitor
  approvals in the same indication.
- Safety drift: FAERS reports per quarter normalized by estimated exposure, with the
  usual caveats (stimulated reporting after news, duplicates).

## 6. Tests

Fixtures: one CDER NDA with supplements, one CBER BLA (to prove the second path works),
one PMA device, one CRL record.
