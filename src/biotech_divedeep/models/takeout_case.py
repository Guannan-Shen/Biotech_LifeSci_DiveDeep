"""Pre-deal case studies: coded signals for targets and matched controls, plus the private process (D-041).

Specification: `docs/framework/takeout_case_study.md`.

Two tables feed this module:

- `data/reference/takeout_case_signals.csv`: one row per public signal per company, for targets
  (`role = case`) and for matched non-targets (`role = control`). Codes come from
  `config/takeout_signals.yaml`. Every row carries `available_at`, so a signal can be placed in a
  window relative to the case's announcement date (controls inherit their case's date).
- `data/reference/takeout_case_process.csv`: one row per deal, coded from the "Background of the
  Offer/Merger" section of the SC 14D9 or merger proxy: first contact, initiator, parties
  contacted, NDAs, bids, price path. This is known only after the deal; it explains the setup but
  never enters a forecast.

The case-control comparison is what turns stories into a likelihood ratio a hazard model can use.
Coding targets alone repeats the choice-based sampling error (Palepu 1986).
"""

from __future__ import annotations

import csv
import statistics
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import yaml

ROLES = {"case", "control"}
PRECISION = {"day", "month", "year"}
INITIATORS = {"buyer", "target", "banker", "activist", "unknown"}

# Windows in days before the announcement (T0). The forecast-relevant span is W1 to W3; W4 holds
# leaks and media reports in the last week, which are reactions, not setup.
WINDOWS: tuple[tuple[str, int, int], ...] = (
    ("W0_before_2y", 731, 100_000),
    ("W1_2y_to_1y", 366, 730),
    ("W2_1y_to_3m", 91, 365),
    ("W3_3m_to_1w", 8, 90),
    ("W4_last_week", 1, 7),
    ("T0_or_after", -100_000, 0),
)
SETUP_WINDOWS = {"W1_2y_to_1y", "W2_1y_to_3m", "W3_3m_to_1w"}


@dataclass(frozen=True)
class SignalDef:
    code: str
    name: str
    direction: str
    lead: str
    public: bool
    source: str
    definition: str


def load_catalog(path: str | Path) -> dict[str, SignalDef]:
    with open(path) as fh:
        raw = yaml.safe_load(fh)
    out = {}
    for code, d in raw["signals"].items():
        if d["direction"] not in {"up", "down", "unclear"}:
            raise ValueError(f"{code}: bad direction")
        out[code] = SignalDef(
            code, d["name"], d["direction"], d["lead"], bool(d["public"]), d["source"], d["definition"]
        )
    return out


@dataclass(frozen=True)
class CaseSignal:
    case_id: str  # the deal_id of the case; controls carry their case's id
    role: str
    ticker: str
    t0: str  # announcement date of the case (controls share it)
    code: str
    available_at: str
    date_precision: str
    description: str
    evidence_class: str
    source_url: str

    @property
    def days_before(self) -> int:
        return (date.fromisoformat(self.t0) - date.fromisoformat(self.available_at)).days

    @property
    def window(self) -> str:
        return window_of(self.days_before)


def window_of(days_before: int) -> str:
    for name, lo, hi in WINDOWS:
        if lo <= days_before <= hi:
            return name
    raise ValueError(days_before)


def load_signals(path: str | Path, catalog: Mapping[str, SignalDef]) -> list[CaseSignal]:
    with open(path, newline="") as fh:
        rows = list(csv.DictReader(fh))
    out = []
    for r in rows:
        if r["role"] not in ROLES:
            raise ValueError(f"{r['case_id']}: role {r['role']!r}")
        if r["code"] not in catalog:
            raise ValueError(f"{r['case_id']}: unknown signal code {r['code']!r}")
        if r["date_precision"] not in PRECISION:
            raise ValueError(f"{r['case_id']}: precision {r['date_precision']!r}")
        out.append(
            CaseSignal(
                case_id=r["case_id"], role=r["role"], ticker=r["ticker"], t0=r["t0"], code=r["code"],
                available_at=r["available_at"], date_precision=r["date_precision"], description=r["description"],
                evidence_class=r["evidence_class"], source_url=r["source_url"],
            )
        )
    return out


