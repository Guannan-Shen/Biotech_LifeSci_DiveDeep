# Open Questions

| ID | Question | Why it matters | Owner | Status |
|---|---|---|---|---|
| Q-001 | Capital scale and minimum liquidity per position? | Sets micro-cap floor, max position size, cost model | Investor | Open |
| Q-002 | Long-only, or are shorts, options or an XBI hedge allowed? | Changes portfolio construction and which signals are usable (e.g., short left tail) | Investor | Open |
| Q-003 | Data budget for paid sources (FMP upgrade, delisted price history, options data)? | Survivorship-free backtests need delisted prices; current FMP plan blocks batch endpoints | Investor | Open |
| Q-004 | Where do connectors run (this cloud environment, a local machine, a scheduled cloud job)? | This environment's network policy blocks sec.gov, data.sec.gov, api.fda.gov and clinicaltrials.gov | Investor | Open |
| Q-005 | Target number of holdings and review cadence? | Weekly review assumed; affects turnover and event clustering limits | Investor | Open |
| Q-006 | Confirm phase-gate thresholds in D-011. | Defines when the system earns real capital | Investor | Open |
| Q-007 | REPL: confirm approval date and product name of the approved therapy. | Investor says "just got FDA approved"; not verified in repo | Data (M2) | Open |
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
