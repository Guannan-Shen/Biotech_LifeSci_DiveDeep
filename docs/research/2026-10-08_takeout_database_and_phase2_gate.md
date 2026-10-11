# Takeout Database and the Phase 2 Gate (H8, H16)

Written 2026-10-08 after the investor's request: build a database of biotech companies that got
bought, find the common traits, and look for the next target before the news; and test the view
that clean, best-in-class Phase 2 data is the point where the odds turn in the investor's favour.
Decisions D-034 to D-037. Evidence classes: F fact, G management guidance, A own assumption,
U unverified. Every deal row is U until the target's 8-K and SC 14D9 or DEFM14A are read on a
machine with EDGAR access (this environment cannot open sec.gov).

## 0. Summary

1. **The two theories are one theory.** Acquirers buy de-risked mechanisms. In the 88-deal table
   (2019 to 2026-10-08) 65% of targets had randomized Phase 2, pivotal or commercial data before
   the deal, and 65% of lead assets were not yet approved. Clean mid-stage data is the most common
   trigger for a clinical-stage takeout; commercial assets are the other half.
2. **A table of targets cannot find the next target by itself.** It shows what targets look like,
   not how often companies with those traits get bought. Palepu (1986) showed that this
   choice-based design overstates accuracy and that the excess return of correctly predicted
   targets is eaten by the many false positives. The fix is a company-quarter hazard model with
   every listed biotech in the denominator (P5, Q-032).
3. **Takeout is a kicker, not a thesis.** With a base hazard of about 3.5% a year (A) and a median
   premium of 40% to the last close (n=14 sourced 2025-2026 deals; IQR 28% to 63%), the expected
   kicker for an average name is about 1.4% a year. A strong profile (clean Phase 2, gap area,
   USD 0.3-2B) scores about 8% a year (A), worth about 3.5% a year. Only a basket makes a deal
   likely: 15 names at 8% each give a 71% chance of at least one deal in a year (independence
   assumed; real deal waves cluster). Every name must still pass the survival, business quality
   and price gates on its standalone case.
4. **"Buy before the news" mostly means buying months ahead.** The last-close premium understates
   what holders earned when the stock ran up first: Ventyx 2% to the last close vs 62% to the
   30-day VWAP, Terns 6% vs 31% to the 60-day VWAP, Forte 41% vs 86% to the VWAP since its
   readout. The gap (VWAP premium minus last-close premium; windows differ by deal) is positive
   in 8 of 10 deals that report both, median +14 points.
   The run-up starts on media reports or rumours; the investor who owns the name before that
   collects it, and whoever buys the rumour gets the thin remainder plus deal-break risk.
5. **Phase 2 base rates support the instinct, with a catch.** BIO, Informa and QLS (2011-2020):
   28.9% of Phase 2 programs advance to Phase 3, the lowest transition; likelihood of approval
   from Phase 1 is 7.9%. Once Phase 2 is cleared, approval odds rise to about 52% (57.8% Phase 3
   to filing times 90.6% filing to approval). That is a coin flip, and the market reprices the
   stock on the day of the data, so the edge has to come from judging which positive Phase 2s
   are real.
6. **The best-looking Phase 2 results shrink the most.** A Phase 2 that just clears significance
   is inflated by selection. Worked example (section 5): an effect of 10 with SE 4 (z = 2.5),
   shrunk toward a class prior, implies a Phase 3 sized for 90% power at 10 has about a 54%
   chance of success. The same effect with SE 2.5 (a larger trial) gives 70%. "Clean" is about
   the width of the interval and the design, not the size of the point estimate.
7. **Pacira (2026-10-08) is a different archetype from the Phase 2 story.** A cash-generating
   specialty pharma (LTM revenue about USD 746M, adjusted EBITDA about 177M) bought at about 2.2x
   revenue by a generics major, after an activist proxy contest that demanded a sale review and
   with a volume-limited generic entry for EXPAREL from early 2030. Activism plus a known loss of
   exclusivity plus a buyer whose skill is managing off-patent decline: that profile matters for
   the `commercial_pharma` names already in the repo (HROW, ETON).

## 1. The Pacira case

