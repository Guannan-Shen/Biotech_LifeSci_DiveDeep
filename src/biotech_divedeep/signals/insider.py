"""Insider and 10%-holder trades from Form 4: what is a signal and what is plumbing (H18 part B).

Most Form 4 lines carry no view on value: grants, option exercises, tax withholding, gifts, plan
sales, and, in small biotech above all, funds buying in the company's own financing. This module
sorts every line into a class, flags routine traders, and clusters the discretionary lines into
events that an event study (`signals/supply.py` machinery) can measure.

Classes (`classify`):

- `open_market_buy`: code P outside any financing window and not part of a group buy.
- `offering_participation`: code P within `window_days` of a known financing (424B, 8-K item
  3.02), or two or more filings buying on the same date at the same price with a 10% owner
  among them (the fingerprint of a registered direct, PIPE or underwritten offering).
- `open_market_sale`: code S without a Rule 10b5-1 flag. `plan_sale`: code S under a plan
  (checkbox from 2023, footnote text before).
- `tax_withholding` (F), `grant` (A), `exercise` (M, X, C), `gift` (G), `to_issuer` (D).
- `distribution`: code J disposals, mostly in-kind distributions by venture funds to their
  partners, which put stock in hands that tend to sell (supply, not information).
- `other`: everything else.

Routine vs opportunistic (Cohen, Malloy and Pomorski 2012): an insider with open-market trades in
each of the three prior calendar years is `routine` if every one of those years has a trade in
the same calendar month as the current trade, otherwise `opportunistic`; insiders with a shorter
history are `unclassified`. The three-year look-back uses filing dates before the current trade
only.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from datetime import date, timedelta

from biotech_divedeep.connectors.sec_ownership import InsiderTxn

DISCRETIONARY = {"open_market_buy", "open_market_sale"}
_CODE_CLASS = {
    "F": "tax_withholding",
    "A": "grant",
    "M": "exercise",
    "X": "exercise",
    "C": "exercise",
    "G": "gift",
    "D": "to_issuer",
}


def role(t: InsiderTxn) -> str:
    """Most senior role on the filing: `ceo_cfo`, `officer`, `director`, `ten_pct_owner`, `other`."""
    title = t.officer_title.lower()
    if t.is_officer and any(k in title for k in ("chief executive", "ceo", "chief financial", "cfo", "president")):
        return "ceo_cfo"
    if t.is_officer:
        return "officer"
    if t.is_director:
        return "director"
    if t.is_ten_pct:
        return "ten_pct_owner"
    return "other"


def collapse_joint_filers(txns: Iterable[InsiderTxn]) -> list[InsiderTxn]:
    """One line per (accession, transaction): a fund, its adviser and its managing members often
    file jointly and each appear as a reporting owner of the same shares."""
    seen: set[tuple] = set()
    out: list[InsiderTxn] = []
    for t in txns:
        key = (t.accession, t.trans_date, t.code, t.shares, t.price, t.acq_disp, t.shares_after)
        if key in seen:
            continue
        seen.add(key)
        out.append(t)
    return out


def group_buy_keys(txns: Sequence[InsiderTxn], min_groups: int = 2) -> set[tuple[str, date, float]]:
    """(issuer, date, price) where several filings bought at one price with a 10% owner among them:
    the fingerprint of a registered direct, PIPE or underwritten offering."""
    groups: dict[tuple[str, date, float], set[str]] = defaultdict(set)
    ten: dict[tuple[str, date, float], bool] = defaultdict(bool)
    for t in txns:
        if t.code != "P" or t.trans_date is None or t.price is None:
            continue
        k = (t.issuer_cik, t.trans_date, round(t.price, 4))
        groups[k].add(t.accession)
        ten[k] = ten[k] or t.is_ten_pct
    return {k for k, accs in groups.items() if len(accs) >= min_groups and ten[k]}


def classify(
    t: InsiderTxn,
    financing_dates: Iterable[date] = (),
    group_keys: set[tuple[str, date, float]] | None = None,
    window_days: int = 7,
) -> str:
    code = t.code
    if code == "P":
        td = t.trans_date
        if td is not None and any(abs((td - f).days) <= window_days for f in financing_dates):
            return "offering_participation"
        key = (t.issuer_cik, td, round(t.price, 4)) if td is not None and t.price is not None else None
        if group_keys and key in group_keys:
            return "offering_participation"
        return "open_market_buy"
    if code == "S":
        return "plan_sale" if t.plan_10b5_1 else "open_market_sale"
    if code == "J":
        return "distribution" if t.acq_disp == "D" else "other"
    return _CODE_CLASS.get(code, "other")


def routine_flags(txns: Sequence[InsiderTxn]) -> dict[tuple[str, str], str]:
    """`routine`, `opportunistic` or `unclassified` for each (accession, owner_cik) open-market trade.

    History counts open-market P and S trades (plan sales included: they are routine by
    construction) by the same owner across all issuers, known by filing date before the trade.
    """
    hist: dict[str, list[tuple[date, date]]] = defaultdict(list)  # owner -> (available_at, trade date)
    for t in txns:
        if t.code in {"P", "S"} and t.trans_date is not None:
            hist[t.owner_cik].append((t.available_at, t.trans_date))
    out: dict[tuple[str, str], str] = {}
    for t in txns:
        if t.code not in {"P", "S"} or t.trans_date is None:
            continue
        y, m = t.trans_date.year, t.trans_date.month
        prior = [d for avail, d in hist[t.owner_cik] if avail < t.available_at and d.year < y]
        years = {d.year for d in prior}
        if not all(y - k in years for k in (1, 2, 3)):
            out[(t.accession, t.owner_cik)] = "unclassified"
            continue
        same_month = {d.year for d in prior if d.month == m}
        routine = all(y - k in same_month for k in (1, 2, 3))
        out[(t.accession, t.owner_cik)] = "routine" if routine else "opportunistic"
    return out


def stake_fraction(t: InsiderTxn) -> float | None:
    """Shares sold as a fraction of the pre-sale holding (S and other disposals)."""
    if t.shares is None or t.shares_after is None or t.acq_disp != "D":
        return None
    before = t.shares_after + t.shares
    return t.shares / before if before > 0 else None


@dataclass
class FlowEvent:
    """A cluster of discretionary trades in one issuer and one direction."""

    issuer_cik: str
    ticker: str
    direction: str  # buy or sell
    trigger_date: date  # filing date on which the cluster crossed the size floor
    first_trade: date
    value_usd: float
    n_insiders: int
    roles: tuple[str, ...]
    any_ten_pct: bool
    opportunistic_share: float | None
    max_stake_fraction: float | None
    accessions: tuple[str, ...] = field(default_factory=tuple)


def cluster_events(
    txns: Sequence[InsiderTxn],
    classes: dict[tuple, str],
    routine: dict[tuple[str, str], str],
    gap_days: int = 14,
    min_value: float = 250_000.0,
    min_stake: float = 0.05,
) -> list[FlowEvent]:
    """Cluster discretionary lines per issuer and direction; a cluster closes after `gap_days`
    calendar days without a new filing. The event fires on the filing date at which cumulative
    value reaches `min_value` (sales also need one seller to have sold at least `min_stake` of
    the holding). `classes` maps `line_key` to the class (`classify_all`).

    Known limitation: affiliated funds that file separate Form 4s for open-market buys at one
    weighted-average price look like a group buy; known financing dates are the primary route."""
    lines = [t for t in txns if classes.get(line_key(t)) in DISCRETIONARY]
    lines.sort(key=lambda t: (t.issuer_cik, t.available_at))
    out: list[FlowEvent] = []
    by_issuer: dict[tuple[str, str], list[InsiderTxn]] = defaultdict(list)
    for t in lines:
        direction = "buy" if classes[line_key(t)] == "open_market_buy" else "sell"
        by_issuer[(t.issuer_cik, direction)].append(t)
    for (cik, direction), ts in by_issuer.items():
        clusters: list[list[InsiderTxn]] = []
        for t in ts:
            if clusters and (t.available_at - clusters[-1][-1].available_at) <= timedelta(days=gap_days):
                clusters[-1].append(t)
            else:
                clusters.append([t])
        for cl in clusters:
            total, trigger = 0.0, None
            stake_ok = direction == "buy"
            for t in cl:
                total += t.value or 0.0
                sf = stake_fraction(t)
                stake_ok = stake_ok or (sf is not None and sf >= min_stake)
                if trigger is None and total >= min_value and stake_ok:
                    trigger = t.available_at
            if trigger is None:
                continue
            flags = [routine.get((t.accession, t.owner_cik), "unclassified") for t in cl]
            known = [f for f in flags if f != "unclassified"]
            stakes = [s for t in cl if (s := stake_fraction(t)) is not None]
            out.append(
                FlowEvent(
                    issuer_cik=cik,
                    ticker=cl[0].ticker,
                    direction=direction,
                    trigger_date=trigger,
                    first_trade=min(t.trans_date or t.available_at for t in cl),
                    value_usd=total,
                    n_insiders=len({t.owner_cik for t in cl}),
                    roles=tuple(sorted({role(t) for t in cl})),
                    any_ten_pct=any(t.is_ten_pct for t in cl),
                    opportunistic_share=(sum(f == "opportunistic" for f in known) / len(known)) if known else None,
                    max_stake_fraction=max(stakes) if stakes else None,
                    accessions=tuple(sorted({t.accession for t in cl})),
                )
            )
    out.sort(key=lambda e: (e.trigger_date, e.ticker))
    return out


def line_key(t: InsiderTxn) -> tuple:
    return (t.accession, t.trans_date, t.code, t.shares, t.price, t.owner_cik)


def classify_all(
    txns: Sequence[InsiderTxn], financing: dict[str, list[date]] | None = None
) -> dict[tuple, str]:
    """Class for every line; `financing` maps issuer CIK to known financing dates."""
    keys = group_buy_keys(txns)
    fin = financing or {}
    return {line_key(t): classify(t, fin.get(t.issuer_cik, ()), keys) for t in txns}
