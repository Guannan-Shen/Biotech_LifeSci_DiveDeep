"""H18 part B and H4 on the local machine: Form 4 and 13F data sets to events, events to returns.

sec.gov does not resolve from the cloud sandbox, so this runs where SEC is reachable. Steps:

1. fetch: quarterly SEC Insider Transactions Data Sets (and, if given, 13F data set URLs) into
   `data/raw/sec_ownership/` (needs SEC_USER_AGENT with a name and email; at most a few requests).
2. insider: parse, collapse joint filers, classify each line, flag routine traders, cluster the
   discretionary lines into buy and sell events for tickers in the research universe.
   Writes `data/silver/ownership/insider_lines.csv.gz` and `insider_events.csv`.
3. study: measure the events with `signals/supply.py` (run-matched controls, BHAR vs
   `EW_LIFESCI_200M`) for the pre-registered cells B1 to B3, one period at a time.
4. funds: 13F data sets to position changes, specialist issuer-quarters and fund skill.

Pre-registration: `notes/backtests/2026-10-12_H18_insider_and_holder_flow.md`.

Usage:
    export SEC_USER_AGENT="Your Name your@email"
    python scripts/ownership_flow.py fetch --quarters 2020q1 2026q2
    python scripts/ownership_flow.py insider data/raw/sec_ownership/*_form345.zip [--financing f.csv]
    python scripts/ownership_flow.py study --period in_sample
    python scripts/ownership_flow.py funds data/raw/sec_ownership/*13f*.zip --cusip-map cusips.csv
"""

from __future__ import annotations

import argparse
import csv
import gzip
import os
import sys
import time
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from biotech_divedeep.connectors.sec_ownership import read_13f_dataset, read_insider_dataset  # noqa: E402
from biotech_divedeep.signals.fund_flow import (  # noqa: E402
    issuer_quarters,
    latest_positions,
    normalize_issuer,
    position_changes,
)
from biotech_divedeep.signals.insider import (  # noqa: E402
    classify_all,
    cluster_events,
    collapse_joint_filers,
    line_key,
    role,
    routine_flags,
)

RAW = ROOT / "data" / "raw" / "sec_ownership"
SILVER = ROOT / "data" / "silver" / "ownership"
UNIVERSE = ROOT / "data" / "reference" / "us_lifesci_universe.csv"
INSIDER_URL = "https://www.sec.gov/files/structureddata/data/insider-transactions-data-sets/{q}_form345.zip"


def quarters(a: str, b: str) -> list[str]:
    ya, qa = int(a[:4]), int(a[-1])
    yb, qb = int(b[:4]), int(b[-1])
    out = []
    while (ya, qa) <= (yb, qb):
        out.append(f"{ya}q{qa}")
        ya, qa = (ya + 1, 1) if qa == 4 else (ya, qa + 1)
    return out


def cmd_fetch(args: argparse.Namespace) -> None:
    import httpx

    ua = os.environ.get("SEC_USER_AGENT", "")
    if "@" not in ua:
        sys.exit("SEC_USER_AGENT must hold a name and an email (SEC rejects anonymous clients)")
    RAW.mkdir(parents=True, exist_ok=True)
    urls = [INSIDER_URL.format(q=q) for q in quarters(*args.quarters)] + list(args.url or [])
    with httpx.Client(headers={"User-Agent": ua}, timeout=120, follow_redirects=True) as client:
        for url in urls:
            dest = RAW / url.rsplit("/", 1)[-1]
            if dest.exists():
                continue
            r = client.get(url)
            if r.status_code != 200:
                print(f"{r.status_code} {url}")
                continue
            dest.write_bytes(r.content)
            print(f"saved {dest.name} ({len(r.content) / 1e6:.1f} MB)")
            time.sleep(0.5)  # well under SEC's 10 requests per second


def universe_tickers(path: Path) -> set[str]:
    keep = {"therapeutics", "tools", "diagnostics"}
    with open(path, newline="") as fh:
        return {r["symbol"].upper() for r in csv.DictReader(fh) if r["layer"] in keep}


def load_financing(path: Path | None) -> dict[str, list[date]]:
    """Optional CSV with issuer_cik,date of known financings (424B5, 8-K item 3.02)."""
    out: dict[str, list[date]] = defaultdict(list)
    if path is None:
        return out
    with open(path, newline="") as fh:
        for r in csv.DictReader(fh):
            out[r["issuer_cik"].lstrip("0")].append(date.fromisoformat(r["date"]))
    return out


