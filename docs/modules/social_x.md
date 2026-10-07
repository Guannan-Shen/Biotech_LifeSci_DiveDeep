# M13 Social / X Tracker

Status: design (added 2026-10-05, D-015). Phase 2 build target for a curated account
list; attention metrics in Phase 3.

## 1. Why X matters here

- **Venture-like companies talk on X first.** Founders and executives of early-stage
  public companies (MRLN is a clear case) post flight tests, customer visits and hiring
  before the press release, sometimes instead of one.
- **Biotech science is debated on X.** Clinicians and analysts dissect conference
  abstracts and topline data within minutes; this is where a weak subgroup or a safety
  imbalance is noticed first.
- **Attention is measurable.** Cashtag volume in small caps tracks retail crowding,
  which tends to mean-revert (H10).

## 2. Regulation FD and evidence classes

The SEC's 2013 guidance (the Netflix report) allows companies to disclose material
information on social media **if** they have told investors which channels they use.
So the first task per company is to check its 8-Ks, 10-K and IR site for designated
channels.

| Account tier | Examples | Evidence class | Use |
|---|---|---|---|
| T1 designated corporate channel | Company account named in filings as a disclosure channel | `fact` (same as a press release), `management_guidance` for forward-looking posts | Events, guidance ledger |
| T2 official but not designated | Executive personal accounts, company account without designation | `management_guidance` or `unverified` | Early signals; confirm against filings |
| T3 counterparties and regulators | Customer program offices, military units, FAA, partner companies | `unverified` until matched to a primary record | Corroboration of contracts and tests |
| T4 domain press and experts | Trade journalists, KOL clinicians, aerospace engineers | `unverified` | Context, critiques, leads to verify |
| T5 crowd | Cashtag posts, retail accounts | Never a source of facts | Attention and sentiment metrics only |

## 3. Signals

1. **Disclosure events (T1-T2)**: posts classified into the event taxonomy, timestamped
   by `created_at`, linked to the later 8-K or PR. Measures the lead time.
2. **Guidance claims**: dated forward-looking statements go into the guidance ledger
   (`docs/modules/company_news.md`, section 3), so executive posts count toward the
   management credibility score.
3. **Corroboration (T3)**: a customer or regulator post that confirms a milestone
   raises confidence in the catalyst calendar.
4. **Critique detection (T4)**: expert posts flagging data problems, linked to the asset.
5. **Attention z-score (T5)**: daily cashtag mention count vs its own 60-day baseline,
   normalized by float and dollar volume. Tested as a reversal signal (H10).
6. **Deletions and edits**: a deleted executive post is itself an event; record the
   fact of deletion (see compliance below for what content may be kept).

## 4. Data access

- **Official X API v2** is the only compliant route for systematic collection. Pricing
  and tiers have changed several times; verify the current plan and limits before
  budgeting (open question Q-012). Credentials via `X_BEARER_TOKEN`; never committed.
- Endpoints needed: user lookup, user timelines for a curated list, recent search for
  cashtags (`$MRLN`) and asset codes, post counts for attention metrics.
- Scraping the website breaches the terms of service and breaks often; not used.
- Fallback without API budget: a manually maintained account list reviewed weekly, with
  notable posts logged by hand into `notes/` as `unverified` events.

## 5. Compliance and storage

- The X developer terms have required honoring user deletions in stored content; check
  the current version. Design: store post id, author id, `created_at`, our derived
  classification and a content hash in the immutable store; keep full text in a
  separate, purgeable table so deletions can be honored without breaking the audit
  trail.
- Store only what a signal needs. No profiling of private individuals; T5 data is used
  in aggregate counts only.

## 6. Manipulation guardrails

- Small caps attract coordinated promotion and bots. T5 never moves a probability.
- Attention spikes without a matching T1-T3 event are treated as crowding, not news.
- Account lists are curated by tier and reviewed quarterly; new accounts start at T4.

## 7. Account list format (Phase 2)

`config/x_accounts.yaml`:

```yaml
- handle: example_handle          # without @
  tier: T1
  company: MRLN
  role: corporate                 # corporate | executive | customer | regulator | press | expert
  designated_reg_fd: unknown      # true | false | unknown, with source once checked
  source: "how we know this account is official"
```

Handles are added only after verification against the company website or filings.

## 8. Attention without the X API (added 2026-10-07, D-027)

The 2026-10-06 case study missed the attention force because M13 has no feed. Until Q-012 is
decided, three routes cover part of the gap:

| Route | What it measures | Tooling | Caveat |
|---|---|---|---|
| Wikimedia pageviews (REST, free, needs a User-Agent with contact) | Daily views of company and concept pages | `scripts/attention_proxies.py`, `signals/attention.py` | Curiosity, not trading intent; English Wikipedia only |
| GDELT DOC 2.0 `timelinevol` (free) | Share of online news coverage matching a query | Same script | News, not social; coverage lag of hours |
| Manual X log | Notable posts the investor or the weekly review sees (T1-T5), with URL, author tier, time and reach | A row per post in `notes/` as `unverified` events | Selection bias; record what was looked for, not only what was found |

Signal definition: `abnormal_attention` is the z-score of log(1 + daily count) against the
trailing 60 days, excluding the current day. Test with H10 and H13: does peak abnormal
attention on a theme's company and concept pages lead or coincide with the price peak, and do
names with the largest attention z-scores fall most after a heavy-distribution day? Terms are
listed in `config/attention_terms.yaml`; raw responses go to `data/raw/attention/<date>/`.
