# Takeout History, the Listed Life-Science Universe and a Case-Study Method

Written 2026-10-09. The investor asked three things after the takeout database of 2026-10-08:
(1) extend the deal database back in time; (2) study each buyout one by one, especially the setup
before the deal, building on existing work rather than reinventing it; (3) list every US-listed
biotech and life-science company, starting from XBI and IBB. Decisions D-038 to D-041. Evidence
classes: F fact, G management guidance, A own assumption, U unverified.

## 0. Summary

1. **A free, point-in-time listing record exists.** The public GitHub repository
   `rreichel3/US-Stock-Symbols` has committed the Nasdaq stock screener (NASDAQ, NYSE and NYSE
   American, with sector, industry, market cap and country) about once a day since 2021-01-30. Its
   git history is a survivorship-free listing panel: 70 monthly snapshots, 1,595 life-science
   symbols, 639 exits. It is the only route this environment has (sec.gov, ssga.com, ishares.com
   and Nasdaq do not resolve; FMP's plan now blocks ETF holdings and M&A).
2. **The full universe today: 941 companies** in six layers (snapshot 2026-10-09): 662
   therapeutics, 35 tools, 10 services, 41 diagnostics, 3 software and data, 190 medtech
   (`data/reference/us_lifesci_universe.csv`). 211 therapeutics companies are US-domiciled with a
   market cap of USD 0.3-10B, the core of the mandate. XBI and IBB columns hold rule proxies until
   the sponsor files are fetched on the local machine (`scripts/fetch_etf_holdings.py`).
3. **The listing history audits the deal table.** Every 2021-2026 deal in the 10-08 table matches a
   listing exit except three with clear reasons (Pacira and Avidity have not closed; Biohaven's
   spin-off kept BHVN). The exits also led to 46 deals from 2021-2026 that the table lacked,
   including ten 2025-2026 deals: Gilead-Arcellx (USD 7.8B), Lilly-Centessa (6.3B plus CVR), GSK-RAPT (2.2B),
   Neurocrine-Soleno (2.9B), Chiesi-KalVista (1.9B), ARCHIMED-Esperion, BioCryst-Astria,
   Zymeworks-Theravance, Ligand-XOMA and BioNTech-CureVac. Of 133 large (above USD 300M)
   therapeutics exits, 113 are now matched deals, 14 are resolved non-deals and 6 are open.
4. **The takeout hazard is now measured, and size matters more than assumed.** 2021-02 to 2026-10,
   strategic and contested deals over listed therapeutics company-years: micro (under USD 0.3B)
   0.6% a year, small (0.3-2B) 4.8%, mid (2-10B) 8.1%, pooled under USD 25B 2.6% (80% interval
   2.3% to 2.9%). The 10-08 priors assumed 3.5% for everyone with mild size ratios; the measured
   gradient from micro to mid is about 14-fold. `config/takeout_priors.yaml` now uses it (D-040).
5. **The deal table now spans 2005-2026: 229 deals** (218 strategic or contested), up from 88
   (2019-2026). 33 rows carry a source URL; the rest are recall rows flagged for EDGAR checks.
   Across eras (strategic and contested only): CVRs rose from 3% of deals (2005-2012) to 24%
   (2019-2024) and 41% (2025-2026); public contests (hostile or competing bids) fell from 24% to
   1-5%; approved-product targets fell from 61% to 41-48%. Older rows over-represent famous deals,
   so the size of each shift is uncertain; the direction of the contest decline matches Boone and
   Mulherin (2007): competition moved into the private process.
6. **Existing work covers the method, not the biotech features.** The literature gives the case
   design (Palepu 1986: never study targets alone), the background-section coding
   (Boone and Mulherin 2007), the run-up economics (Schwert 1996), options leakage (Augustin,
   Brenner and Subrahmanyam 2019), pharma hazard models (Duflos and Pfister 2008) and partner
   effects (Higgins and Rodriguez 2006). None of it measures Phase 2 quality, pharma options on the
   lead asset, dated loss of exclusivity or a small-cap biotech denominator point-in-time. Those
   are the repo's contribution. Details in `docs/framework/takeout_case_study.md` section 2.
7. **The case-study method is case-control.** Each buyout is coded with at least two matched
   non-targets (same layer, size band and business stage, 90 days before the deal), on the same
   signal catalog (`config/takeout_signals.yaml`, 34 signals in nine groups), plus the private
   process from the SC 14D9 or merger-proxy background section. A four-deal pilot already shows
   three different shapes of sale (section 6).

## 1. Data access on 2026-10-09

| Source | Result | Route used instead |
|---|---|---|
| sec.gov, efts.sec.gov | DNS failure (shell and WebFetch) | Search summaries of filings; EDGAR scripts for the local machine |
| ssga.com (XBI), ishares.com (IBB) | DNS failure | Rule proxies; `scripts/fetch_etf_holdings.py` for the local machine |
| api.nasdaq.com, nasdaqtrader.com | DNS failure | GitHub mirror of the Nasdaq screener |
| FMP MCP (ETF holdings, screener, M&A, profiles) | Blocked by plan tier | None needed |
| raw.githubusercontent.com, github.com, pypi.org | Reachable | Listing history |
| Web search | Works | Deal terms, process narratives |

## 2. The listed universe (task 3)

**Method.** `connectors/listings.py` classifies each screener row by Nasdaq's SIC-based industry
label, in this order: curated override by ticker (`lifesci_layer_overrides.csv`, 119 rows), removal
of warrants, units, rights, preferreds and blank-check shells, the industry default, then a
name-keyword rescue for ambiguous labels (Intellia sits under "diagnostic substances") and a care
or insurance keyword exclusion. Fresh IPOs with a blank industry are rescued by name. Every row is
`own_assumption`.

| Layer (2026-10-09) | Total | Micro under 0.3B | Small 0.3-2B | Mid 2-10B | Large 10-25B | Mega over 25B |
|---|---|---|---|---|---|---|
| therapeutics | 662 | 358 | 177 | 83 | 18 | 26 |
| tools | 35 | 13 | 6 | 5 | 4 | 7 |
| services (CRO, CDMO) | 10 | 3 | 2 | 1 | 3 | 1 |
| diagnostics | 41 | 18 | 9 | 8 | 2 | 4 |
| software and data | 3 | 0 | 1 | 1 | 0 | 1 |
| medtech | 190 | 99 | 46 | 22 | 9 | 13 |

Therapeutics: 608 on NASDAQ, 27 on NYSE, 27 on NYSE American; 506 US-domiciled; 53 ADRs. The
listed therapeutics count was 689 in February 2021, peaked at 822 in January 2023 and is 670 in
the latest panel month: the 2020-2021 IPO wave and its unwinding.

**XBI and IBB.** The sponsor files could not be fetched. Two proxies stand in (A):
`ibb_rule_proxy` (NASDAQ-listed therapeutics above USD 200M: 325 names; IBB holds about 250, so the
proxy over-includes by the volume and Nasdaq-tier rules it cannot see) and `xbi_rule_proxy`
(US-domiciled therapeutics above USD 500M, excluding known GICS Pharmaceuticals names: 192 names;
XBI holds roughly 130-145). Running `python scripts/fetch_etf_holdings.py` on the local machine
fills `in_xbi`, `xbi_weight_pct`, `in_ibb` and `ibb_weight_pct`; the builder picks up the newest
file automatically. XBI excludes GICS Pharmaceuticals, so specialty pharma such as HROW, ETON and
PCRX is likely outside it: the benchmark and the commercial-pharma names differ in composition,
not just in weights (check once the file is fetched).

**Caveats.** Nasdaq's labels file Thermo Fisher and Danaher under industrial machinery, Certara and
Tempus under software, and UnitedHealth under medical specialities; overrides fix the ones found.
Software and data has only three names because most AI-bio companies file under pharmaceutical
preparations and stay in therapeutics with an `ai_platform` sublayer; the AI fit matrix flags them
(23 of 23 matched).

## 3. What the listing history found (task 1, completeness)

`scripts/listing_history.py` samples one commit a month, keeps every row, and folds companies into
spells. Three data problems surfaced and are handled in code:

1. **Label flicker.** Translate Bio and Akouos read "specialty chemicals" for part of 2021. Each
   company now gets one stable layer, the most frequent across its snapshots (`stable_layers`).
2. **Ticker reuse.** RNA (Prosensa, then Avidity), RXDX (Ignyta, then Prometheus), CCXI
   (ChemoCentryx, then a Churchill Capital SPAC), TBIO (Translate Bio, then Telesis Bio), RDUS
   (Radius Health, then Radius Recycling), FACT and ANAC. A symbol that returns after a gap under a
   different name starts a new spell; deal matching keys on ticker plus date.
3. **Renames.** MindMed became Definium (DFTX), Cybin became Helus (HELP), Galecto became Damora
   (DMRA), BeiGene became BeOne (ONC). A rename that changes both name and ticker looks like an
   exit; `lifesci_exit_resolutions.csv` records them.

Exit outcomes, therapeutics layer:

| Exit size (last market cap) | Exits | Matched to a deal | Resolved non-deal | Open |
|---|---|---|---|---|
| Large, above USD 300M | 133 | 113 | 14 | 6 |
| Mid, USD 50-300M | 89 | 3 | 0 | 86 |
| Small, below USD 50M | 246 | 2 | 0 | 244 |

The 330 open small and mid exits mix failures, reverse mergers, cash-shell sales (Concentra
Biosciences bought several in 2025) and small takeouts. Resolving them needs EDGAR (Form 25, 8-K
item 2.01, SC 14D9): Q-037. Until then the micro-band hazard is a floor.

## 4. The measured takeout hazard

`python scripts/takeout_base_rate.py` (D-040). Numerator: strategic and contested deals whose
target was a listed therapeutics company in the snapshot before the announcement month, with the
band read from that snapshot. Denominator: therapeutics company-months per band (large pharma,
generics, animal health and royalty vehicles excluded), divided by 12. Prior Beta(1, 25).

| Band | Company-years | Deals | Annual hazard | 80% interval |
|---|---|---|---|---|
| Micro, under USD 0.3B | 2,508 | 15 | 0.6% | 0.4% to 0.8% |
| Small, USD 0.3-2B | 1,191 | 58 | 4.8% | 4.1% to 5.7% |
| Mid, USD 2-10B | 404 | 34 | 8.1% | 6.5% to 9.9% |
| Large, USD 10-25B | 62 | 1 | 2.3% | 0.6% to 4.4% |
| Mega, above USD 25B | 23 | 1 | 4.1% | 1.1% to 7.9% |
| All under USD 25B | 4,165 | 108 | 2.6% | 2.3% to 2.9% |

What changes: the takeout kicker (hazard times premium, D-036) for a mid-cap name at the 40%
median premium is about 3.2% a year, for a small cap about 1.9%, for a micro cap about 0.2%. The
10-08 priors gave a micro cap 1.4% (3.5% times 0.4) and a mid cap 4.2% (3.5% times 1.2): about
twice the measured micro rate and about half the measured mid rate. A 2021-2026 window is one deal cycle (a weak 2022-2023, a hot 2025-2026); the per-year
split is the next check before trusting the level.

## 5. The expanded deal table (task 1, time range)

`data/reference/biotech_takeouts.csv`: 229 rows, 2005-01 to 2026-10-08. New columns `deal_kind`
(strategic, contested, parent_buy_in, going_private, distressed, cash_shell) and
`prior_relationship` (acquirer was a partner, licensee or holder). Strategic and contested rows by
era (`python scripts/takeout_screen.py summary --since 2005 --until 2012`, and so on):

| Era | Deals | Approved lead asset | Phase 1 or earlier | Randomized Ph2, pivotal or commercial data | Big pharma buyer | CVR | Contested |
|---|---|---|---|---|---|---|---|
| 2005-2012 | 38 | 61% | 5% | 84% | 68% | 3% | 24% |
| 2013-2018 | 46 | 46% | 9% | 74% | 54% | 20% | 11% |
| 2019-2024 | 90 | 41% | 11% | 70% | 68% | 24% | 1% |
| 2025-2026 | 44 | 48% | 7% | 64% | 55% | 41% | 5% |

Caveats: 2005-2018 rows come from recall (`date_precision = approx`, no URL) and favour memorable
deals; private targets are excluded; premiums exist only for sourced rows (20 in 2025-2026, median
40%, IQR 31% to 60%). Use pre-2021 rows for composition, not for rates.

## 6. Case-study pilot (task 2)

Method: `docs/framework/takeout_case_study.md`. Four 2026 cases, coded only from search summaries
(all U); controls are selected but not yet coded.

| Case | Shape of sale | Private process (background section) | Public setup signals (window) | Controls |
|---|---|---|---|---|
| Crinetics (CRNX), Vertex, USD 85 | Buyer-initiated, one bidder, asset-driven | Vertex called the CEO 2026-03-14; bid 78 on 03-24; rejected 04-05; 84.50 late May; 85 "best and final" 06-19; signed 07-06. 114 days, no leak (102% premium to last close) | Approval of PALSONIFY (W2) | KNSA, LQDA |
| Ventyx (VTYX), Lilly, USD 14 | Target-run auction after data | After positive VTX3232 Phase 2 data (October 2025) the company approached 16 large pharmas; three did deep diligence; signed 2026-01-07 | Sanofi equity and ROFN on VTX3232 (W1, recall); Phase 2 data (W3); WSJ report the day before (W4) | ACRS, BIOA |
| Soleno (SLNO), Neurocrine, USD 53 | Commercial launch bought by a launch-capable buyer | Agreement 2026-04-05; background not yet read | Approval (W1); first launch year about USD 190M (W3); short-seller report (W2, recall) | RARE, MESO |
| Pacira (PCRX), Viatris, USD 36.50 | Activist-pressured sale of a cash-generating franchise with a dated loss of exclusivity | Background due with the tender offer | Settlement fixing 2030 generic entry (W1); new Paragraph IV filers (W2); DOMA proxy contest, lost 2026-06-09 (W2) | ETON, PHAR |

Early lessons, each a hypothesis for coding at scale, not a finding:

- **Buyer-initiated deals give no public warning inside the process.** Crinetics ran 114 days
  without a leak; the only usable signal was the approval nine months earlier. For asset-driven
  deals the predictor is the asset, and the timing is unknowable.
- **Target-run auctions follow data and announce themselves through the company's behaviour.**
  Ventyx shopped itself to 16 buyers within three months of its Phase 2 data. Signal E1 (no raise
  after good data) and the process length are the testable pair.
- **A ROFN holder does not have to buy.** Sanofi held a right of first negotiation on VTX3232
  (recall, to verify); Lilly bought. B1 may mark interest in the asset class, not the buyer.
- **Pacira's setup was public for a year**: a dated generic entry, new patent challengers and an
  activist demanding a sale. Activists can lose the vote and win the outcome.
- **ETON is a control for Pacira and a watchlist name.** Coding it is both a control row and a
  direct input to Q-036 (whether ETON and HROW get takeout scores).

## 7. What this changes and what comes next

- H8: the base hazard and size ratios are measured; stage and trait ratios remain A until the case
  set reaches 20 coded cases with controls, or P5 fits them jointly.
- The XBI benchmark composition question (GICS Pharmaceuticals excluded) affects H6 and the
  commercial-pharma names: check once the holdings file exists.
- Next steps: Q-037 (resolve small and mid exits on EDGAR), Q-038 (fetch ETF holdings locally),
  Q-039 (code the four pilot cases and eight controls from the filings), Q-040 (sample 30 cases
  from 2021-2026 by band and year for the first likelihood ratios), Q-041 (13F accumulation before
  deals, the RAPT pattern).

## Sources

- Listing mirror: https://github.com/rreichel3/US-Stock-Symbols (git history from 2021-01-30)
- Index rules: [NBI methodology](https://indexes.nasdaqomx.com/docs/methodology_NBI.pdf); S&P Select Industry rules via the [Global X CURE methodology](https://globalxetfs.com.au/content/files/CURE-Index-Methodology.pdf) and [BioCentury on the 2024 XBI weighting change](https://www.biocentury.com/article/652965/biotech-losing-its-xbi-barometer)
- 2026 deals: per-row `source_url` in `data/reference/biotech_takeouts.csv`
- Crinetics process: [BioPharma Dive](https://www.biopharmadive.com/news/vertex-crinetics-acquisition-deal-bidder-process/825952/)
- Ventyx process and leak: [TipRanks summary of the proxy supplement](https://www.tipranks.com/news/company-announcements/ventyx-faces-eli-lilly-acquisition-delisting-and-litigation), [Bloomberg Law on the WSJ report](https://news.bloomberglaw.com/private-equity/lilly-nearing-1-billion-deal-with-biotech-ventyx-wsj-says-2)
- Pacira contest: [annual meeting result](https://finviz.com/news/360707/pacira-biosciences-announces-stockholders-have-elected-all-three-of-the-companys-director-nominees-at-annual-meeting)
- Literature: see `docs/framework/takeout_case_study.md` section 2; [Boone and Mulherin (2007)](https://ideas.repec.org/a/bla/jfinan/v62y2007i2p847-875.html), [Augustin et al. (2019)](https://ideas.repec.org/a/inm/ormnsc/v65y2019i12p5697-5720.html), [Higgins and Rodriguez (2006)](https://ideas.repec.org/a/eee/jfinec/v80y2006i2p351-383.html), [Duflos and Pfister (2008)](https://ideas.repec.org/p/mse/cesdoc/bla08057.html), [Danzon, Epstein and Nicholson (NBER w10536)](https://www.nber.org/system/files/working_papers/w10536/w10536.pdf), [Cunningham, Ederer and Ma (2021)](https://papers.ssrn.com/abstract=3241707), [Arroyabe et al. (2021)](https://onlinelibrary.wiley.com/doi/full/10.1111/radm.12462), [RBC review via BioPharma Dive](https://www.biopharmadive.com/news/biotech-takeover-targets-rbc-mergers-acquisitions-deals/815061/)