def cmd_insider(args: argparse.Namespace) -> None:
    tickers = universe_tickers(args.universe)
    lines = []
    for z in args.zips:
        rows = [t for t in read_insider_dataset(Path(z)) if t.ticker in tickers]
        lines.extend(rows)
        print(f"{Path(z).name}: {len(rows)} universe lines")
    lines = collapse_joint_filers(lines)
    classes = classify_all(lines, load_financing(args.financing))
    routine = routine_flags(lines)
    SILVER.mkdir(parents=True, exist_ok=True)
    with gzip.open(SILVER / "insider_lines.csv.gz", "wt", newline="") as fh:
        w = csv.writer(fh)
        w.writerow([
            "available_at", "trans_date", "ticker", "issuer_cik", "owner_cik", "owner_name", "role", "ten_pct",
            "code", "class", "routine", "shares", "price", "value_usd", "shares_after", "plan_10b5_1", "accession",
        ])
        for t in lines:
            w.writerow([
                t.available_at, t.trans_date, t.ticker, t.issuer_cik, t.owner_cik, t.owner_name, role(t), t.is_ten_pct,
                t.code, classes[line_key(t)], routine.get((t.accession, t.owner_cik), ""), t.shares, t.price,
                t.value, t.shares_after, t.plan_10b5_1, t.accession,
            ])
    events = cluster_events(lines, classes, routine, min_value=args.min_value, min_stake=args.min_stake)
    with open(SILVER / "insider_events.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow([
            "trigger_date", "ticker", "issuer_cik", "direction", "first_trade", "value_usd", "n_insiders", "roles",
            "any_ten_pct", "opportunistic_share", "max_stake_fraction", "accessions",
        ])
        for e in events:
            w.writerow([
                e.trigger_date, e.ticker, e.issuer_cik, e.direction, e.first_trade, round(e.value_usd), e.n_insiders,
                " ".join(e.roles), e.any_ten_pct, e.opportunistic_share, e.max_stake_fraction, " ".join(e.accessions),
            ])
    counts: dict[str, int] = defaultdict(int)
    for c in classes.values():
        counts[c] += 1
    print("line classes:", dict(sorted(counts.items(), key=lambda x: -x[1])))
    print(f"{len(events)} events -> {SILVER / 'insider_events.csv'}")


def cmd_study(args: argparse.Namespace) -> None:
    import supply_after_run as A

    from biotech_divedeep.signals.supply import Segment, SupplyParams, day_states, match_events

    bench = A.load_bench(A.BENCH_FILE)
    calendar = sorted(bench)
    p = SupplyParams()
    segments = A.load_segments(A.SILVER, calendar, bench, p)
    segments = [Segment(s.symbol, s.layer, s.series, s.caps, day_states(s.series, s.caps, p)) for s in segments]
    with open(SILVER / "insider_events.csv", newline="") as fh:
        rows = list(csv.DictReader(fh))
    lo, hi = A.PERIODS[args.period]

    def pick(pred) -> list[tuple[str, date]]:
        out = []
        for r in rows:
            d = date.fromisoformat(r["trigger_date"])
            if lo <= d <= hi and pred(r):
                out.append((r["ticker"], d))
        return out

    def opp(r: dict) -> float | None:
        return float(r["opportunistic_share"]) if r["opportunistic_share"] not in ("", "None") else None

    def sell(r: dict) -> bool:
        return r["direction"] == "sell"

    def buy(r: dict) -> bool:
        return r["direction"] == "buy"

    cells = {
        "B1 sells in run state": (pick(sell), True),
        "B1 sells, 10% owner in cluster": (pick(lambda r: sell(r) and r["any_ten_pct"] == "True"), True),
        "B2 buys, opportunistic": (pick(lambda r: buy(r) and (opp(r) or 0) >= 0.5), False),
        "B2 buys, routine": (pick(lambda r: buy(r) and opp(r) is not None and opp(r) < 0.5), False),
        "B3 cluster buys (3+ insiders)": (pick(lambda r: buy(r) and int(r["n_insiders"]) >= 3), False),
        "B3 single-insider buys": (pick(lambda r: buy(r) and int(r["n_insiders"]) == 1), False),
    }
    print(f"| cell ({args.period}) | n | event BHAR 126 | matched diff 126 | 90% interval | BHAR 252 | diff 252 |")
    print("|---|---|---|---|---|---|---|")
    for name, (dated, need_run) in cells.items():
        matched = match_events(segments, calendar, bench, p, A.HORIZONS, dated=dated, require_run=need_run)
        ev = [e for e in matched if e.controls]
        s126, s252 = A.summarize(ev, 126), A.summarize(ev, 252)
        print(
            f"| {name} | {s126['n']} | {A.pct(s126['event_mean'])} | {A.pct(s126['diff_mean'])} | "
            f"{A.pct(s126['diff_lo'])} to {A.pct(s126['diff_hi'])} | {A.pct(s252['event_mean'])} | "
            f"{A.pct(s252['diff_mean'])} |"
        )


