"""Specialist fund flow from 13F: position changes, issuer aggregates and point-in-time fund skill
(H4, H18 part B5 and B6).

"Follow the good biotech funds" needs two things the raw 13F does not give:

1. **Changes, not levels.** A fund that has held a name for five years says little this quarter;
   a new position, a doubled one or an exit does. `position_changes` diffs consecutive quarters
   per fund and CUSIP. `available_at` is the 13F filing date, up to 45 days after quarter end, so
   any signal is at least that stale. Options rows (puts and calls) are kept apart.
2. **A measured definition of "good".** Reputation is survivorship-biased: the funds we call good
   are the ones that survived. `fund_skill` scores each fund only on the realized outcomes of its
   *earlier* new positions (BHAR over the two quarters after each 13F filing date, measured only
   once that window has closed before the as-of date), shrunk toward zero with a normal-normal
   model so that a fund with three lucky picks does not top the table.

13F limits that no code fixes: long positions only (no shorts, so a specialist's "long" may be one
leg of a pair), quarter-end snapshots (intra-quarter round trips are invisible), a 45-day delay,
and confidential treatment for some positions. 13D and 13G amendments (5% holders) are timelier
for the largest stakes.
"""

from __future__ import annotations

import math
import re
from collections import defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import date

from biotech_divedeep.connectors.sec_ownership import Holding13F


def latest_positions(holdings: Iterable[Holding13F]) -> dict[tuple[str, date], dict[str, tuple[float, date]]]:
    """(filer, period) -> CUSIP -> (shares, available_at) for stock rows, after amendments.

    A RESTATEMENT amendment replaces the filer's whole report for that period (its filing date
    becomes `available_at`); a NEW HOLDINGS amendment adds rows. Originals filed later than an
    earlier original for the same period replace it as well.
    """
    by_report: dict[tuple[str, date], dict[str, list[Holding13F]]] = defaultdict(lambda: defaultdict(list))
    for h in holdings:
        if h.period is None or h.put_call:
            continue
        by_report[(h.filer_cik, h.period)][h.accession].append(h)
    out: dict[tuple[str, date], dict[str, tuple[float, date]]] = {}
    for key, filings in by_report.items():
        ordered = sorted(filings.values(), key=lambda rows: (rows[0].available_at, rows[0].accession))
        pos: dict[str, tuple[float, date]] = {}
        for rows in ordered:
            kind = rows[0].amendment_type
            if kind != "NEW HOLDINGS":
                pos = {}
            agg: dict[str, float] = defaultdict(float)
            for h in rows:
                agg[h.cusip] += h.shares or 0.0
            for cusip, sh in agg.items():
                pos[cusip] = (sh, rows[0].available_at)
        out[key] = pos
    return out


@dataclass(frozen=True)
class PositionChange:
    filer_cik: str
    cusip: str
    period: date
    available_at: date
    kind: str  # new, add, trim, exit, hold
    shares_prev: float
    shares_now: float

    @property
    def change(self) -> float | None:
        return self.shares_now / self.shares_prev - 1.0 if self.shares_prev > 0 else None


def _quarters_apart(a: date, b: date) -> int:
    return (b.year - a.year) * 4 + (b.month - 1) // 3 - (a.month - 1) // 3


def position_changes(
    positions: dict[tuple[str, date], dict[str, tuple[float, date]]], add_trim: float = 0.25
) -> list[PositionChange]:
    """Quarter-over-quarter changes per filer and CUSIP. Only consecutive quarters are compared;
    a skipped report breaks the chain. `add_trim` is the relative change that counts as add or
    trim (25% by default); smaller moves are `hold`."""
    by_filer: dict[str, list[date]] = defaultdict(list)
    for filer, period in positions:
        by_filer[filer].append(period)
    out: list[PositionChange] = []
    for filer, periods in by_filer.items():
        periods.sort()
        for prev, cur in zip(periods, periods[1:], strict=False):
            if _quarters_apart(prev, cur) != 1:
                continue
            p, c = positions[(filer, prev)], positions[(filer, cur)]
            avail = max((a for _, a in c.values()), default=None)
            if avail is None:
                continue
            for cusip in set(p) | set(c):
                sp = p.get(cusip, (0.0, avail))[0]
                sc, a = c.get(cusip, (0.0, avail))
                if sp <= 0 and sc > 0:
                    kind = "new"
                elif sp > 0 and sc <= 0:
                    kind = "exit"
                elif sp > 0 and sc / sp - 1.0 >= add_trim:
                    kind = "add"
                elif sp > 0 and sc / sp - 1.0 <= -add_trim:
                    kind = "trim"
                else:
                    kind = "hold"
                out.append(PositionChange(filer, cusip, cur, a if sc > 0 else avail, kind, sp, sc))
    out.sort(key=lambda x: (x.available_at, x.cusip, x.filer_cik))
    return out


