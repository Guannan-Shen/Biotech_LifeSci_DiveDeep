# Adjacent Sleeve: Regulated Deep-Tech (`regulated_deeptech`)

Added 2026-10-05 (D-013). Applies the biotech framework to listed companies outside
life sciences that behave like clinical-stage biotech: venture-like risk, finite cash
runway, and a value step that depends on a regulator or a large institutional customer.
Pilot company: MRLN (Merlin, AI autonomous flight). Candidate peers to evaluate later:
eVTOL, space, defense autonomy, nuclear and fusion names; each must pass the same gates.

## 1. Why the transfer works

A clinical-stage biotech is a bundle of three things: a cash balance that burns, a
sequence of gated milestones with uncertain timing, and a payoff that arrives only
after an external authority says yes. Certification-bound aerospace and
defense-program companies have the same structure. The survival and price gates
transfer unchanged; the evidence gate needs new sources.

## 2. Concept map

| Biotech concept | Regulated deep-tech equivalent | Notes |
|---|---|---|
| FDA approval | FAA (or EASA, CAANZ) type certificate or supplemental type certificate (STC) | Certification of AI/ML software has no settled precedent; timelines carry extra uncertainty |
| Clinical phases (1, 2, 3) | Certification stages of involvement (SOI 1 to 4 under DO-178C software assurance), flight test campaigns | SOI 4 is the final software audit before credit |
| Trial readout | Flight test milestone, design review (PDR, CDR), operational demonstration | Company-reported; few independent registries |
| PDUFA date | Certification target date (management guidance only) | No public goal date exists |
| AdCom | Issue papers, special conditions, public comment dockets | Visible in FAA and Federal Register dockets |
| Partnership / licensing | Government contracts: SBIR/STTR, OTA prototypes, program of record | Prototype money is small; a program of record is the commercial inflection |
| Payer coverage | Customer budget lines: DoD appropriations, NDAA language, program office funding | Budget documents are public and dated |
| Launch execution | Fleet integration orders, units installed, recurring software/service revenue per aircraft | Equivalent of patient starts and persistence |
| ClinicalTrials.gov | USAspending.gov, SAM.gov, FPDS, daily DoD contract announcements | Award amounts and obligations are point-in-time records |
| FAERS safety | Incident reports (NTSB, FAA), test mishaps | Low frequency, high impact |
| Specialist biotech funds | Deep-tech and defense-focused funds, strategic investors | Same 13F/13D method; different fund list |

## 3. M14 data sources (design)

| Source | Use | Point-in-time key |
|---|---|---|
| EDGAR (M1) | 10-Q/K, 8-K, S-1/S-3, 424B3 resale prospectuses, warrant and earnout terms, lockups | acceptanceDateTime |
| USAspending.gov API | Prime and sub-awards to the company (by UEI), obligations over time | action date + data refresh lag |
| SAM.gov | Entity registration (UEI, CAGE), contract opportunities naming the technology | posted date |
| defense.gov daily contract announcements | Awards above the reporting threshold | publication date |
| FAA Dynamic Regulatory System, regulations.gov dockets | STCs, exemptions, issue papers, special conditions | docket post date |
| Federal Register | Rules affecting autonomy, airspace and certification | publication date |
| Company IR and X (M4, M13) | Flight-test news, customer announcements | post or release time |

## 4. Gates, adapted

**Evidence gate.** One sentence for who pays: a named program office or customer with a
budget line beats "addressable market". Write two falsifiers, for example: a certification
milestone slips more than two quarters, or a prototype contract ends without a follow-on.

**Survival gate.** Same arithmetic as biotech (`docs/modules/edgar.md`, section 5). Add:
- SPAC-specific supply: PIPE resale registrations, warrants (strike, exercisability,
  redemption terms), earnout shares, sponsor lockup dates.
- Government revenue timing: awards are obligated in tranches; announced ceiling values
  are not revenue.

**Price gate.** Three scenarios at one date. Two numbers anchor every scenario:
- **Cash floor per share** = (usable cash at valuation date, projected) / diluted shares.
  A stock below its cash floor prices in either continued burn or distrust of management.
- **Option value** = market cap minus projected cash; the part of the price that pays
  for the technology. Negative option value means the market expects the cash to be
  burned without a return.

## 5. Base rates to collect before assigning probabilities

- De-SPAC performance: academic studies of the 2020-2022 SPAC cohort report weak
  post-merger returns on average; collect the evidence and measure our own cohort
  (H11).
- Certification timelines for novel software and new aircraft categories versus first
  guidance (the eVTOL cohort is a natural reference class).
- Conversion rate from SBIR/OTA prototype awards to programs of record.

## 6. Risk budget

- Sleeve cap: 15% of portfolio (proposed, open question).
- Each name sized as an event position (loss budget / stress drawdown), stress drawdown
  at least 70% for pre-revenue names.
- Count shared exposures: defense budget cycle, AI theme, SPAC-overhang cohort,
  small-cap liquidity.
