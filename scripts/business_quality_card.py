"""Print the numeric part of the business quality card for one or more tickers.

Usage: python scripts/business_quality_card.py HROW MRLN [--as-of 2026-10-08]

Reads the ledgers in data/reference/ (product_revenue_map, guidance_ledger, costly_signal_ledger,
deal_ledger, business_quality_scorecard) and prints: revenue concentration and protection-weighted
life (lens A), revenue share by moat grade (lens B), the business model grade with its blocking
reasons (lens C), guidance credibility, costly-signal score and deal multiples (lens D), and the
cap on any scenario that assumes guidance is met. Judgments stay in the CSVs and the memos; this
script only does the arithmetic so it can be re-run every quarter.
"""

from __future__ import annotations

import argparse
import csv
from datetime import date
from pathlib import Path

from biotech_divedeep.models.business_quality import (
    business_model_grade,
    costly_signal_score,
    deal_multiple,
    guidance_credibility,
    guidance_scenario_cap,
    load_guides,
    load_product_map,
    load_scorecard,
    load_signals,
    people_grade,
    protection_weighted_life,
    revenue_concentration,
)

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "data" / "reference"

# Inputs the ledgers do not hold yet (A/U, see the business quality notes in docs/research/).
# Candor flags: HROW auditor change and late FY2024 10-K; MRLN anonymous culture complaints (B6).
CANDOR_FLAGS = {"HROW": 1, "MRLN": 1}
ALIGNED = {"HROW": True, "MRLN": True}  # open-market CEO purchase (HROW); founder holds about 11.5% (MRLN)
REVENUE_TO_OPEX = {"MRLN": 2.2 / 30.0}  # Q2 2026 revenue over an approximate quarterly cash cost base


def card(ticker: str, as_of: date) -> None:
    print(f"\n=== {ticker} business quality card (as of {as_of}) ===")
    lines = [
        r for r in load_product_map(REF / "product_revenue_map.csv", ticker) if r["line_type"] != "software_licence"
    ]
    revenue = {r["line"]: float(r["revenue_usd_m"]) for r in lines}
    total = sum(revenue.values())
    wide_share = 0.0
    if total > 0:
        conc = revenue_concentration(revenue)
        life = protection_weighted_life(
            [
                (float(r["revenue_usd_m"]), date.fromisoformat(r["protection_end"]) if r["protection_end"] else None)
                for r in lines
            ],
            as_of,
        )
        by_grade: dict[str, float] = {}
        for r in lines:
            by_grade[r["moat_grade"]] = by_grade.get(r["moat_grade"], 0.0) + float(r["revenue_usd_m"]) / total
        wide_share = by_grade.get("wide", 0.0)
        print(f"A  revenue in period {total:.1f}M; HHI {conc.hhi:.3f}; top line {conc.top_name} {conc.top_share:.0%}")
        print(f"A  protection-weighted life {life:.1f} years")
        print("B  revenue share by moat grade: " + ", ".join(f"{k} {v:.0%}" for k, v in sorted(by_grade.items())))

    grade = business_model_grade(
        load_scorecard(REF / "business_quality_scorecard.csv", ticker), wide_share, REVENUE_TO_OPEX.get(ticker)
    )
    print(f"C  business model: {grade.grade} (sum {grade.total} over {grade.scored} scored, {grade.zeros} at zero)")
    for reason in grade.reasons:
        print(f"     - {reason}")

    cred = guidance_credibility(load_guides(REF / "guidance_ledger.csv", ticker))
    lo, hi = cred.interval
    mse = "n/a" if cred.mean_signed_error is None else f"{cred.mean_signed_error:+.1%}"
    print(
        f"D1 guidance: {cred.hits}/{cred.resolved} hit, {cred.pending} pending; posterior {cred.mean:.2f} "
        f"(80% CI {lo:.2f}-{hi:.2f}); mean signed error {mse}"
    )
    sig = costly_signal_score(load_signals(REF / "costly_signal_ledger.csv", ticker))
    print(
        f"D4 costly signals: {sig.pre_committed} pre-committed ({sig.resolved} resolved, {sig.pending} pending), "
        f"{sig.unqualified} unqualified, {sig.post_hoc} post hoc, {sig.short_termist} short-termist"
    )

    with open(REF / "deal_ledger.csv", newline="") as fh:
        for d in csv.DictReader(fh):
            if d["ticker"] != ticker or d["deal_type"] == "financing" or not d["revenue_after_usd_m"]:
                continue
            paid = sum(float(d[k]) for k in ("paid_upfront_usd_m", "milestones_max_usd_m") if d[k])
            mult = deal_multiple(float(d["revenue_after_usd_m"]), paid)
            print(
                f"D2 deal {d['deal_id']} {d['asset'][:40]}: "
                f"{mult:.2f}x revenue ({d['revenue_after_period']}) per dollar paid"
            )

    pg = people_grade(cred, CANDOR_FLAGS.get(ticker, 0), ALIGNED.get(ticker), sig.paid_off_credit)
    print(f"D  people grade: {pg}")
    if cred.resolved >= 3:
        print(f"-> cap on any scenario that assumes guidance is met: {guidance_scenario_cap(cred):.0%}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("tickers", nargs="+")
    parser.add_argument("--as-of", default=date.today().isoformat())
    args = parser.parse_args()
    for t in args.tickers:
        card(t.upper(), date.fromisoformat(args.as_of))


if __name__ == "__main__":
    main()
