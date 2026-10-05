# M15 Long-Form Media & Dissent Tracker

Status: design (added 2026-10-05, D-020). Origin: the investor's TODO about YouTube and
podcasts, prompted by the Humacyte / Symvess whistleblower episode
(`docs/research/humacyte_symvess_case.md`). Phase 2 for a manual dissent register;
Phase 3 for automated transcript search.

## 1. Why this source matters

Filings and press releases are written by the company. Regulators publish decisions,
often without the internal disagreement behind them. Long-form media is where the people
who saw the inside speak at length: former FDA reviewers and consultants, trial
investigators, surgeons who used the product, ex-employees, and domain experts. In the
Humacyte case, an FDA consultant who retired in protest gave the clearest public account
of the weaknesses in the approval evidence. That is information the market could have
priced, and it lived in interviews, petitions and investigative journalism rather than
in any data feed.

The goal is a **dissent register**: for each company and asset, every credible public
criticism, who made it, what evidence they cite, and whether primary records confirm it.

## 2. Sources

| Source | Examples | Access |
|---|---|---|
| Podcasts | Whistleblower, biotech, aviation and defense shows | RSS feeds (episode metadata); transcripts from show notes, platform transcripts, or local speech-to-text on audio |
| YouTube | Interviews, conference talks, investigative channels | YouTube Data API v3 (search, metadata); captions where the owner allows |
| Conference talks and panels | Medical society meetings, aviation and defense conferences | Video archives |
| Investigative press | NYT, Bloomberg, STAT, ProPublica, trade press | Article metadata; full text where licensed |
| Petitions and letters | Citizen petitions to FDA (regulations.gov dockets), congressional letters, academic petitions | Public dockets |
| Regulator documents | FDA review memos, summary basis for regulatory action, AdCom transcripts, CRLs | FDA sites (M2) |
| Employee reviews | Glassdoor, Indeed | Manual reading only; anonymous, low weight |

## 3. Speaker credibility tiers

Evidence class is always `unverified` until a primary record confirms the claim. The tier
sets how hard we look for that confirmation.

| Tier | Speaker | Example | Weight |
|---|---|---|---|
| D1 | Former regulator staff, reviewers or consultants on the file | FDA consultant on the Symvess review | Highest; triggers an immediate primary-record check |
| D2 | Trial investigators, treating physicians, ex-employees with named roles | Surgeons who implanted the product | High |
| D3 | Independent domain experts and academics | Autonomy researchers commenting on AI pilots | Medium; often general rather than company-specific |
| D4 | Journalists summarizing D1-D3 sources | Investigative articles | Medium; follow to the underlying source |
| D5 | Anonymous reviews, retail commentary, short-seller marketing | Glassdoor, stock forums | Low; context only, never moves a probability alone |

Short sellers and promoters both have positions. Record the speaker's known financial
interest next to every claim.

## 4. Dissent register (record format)

`data/reference/dissent_register.csv` (manual in Phase 2, partly automated later):

| Field | Meaning |
|---|---|
| dissent_id | Stable id |
| ticker, asset_id | Links to entity master |
| first_public_at | Earliest timestamp the claim was public (episode date, article date, petition filing) |
| speaker, tier, known_interest | Who, D1-D5, any position or affiliation |
| claim_type | efficacy_evidence, safety, manufacturing, regulatory_process, governance, financial, technology_readiness |
| claim | One-sentence summary |
| quote, source_url, timestamp_in_media | Exact words and where they are (minute mark for audio/video) |
| primary_check | Which primary record could confirm or refute it (review memo, MAUDE, 10-Q note) |
| status | open, corroborated, partially_corroborated, refuted |
| price_at_first_public, price_reaction | For H12 event studies |

## 5. Pipeline (Phase 3)

1. Watchlist-driven search: company names, tickers, asset codes and product names across
   podcast RSS, YouTube search and press archives, daily.
2. Transcripts: captions or speech-to-text, stored with timestamps; raw media is not kept.
3. LLM extraction of claims with quoted spans and minute marks; classified by claim type.
4. Human review assigns tier and opens the primary check.
5. Corroborated D1-D2 claims become `Event`s (event_type `credible_dissent`) and feed the
   survival gate, scenario probabilities and the H12 study.

## 6. Guardrails

- A dissent claim never becomes a fact without a primary record.
- Defamation and fairness: store claims as attributed quotes; the register records what
  was said publicly, by whom, never our own allegation.
- Respect platform terms (YouTube API terms; podcast copyright). Store transcripts for
  research use only; do not republish.
- Selection bias: dissent exists about many products that turn out fine. H12 must be
  tested on a labeled set that includes refuted and harmless dissent, not only famous
  cases.

## 7. First applications

- Humacyte (HUMA): retrospective case study, `docs/research/humacyte_symvess_case.md`.
- Merlin (MRLN): current dissent scan, `docs/memos/MRLN.md`, section 5 (bad-news register).
