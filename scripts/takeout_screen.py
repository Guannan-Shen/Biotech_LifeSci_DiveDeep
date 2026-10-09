"""Takeout database summary, takeout score, Phase 2 shrinkage and basket arithmetic (H8, H16).

Usage:
  python scripts/takeout_screen.py summary [--since 2025]
  python scripts/takeout_screen.py score --stage phase2_clean --mcap 1.5 --traits acquirer_gap_area [--premium 0.45]
  python scripts/takeout_screen.py phase2 --estimate 10 --se 4 --prior-mean 3 --prior-sd 4 [--design-effect 10]
  python scripts/takeout_screen.py basket 0.08 0.08 0.05 ...

`summary` describes acquired companies only (selection on the outcome; see the research note
`docs/research/2026-10-08_takeout_database_and_phase2_gate.md` section 3). `score` uses the
own_assumption priors in `config/takeout_priors.yaml` until P5 is fitted.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from biotech_divedeep.models.phase2 import (
    assurance,
    exaggeration_ratio,
    phase3_se_for_power,
    power,
    shrink_effect,
)
from biotech_divedeep.models.takeout import (
    basket_deal_distribution,
    expected_kicker,
    load_deals,
    load_priors,
    score_takeout,
    summarize_deals,
)

ROOT = Path(__file__).resolve().parents[1]
DEALS = ROOT / "data" / "reference" / "biotech_takeouts.csv"
PRIORS = ROOT / "config" / "takeout_priors.yaml"


def _pct(x: float) -> str:
    return f"{100 * x:.0f}%"


def cmd_summary(args: argparse.Namespace) -> None:
    deals = [d for d in load_deals(DEALS) if d.year >= args.since]
    s = summarize_deals(deals)
    sourced = sum(bool(d.source_url) for d in deals)
    print(f"Deals announced since {args.since}: {s.n} (all evidence `unverified`; {sourced} with a source URL)")
    print(f"Lead asset not yet approved: {_pct(s.share_clinical)}")
    print(f"Randomized Phase 2, pivotal or commercial data before the deal: {_pct(s.share_with_phase2_plus_data)}")
    for title, table in (
        ("Stage at deal", s.by_stage),
        ("Data before deal", s.by_key_data),
        ("Acquirer type", s.by_acquirer_type),
        ("Therapeutic area", s.by_area),
        ("Consideration", s.by_consideration),
    ):
        print(f"\n{title}:")
        for key, n in table.items():
            print(f"  {key:<22} {n:>3}  {_pct(n / s.n):>4}")
    if s.premium_last_close:
        q1, med, q3 = s.premium_last_close
        print(f"\nPremium to last close (n={s.premium_n}): median {med:.0f}%, IQR {q1:.0f}% to {q3:.0f}%")
    if s.leakage_gap_median is not None:
        print(f"Median VWAP premium minus last-close premium: {s.leakage_gap_median:+.0f} points")
    if s.equity_value_median_usd_b is not None:
        print(f"Median equity value: USD {s.equity_value_median_usd_b:.1f}B")


def cmd_score(args: argparse.Namespace) -> None:
    priors = load_priors(PRIORS)
    sc = score_takeout(priors, args.stage, args.mcap, args.traits, args.horizon)
    print(f"Likelihood ratio vs base: {sc.likelihood_ratio:.2f}")
    for name, ratio in sc.factors:
        print(f"  {name:<40} x{ratio:.2f}")
    band = f"{_pct(sc.p_low)} / {_pct(sc.p_mid)} / {_pct(sc.p_high)}"
    print(f"Takeout probability over {args.horizon:g} year(s): {band} (low / mid / high base)")
    kicker = 100 * expected_kicker(sc.p_mid, args.premium)
    print(f"Expected kicker at a {_pct(args.premium)} premium to your entry: {kicker:.1f}% (mid)")


def cmd_phase2(args: argparse.Namespace) -> None:
    post = shrink_effect(args.estimate, args.se, args.prior_mean, args.prior_sd)
    design = args.design_effect if args.design_effect else args.estimate
    se3 = phase3_se_for_power(design, args.power)
    print(f"Phase 2 estimate {args.estimate:g} (SE {args.se:g}, z {args.estimate / args.se:.2f})")
    print(f"Shrunk effect: {post.mean:.2f} (SD {post.sd:.2f}); weight on the Phase 2 data {_pct(post.weight_on_data)}")
    print(f"Phase 3 sized for {_pct(args.power)} power at {design:g}: SE {se3:.2f}")
    print(f"  power the sponsor quotes (at {design:g}):     {_pct(power(design, se3))}")
    print(f"  power at the shrunk effect:                {_pct(power(post.mean, se3))}")
    print(f"  assurance (averaged over the posterior):   {_pct(assurance(post, se3))}")
    if post.mean > 0:
        ratio = exaggeration_ratio(post.mean, args.se)
        print(f"Exaggeration of a significant Phase 2 if the truth were {post.mean:.2f}: x{ratio:.2f}")


def cmd_basket(args: argparse.Namespace) -> None:
    pmf = basket_deal_distribution(args.probabilities)
    print(f"Names: {len(args.probabilities)}; expected deals: {sum(args.probabilities):.2f}")
    print(f"P(no deal) {_pct(pmf[0])}; P(at least one) {_pct(1 - pmf[0])}; P(two or more) {_pct(1 - pmf[0] - pmf[1])}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("summary")
    p.add_argument("--since", type=int, default=2019)
    p.set_defaults(func=cmd_summary)
    p = sub.add_parser("score")
    p.add_argument("--stage", required=True)
    p.add_argument("--mcap", type=float, required=True, help="market cap, USD billions")
    p.add_argument("--traits", nargs="*", default=[])
    p.add_argument("--horizon", type=float, default=1.0)
    p.add_argument("--premium", type=float, default=0.45)
    p.set_defaults(func=cmd_score)
    p = sub.add_parser("phase2")
    p.add_argument("--estimate", type=float, required=True)
    p.add_argument("--se", type=float, required=True)
    p.add_argument("--prior-mean", type=float, required=True)
    p.add_argument("--prior-sd", type=float, required=True)
    p.add_argument("--design-effect", type=float)
    p.add_argument("--power", type=float, default=0.9)
    p.set_defaults(func=cmd_phase2)
    p = sub.add_parser("basket")
    p.add_argument("probabilities", type=float, nargs="+")
    p.set_defaults(func=cmd_basket)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
