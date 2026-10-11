# QSI vs NAUT: Two Ways to Read a Protein, and How Their Stocks Digest News

Date: 2026-10-11. Archetype `tools` (pre-commercial). Lenses: business quality gate
(`docs/framework/business_quality.md`), survival and price gates (framework section 3), H1 (dilution
machinery), H17 (post-announcement drift, added today, D-043). Companion memo: `docs/memos/QSI_NAUT.md`.
Research note, not investment advice. **F** fact, **G** management guidance, **A** own assumption or
inference, **U** unverified (press summaries and aggregators; 8-K, 10-Q and the papers to re-read).
WebFetch and sec.gov do not resolve from this sandbox, so every company number below is **U** unless
marked otherwise. Prices are **F** from the listing mirror (D-044).

## 1. Bottom line

1. **They answer different questions.** Quantum-Si (QSI) asks *which amino acids are in this
   stretch of protein*: it cuts proteins into peptides and reads them residue by residue. Nautilus
   (NAUT) asks *which molecular form of this protein is present, and how many copies*: it keeps each
   protein chain whole, pins it to a spot, and maps it with repeated rounds of fluorescent probes. One
   is a sequencer of fragments; the other is a counter of intact molecules. Neither is "protein
   sequencing" in the way Illumina sequences DNA.
2. **The digestion step is forced by the chemistry, not chosen for convenience.** QSI's readout
   needs a free amino group at the front of the chain and loses fidelity with every residue read, so
   it must work on short pieces with fresh, unblocked fronts. Most human proteins have a chemically
   capped front end, and almost all are far longer than the read length (section 3.2).
3. **The intact design buys proteoforms; it does not buy binding partners.** Keeping the chain whole
   preserves which modifications sit together on one molecule, which is what the tau work shows.
   Protein complexes and interactions are a different matter: single-molecule immobilization and
   probe access generally require unfolding, and nothing found today shows Nautilus reading native
   complexes (Q-047). The "different bindings" Nautilus does exploit are the probes' binding
   patterns, which encode identity.
4. **Each design carries its own failure mode, and both have now shown it.** QSI's risk is
   engineering a new instrument (Proteus moved from end-2026 to Q2 2027). NAUT's risk is reagent
   science: its broadscale proteome mode depends on hundreds of low-specificity probes, and on
   2026-07-28 it said probe performance does not support 2027 general availability at target specs,
   with no new date. The stock fell 28% that day and drifted another 29% (abnormal) over the next
   month.
5. **Business quality: both `unproven`.** Revenue is about 1% of operating expenses for each.
   Guidance credibility differs sharply: QSI 2 of 3 dated guides hit (posterior 0.57), NAUT 0 of 5
   with an average slip of about nine months (posterior 0.22, people grade `discount` under D-046).
6. **Drift.** Earnings days are mostly non-events for these names; the information comes with
   timeline and data news. QSI's attention spikes without news reversed within 60 sessions nine
   times out of eleven. Both stocks just rose about 63% in 21 sessions with live ATM programs: an H1
   dilution flag, and the setup that has preceded QSI's reversals.

## 2. The measurement problem both companies are attacking

Why proteins are harder than DNA (textbook background, A unless cited):

- **No copying.** DNA can be amplified by PCR; proteins cannot. Every protein method counts the
  molecules that are physically there, so sensitivity and dynamic range are hardware problems.
- **Twenty letters plus decorations.** DNA has four bases. Proteins have twenty amino acids, and
  after translation they are cut, spliced into isoforms and decorated with phosphate, acetyl,
  sugar, ubiquitin and other groups. One gene gives many **proteoforms** (Smith and Kelleher 2013
  coined the term; Aebersold et al. 2018 estimate millions of human proteoforms from about 20,000
  genes).
- **Dynamic range.** In plasma, albumin outnumbers the rarest signalling proteins by about ten
  orders of magnitude (Anderson and Anderson 2002). A method that counts a few million molecules
  sees only the top of that range unless the sample is enriched.

