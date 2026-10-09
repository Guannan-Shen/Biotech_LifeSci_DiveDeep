# Open Questions

| ID | Question | Why it matters | Owner | Status |
|---|---|---|---|---|
| Q-001 | Capital scale and minimum liquidity per position? | Sets micro-cap floor, max position size, cost model | Investor | Open |
| Q-002 | Long-only, or are shorts, options or an XBI hedge allowed? | Changes portfolio construction and which signals are usable (e.g., short left tail) | Investor | Open |
| Q-003 | Data budget for paid sources (FMP upgrade, delisted price history, options data)? | Survivorship-free backtests need delisted prices; current FMP plan blocks batch endpoints | Investor | Open |
| Q-004 | Where do connectors run (this cloud environment, a local machine, a scheduled cloud job)? | This environment's network policy blocks sec.gov, data.sec.gov, api.fda.gov and clinicaltrials.gov | Investor | Open |
| Q-005 | Target number of holdings and review cadence? | Weekly review assumed; affects turnover and event clustering limits | Investor | Open |
| Q-006 | Confirm phase-gate thresholds in D-011. | Defines when the system earns real capital | Investor | Open |
| Q-007 | REPL: confirm approval date and product name of the approved therapy. | Investor says "just got FDA approved"; not verified in repo | Data (M2) | Answered 2026-10-07: FDA accelerated approval of vusolimogene oderparepvec-wtpg (TUDRIQEV) with nivolumab, 2026-08-06 (fda.gov) |
| Q-008 | Which OpenAI / Lilly / Novo collaborations with DNA exist, and are any revenue-bearing? | Core of the DNA thesis | Data (M1, M4) | Open |
| Q-009 | Date and method of the Breakthrough specialist-concentration table? | Needed before using it as a signal | Investor | Open |
| Q-010 | Keep the original Chinese framework draft somewhere? Only the English translation is committed. | English-only rule vs provenance | Investor | Open |
| Q-011 | Adjacent sleeve: confirm 15% cap and pick a diagnostic benchmark (aerospace/defense ETF, or an equal-weight peer basket of de-SPAC deep-tech). | Sizing and evaluation of MRLN-type names | Investor | Open |
| Q-012 | X API budget and tier; which accounts to follow per company. | M13 build scope | Investor | Open |
| Q-013 | Results of `scripts/check_data_access.py` on the investor's machine. | Decides where Phase 1 connectors run (Q-004) | Investor | Open |
| Q-014 | MRLN: verify diluted share count, quarterly burn split, preferred accrued value and terms, PIPE resale size, deal-projection details, executive turnover (8-K 5.02), Reg FD social channels. KC-135 status found: test flights since 2024, still a prototype program. | Memo cannot assign probabilities without them | Data (M1, M13, M14) | Open (partly answered) |
| Q-015 | YouTube Data API key and a podcast transcript route (platform transcripts vs local speech-to-text)? | M15 automation in Phase 3 | Investor | Open |
| Q-016 | Daily price history for HUMA and MRLN: the FMP plan blocks charts. Pull on the local machine or a second vendor? | H12 case study returns; H11 supply-day volume | Investor | Open |
| Q-017 | Daily price and volume history for the AI-bio cohort (36 symbols) and ARKG holdings history. FMP plan allows only profiles here; Yahoo, Stooq, Nasdaq and ark-funds.com are blocked from this sandbox. Run on the local machine? | H13 test, distribution-day counts, moving averages for the 7.4 calendar | Investor | Open |
| Q-018 | ARK daily trade files as a flow source: acceptable to scrape on the local machine, or use a vendor? | D-023 thematic flow signal | Investor | Open |
| Q-019 | QSI fell from 1.55 (10-02 close) to 1.28 (10-05 close), -17%, with no explanation found. Financing, filing or a data error? | Two-day path table in the 10-06 case study | Data (M1) | Open |
| Q-020 | October FOMC hike odds: sources quote about 36% to 73%. Which is current, from CME FedWatch? | Scenario signposts in the 10-06 case study | Data (M5) | Open |
| Q-021 | Link to the AI drug discovery article the investor saw spread on X over 2026-10-03/04 and 10-05 (author, time, reach). | Dates the attention peak against the 10-05 melt-up; x.com is blocked here and search did not find it | Investor | Open |
| Q-022 | If shorts become allowed (Q-002): borrow cost and availability for TWST, TXG, TEM; options access and approval level. | Decides whether the D-029 structures are usable | Investor | Open |
| Q-023 | VERA: was atacicept approved on or after the 2026-07-07 PDUFA date? | Needed to place VERA in the launch layer | Data (M2) | Open |
| Q-024 | HROW: debt maturities, covenants and interest cost; split of the guided H2 step-up between VEVYE price and volume. | H1 check before any HROW position; the Q3 falsifier depends on it | Data (M1) | Partly answered 2026-10-07: USD 300M 8.625% senior unsecured notes due 2030, cash USD 83.9M (U, 10-Q); price vs volume split still open (`docs/memos/HROW.md`) |
| Q-025 | Consensus revenue estimates for forward P/S: FMP estimates are plan-blocked. Upgrade, another vendor, or stay with guidance and run rates? | Forward multiples beyond the current fiscal year | Investor | Open |
| Q-026 | Profitability, cash and debt for the launch and commercial layer (TARS, MDGL, TVTX, MIRM, AXSM, KRYS, RYTM, INSM). | Growth gap ignores margins and balance sheets | Data (M1, M7) | Open |
| Q-027 | HROW: VEVYE revenue per TRx by quarter (absolute TRx counts), IHEEZO demand units for 2025, and distributor inventory disclosures around the 2026-04-01 pass-through expiry. | Price tests for both lead products; decides whether HROW-S03 stays `short_termist` | Data (M1, M4) | Open |
| Q-028 | HROW: notes outstanding are USD 250M at pricing (Sept 2025) but about USD 300M in the 2026-06-30 10-Q (U). Was there a USD 50M add-on, and at what price? | Net debt, interest and the C8 score | Data (M1) | Open |
| Q-029 | HROW: Orange Book listings for IHEEZO and TYRVAYA (exact patent expiry dates); revenue of the four non-TRIESENCE Novartis products. | Protection-weighted life; Novartis deal multiple | Data (M2, M1) | Open |
| Q-030 | MRLN: did management give H2 2026 revenue guidance (USD 4-6M per one summary, none per another)? Pull the S-4 projections table for the USD 32M FY2026 figure. | Guidance ledger entries for MRLN | Data (M1) | Open |
| Q-031 | Should the business quality grades feed position sizing automatically, or stay advisory until H15 is tested? | Section 6 of the business quality spec makes them binding on scenario weights only | Investor | Open |
| Q-032 | Complete takeout event list and denominator: all SC TO-T, SC 14D9 and DEFM14A filings for SIC 2834/2835/2836/8731 targets since 2005, plus listed company-quarters by market cap. Run on the local machine (EDGAR full-text search)? | H8 hazard model and the base hazard in `config/takeout_priors.yaml` | Data (M1) | Open |
| Q-033 | Pacira: unaffected close and premium; whether the tender launched; any go-shop or competing bid. | Premium row TK-2026-01; commercial_pharma takeout profile | Data (M1) | Open |
| Q-034 | Pre-register the H8 hazard model (features, periods, Brier baseline) before pulling the event list. | Multiple-testing discipline (D-010) | Research | Open |
| Q-035 | Mechanism-class priors for Phase 2 shrinkage: which source of Phase 2 to Phase 3 effect pairs (published meta-research, hand-labelled from ctgov results)? | P6 assurance is illustrative until calibrated | Research | Open |
| Q-036 | Should HROW and ETON get takeout scores now? Both are `commercial_pharma` with acquisitive histories; Pacira's profile (activist, known loss of exclusivity, generics-major buyer) is the nearest analog. | Business quality cards and the do-not-sell-cheap flag | Investor | Open |