def cmd_funds(args: argparse.Namespace) -> None:
    import yaml

    cfg = yaml.safe_load(open(args.funds))
    ciks = {str(f["cik"]).lstrip("0") for f in cfg["funds"] if f.get("cik")}
    if not ciks:
        sys.exit("no fund CIKs in the config yet: resolve them on EDGAR and set `cik` first")
    holdings = []
    for z in args.zips:
        holdings.extend(read_13f_dataset(Path(z), ciks))
    cusip_to_ticker: dict[str, str] = {}
    if args.cusip_map:
        with open(args.cusip_map, newline="") as fh:
            cusip_to_ticker = {r["cusip"].upper(): r["ticker"].upper() for r in csv.DictReader(fh)}
    name_to_ticker: dict[str, str] = {}
    with open(args.universe, newline="") as fh:
        for r in csv.DictReader(fh):
            name_to_ticker.setdefault(normalize_issuer(r["name"].replace("Common Stock", "")), r["symbol"])
    cusip_names = {h.cusip: h.issuer_name for h in holdings}
    changes = position_changes(latest_positions(holdings))
    quarters_ = issuer_quarters(changes, ciks)
    SILVER.mkdir(parents=True, exist_ok=True)
    with open(SILVER / "specialist_issuer_quarters.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["period", "available_at", "cusip", "ticker", "ticker_source", "issuer_name", "holders", "new",
                    "adds", "trims", "exits", "net_buyers", "shares"])
        for q in quarters_:
            tk = cusip_to_ticker.get(q.cusip)
            src = "cusip_map" if tk else ""
            if not tk:
                tk = name_to_ticker.get(normalize_issuer(cusip_names.get(q.cusip, "")), "")
                src = "name_match_unverified" if tk else ""
            w.writerow([q.period, q.available_at, q.cusip, tk, src, cusip_names.get(q.cusip, ""), q.holders, q.new,
                        q.adds, q.trims, q.exits, q.net_buyers, round(q.shares)])
    with open(SILVER / "specialist_position_changes.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["available_at", "period", "filer_cik", "cusip", "kind", "shares_prev", "shares_now"])
        for c in changes:
            w.writerow([c.available_at, c.period, c.filer_cik, c.cusip, c.kind, c.shares_prev, c.shares_now])
    print(f"{len(holdings)} holdings, {len(changes)} changes, {len(quarters_)} issuer-quarters -> {SILVER}")
    print("Fund skill needs prices per new position: run `study`-style BHARs on specialist_position_changes.csv")
    print("with kind == new, then signals.fund_flow.fund_skill per fund and as-of date (B5).")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch")
    f.add_argument("--quarters", nargs=2, default=["2020q1", "2026q2"])
    f.add_argument("--url", nargs="*", help="extra data set URLs, e.g. 13F ZIPs from the SEC data page")
    i = sub.add_parser("insider")
    i.add_argument("zips", nargs="+")
    i.add_argument("--universe", type=Path, default=UNIVERSE)
    i.add_argument("--financing", type=Path)
    i.add_argument("--min-value", type=float, default=250_000.0)
    i.add_argument("--min-stake", type=float, default=0.05)
    s = sub.add_parser("study")
    s.add_argument("--period", choices=["in_sample", "out_of_sample", "holdout"], required=True)
    u = sub.add_parser("funds")
    u.add_argument("zips", nargs="+")
    u.add_argument("--funds", type=Path, default=ROOT / "config" / "specialist_funds.yaml")
    u.add_argument("--cusip-map", type=Path)
    u.add_argument("--universe", type=Path, default=UNIVERSE)
    args = ap.parse_args()
    {"fetch": cmd_fetch, "insider": cmd_insider, "study": cmd_study, "funds": cmd_funds}[args.cmd](args)


if __name__ == "__main__":
    main()