@dataclass(frozen=True)
class IssuerQuarter:
    cusip: str
    period: date
    available_at: date  # latest filing date among the funds counted (conservative)
    holders: int
    new: int
    exits: int
    adds: int
    trims: int
    shares: float

    @property
    def net_buyers(self) -> int:
        return self.new + self.adds - self.exits - self.trims


def issuer_quarters(changes: Iterable[PositionChange], funds: set[str]) -> list[IssuerQuarter]:
    """Aggregate the changes of the `funds` (filer CIKs) per CUSIP and quarter."""
    acc: dict[tuple[str, date], list[PositionChange]] = defaultdict(list)
    for ch in changes:
        if ch.filer_cik in funds:
            acc[(ch.cusip, ch.period)].append(ch)
    out = []
    for (cusip, period), chs in acc.items():
        out.append(
            IssuerQuarter(
                cusip=cusip,
                period=period,
                available_at=max(c.available_at for c in chs),
                holders=sum(c.shares_now > 0 for c in chs),
                new=sum(c.kind == "new" for c in chs),
                exits=sum(c.kind == "exit" for c in chs),
                adds=sum(c.kind == "add" for c in chs),
                trims=sum(c.kind == "trim" for c in chs),
                shares=sum(c.shares_now for c in chs),
            )
        )
    out.sort(key=lambda x: (x.period, x.cusip))
    return out


@dataclass(frozen=True)
class Skill:
    mean: float  # posterior mean of the fund's average 2-quarter BHAR on new positions
    sd: float
    n: int
    raw_mean: float | None


def fund_skill(
    outcomes: Sequence[tuple[date, float]],
    as_of: date,
    prior_mean: float = 0.0,
    prior_sd: float = 0.05,
    obs_sd: float = 0.5,
) -> Skill:
    """Normal-normal posterior of a fund's skill from outcomes realized strictly before `as_of`.

    `outcomes` are (realized_on, bhar) pairs: realized_on is the date the measurement window
    closed. `prior_sd` (5 points of 2-quarter BHAR) says most funds are close to zero skill;
    `obs_sd` (50 points) is the spread of single-name small-cap biotech outcomes. With these
    values a fund needs about 100 new positions before its own record outweighs the prior.
    """
    xs = [x for d, x in outcomes if d < as_of]
    n = len(xs)
    if n == 0:
        return Skill(prior_mean, prior_sd, 0, None)
    prec = 1.0 / prior_sd**2 + n / obs_sd**2
    mean = (prior_mean / prior_sd**2 + sum(xs) / obs_sd**2) / prec
    return Skill(mean, math.sqrt(1.0 / prec), n, sum(xs) / n)


def terciles(scores: dict[str, float]) -> dict[str, str]:
    """`top`, `middle`, `bottom` by score (ties broken by key for determinism)."""
    order = sorted(scores, key=lambda k: (scores[k], k))
    n = len(order)
    out = {}
    for i, k in enumerate(order):
        out[k] = "bottom" if i < n / 3 else ("middle" if i < 2 * n / 3 else "top")
    return out


_SUFFIX = re.compile(
    r"\b(INC|INCORPORATED|CORP|CORPORATION|CO|COMPANY|LTD|LIMITED|PLC|NV|N V|SA|AG|SE|LLC|LP|HOLDINGS?|"
    r"GROUP|COM|NEW|CL A|CLASS A|ORD|SHS|ADR|SPONSORED ADR|THE)\b"
)


def normalize_issuer(name: str) -> str:
    """Upper case, punctuation dropped, legal suffixes removed: for matching 13F issuer names to
    the universe when no CUSIP map is available. Matches are `unverified` until checked."""
    t = re.sub(r"[^A-Z0-9 ]", " ", name.upper())
    t = _SUFFIX.sub(" ", t)
    return " ".join(t.split())
