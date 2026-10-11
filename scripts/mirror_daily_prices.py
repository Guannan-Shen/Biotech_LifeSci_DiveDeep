"""Daily closes, volumes and life-science benchmarks from the screener mirror's git history.

FMP's plan blocks historical prices and the price sites do not resolve from the cloud sandbox,
but the public mirror `rreichel3/US-Stock-Symbols` (D-039) commits the full Nasdaq screener
about once a day since 2021-01-30. Each row carries `lastsale`, `netchange`, `volume` and
`marketCap`, so every snapshot gives that day's close and its one-day return
(`netchange / (lastsale - netchange)`, which the screener computes from the adjusted prior close).

Outputs:
- `data/silver/prices/mirror_daily_lifesci.csv.gz` (git-ignored): one row per life-science
  symbol and trading date (layer from `connectors/listings.py`, point-in-time).
- `--focus-out` (default `data/reference/mirror_daily_focus.csv`): long table for the focus
  tickers plus two benchmark series:
  - `EW_LIFESCI_200M`: equal-weight one-day return of point-in-time therapeutics and tools
    names with prior-day market cap of at least USD 200M (an XBI-like proxy; XBI itself is an
    ETF and is not in the screener). Returns winsorized to [-60%, +150%].
  - `EW_TOOLS`: the same for the tools layer only (the diagnostic tools benchmark, D-006).

Trade dates follow `core.calendar.snapshot_trade_date`. Snapshots that repeat the previous
trading day (weekend and holiday commits) are dropped by fingerprint.

Usage:
    python scripts/mirror_daily_prices.py --repo /path/to/US-Stock-Symbols.git \
        --focus QSI NAUT --since 2021-06-01 [--focus-out data/reference/qsi_naut_daily.csv]
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from biotech_divedeep.connectors.listings import EXCHANGES, classify, load_overrides  # noqa: E402
from biotech_divedeep.core.calendar import snapshot_trade_date  # noqa: E402

MIRROR = "https://github.com/rreichel3/US-Stock-Symbols.git"
OVERRIDES = ROOT / "data" / "reference" / "lifesci_layer_overrides.csv"
SILVER = ROOT / "data" / "silver" / "prices" / "mirror_daily_lifesci.csv.gz"
BENCH_LAYERS = {"therapeutics", "tools"}
BENCH_MIN_CAP = 2e8
WINSOR = (-0.6, 1.5)
MIN_ROWS = 5000


def _num(text: str | None) -> float | None:
    if text is None:
        return None
    t = str(text).replace("$", "").replace(",", "").replace("%", "").strip()
    if not t or t.upper() in {"NA", "N/A"}:
        return None
    try:
        return float(t)
    except ValueError:
        return None


def ensure_repo(repo: Path) -> None:
    if repo.exists():
        return
    subprocess.run(["git", "clone", "-q", "--bare", MIRROR, str(repo)], check=True)


def commits(repo: Path, since: str) -> list[tuple[str, datetime]]:
    path = "nasdaq/nasdaq_full_tickers.json"
    cmd = ["git", "-C", str(repo), "log", "--reverse", "--format=%H %cI", "HEAD", "--", path]
    out = subprocess.run(cmd, check=True, capture_output=True, text=True).stdout
    rows = []
    for line in out.splitlines():
        sha, iso = line.split()
        ts = datetime.fromisoformat(iso)
        if ts.date().isoformat() >= since:
            rows.append((sha, ts))
    return rows


class BlobReader:
    """Streams `sha:path` blobs through one `git cat-file --batch` process."""

    def __init__(self, repo: Path) -> None:
        self.proc = subprocess.Popen(
            ["git", "-C", str(repo), "cat-file", "--batch"], stdin=subprocess.PIPE, stdout=subprocess.PIPE
        )

    def read(self, spec: str) -> bytes | None:
        assert self.proc.stdin and self.proc.stdout
        self.proc.stdin.write(spec.encode() + b"\n")
        self.proc.stdin.flush()
        header = self.proc.stdout.readline().decode().split()
        if len(header) < 3 or header[1] == "missing":
            return None
        size = int(header[2])
        data = self.proc.stdout.read(size)
        self.proc.stdout.read(1)  # trailing newline
        return data

    def close(self) -> None:
        if self.proc.stdin:
            self.proc.stdin.close()
        self.proc.wait()


def one_day_return(last: float | None, change: float | None) -> float | None:
    if last is None or change is None:
        return None
    prev = last - change
    if prev <= 0:
        return None
    return last / prev - 1.0


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--repo", type=Path, required=True)
    p.add_argument("--since", default="2021-06-01")
    p.add_argument("--focus", nargs="+", default=["QSI", "NAUT"])
    p.add_argument("--focus-out", type=Path, default=ROOT / "data" / "reference" / "mirror_daily_focus.csv")
    p.add_argument("--no-silver", action="store_true", help="skip the full life-science silver table")
    args = p.parse_args()

    ensure_repo(args.repo)
    overrides = load_overrides(OVERRIDES)
    focus = {t.upper() for t in args.focus}
    reader = BlobReader(args.repo)
    layer_cache: dict[tuple[str, str, str, str], str] = {}

    focus_rows: list[list] = []
    silver_rows: list[list] = []
    last_fp: tuple | None = None
    last_date: date | None = None
    kept = skipped_dup = skipped_small = 0

    for sha, ts in commits(args.repo, args.since):
        trade = snapshot_trade_date(ts)
        raw: dict[str, list[dict]] = {}
        for ex in EXCHANGES:
            blob = reader.read(f"{sha}:{ex}/{ex}_full_tickers.json")
            try:
                raw[ex] = json.loads(blob) if blob else []
            except json.JSONDecodeError:
                raw[ex] = []
        if sum(len(v) for v in raw.values()) < MIN_ROWS:
            skipped_small += 1
            continue
        fp = tuple((r.get("symbol"), r.get("lastsale"), r.get("pctchange")) for r in raw["nasdaq"][:300])
        if fp == last_fp or (last_date is not None and trade <= last_date):
            skipped_dup += 1
            continue
        last_fp, last_date = fp, trade
        kept += 1

        bench: list[float] = []
        tools: list[float] = []
        seen: set[str] = set()
        for ex in EXCHANGES:
            for row in raw[ex]:
                sym = (row.get("symbol") or "").strip().upper()
                if not sym or sym in seen:
                    continue
                seen.add(sym)
                key = (sym, row.get("name") or "", row.get("industry") or "", row.get("sector") or "")
                layer = layer_cache.get(key)
                if layer is None:
                    layer = classify(row, ex, overrides).layer
                    layer_cache[key] = layer
                is_focus = sym in focus
                if not is_focus and layer not in {"therapeutics", "tools", "diagnostics", "services", "software_data"}:
                    continue
                last = _num(row.get("lastsale"))
                change = _num(row.get("netchange"))
                vol = _num(row.get("volume"))
                cap = _num(row.get("marketCap"))
                r1 = one_day_return(last, change)
                if is_focus:
                    focus_rows.append([trade.isoformat(), sym, last, r1, vol, cap])
                if not args.no_silver:
                    silver_rows.append([trade.isoformat(), sym, layer, last, r1, vol, cap])
                if r1 is None or cap is None or layer not in BENCH_LAYERS:
                    continue
                prior_cap = cap / (1.0 + r1) if r1 > -1.0 else None
                if prior_cap is None or prior_cap < BENCH_MIN_CAP:
                    continue
                rw = min(max(r1, WINSOR[0]), WINSOR[1])
                bench.append(rw)
                if layer == "tools":
                    tools.append(rw)
        for name, vals in (("EW_LIFESCI_200M", bench), ("EW_TOOLS", tools)):
            if vals:
                focus_rows.append([trade.isoformat(), name, None, sum(vals) / len(vals), len(vals), None])
    reader.close()

    args.focus_out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.focus_out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["date", "symbol", "close", "ret_1d", "volume_or_n", "market_cap_usd"])
        for r in focus_rows:
            w.writerow([
                r[0], r[1],
                "" if r[2] is None else f"{r[2]:.4f}",
                "" if r[3] is None else f"{r[3]:.6f}",
                "" if r[4] is None else f"{r[4]:.0f}",
                "" if r[5] is None else f"{r[5]:.0f}",
            ])
    if not args.no_silver:
        SILVER.parent.mkdir(parents=True, exist_ok=True)
        with gzip.open(SILVER, "wt", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["date", "symbol", "layer", "close", "ret_1d", "volume", "market_cap_usd"])
            w.writerows(silver_rows)
    print(f"kept {kept} trading days; dropped {skipped_dup} repeats and {skipped_small} short snapshots")
    print(f"focus rows {len(focus_rows)} -> {args.focus_out}")


if __name__ == "__main__":
    main()