Mass spectrometry handles this today in two styles that map neatly onto the two companies:
**bottom-up** (digest, measure peptides, infer proteins) and **top-down** (measure intact
proteoforms). QSI is a single-molecule, optical version of bottom-up. NAUT is a single-molecule,
affinity version of top-down. That framing tells you who each one really competes with: QSI with
bottom-up MS and Edman sequencing for purified samples, NAUT with top-down MS and immunoassays.

## 3. Quantum-Si: read the peptide

### 3.1 How it works

Published mechanism (Reed et al., Science 2022, 378:186; F for the paper, U for product details):

1. Proteins are denatured and **digested** into peptides; upstream prep is similar to bottom-up MS
   (the company's own description). Lys-C digestion and C-terminal attachment are our reading of
   the workflow (A; confirm in Q-048).
2. Peptides are immobilized by one end in nanoscale wells, ideally one peptide per well.
3. A mix of dye-labelled **N-terminal amino acid recognizers** (engineered from ClpS-family
   proteins that naturally bind N-terminal Phe, Tyr, Trp) binds on and off the peptide's front
   residue. Each binding pulse has a characteristic duration, brightness and, on Platinum,
   fluorescence lifetime.
4. **Aminopeptidases** in the same mix clip the front residue off; the next residue is exposed and
   a new pulse pattern begins. The read is a time series of kinetic signatures.
5. Software aligns the series to reference peptides ("alignments" is the company's throughput
   metric). Recognizers covered a subset of the twenty residues; the developmental kit reached 17
   in May 2026, 18 on integrated Proteus instruments by September, and 19 on 2026-10-08, with all 20
   targeted by year-end (G).

Platinum and Platinum Pro use a CMOS chip that times photon arrival. **Proteus** switches to camera
optics with four flow cells of 20 million wells (KinetIQ arrays on fused silica), about 6-7 million
peptides per run, a new controlled-cleavage chemistry, and a list price of USD 425K (G, U). Interim
HUPO data on 2026-09-28: a median 30 times more alignments per chamber than Platinum Pro on control
peptides, 60 times projected per four-chamber run (G, a projection).

### 3.2 Why it has to digest first

| Reason | Mechanism | Consequence if you skip digestion |
|---|---|---|
| Blocked front ends | Recognizers and aminopeptidases need a free alpha-amino group. Most human proteins are N-terminally acetylated (Arnesen et al. 2009 report about 80-90% of soluble human proteins), which caps that group. | An intact acetylated protein gives no signal at all. Digestion creates new, unblocked fronts on every internal peptide. |
| Read length | Each cycle (bind, read, cleave) can fail, stall or skip; residue-specific cleavage rates vary. Error compounds with length, so useful reads are short. | A median human protein of several hundred residues cannot be read end to end; the read would decay long before the far end. |
| Accessibility | A folded protein buries its termini and backbone. | Recognizers cannot reach the front residue reliably. |
| Loading and uniformity | Wells are nanoscale and loading is statistical (Poisson); small, similar-sized analytes load and attach predictably. | Large, sticky, variably folded proteins load unevenly and clog wells. |
| Workflow fit | The same digestion protocols already run in proteomics cores. | A new sample prep would be another adoption barrier. |

The first two are decisive (A, reasoning from the published chemistry). The others make digestion
convenient; those two make it unavoidable for an N-terminal degradation chemistry.

### 3.3 What digestion costs

- **Proteoform connectivity is destroyed.** Two modifications 150 residues apart end up on
  different peptides; the method measures each site's occupancy, never whether they co-occur on one
  molecule.
- **Protein inference.** Peptides shared between isoforms or family members cannot be assigned
  uniquely, the classic bottom-up problem.
- **The native N-terminal peptide is usually lost** (it stays blocked), along with information on
  processing at the protein's front end.
- **Gaps in the read.** Until all 20 residues are recognized, a read is a partial sequence with
  timing gaps, so identification still leans on a reference database.
- **Depth.** Millions of peptides per run is deep for a purified protein or a simple mixture and
  shallow for plasma or a whole-cell proteome, where MS (Orbitrap Astral class) quantifies thousands
  of proteins per hour.

### 3.4 What it is good at

Residue-level evidence on purified or low-complexity samples: confirming the sequence of a biologic
or engineered protein, detecting single amino acid variants and site-specific modifications, protein
identification in labs without MS, barcoded protein libraries. The company sizes the non-human
proteomics market (synthetic biology, biologics, model organisms) at more than USD 4B a year (G).
That is where single-molecule residue reads beat MS on simplicity and sensitivity. Plasma
biomarker discovery is not.

## 4. Nautilus: map the intact molecule

### 4.1 How it works

From the PrISM preprint (bioRxiv 10.1101/2021.10.11.463967; simulations) and the Nature Methods tau
paper (published 2026-09-04; U for details not re-read):

1. Proteins are **not digested**. Each molecule is attached to its own optically resolvable landing
   pad on a dense array (company design target about 10 billion sites; the preprint's simulations
   assume a 10-billion-molecule chip).
2. **Iterative cycles**: a fluorescent probe (or probe mix) is flowed in, binding is imaged at every
   pad, the probe is removed, and the next one is applied. Hundreds of cycles give each molecule a
   binding fingerprint.
3. Two modes:
   - **Broadscale (PrISM)**: hundreds of *multi-affinity* probes, each binding short epitopes (about
     three residues) with high affinity and low specificity. No single probe identifies anything; the
     pattern across all probes, decoded by a machine-learning model against a reference proteome, does.
     Simulated: more than 98% of proteins identifiable, 9.5-11.5 orders of dynamic range.
   - **Targeted proteoform**: a panel of highly specific antibodies against isoform features and
     modification sites. Every molecule's combination of positives is a proteoform call. Tau: 130
     proteoform groups resolved out of up to 768 feasible combinations, detection at 0.1% of a sample,
     median CV under 5.5%; the paper's finding is that disease modifications accumulate on single tau
     molecules in ordered, non-random patterns (U).

### 4.2 What intact buys

- **Combinations on one molecule.** The tau result is impossible for any digest-first method:
  co-occurrence of phosphosites and isoform features is a property of the molecule, not of any
  peptide. Top-down MS can do it in principle but struggles with large, heavily modified proteins
  (tau has 441 residues in its longest isoform and dozens of phosphosites).
- **No front-end chemistry.** N-terminal acetylation is irrelevant; nothing is read from the end.
- **Counting, not inferring.** One molecule, one pad, one call: quantification is a count, and
  there is no peptide-to-protein inference step.
- **Scale.** Billions of pads, if achieved, give dynamic range that per-run peptide counts cannot.

### 4.3 What intact does not buy, and what it costs

- **Intact chain is not native structure.** On the user's question about "different bindings":
  the platform preserves the covalent chain, so it sees the **form** of the protein. Protein-protein
  complexes and other binding partners are generally lost when molecules are separated onto
  individual pads, and probe access to short linear epitopes usually needs unfolding (A; whether
  Nautilus denatures is Q-047). The binding that the platform exploits is the **probes'** binding to
  each molecule. Interaction mapping stays with crosslinking MS, native MS and proximity assays.
- **It is not sequencing.** Identity is inferred from which probes stick. Anything the probe panel
  cannot see does not exist for the instrument: a novel variant, an unexpected modification, an
  organism without a good reference proteome.
- **Epitope masking and cross-reactivity.** A modification next to an antibody's epitope can block
  binding; antibodies cross-react. Both bias proteoform calls in ways that must be validated assay
  by assay.
- **Reagents are the product.** Broadscale lives or dies on the probe library. The July 2026 miss
  is that risk realised: assay changes "did not sufficiently improve probe performance" for 2027 GA
  at target specs (U, company release). The response was to halve the broadscale team and triple
  proteoform staff, targeting about 20 proteoform assays by mid-2028 (G).
- **Assay-by-assay economics.** A proteoform menu is closer to an immunoassay business than to a
  platform: each assay needs antibodies, validation and a biological use case. The tau assay serves
  neurodegeneration research (MJFF grant revenue, Baylor as first early access customer); AKT1 is
  the first oncology assay, due in early access in late 2026 (G).

## 5. Side by side

| Dimension | QSI (Platinum Pro now, Proteus Q2 2027 G) | NAUT (early access now, Voyager mid-2027 G) |
|---|---|---|
| Unit measured | Peptide (protein fragment) | Intact protein chain |
| Readout | Kinetics of N-terminal recognizer binding during stepwise cleavage | Binary binding fingerprint over hundreds of probe cycles |
| Identity comes from | Residue reads aligned to references (de novo once all 20 residues read) | Probe pattern decoded against a reference (broadscale) or a defined antibody panel (proteoform) |
| Preserves | Residue order within a peptide; site-level modifications and variants | Which features co-occur on one molecule (proteoform); molecule counts |
| Loses | Connectivity across peptides; native N-terminus; protein inference ambiguity | Anything without a probe; residue-level sequence; novel variants |
| Native complexes | No (denatured and digested) | Not shown (Q-047) |
| Best sample | Purified proteins, simple mixtures, biologics, synthetic biology | Complex lysates and tissue for targeted proteoforms; whole proteomes if broadscale works |
| Bottleneck so far | Instrument engineering, recognizer coverage | Probe performance (broadscale), antibody validation (proteoforms) |
| Main substitute | Bottom-up MS, Edman services | Top-down MS, immunoassays (Simoa, MSD), Olink and SomaScan for broad screens |
| Revenue model | Instrument (Proteus USD 425K list) plus kits; placements to seed the base | Instrument plus assay kits; early access and grants today |
| What would prove it | Proteus specs at launch, placements and kit pull-through per system | Pre-order count, assays launched on schedule, broadscale date with specs |

**Two worked examples (A).**

*A tau molecule* carrying phosphates at S202, T205 and T231 on the 0N4R isoform. QSI after
digestion sees a peptide with pS202 and pT205 (they sit close together), a separate peptide with
pT231, and isoform-specific peptides from other copies, all pooled across molecules. It can report
how often each site is phosphorylated. It cannot report how many molecules carry all three plus the
0N4R splice. Nautilus reports exactly that count, if its antibodies for each feature work on the
same molecule without masking each other.

*A therapeutic antibody* with an unexpected single amino acid substitution from a manufacturing cell
line. QSI reads the substitution in the affected peptide. Nautilus misses it unless a probe was
designed for that variant.

**The out-of-the-box read.** The two are closer to complements than rivals: QSI fits the biologics
and synthetic-biology bench, NAUT the neuro and signalling biology lab. Their common enemy is mass
spectrometry, which keeps getting faster and is already in the cores where both must sell. The
investable question for each is narrow: on which job does a single-molecule optical instrument beat
an Astral-class MS on cost, simplicity or information content? QSI's answer is residue-level reads
without an MS expert; NAUT's answer is proteoform combinations that MS cannot resolve on large,
heavily modified proteins. Both answers are plausible; neither has a paid installed base yet.

## 6. Business quality cards (as of 2026-10-11)

Numbers from `python scripts/business_quality_card.py QSI NAUT --as-of 2026-10-11`; rows in
`product_revenue_map.csv`, `business_quality_scorecard.csv`, `guidance_ledger.csv`,
`costly_signal_ledger.csv`, `deal_ledger.csv`.

| Lens | QSI | NAUT |
|---|---|---|
| Product map | Platinum Pro and kits: Q2 2026 revenue USD 0.344M (FY2025 2.4M at 47% gross margin); shrinking by design until Proteus. Proteus pre-revenue. | Iterative Mapping early access (tau assay): Q2 2026 revenue USD 0.2M, mostly an MJFF grant plus the first sale. Voyager pre-revenue. |
| Moat | None today; candidates are recognizer chemistry and the semiconductor and optics stack, untested by price or share. Trend eroding while the base waits for Proteus. | None today; candidates are single-molecule array know-how and validated antibody panels. Broadscale probe library unproven. |
| Business model (C1-C8) | `unproven`: sum 4 of 16, four zeros (pricing power, capital intensity, operating leverage, dependency); revenue 1% of opex. | `unproven`: three criteria not scorable; four zeros; revenue 1% of opex. |
| People: guidance | 2 of 3 dated guides hit (Platinum 2022, generous; Platinum Pro H1 2025, early; Proteus end-2026, missed by about six months). Posterior 0.57 (80% CI 0.33-0.80), mean slip +30 days. | 0 of 5 hit: launch 2023, mid-2024, late 2025, late 2026, broadscale GA H1 2027. Posterior 0.22 (80% CI 0.07-0.41), mean slip +274 days. |
| People: costly signals | One `post_hoc` (the extra design cycle, explained alongside the slip). | Two `post_hoc` (2025 RIF, 2026 broadscale reallocation). |
| People grade | `verify` | `discount` (D-046: habitual timeline optimism) |
| So what for the price | Scenarios assuming Proteus on time are capped at 80% total weight. | Scenarios assuming guidance met are capped at 41%. Size as an event position either way. |

## 7. Survival gate and dilution machinery (H1)

| Item | QSI | NAUT |
|---|---|---|
| Price 2026-10-08; market cap | 1.22; USD 267M (F, mirror) | 1.82; USD 232M (F, mirror) |
| Shares | about 219M (A: cap / price) | 127.3M at 2026-07-24 (U, 10-Q cover) |
| Cash and investments 2026-06-30 | USD 169.9M (U) | USD 129.2M, of which 84.0M current (U) |
| Quarterly burn | Adjusted EBITDA about -21M in Q2; RIF saves about 12M a year (U) | About 14.2M cash burn in Q2 (U) |
| Estimated cash 2026-09-30 | about USD 150M before any ATM proceeds (A) | about USD 115M (A) |
| Enterprise value | about USD 117M (A) | about USD 117M (A) |
| Runway guide | Into Q4 2028 (G) | Into Q1 2028; raise expected by mid-2027 (G) |
| Next key event plus 12 months | Proteus Q2 2027 plus 12 = Q2 2028: covered on guidance | Voyager shipments mid-2027 plus 12 = mid-2028: not covered |
| Dilution machinery | 100M Leerink ATM on file since Sept 2025 (U); 50M registered direct at 1.67 in July 2025 | 125M TD Cowen ATM, 424B5 about 2026-09-18 (U); 300M shelf |
| Run-up | +63% in 21 sessions, +95% from 0.795 on 09-28 to 1.55 on 10-02 | +63% in 21 sessions, +117% from 0.905 on 09-04 to 1.96 on 10-02 |
| H1 flag | **On** (effective shelf, live ATM, recent run-up) | **On** (same, plus runway short of event plus 12 months) |

The two companies now carry nearly identical enterprise values. A month ago the market paid about
USD 25M of enterprise value for QSI's technology (price 0.80, cash about 150M; A) and a similar
order for NAUT; the HUPO and Nature Methods news quadrupled that in two weeks.

## 8. Post-announcement drift applied to QSI and NAUT

Method: `src/biotech_divedeep/signals/drift.py`; data and log: `qsi_naut_daily_2021_2026.csv`,
`announcement_events.csv`, output `announcement_drift_qsi_naut.csv`; run with
`python scripts/announcement_drift.py QSI NAUT`. Benchmark `EW_LIFESCI_200M`, which reproduces
XBI's path well (index 1.00 in June 2021, 0.49 at the June 2022 low, 0.46 in October 2023, 0.45 in
April 2025, 1.08 on 2026-09-04). Day 0 is the first session that could react; drift is BHAR from
the close of day +1. With 45 announcements and 23 shocks across two names, none of this is a test.

