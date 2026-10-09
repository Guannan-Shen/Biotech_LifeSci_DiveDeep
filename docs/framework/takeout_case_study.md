# Takeout Case Studies: How a Biotech Gets Sold (H8, D-041)

Written 2026-10-09 after the investor asked for a case study of each buyout, with the pre-buyout
setup as the focus, to understand and predict these events, and asked what others had already
built. This document is the method. Results live in
`docs/research/2026-10-09_takeout_history_universe_and_case_method.md`.

Evidence classes: F fact, G management guidance, A own assumption, U unverified.

## 1. The design in one paragraph

A case study of a target alone teaches a story, not a probability: every target "had" a good asset
and an interested buyer in hindsight. Each case is therefore coded together with two or more
**matched controls**, companies of the same layer, size band and business stage that were *not*
bought within a year, using the same signal catalog and the same dates. Each company gets two
records: **public signals** dated by `available_at` (what an investor could have seen) and, for the
target only, the **private process** read from the "Background of the Offer" or "Background of the
Merger" section that US law requires in the SC 14D9 or merger proxy (what was really going on).
Signals that show up more often in targets than in controls, inside the setup windows, become
likelihood ratios for the takeout score; the private process tells us how early a public signal can
lead and which signals are reactions rather than setup.

## 2. What others have built, and what we reuse

