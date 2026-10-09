# Research Backlog

Ideas not yet scheduled. Promote to the blueprint roadmap when they earn a slot.

## Signals and hypotheses
- Financing window index from weekly 424B counts (M5); interaction with H1.
- Management credibility score: guided vs actual catalyst dates (M3, M4).
- `pcd_actual` on ctgov as a leading indicator of topline timing (M3, M6).
- Specialist exits as a left-tail predictor (H4 x H1).
- Launch order vs peak share for fast-follow targets; quantifies the value of AI speed (M10).
- Cash-shell detection: market cap near net cash after failed programs; separate model from operating companies.
- CRL text vs sponsor press release: spin score as a credibility input (M2).
- FAERS report counts as a launch-utilization proxy, with stimulated-reporting controls.
- Implied move from options vs model stress move before binaries.

- Below-cash small caps: re-rating base rate conditional on burn cuts vs continued burn (biotech and adjacent).
- De-SPAC supply calendar (PIPE resale, warrants, earnouts, lockups) as a drift predictor (H11).
- X: lead time of executive posts over 8-Ks; cashtag attention z-score reversal (H10).
- Thematic ETF flow (ARK daily trades, ARKG creations and redemptions) as a negative signal distinct from specialist conviction (D-023).
- Sell-side target-hike clustering after large runs as a late-stage marker (count of target raises per name in 5 sessions vs the run size).
- AI labs entering wet-lab biology (Anthropic, others): track as a two-sided event for data generators (customer and competitor) and for gene-editing IP.
- Lilly TuneLab vendor list and any disclosed revenue from it (TWST, DNA): first quantitative test of fundamental H9.
- H14 event study: giant announcements with vs without financial terms (M16 log); pre-register before pulling prices.
- Launch-analog library seeded from the 2026 launch layer (MYQORZO, BRINSUPRI, YUTREPIA, TUDRIQEV, AUVELITY agitation, IMCIVREE HO): patients, start forms, net revenue by quarter since approval (H2).
- Demand vs net revenue divergence (prescriptions up, net revenue lagging: HROW, ARDX) as a launch-drift signal.
- Takeout base rate for approved-product small and mid caps (2026: APLS, CPRX, CRNX) and premium distribution (H8).
- Attention lead-lag: Wikimedia and GDELT peaks vs price peaks for theme cohorts (2000 genomics, 2021 ARKG, 2026 AI-bio) (H10, H13).
- Issuance as a top signal: follow-ons, ATMs and converts within 63 days after a theme peak (GSY attribute; H13 A1).

## Adjacent sleeve candidates (screen before adding)
- eVTOL, space, defense autonomy, nuclear and fusion names that pass the same gates.

## Insight questions
- Which indications have high burden, low therapy coverage and few Phase 2+ entrants?
- Modality economics under current IRA rules; track any legislative changes as regime events.
- Do AI-data tool companies (PACB, TXG, TWST, QSI, ILMN) show measurable revenue from AI or foundation-model customers before AI-native pipelines read out (H9)?

## Moved from TODO.md (investor, 2026-10-05)
- [x] Another important data/information source is YouTube, or other podcasts, providing
  deep dives on specific companies and domains. Example: for Humacyte, the YouTube video
  "Whistleblower Exposes FDA Approval of Dangerous Vascular Graft for Military Use" from
  the American Whistleblower Podcast showed that Symvess (acellular tissue engineered
  vessel-tyod) is not that reliable, even after FDA approval. We need a source where
  doctors from FDA, or scientists from other regulators, may speak the truth.
  **Status:** designed as M15 (`docs/modules/long_form_media.md`), case study in
  `docs/research/humacyte_symvess_case.md`, register in
  `data/reference/dissent_register.csv` (D-020).
- [ ] Add the American Whistleblower Podcast episode date and speaker to the register.

## Data sources to evaluate
- AACT (CTTI) for point-in-time ctgov history.
- SEC Form 13F and insider transaction data sets.
- CMS Part D / Part B spending dashboards; ICER reports.
- IHME GBD results tool.
- Delisted price history vendors (Q-003).

## Theme case studies
- 2026-10-07 follow-ups: launch layer screen and stretch, valuation and reversal odds (done).
- 2026-10-06 AI-bio data layer reversal: done (`docs/research/2026-10-06_ai_bio_theme_reversal.md`). Follow-up after Q3 reports (mid November): score each fit-matrix falsifier and the scenario signposts.

## Memos to write (research order, Phase 2)
PACB, SDGR, RXRX, then TEM, GRAL, QSI, DNA, REPL, IOVA, SLS, EDSA, HROW, ETON.
HROW moves up if Q3 (November) passes its falsifier (`docs/research/2026-10-07_launch_layer_screen.md` section 3).

## Business quality gate (added 2026-10-08)
- [ ] Pre-register H15 in `notes/backtests/` (guidance-miss event study; credibility sort) before pulling prices.
- [ ] Backfill the guidance ledger from 8-K exhibits for every commercial and launch name (ETON, REPL, IOVA first), so H15 has a sample.
- [ ] Apply the card to ETON next; it shares HROW's archetype and its acquisition-driven growth needs the deal ledger.
- [ ] After Q3 (mid November): resolve HROW's Q3 product price tests and re-score C3 and the IHEEZO moat.
- [ ] Contribution multiple per deal (revenue minus royalty, COGS and attributable selling cost) once segment data allow it.

## Takeout and Phase 2 screen (added 2026-10-08)
- [ ] Verify the 64 recall-only rows of `biotech_takeouts.csv` against EDGAR and add premiums (unaffected close and VWAP) for every row.
- [ ] Pull the complete event list and the company-quarter denominator (Q-032); compute the empirical base hazard and replace `base_annual_hazard`.
- [ ] Pre-register the H8 hazard model (Q-034), then fit it with time-split validation.
- [ ] Build the readout list for H16 from 8-K item 8.01 toplines (M1, M4) and ctgov versions (M3); recruit a second grader.
- [ ] Acquirer gap map: large pharmas' 2027-2032 loss-of-exclusivity revenue by therapeutic area (feeds `acquirer_gap_area`).
- [ ] Score the seed list in section 8 of the research note once stage, cash and holders are verified; add HROW and ETON if Q-036 says yes.
- [ ] Merger-arbitrage side note: spreads on announced deals with CVRs (Biogen-Apellis, Lilly-AtaiBeckley) as a lower-variance sleeve, if Q-002 allows.