**Baselines.** Both stocks lose to the benchmark most of the time: the unconditional median
BHAR over days +2 to +60 is -16% for QSI and -7% for NAUT (means -4.5% and -3.0%; returns are
right-skewed). Every event result has to beat those medians, not zero.

| Finding | Evidence | Reading |
|---|---|---|
| Earnings are mostly non-events | 38 of 45 announcements `neutral`; median absolute EAR on earnings 6% with median abnormal volume 1.05x | For pre-revenue platforms the quarterly number carries little news. EPS surprise would be noise. |
| Timeline slips are where the information is | NAUT-E18 (2026-07-28, broadscale miss): EAR -40%, then BHAR -29% over +2 to +20 (baseline median -4%). NAUT-E12 (2025-02-27, launch to late 2026, RIF): EAR -7%, then -26% (+2 to +20) and -35% (+2 to +60). QSI-E21 (2026-08-14, Proteus to Q2 2027 with a runway extension): EAR -7%, flat after. | Slips drifted when they also cut scope or added cost; the QSI slip came packaged with a longer runway and did not. Consistent with H17 P2 and with H15. |
| Big negative surprises are noisy in micro caps | QSI-E09 (August 2023, EAR -41%) then +15% at day +20 and -22% at day +60; QSI-E14 (November 2024, EAR -15%) then +147% at day +20, swamped by the "quantum" name rally | Two names cannot separate drift from the next shock. That is why H17 is pre-registered on the universe. |
| QSI's no-news spikes reverse | 11 positive shocks, median EAR +27%; median BHAR +2 to +60 of -29% (vs -16% baseline), negative in 9 of 11. The late-2024 run (two-day abnormal returns of +107% from 2024-11-20 and +133% from 2024-12-26) is the cleanest case: name-driven buying, no company news, then -50% abnormal over days +2 to +60 after the December spike. | Chan (2003) news vs no-news; attention-driven buying in a cheap, high-retail stock (H10). |
| NAUT's spikes did not | 7 positive shocks; the late-2025 cluster (Sept-Nov 2025) kept rising (+113%, +48% at day +60) | Some unexplained moves are information arriving early (the tau and proteoform work became public later). The shock rule cannot tell them apart; that is a question for H17 P4 with attention data. |
| Positive news with a live ATM | NAUT: Nature Methods paper (dated 09-04 in summaries; the volume spike came 09-09, EAR +14%, then +108% abnormal over days +2 to +20), ATM prospectus about 09-18, HUPO-week shock 09-29 (+27% two-day on 19x volume), Leerink initiation 10-02 (+20%). QSI: HUPO data 09-29 (EAR +32%), then -17% on 10-05 on 19M shares (Q-019). | Exactly the H17 P3 setup: positive reaction, then supply. The 10-05 QSI drop fits ATM selling or profit-taking; the Q3 10-Q will tell (Q-044). |