| Item | Value | Class | Source |
|---|---|---|---|
| Terms | USD 36.50 per share cash, equity value about USD 1.65B; tender offer then a DGCL 251(h) merger; close expected by end of 2026 | U | [Pacira 8-K exhibit 99.1](https://www.sec.gov/Archives/edgar/data/0001396814/000110465926114571/tm2627240d2_ex99-1.htm) |
| Conditions | Majority of shares tendered; HSR clearance; both boards unanimous | U | same; [SC TO-C](https://www.sec.gov/Archives/edgar/data/0001396814/000114036126039025/ef20083514_sctoc.htm) |
| Business | EXPAREL and ZILRETTA; LTM to 2026-06-30 revenue about USD 746M, adjusted EBITDA about USD 177M | U | same |
| Activism | DOMA Perpetual ran a 2026 proxy contest asking for a review of strategic alternatives including a sale; ISS and Glass Lewis backed management | U | [Glass Lewis report summary](https://www.streetinsider.com/Board+Changes/Glass+Lewis+backs+Pacira+BioSciences+director+nominees/26566969.html), [DOMA letter](https://finviz.com/news/356032/doma-perpetual-director-nominees-send-letter-to-shareholders-of-pacira-biosciences) |
| Exclusivity | 2025 settlement licenses volume-limited generic EXPAREL from a confidential date in early 2030, ramping to the high thirties percent of volume; unlimited no earlier than 2039; last Orange Book patent 2044; new Paragraph IV filers in October 2025 | U | [settlement coverage](https://www.tipranks.com/news/the-fly/pacira-announces-settlement-of-u-s-patent-litigation-for-exparel), [Q1 2026 10-Q](https://www.sec.gov/Archives/edgar/data/0001396814/000162828026028871/pcrx-20260331.htm) |
| Premium | Not found yet; needs the unaffected close (Q-033) | | |

Reading: the proxy contest lost on paper and won in practice; five months later the company was
sold. An activist demanding a sale review is one of the few public traits with a plausible causal
link to a deal (the `activist_or_strategic_review` likelihood ratio of 2.0 in the priors is A).

## 2. The database

`data/reference/biotech_takeouts.csv`, one row per definitive agreement to acquire a US-listed
biotech or specialty pharma, 2019-01 to 2026-10-08. 88 rows. (Update 2026-10-09: extended to
2005-2026, 229 rows, with `deal_kind`; the measured base hazard replaces the assumed one. See
`docs/research/2026-10-09_takeout_history_universe_and_case_method.md`.)

| Column group | Fields |
|---|---|
| Deal | `deal_id`, target, ticker, acquirer, `acquirer_type`, `announced_on`, `date_precision` |
| Terms | price per share, CVR maximum, equity value (USD B), premium to the last close, premium to a VWAP (window in `note`), consideration |
| Asset | lead asset, `stage_at_deal`, `key_data_before_deal`, therapeutic area, modality |
| Context | `activist_or_review` |
| Evidence | `evidence_class` (all U), `source_url`, `note` |

**Provenance and caveats.**

- 24 rows (all 2025-2026 deals) were checked on 2026-10-08 against web search results that quote
  the press release or filing; each has a `source_url`. Premiums appear only where a source gave
  one (14 rows).
- 64 rows (2019-2025) come from recall and carry no URL; their `note` says so. Prices and
  equity values are approximately right; dates carry `date_precision = approx`. They are useful
  for the stage and data mix, not for premium statistics.
- The sample is not complete. Larger and more memorable deals are over-represented, and private
  targets are excluded by design. Do not compute a hazard from it until a complete list is pulled
  from EDGAR (SC TO-T, SC 14D9 and DEFM14A filings by SIC code; Q-032).
- Two rows are not strategic takeouts: Generation Bio (cash shell bought by XOMA Royalty) and
  2seventy bio (partner buy-out at a low price). They stay in the table because a survivorship-free
  record needs the distressed tail.
- Correction to `docs/research/2026-10-07_launch_layer_screen.md` section 4: the 2026 premiums were
  not "moderate (about 20-30%)". Catalyst was 21% to its unaffected close, but Apellis was 140% to
  its 2026-03-30 close and Crinetics 102%. The floor under approved-product names is higher than
  that note said.

## 3. What the targets look like (descriptive only)

Output of `python scripts/takeout_screen.py summary` on 2026-10-08:

| Trait | All 88 (2019-2026) | 33 deals since 2025 |
|---|---|---|
| Lead asset approved | 35% | 42% |
| Phase 3 or filed | 30% | 24% |
| Phase 2 | 24% | 21% |
| Phase 1 or earlier | 11% | 12% |
| Randomized Phase 2, pivotal or commercial data before the deal | 65% | 64% |
| Only Phase 1 proof of concept | 19% | 18% |
| Buyer is big pharma | 80% | 67% |
| Cash only / cash plus CVR | 74% / 24% | 64% / 36% |
| Top areas | oncology 26%, immunology 16%, neurology 14% | oncology 21%, immunology 12% |
| Median equity value | USD 3.2B | USD 3.3B |
| Premium to last close (sourced, n=14) | median 40%, IQR 28% to 63% | same rows |

Five traits worth testing in the hazard model, each with the counter-argument:

1. **Human proof of concept on a validated or hot mechanism.** IL-13 and TL1A antibodies,
   incretins and amylin, FGF21, BCR-ABL and ALK kinase inhibitors, CD122. Counter: the same data
   that attract a buyer also attract a follow-on offering, which caps the run.
2. **Size the buyer can digest.** Median USD 3.2B; USD 1-15B covers most rows. Counter: in this
   size band a deal happens to a few percent of names a year.
3. **An existing partner or holder.** Lilly-Verve, Sanofi-Principia, Sanofi-Translate,
   Novo-Dicerna, Sanofi-Provention, BMS-2seventy, Pfizer-Biohaven (all A, from recall). Counter:
   partners also walk away, and a partner with a right of first negotiation can depress bids.
4. **Activists and strategic reviews.** Pacira (DOMA), Dynavax (Deep Track, U), Sage (Biogen's
   unsolicited bid, U). Counter: activism clusters in underperformers, which is a left-tail trait.
5. **CVRs bridge disagreement.** 36% of 2025-2026 deals carried a CVR. A CVR is the buyer saying
   it does not believe the bull case in full; value the CVR at a fraction of face.

A takeout does not validate the asset. Oxbryta (bought with GBT in 2022) was withdrawn in 2024;
magrolimab (Forty Seven, 2020) and emraclidine (Cerevel, 2023) failed after their deals (A, from
recall). The premium was paid to the seller; the risk moved to the buyer.

## 4. From traits to a forecast (H8, P5)

**Design.** Discrete-time hazard model on company-quarters, 2005 onwards, every US-listed
biotech with market cap above USD 100M (survivorship-free). Event: a definitive agreement in the
next four quarters. Features measured at quarter start with `available_at`: stage and data class
of the lead asset, Phase 2 grade (section 5), market cap band, net cash and runway, specialist
ownership (H4), activist 13D or proxy filing, big-pharma equity or option, therapeutic-area gap
score (count of large pharmas with 2027-2032 loss of exclusivity in the area), deal-wave index
(trailing four-quarter biotech M&A value), XBI regime. Baseline to beat: stage-only base rates.
Metric: Brier score and calibration, time-split. Pre-registration due before data are pulled
(Q-034).

**Today.** `models/takeout.py` scores a profile with the odds-times-likelihood-ratio priors in
`config/takeout_priors.yaml` (A). It ranks; it does not forecast. Examples:

| Profile | Likelihood ratio | Annual probability (low / mid / high base) | Kicker at a 45% premium |
|---|---|---|---|
| Approved product, USD 1.2B, activist, subscale sales force (Pacira-like) | 3.4 | 6% / 11% / 15% | 4.9% |
| Clean randomized Phase 2, USD 1.5B, acquirer gap area | 2.3 | 5% / 8% / 11% | 3.5% |
| Phase 1, USD 0.2B, under 12 months of runway | 0.16 | 0% / 1% / 1% | 0.3% |

**What to do with a score.** Treat it as a tie-breaker inside a basket of names that already pass
the survival, business quality and price gates, and as a reason not to sell a name that is
cheap on its standalone case. Never pay up for it: once the rumour is public the premium to your
entry is the residual, and the deal-break downside is a full round trip.

## 5. The Phase 2 gate (H16, P6)

**Base rates.**

| Transition | BIO/Informa/QLS 2011-2020 | Investor's statement |
|---|---|---|
| Phase 1 to Phase 2 | 52.0% advance (U, primary report not opened) | "about 35% fail in Phase 1": BIO implies 48% do not advance; Wong, Siah and Lo (2019) give higher Phase 1 success, so 35% sits inside the published range |
| Phase 2 to Phase 3 | 28.9% advance (U, secondary source) | "the vast majority fail in Phase 2": yes in BIO, 71% do not advance |
| Phase 3 to filing | 57.8% (A, recall of the same report) | |
| Filing to approval | 90.6% (A, recall) | |
| Phase 1 to approval | 7.9% (U, BIO summary) | |
| Phase 3 to approval | about 52% (computed from the two rows above) | "once they clear Phase 2 the odds are much more in our favour": from about 1 in 12 to about 1 in 2 |

Wong, Siah and Lo (Biostatistics 2019, 2000-2015) report a higher overall success rate (13.8%,
oncology 3.4%), but a published corrigendum changed their Phase 2 to Phase 3 numbers, so use the
corrected tables before quoting them. Not every Phase 2 failure is efficacy: Arrowsmith (2011,
Phase 2 failures 2008-2010) attributed about half to efficacy, about a fifth to safety and about
three tenths to strategy (A, recall; check before citing). A strategic stop at a small company
usually means the money ran out.

**Why "clean and best in class" is the right instinct and still not enough.**

- Selection inflates. Programs move forward because the Phase 2 estimate came out high; small
  trials that cross p < 0.05 overstate the effect (Gelman and Carlin 2014, type M error). At a
  true effect of 6.5 and SE 4, a significant Phase 2 overstates the effect 1.63-fold on average.
- Sponsors power Phase 3 on the inflated estimate. Assurance, the probability of success averaged
  over the uncertainty in the effect, is lower than the quoted power.
- Best in class is usually a cross-trial claim. Different baselines, endpoints, time points and
  rescue rules can move an apparent gap by more than the gap. Only head-to-head data, or a
  comparison with matched populations and endpoints, counts in the scorecard.

`python scripts/takeout_screen.py phase2 --estimate 10 --se 4 --prior-mean 3 --prior-sd 4`:

| Phase 2 | Shrunk effect | Weight on the data | Quoted Phase 3 power | Assurance |
|---|---|---|---|---|
| 10, SE 4 (z = 2.5) | 6.5 | 50% | 90% | 54% |
| 10, SE 2.5 (z = 4.0) | 8.0 | 72% | 90% | 70% |

The prior (mean 3, SD 4) is A and exists only to show the mechanics; P6 calibrates it per
mechanism class from labelled Phase 2 to Phase 3 pairs. The first row lands near the 58% Phase 3
transition rate, which is what a typical "positive" Phase 2 is.

**The scorecard** (`models/phase2.py`, `grade_phase2`). Gates: randomized and controlled;
pre-specified primary endpoint met (the registry entry must match the release); no new safety
signal. Graded items (0/1/2, weighted): clinically meaningful effect, dose response, consistent
secondaries and subgroups, registrational endpoint and population, adequate size, durability,
best-in-class evidence, mechanism validated in humans elsewhere, independent confirmation.
Labels: `clean` (all gates, graded share at least 0.65), `positive_not_clean`, `not_clean`.
Forte's vitiligo data (randomized 3:1, 43 patients, Phase 1b) would pass the gates and score low on
size and registrational endpoint; argenx still paid USD 2.2B within 18 days. Buyers pay for
mechanism and option value, not only for statistical cleanliness, which is why the takeout score
and the Phase 2 grade are separate inputs.

**The market prices the data on the day.** The open question for H16 is whether anything is
left after the first day. Cue Biopharma (2026-09-21) rose more than 40% on a positive randomized
Phase 2 in chronic spontaneous urticaria with an active comparator, then fell over 27% intraday on
funding concerns (U, [ad-hoc-news](https://www.ad-hoc-news.de/boerse/news/nebenwerte/cue-biopharma-stock-swings-after-positive-cue-221-phase-2-data-and/70149440)).
The pattern to test: data spike, follow-on offering, supply absorbed (H1, D-018 volume rules),
then drift if the data were clean. That gives an entry after the offering instead of chasing the
spike.

## 6. Hypotheses and how they will be tested

- **H8 (revised).** A company-quarter hazard model with stage, Phase 2 grade, size, activist,
  partner and gap-area features predicts 12-month takeouts better than stage base rates (Brier,
  time-split); a top-decile basket that also passes the H1 survival screen beats XBI over rolling
  12 months. Pre-registration pending (Q-034).
- **H16 (new).** Among positive randomized Phase 2 readouts by US small and mid caps, those graded
  `clean` earn positive excess return vs XBI from the close after the first post-data financing (or
  day +20 if none) to day +126 and +252, and beat `positive_not_clean` readouts. Pre-registered in
  `notes/backtests/2026-10-08_H16_phase2_quality_drift.md` before any data were pulled.

## 7. Weekly workflow (once M3 and M4 feed readouts)

1. Every positive Phase 2 topline in the research universe gets a scorecard row (gates and graded
   items, with the registry record checked against the release).
2. Compute assurance with the mechanism-class prior; record it as A.
3. Score takeout hazard; record factors.
4. Wait for the financing; check supply absorption with the volume rules.
5. Names that pass survival, business quality and price gates and score `clean` enter the
   candidate list; the takeout score breaks ties and sets the "do not sell cheap" flag.

## 8. Seed list for the next screen (not scored, not recommendations)

Named as takeout candidates in 2026 by sell-side lists or surveys; stage and data not yet checked
against filings: Revolution Medicines, Xenon, Arrowhead (RBC, March 2026,
[BioPharma Dive](https://www.biopharmadive.com/news/biotech-takeover-targets-rbc-mergers-acquisitions-deals/815061/));
Abivax, CG Oncology, Centessa (Truist survey,
[TipRanks](https://www.tipranks.com/news/these-are-the-most-and-least-likely-biotech-takeover-targets-for-2026));
Viking, BioCryst, Iovance (Zacks); Evommune, Structure Therapeutics, Scholar Rock (press lists).
IOVA is in the watchlist as a `launch` name; scoring it does not change D-024 (keep IOVA out of the
AI theme). Several names in these lists are above USD 10B, where the size band lowers the score.

## Sources

- Pacira: [8-K ex. 99.1](https://www.sec.gov/Archives/edgar/data/0001396814/000110465926114571/tm2627240d2_ex99-1.htm), [SC TO-C](https://www.sec.gov/Archives/edgar/data/0001396814/000114036126039025/ef20083514_sctoc.htm), [Viatris 8-K](https://www.sec.gov/Archives/edgar/data/0001792044/000114036126039024/ef20083514_ex99-1.htm)
- Deal terms: per-row `source_url` in `data/reference/biotech_takeouts.csv`
- 2026 deal volume: [GeneOnline on IQVIA H1 2026](https://www.geneonline.com/2026-biopharma-ma-trends-big-pharmas-130-billion-h1-deal-spree-nearly-tops-all-of-2025/)
- Base rates: [BIO 2011-2020 report page](https://www.bio.org/clinical-development-success-rates-and-contributing-factors-2011-2020), [Wong, Siah and Lo 2019 and corrigendum](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6409416/)
- Takeover prediction: Palepu, K. G. (1986), "Predicting takeover targets: a methodological and empirical analysis", Journal of Accounting and Economics 8(1), 3-35
- Type M error: Gelman, A. and Carlin, J. (2014), "Beyond power calculations", Perspectives on Psychological Science 9(6), 641-651
- Assurance: O'Hagan, A., Stevens, J. W. and Campbell, M. J. (2005), "Assurance in clinical trial design", Pharmaceutical Statistics 4(3), 187-201
