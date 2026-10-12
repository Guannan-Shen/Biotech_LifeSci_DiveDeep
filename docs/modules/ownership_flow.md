# M17: Insider and specialist-fund flow

Status: design and code v0.1 (2026-10-12). Hypotheses: H18 (insider and holder flow), H4
(specialist conviction). Pre-registration: `notes/backtests/2026-10-12_H18_insider_and_holder_flow.md`.
First results: `docs/research/2026-10-12_insider_holder_flow.md`.

## 1. Purpose

Track who buys and sells: officers and directors (Form 4), 10% holders and specialist funds
(Form 4, 13D/G, 13F), planned sales (Form 144), and the company itself (424B, ATM use in the
10-Q). Then measure what follows each kind of flow, so the investor's rules of thumb become
tested flags:

- insider buying is not a reliable buy signal on its own;
- block selling after a big rally marks a stock as somewhat overvalued, even if it does not fall
  at once.

The module's job in the decision system is mostly defensive (left-tail avoidance, D-008): an
**exit or trim flag** after supply following a run, an **entry checklist item** for opportunistic
insider buying, and a **specialist conviction score** that weights funds by measured skill.

## 2. Sources and point-in-time keys

| Source | What it shows | `available_at` | Delay | Code |
|---|---|---|---|---|
| Form 4 | Officer, director and 10% owner trades, code per line, 10b5-1 flag (from 2023) | Filing date | 2 business days after the trade | `connectors/sec_ownership.py` (data set and XML) |
| Form 144 | Notice of a planned sale by an affiliate (more than 5,000 shares or USD 50,000 in 3 months) | Filing date | Filed by the time the order is placed; leads the Form 4 | `parse_form144_xml` |
| 10-Q / 10-K Item 408(a) | Adoption and termination of 10b5-1 plans by officers and directors (from 2023) | Filing date | Up to a quarter | Not yet parsed (Q-054) |
| SC 13D / 13G and amendments | 5% holders crossing thresholds, activist intent | Filing date | 13D within 5 business days since 2024 (10 days before); 13G for institutions within 45 days of quarter end (recall of the 2023 rule, `unverified`) | Planned (M1) |
| 13F-HR | Quarter-end long positions of managers above USD 100M | Filing date | Up to 45 days after quarter end | `read_13f_dataset` |
| 424B5, 8-K 3.02, 10-Q ATM note | Company share sales (offerings, PIPEs, ATM) | Filing date | Same day to a quarter (ATM) | M1 dilution panel |
| Listing mirror (prices, volume, market cap) | Heavy-volume down days, implied share count | Close of the day (D-044 timing) | Daily | `signals/supply.py` |

SEC bulk files: Insider Transactions Data Sets (quarterly ZIPs of Forms 3, 4, 5) and Form 13F
Data Sets, both on sec.gov, run on the local machine (`scripts/ownership_flow.py fetch`).

Blind spots that matter in biotech:

1. **Foreign private issuers** (many ADR and Nasdaq-listed European biotechs) are exempt from
   Section 16: no Form 4 at all. Their insiders' trades show only in home-country filings and
   13D/G. Part A (identity-free supply days) is the only flow signal for them (Q-055).
2. **Company ATM sales** do not appear in Form 4. They show as heavy volume on up days and in the
   next 10-Q; part A catches the down-day share of it and the implied share count catches the rest.
3. **Shorts** are invisible in 13F, and many specialists run long/short books.
4. **Joint filers**: a fund, its adviser and its managers report the same shares; collapse them
   (`collapse_joint_filers`) before counting.

## 3. Classification of Form 4 lines

Every line gets one class (`signals/insider.py`). Only `open_market_buy` and `open_market_sale`
are discretionary and enter events; the rest are plumbing.

| Class | Rule | Why it matters |
|---|---|---|
| `open_market_buy` | Code P outside a financing window and not a group buy | The only buy with an information claim |
| `offering_participation` | Code P within 7 days of a known financing, or several filings buying on one date at one price with a 10% owner among them | In small biotech most "insider buying" headlines are funds taking their allocation in the company's own raise. That is a financing, and it usually comes with dilution |
| `open_market_sale` | Code S without a 10b5-1 flag | Discretionary supply |
| `plan_sale` | Code S under a 10b5-1 plan | Timing set months earlier; the decision is the plan adoption date (Item 408, Q-054) |
| `tax_withholding` | Code F | Mechanical |
| `distribution` | Code J disposal | Venture funds distributing shares to their partners in kind; the partners then sell. Supply, not information |
| `grant`, `exercise`, `gift`, `to_issuer` | Codes A; M, X, C; G; D | Mechanical |