| Work | What it found or offers | How we use it |
|---|---|---|
| Palepu (1986), J. Accounting and Economics | Target-only samples overstate prediction accuracy; false positives eat the excess return | The reason for matched controls and the full-denominator hazard (D-034) |
| Boone and Mulherin (2007), "How are firms sold?", J. Finance | Read the background sections of 400 deals: about half were private auctions, half one-bidder negotiations; public bidding shows a small part of real competition; target returns similar either way | Template for `takeout_case_process.csv` (initiator, parties contacted, NDAs, bids) |
| Schwert (1996), "Markup pricing in mergers and acquisitions", J. Financial Economics | Pre-bid run-up and post-announcement markup are mostly uncorrelated: the run-up is an added cost to the bidder | Supports D-037 (record last-close and VWAP premiums; the gap is a study variable) |
| Betton, Eckbo, Thompson and Thorburn (2014), J. Financial Economics | Toeholds and market feedback; part of the run-up anticipates the bid | Caution when reading run-ups as leakage |
| Augustin, Brenner and Subrahmanyam (2019), Management Science | 1,859 US takeovers 1996-2012: about 25% show abnormal option volume before the announcement, concentrated in short-dated out-of-the-money calls; the SEC litigates about 8% | Signal H1; needs an options data source (not in the repo) |
| Duflos and Pfister (2008), duration model of pharma acquisitions 1978-2002, more than 400 firms | Firms with more radical patents face a higher hazard of being targeted; acquirers have falling sales and lower Tobin's q | Precedent for the discrete-time hazard (P5) and for acquirer-side "need" features |
| Danzon, Epstein and Nicholson (NBER w10536, 2004; MDE 2007) | Pharma-biotech mergers: larger enterprise value raises target odds; number of marketed drugs not significant; small biotechs in financial trouble sell (A, recall of the abstract) | Size and distress features; our measured size gradient agrees |
| Higgins and Rodriguez (2006), J. Financial Economics | 160 pharma acquisitions 1994-2001: acquirer returns rise with prior access to the target's R&D (alliances) and with acquirer "desperation" (pipeline decline) | Signals B1 and B2 (partner, option, equity) and the acquirer gap (B3) |
| Arroyabe et al. (2021), R&D Management | Patent expiry drives acquisition decisions; penalized logit for rare events (King and Zeng 2001) | P5 estimation: rare-event correction (Firth or King-Zeng) |
| Cunningham, Ederer and Ma (2021), "Killer acquisitions", J. Political Economy | 5.3-7.4% of pharma acquisitions kill overlapping projects; deals bunch below antitrust thresholds | Post-deal asset fate column; a buyer with an overlapping franchise may pay to remove a threat |
| Text-based target prediction (Erasmus master's thesis) | 10-K text classifiers did not beat numeric models | Do not expect narrative text alone to add signal; code specific events |
| STAT analysis of more than 250 acquisitions 2000-2021 (2022) | About a quarter of 2013-2018 targets had not started Phase 2 | Stage mix check for our older rows |
| RBC (Timashev) review of 85 M&A media reports since 2021 | Tier-one outlets were right 60-70% of the time, Betaville 20-30%; best 30-day returns after Bloomberg and FT stories | Signal B5 and its source weighting |
| Deal databases | SDC Platinum / LSEG Deals (academic standard, via WRDS), Capital IQ, PitchBook, Cortellis Deals, DealForma, Evaluate (paid); BioPharma Dive tracker (free, whole-company deals with at least USD 50M upfront), Fierce Biotech tracker (2023+), Biobucks, BiopharmaWatch | Cross-check the deal table; buying SDC or DealForma access would close Q-032 fastest |
| Open-source EDGAR tooling | OpenEDGAR (LexPredict, MIT licence) and EDGAR-CRAWLER parse filings; neither extracts background sections out of the box | Base for an M1 parser of SC 14D9 and DEFM14A background sections |

Gaps none of this covers, which the repo fills: biotech-specific features measured point-in-time
(Phase 2 quality grade, pharma option or ROFN on the lead asset, dated loss of exclusivity,
acquirer gap by therapeutic area), a listed-company denominator for small caps, and signals coded
for non-targets with the same rules.

## 3. The two records per company

### 3.1 Public signals (`data/reference/takeout_case_signals.csv`)

One row per signal per company. Codes and definitions are in `config/takeout_signals.yaml`
(groups A asset and data, B strategic interest, C ownership and activism, D governance and
preparation, E capital behaviour, F commercial position and exclusivity, G disclosure behaviour,
H market microstructure, I dissent). Columns: `case_id` (the deal), `role` (case or control),
`ticker`, `t0` (the case's announcement date, shared by its controls), `code`, `available_at`,
`date_precision` (day, month or year), `description`, `evidence_class`, `source_url`.

Windows relative to `t0` (`models/takeout_case.py`):

| Window | Days before T0 | Use |
|---|---|---|
| W1 | 366-730 | long setup: partnerships, equity stakes, settlements fixing exclusivity |
| W2 | 91-365 | medium setup: data, approvals, activists, governance changes |
| W3 | 8-90 | short setup: financing behaviour, run-ups, skipped events |
| W4 | 1-7 | leaks and media reports: reactions, excluded from likelihood ratios |

### 3.2 Private process (`data/reference/takeout_case_process.csv`), targets only

Coded from the background section: `first_contact_on`, `initiator` (buyer, target, banker,
activist), `parties_contacted`, `ndas_signed`, `written_bids`, `first_price_usd`,
`final_price_usd`, `banker_engaged_on`, `go_shop`. Two derived quantities matter most:

- **Process length** (first contact to announcement): the lead time a public signal must beat to
  be useful. Crinetics: 114 days, buyer-initiated, one bidder (U).
- **Initiator**: a buyer-initiated deal follows the asset (data, approval); a target-initiated sale
  follows the company's situation (runway, activist, loss of exclusivity). The two need different
  predictors.

The background section also discloses **management projections** given to the bankers. Those are
the company's own risk-adjusted forecasts: add them to `guidance_ledger.csv` (they count as
guidance under D-032) and compare them with our rNPV for the same assets.

## 4. Choosing controls

`scripts/takeout_case_controls.py` ranks every listed therapeutics company in the target's cap
band by distance in log market cap, using the monthly snapshot about 90 days before T0, and drops
companies that were not still listed at T0 or that were themselves announced as targets within
365 days. The pool goes to `data/silver/takeout_control_pools.csv`. The coder then picks at least
two controls with the same business stage (commercial, launch, clinical) and, where possible, the
same area, and records the reason in `data/reference/takeout_case_controls.csv`. Rules:

1. Pick controls before coding any signal for them, so the choice cannot be steered by what
   their files contain.
2. Code controls with the same diligence as the case: the same filings, the same window.
3. A control that is bought later (outside the 365-day window) stays a control for this case and
   becomes a case of its own.
4. Controls whose 365-day window has not ended are `censored`; keep them, flag them.

## 5. Coding protocol for one case (about two hours with EDGAR access)

1. Deal row: confirm terms in the target's 8-K exhibit 99.1; record the unaffected date and both
   premiums (D-037).
2. Background section: code the process table; quote the dates; note each competing party.
3. Public signals, T0 minus 24 months to T0: walk the 8-K index (items 1.01, 3.03, 5.02, 8.01),
   SC 13D and 13G, 13F changes of specialist funds (H4 data), S-3 and 424B, press releases, and
   prices against XBI. Use `available_at`, not the event date.
4. Controls: same walk for each control over the same calendar window.
5. Outcome after the deal: CVR paid or not, lead asset approved or failed, deal closed or broke.
6. One paragraph in the research note: the setup in plain words, the initiator, the public signal
   with the longest honest lead, and what a control with the same signal did.

## 6. Turning cases into priors

`signal_rates` in `models/takeout_case.py` counts, for each code, the share of cases and of
controls with the signal inside W1-W3 and returns a Haldane-corrected likelihood ratio. With 30
cases and 60 controls, a signal present in 40% of cases and 10% of controls has a ratio of about
3.8 with a wide interval; anything built on fewer than 20 cases stays `own_assumption`. Ratios feed
`config/takeout_priors.yaml` only through a decision-log entry, and P5 (the fitted hazard) replaces
them all once the EDGAR panel exists.

## 7. Failure modes

- **Hindsight coding**: reading a 2025 partnership as a "setup" because the 2026 deal happened.
  The control discipline is the guard; so is coding `available_at` from the filing, not memory.
- **Survivorship in the case list**: famous deals are easier to code. Sample cases from
  `biotech_takeouts.csv` by year and band, not by fame.
- **Reactions mistaken for setup**: media reports, option spikes and run-ups in the last week are
  consequences of a process that has already started. They live in W4 and never enter priors.
- **Base-rate neglect**: a signal with a ratio of 3 moves a 4.8% small-cap hazard to about 13%.
  Most companies with the signal still are not bought within a year.
- **Ticker reuse**: RNA, RXDX, CCXI, TBIO, FACT, ANAC and RDUS each belonged to two companies
  within the period. Key on ticker plus date, never ticker alone.
