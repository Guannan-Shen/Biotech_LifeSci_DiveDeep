# M4 Company News Tracker

Status: design. Phase 1 (feeds) and Phase 2 (extraction).

## 1. Sources, by trust

1. **8-K exhibits (Ex-99.1)** from M1: canonical text and timestamp for material news.
2. **Company IR pages and RSS feeds**: many IR sites run on common platforms with RSS;
   catches non-material news (conference presentations, posters, publications).
3. **Newswires** (GlobeNewswire, Business Wire, PR Newswire, Accesswire): earliest
   timestamp, often minutes before the 8-K.
4. **Earnings call transcripts** (FMP endpoint if the plan allows): guidance language,
   analyst questions.
5. **Scientific conference calendars**: ASCO, AACR, ASH, ESMO, EASL, AAN, ADA, JPM
   Healthcare; abstract release dates are catalysts in their own right.

Aggregator news and social media are context only (`unverified`); they never create
facts.

## 2. Pipeline

1. Fetch -> raw store (HTML/RSS/JSON with fetch time).
2. Deduplicate: newswire item, IR page item and 8-K exhibit for the same release are
   linked as one news event with the earliest credible `available_at`.
3. Classify into the event taxonomy (`docs/framework/archetypes.md`).
4. Extract structured claims with an LLM, each with a quoted source span:
   - dated forward-looking statements ("topline data expected in Q4 2026") ->
     catalyst ledger (M6), class `management_guidance`
   - runway guidance ("cash sufficient into Q4 2028")
   - launch metrics (patients treated, sites activated, scripts)
   - trial results (effect size, CI, p-value, n, safety)
5. Human check promotes fields from `unverified` to `fact` (for reported numbers) or
   keeps them as guidance.

## 3. Guidance ledger

Every dated claim is stored with first-seen date and every later restatement. The
history answers: "When did the company first say Q4 2026, and how many times did the
window move?" This feeds the management credibility score (M3 section 5) and the
trial-delay model (M9).

## 4. Outputs

- `news_items` table (id, ticker, title, url, source, available_at, linked accession).
- `claims` table (news_id, claim_type, structured fields, quote, evidence_class).
- Alerts for watchlist names in the weekly report.