**What this means for the two names now (A).**

1. Both sit right after a positive-news burst with live ATMs. In QSI's own history, spikes like this
   gave back most of their abnormal gain within three months; NAUT's history is mixed. The
   long-only stance is: do not chase, and treat any position bought into the run as a trade with a
   stop, not a thesis.
2. The next scheduled events are Q3 reports (NAUT late October, QSI early November; dates U). For a
   holder, a SEAR of -2 or worse with volume confirmation, or any new timeline slip, is the exit
   signal under H17's long-only rule. For a buyer, a positive reaction to an earnings day is unlikely
   to mean much unless it carries a dated technical milestone.
3. The events that should move these stocks are technical: QSI's all-20-residue demonstration (G by
   year-end) and Proteus beta data; NAUT's AKT1 early access (G late 2026), pre-order counts and any
   broadscale date. Log each one in `announcement_events.csv` when it lands.

## 9. Data notes and limits

- Prices: listing-mirror snapshots, regime-aware dates (D-044, `core/calendar.py`). About 1% of
  days show a stale close against the screener's own one-day return; drift windows use
  close-to-close returns, which telescope over the window. Five missing sessions (two in December
  2022, three in February 2026).
- Event dates mostly come from earnings aggregators; NAUT releases before the open (one release
  confirmed at 06:05 ET), QSI's timing is set to `unknown` and the session is picked by volume.
  Verify on EDGAR (Q-043).