@dataclass(frozen=True)
class SignalRate:
    code: str
    cases_with: int
    n_cases: int
    controls_with: int
    n_controls: int

    @property
    def likelihood_ratio(self) -> float:
        """P(signal | target) / P(signal | non-target), Haldane-Anscombe corrected (add 0.5 to each cell)."""
        p_case = (self.cases_with + 0.5) / (self.n_cases + 1.0)
        p_ctrl = (self.controls_with + 0.5) / (self.n_controls + 1.0)
        return p_case / p_ctrl


def signal_rates(
    signals: Iterable[CaseSignal],
    companies: Sequence[tuple[str, str, str]],
    windows: set[str] = SETUP_WINDOWS,
) -> list[SignalRate]:
    """Share of cases and of controls showing each signal inside `windows`.

    `companies` lists every coded company as (case_id, role, ticker), including companies with no
    signal at all, because a control with nothing to report is the most informative row there is.
    """
    n_cases = sum(1 for _, role, _ in companies if role == "case")
    n_controls = sum(1 for _, role, _ in companies if role == "control")
    hits: dict[str, dict[str, set[tuple[str, str]]]] = {}
    for s in signals:
        if s.window not in windows:
            continue
        hits.setdefault(s.code, {"case": set(), "control": set()})[s.role].add((s.case_id, s.ticker))
    return [
        SignalRate(code, len(h["case"]), n_cases, len(h["control"]), n_controls)
        for code, h in sorted(hits.items())
    ]


# --------------------------------------------------------------------------------------------
# Private process (Background of the Offer/Merger)
# --------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Process:
    deal_id: str
    ticker: str
    announced_on: str
    first_contact_on: str | None
    initiator: str
    parties_contacted: int | None
    ndas_signed: int | None
    written_bids: int | None
    first_price: float | None
    final_price: float | None
    evidence_class: str
    source_url: str

    @property
    def process_days(self) -> int | None:
        if not self.first_contact_on:
            return None
        return (date.fromisoformat(self.announced_on) - date.fromisoformat(self.first_contact_on)).days

    @property
    def price_uplift(self) -> float | None:
        if self.first_price and self.final_price:
            return self.final_price / self.first_price - 1.0
        return None


def _int(text: str) -> int | None:
    return int(text) if text.strip() else None


def _float(text: str) -> float | None:
    return float(text) if text.strip() else None


def load_process(path: str | Path) -> list[Process]:
    with open(path, newline="") as fh:
        rows = list(csv.DictReader(fh))
    out = []
    for r in rows:
        if r["initiator"] not in INITIATORS:
            raise ValueError(f"{r['deal_id']}: initiator {r['initiator']!r}")
        out.append(
            Process(
                deal_id=r["deal_id"], ticker=r["ticker"], announced_on=r["announced_on"],
                first_contact_on=r["first_contact_on"] or None, initiator=r["initiator"],
                parties_contacted=_int(r["parties_contacted"]), ndas_signed=_int(r["ndas_signed"]),
                written_bids=_int(r["written_bids"]), first_price=_float(r["first_price_usd"]),
                final_price=_float(r["final_price_usd"]), evidence_class=r["evidence_class"],
                source_url=r["source_url"],
            )
        )
    return out


@dataclass(frozen=True)
class ProcessSummary:
    n: int
    n_with_dates: int
    median_process_days: float | None
    share_buyer_initiated: float | None
    share_single_bidder: float | None
    median_parties_contacted: float | None
    median_price_uplift: float | None


def summarize_process(rows: Iterable[Process]) -> ProcessSummary:
    rows = list(rows)
    days = [p.process_days for p in rows if p.process_days is not None]
    known_init = [p for p in rows if p.initiator != "unknown"]
    bids = [p for p in rows if p.written_bids is not None]
    parties = [p.parties_contacted for p in rows if p.parties_contacted is not None]
    uplift = [p.price_uplift for p in rows if p.price_uplift is not None]
    return ProcessSummary(
        n=len(rows),
        n_with_dates=len(days),
        median_process_days=statistics.median(days) if days else None,
        share_buyer_initiated=(
            sum(p.initiator == "buyer" for p in known_init) / len(known_init) if known_init else None
        ),
        share_single_bidder=(sum(p.written_bids == 1 for p in bids) / len(bids)) if bids else None,
        median_parties_contacted=statistics.median(parties) if parties else None,
        median_price_uplift=statistics.median(uplift) if uplift else None,
    )