**Routine vs opportunistic** (Cohen, Malloy and Pomorski 2012): an insider with open-market trades
in each of the three prior years who traded in the same calendar month in all three is routine;
the rest with that much history are opportunistic. CMP find opportunistic trades carry the
information (about 82 bp a month value-weighted) and routine trades about none.

**Events** cluster discretionary lines per issuer and direction until 14 calendar days pass
without a new filing. A sell event fires when the cluster reaches USD 250k and one seller has sold
at least 5% of the holding; a buy event at USD 250k. Each event records roles, number of distinct
insiders, the opportunistic share and the largest stake fraction.

## 4. Supply after a run (identity-free)

`signals/supply.py`. Run state on day t: close(t-1) at least 2x close(t-127) and at least 75% of
the 127-day high. Supply day: run state, close down at least 3% and at least 3% below the
benchmark, on at least 3x the volume of days [-60, -11]. Each event is compared with up to three
stocks in run state on the same date, in the same cap band, without a supply day in the prior 20
sessions, nearest in run size. Closes are split-adjusted first (`split_adjust`): the mirror's raw
closes are not, and a 1-for-20 reverse split otherwise reads as a 20x run.

## 5. Specialist funds: changes and measured skill

`config/specialist_funds.yaml` holds the panel (33 specialist funds by style plus 4 generalist
controls; CIKs to resolve, Q-051). `signals/fund_flow.py`:

- `latest_positions` applies 13F amendments (restatements replace, new-holdings amendments add).
- `position_changes` diffs consecutive quarters per fund and CUSIP: `new`, `add` (at least +25%),
  `trim` (at least -25%), `exit`, `hold`. Options rows are kept apart.
- `issuer_quarters` aggregates the panel per CUSIP and quarter: holders, new, adds, trims, exits,
  net buyers.
- `fund_skill` defines "good fund" by record, not by reputation: the shrunk mean of the 2-quarter
  BHAR of each fund's earlier new positions, using only windows that closed before the as-of date.
  Prior N(0, 5 points), single-position spread 50 points, so a fund needs about 100 resolved new
  positions before its own record outweighs the prior. Terciles of this score weight the H4 signal.
- CUSIP to ticker: a map from OpenFIGI or a vendor (Q-053); a normalized-name match against the
  universe is the fallback and is flagged `name_match_unverified`.

Why measure skill: the funds we call good today are the survivors. A panel picked by current
fame credits survivors' past picks and drops the funds that blew up, which overstates any
"follow the specialists" backtest. Closed funds stay in the panel with `active: false`.

## 6. How the flags enter decisions (advisory until H18 passes out of sample)

| Flag | Trigger | Use |
|---|---|---|
| `supply_after_run` | Part A event on a held or candidate name | Trim or exit review within the next quarter, not on the print: in sample, the penalty built from day 60 to day 252 (research note). Stronger for micro caps |
| `holder_block_sale` | B1 event (10% owner or officer discretionary sale in run state) | Same as above, with the seller named |
| `financing_likely` | Either of the above plus a live shelf or ATM | Feeds P1 (financing within 90 days) and the H1 dilution score |
| `opportunistic_insider_buy` | B2 event by an officer or director, not offering participation | Entry checklist item; never sufficient alone |
| `specialist_conviction` | Skill-weighted net new positions from the panel | H4 score; tie-breaker inside names that pass the gates |

## 7. Runbook (local machine)

```
export SEC_USER_AGENT="Your Name your@email"
python scripts/ownership_flow.py fetch --quarters 2020q1 2026q2
python scripts/ownership_flow.py insider data/raw/sec_ownership/*_form345.zip --financing financings.csv
python scripts/ownership_flow.py study --period in_sample
python scripts/ownership_flow.py funds data/raw/sec_ownership/*13f*.zip --cusip-map cusips.csv
python scripts/supply_after_run.py --period in_sample --variants
```

## 8. Tests

`tests/test_supply.py` (run state, supply rule, split adjustment, delisting freeze, matching,
bootstrap, Holm) and `tests/test_ownership_flow.py` (data set join, joint filers, classes, plan
flag, offering participation, routine flags, Form 4 and Form 144 XML, 13F amendments and
changes, fund skill). Fixtures in `tests/fixtures/sec_ownership/` are hand-written in the SEC
layouts until a trimmed real quarter replaces them (Q-050).