- The benchmark is a proxy until XBI total return is available (Q-049).
- Technology statements about Proteus and Voyager are company claims (G) until independent users
  publish.

## Sources

QSI: [Q2 2026 results (Stock Titan)](https://www.stocktitan.net/news/QSI/quantum-si-reports-second-quarter-2026-financial-results-and-v11bmw6bzrnc.html);
[Q2 2026 8-K exhibit](https://www.sec.gov/Archives/edgar/data/0001816431/000181643126000053/qsi8132026ex991.htm);
[HUPO interim Proteus data 8-K](https://www.sec.gov/Archives/edgar/data/0001816431/000181643126000061/proteusvsplatinumdatapr.htm);
[Benzinga on the 09-29 move](https://www.benzinga.com/node/62061702);
[19 amino acids (Finviz)](https://finviz.com/news/400600/quantum-si-demonstrates-detection-of-19-amino-acids-in-proteus-development-program);
[Investor day 2025-11-20](https://www.businesswire.com/news/home/20251120536284/en/Quantum-Si-Highlights-Significant-Development-Advancements-for-Proteus-and-Industry-Leading-Technology-Pipeline-at-Investor-Analyst-Day);
[FY2025 results](https://www.businesswire.com/news/home/20260303534840/en/Quantum-Si-Reports-Fourth-Quarter-and-Full-Year-2025-Financial-Results);
[Q1 2026 call](https://www.fool.com/earnings/call-transcripts/2026/05/07/quantum-si-qsi-q1-2026-earnings-transcript/);
[10-K summary](https://www.stocktitan.net/sec-filings/QSI/10-k-quantum-si-inc-files-annual-report-006f6e0fcf68.html);
[2025 registered direct (424B3)](https://www.sec.gov/Archives/edgar/data/1816431/000114036125039703/ny20056813x2_424b3.htm);
[Q3 2025 10-Q (Leerink ATM)](https://www.sec.gov/Archives/edgar/data/1816431/000181643125000066/qsi-20250930.htm);
[Reed et al. 2022 preprint](https://www.biorxiv.org/content/10.1101/2022.01.04.475002.full.pdf);
[Quantum name rally commentary (Seeking Alpha)](https://seekingalpha.com/article/4747579-quantum-si-another-wrong-horse-on-the-quantum-computing-racetrack-sell).

NAUT: [Q2 2026 release (GlobeNewswire)](https://www.globenewswire.com/news-release/2026/07/28/3334216/0/en/Nautilus-Biotechnology-Reports-Second-Quarter-2026-Financial-Results.html);
[Q2 2026 call highlights](https://www.marketbeat.com/instant-alerts/nautilus-biotechnology-q2-earnings-call-highlights-2026-07-28/);
[Q2 2026 transcript](https://www.marketbeat.com/earnings/reports/2026-7-28-nautilus-biotechnology-inc-stock/);
[Q2 2026 numbers (TradingView)](https://www.tradingview.com/news/tradingview:729979cd5edef:0-nautilus-biotechnology-reports-q2-2026-0-2m-revenue-14-5m-net-loss-129-2m-cash/);
[10-Q summary and ATM (Stock Titan)](https://www.stocktitan.net/sec-filings/NAUT/10-q-nautilus-biotechnology-inc-quarterly-earnings-report-f6eac3d8910b.html);
[Q1 2026 results](https://www.streetinsider.com/Press+Releases/Nautilus+Biotechnology+Reports+First+Quarter+2026+Financial+Results/26378526.html);
[Launch history (GenomeWeb, 2025)](https://www.genomeweb.com/business-news/nautilus-biotech-pushes-launch-date-proteome-platform-late-2026-cuts-16-percent-staff);
[2024 delay (Investing.com)](https://www.investing.com/news/stock-market-news/earnings-call-nautilus-biotechnology-delays-new-platform-launch-to-2025-93CH-3325060);
[Nature Methods tau paper (company blog)](https://nautilus.bio/blog/just-published-in-nature-methods-large-scale-single-molecule-analysis-of-tau-proteoforms/);
[PrISM preprint](https://www.biorxiv.org/content/10.1101/2021.10.11.463967v1.full.pdf+html);
[PrISM explainer](https://www.nautilus.bio/blog/a-brief-introduction-to-prism-the-theoretical-framework-underpinning-the-nautilus-platform/);
[10-02 move and Leerink initiation](https://stockstotrade.com/news/nautilus-biotechnology-inc-naut-news-2026_10_02/).

Context: [Illumina completes SomaLogic acquisition](https://pulse2.com/illumina-completes-acquisition-of-somalogic-to-expand-proteomics-and-multiomics-strategy);
[N-terminal blocking and MS (Analyst 2011)](https://pubs.rsc.org/en/content/articlehtml/2011/an/c0an00384k).
Literature cited from memory, to re-check before reuse: Smith and Kelleher (2013, Nature Methods)
on proteoforms; Aebersold et al. (2018, Nature Chemical Biology) on proteoform counts; Anderson and
Anderson (2002, Mol Cell Proteomics) on plasma dynamic range; Arnesen et al. (2009, PNAS) on
N-terminal acetylation; PEAD literature in the H17 pre-registration.
