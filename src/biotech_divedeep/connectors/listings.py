"""US listing snapshots: classify every listed company into a life-science layer (D-038).

Source: the Nasdaq stock screener (all NASDAQ, NYSE and NYSE American common stocks with sector,
industry, market cap, country, IPO year), as mirrored once a day since 2021-01-30 by the public
GitHub repository `rreichel3/US-Stock-Symbols` (files `<exchange>/<exchange>_full_tickers.json`).
Because the mirror is a git repository, its history is a point-in-time listing record: a symbol
that stops appearing has left the market (takeout, reverse merger, ticker change or failure).

Nasdaq's `industry` field is derived from SIC codes and is stable over time; the `sector` field
was renamed in 2021, so classification keys on industry. Industry labels are noisy at the edges
(tobacco under medicinal chemicals, managed care under medical specialities, Incyte under contract
research), so a row's layer is decided in this order:

1. curated override by ticker (`data/reference/lifesci_layer_overrides.csv`);
2. exclusion of non-common securities (warrants, units, rights, preferreds, notes);
3. industry default layer;
4. for ambiguous industries, a therapeutics keyword in the company name rescues the row
   ("Intellia Therapeutics" filed under diagnostic substances), and a care-delivery or
   insurance keyword excludes it.

Every classification is `own_assumption`; the layer is a research convenience, not a GICS code.
"""

from __future__ import annotations

import csv
import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path

EXCHANGES = ("nasdaq", "nyse", "amex")

LAYERS = ("therapeutics", "tools", "services", "diagnostics", "software_data", "medtech")
EXCLUDED = "excluded"

# Industry -> default layer. Keys are normalized with `_norm_industry`.
INDUSTRY_LAYER: dict[str, str] = {
    "biotechnology: pharmaceutical preparations": "therapeutics",
    "biotechnology: biological products (no diagnostic substances)": "therapeutics",
    "pharmaceuticals and biotechnology": "therapeutics",
    "major pharmaceuticals": "therapeutics",
    "biotechnology: laboratory analytical instruments": "tools",
    "biotechnology: commercial physical & biological research": "services",
    "biotechnology: in vitro & in vivo diagnostic substances": "diagnostics",
    "medical specialities": "diagnostics",
    "precision instruments": "diagnostics",
    "medical/dental instruments": "medtech",
    "biotechnology: electromedical & electrotherapeutic apparatus": "medtech",
    "ophthalmic goods": "medtech",
    "medical electronics": "medtech",
    "industrial specialties": "medtech",
    "medicinal chemicals and botanical products": EXCLUDED,
    "other pharmaceuticals": EXCLUDED,
    "misc health and biotechnology services": EXCLUDED,
    "medical/nursing services": EXCLUDED,
    "hospital/nursing management": EXCLUDED,
    "managed health care": EXCLUDED,
}

# Industries whose default layer only applies inside the Health Care sector (they also hold
# industrial companies: Masco and Pool Corporation sit under industrial specialties).
HEALTH_SECTOR_ONLY = {"industrial specialties", "precision instruments"}

# Industries where a therapeutics keyword in the name overrides the default layer.
AMBIGUOUS = {
    "biotechnology: in vitro & in vivo diagnostic substances",
    "biotechnology: commercial physical & biological research",
    "biotechnology: laboratory analytical instruments",
    "medical specialities",
    "medicinal chemicals and botanical products",
    "other pharmaceuticals",
    "misc health and biotechnology services",
    "precision instruments",
    "industrial specialties",
}

THERAPEUTICS_WORDS = re.compile(
    r"\b(therapeutics?|pharmaceuticals?|pharma|biopharma|biopharmaceuticals?|oncology|medicines|vaccines?|"
    r"biotherapeutics|immunotherapeutics|genetics therapeutics)\b",
    re.IGNORECASE,
)
CARE_WORDS = re.compile(
    r"\b(health ?care|health group|health inc|health,? inc|health corp|insurance|hospitals?|dental|imaging|"
    r"nursing|behavioral|clinics?|cannabis|tobacco)\b",
    re.IGNORECASE,
)
NON_COMMON = re.compile(
    r"\b(warrants?|units?|rights?|preferred|preference|notes due|debentures?|subordinated notes|"
    r"depositary shares,? each representing a 1/|% series)\b",
    re.IGNORECASE,
)
# Applied only when Nasdaq gives no industry at all (new listings); wider than THERAPEUTICS_WORDS.
BLANK_INDUSTRY_WORDS = re.compile(r"(bio|therapeut|pharm|oncolog|medicine|genomic|vaccin)", re.IGNORECASE)
# Blank-check shells and companies that sat under a health-care industry label in older snapshots
# (SPACs before their merger, a theme park operator, crypto miners and treasuries after reverse mergers).
NOT_LIFE_SCIENCE = re.compile(
    r"\b(acquisi\w*(\s+\w+){0,2}\s+corp(oration)?|acquisition co|capital corp|blank check|metals|entertainment|parks|"
    r"digital corporation|infrastructure|strategies inc|resorts|mining)\b",
    re.IGNORECASE,
)


def _norm_industry(text: str) -> str:
    text = re.sub(r"\s+", " ", (text or "").strip().lower())
    return text.replace("resarch", "research")


def _num(text: str | float | None) -> float | None:
    if isinstance(text, (int, float)):
        return float(text)
    text = (text or "").replace("$", "").replace(",", "").strip()
    try:
        return float(text) if text else None
    except ValueError:
        return None


def cap_band(market_cap_usd: float | None) -> str:
    """Bands match `config/takeout_priors.yaml` so the takeout score can read them directly."""
    if market_cap_usd is None or market_cap_usd <= 0:
        return "unknown"
    b = market_cap_usd / 1e9
    if b < 0.3:
        return "micro_under_0.3"
    if b < 2:
        return "small_0.3_to_2"
    if b < 10:
        return "mid_2_to_10"
    if b < 25:
        return "large_10_to_25"
    return "mega_over_25"


@dataclass(frozen=True)
class Override:
    ticker: str
    layer: str
    sublayer: str
    reason: str


def load_overrides(path: str | Path) -> dict[str, Override]:
    with open(path, newline="") as fh:
        rows = list(csv.DictReader(fh))
    out: dict[str, Override] = {}
    for r in rows:
        layer = r["layer"].strip()
        if layer not in LAYERS and layer != EXCLUDED:
            raise ValueError(f"unknown layer {layer!r} for {r['ticker']}")
        ticker = r["ticker"].strip().upper()
        out[ticker] = Override(ticker, layer, r["sublayer"].strip(), r["reason"])
    return out


@dataclass(frozen=True)
class Listing:
    symbol: str
    name: str
    exchange: str
    sector: str
    industry: str
    country: str
    ipo_year: str
    market_cap_usd: float | None
    last_price_usd: float | None
    volume: float | None
    layer: str
    sublayer: str
    rule: str  # which rule set the layer: override, non_common, industry, name_rescue, name_exclude

    @property
    def cap_band(self) -> str:
        return cap_band(self.market_cap_usd)

    @property
    def is_adr(self) -> bool:
        return bool(re.search(r"american depositary|\bADS\b|\bADR\b", self.name, re.IGNORECASE))

    @property
    def in_universe(self) -> bool:
        return self.layer in LAYERS


def classify(row: Mapping[str, str], exchange: str, overrides: Mapping[str, Override] | None = None) -> Listing:
    """Classify one screener row. Unknown industries are excluded."""
    symbol = (row.get("symbol") or "").strip().upper()
    name = (row.get("name") or "").strip()
    sector = (row.get("sector") or "").strip()
    industry = _norm_industry(row.get("industry", ""))
    base = dict(
        symbol=symbol,
        name=name,
        exchange=exchange,
        sector=sector,
        industry=industry,
        country=(row.get("country") or "").strip(),
        ipo_year=(row.get("ipoyear") or "").strip(),
        market_cap_usd=_num(row.get("marketCap")),
        last_price_usd=_num(row.get("lastsale")),
        volume=_num(row.get("volume")),
    )
    ov = (overrides or {}).get(symbol)
    if ov is not None:
        return Listing(**base, layer=ov.layer, sublayer=ov.sublayer, rule="override")
    if "^" in symbol or "/" in symbol or NON_COMMON.search(name):
        return Listing(**base, layer=EXCLUDED, sublayer="non_common", rule="non_common")
    if NOT_LIFE_SCIENCE.search(name):
        return Listing(**base, layer=EXCLUDED, sublayer="not_life_science", rule="name_exclude")
    if not industry:
        # Fresh IPOs carry no sector or industry for a few months (RayzeBio in late 2023).
        if BLANK_INDUSTRY_WORDS.search(name) and not CARE_WORDS.search(name):
            return Listing(**base, layer="therapeutics", sublayer="", rule="blank_industry_name")
        return Listing(**base, layer=EXCLUDED, sublayer="", rule="industry")
    layer = INDUSTRY_LAYER.get(industry, EXCLUDED)
    if industry in HEALTH_SECTOR_ONLY and sector.lower() != "health care":
        layer = EXCLUDED
    rule = "industry"
    if industry in AMBIGUOUS:
        if THERAPEUTICS_WORDS.search(name) and not CARE_WORDS.search(name):
            layer, rule = "therapeutics", "name_rescue"
        elif CARE_WORDS.search(name):
            layer, rule = EXCLUDED, "name_exclude"
    return Listing(**base, layer=layer, sublayer="", rule=rule)


def classify_snapshot(
    rows_by_exchange: Mapping[str, Iterable[Mapping[str, str]]],
    overrides: Mapping[str, Override] | None = None,
) -> list[Listing]:
    """Classify a whole snapshot; a symbol listed on two exchanges keeps its first occurrence."""
    seen: set[str] = set()
    out: list[Listing] = []
    for exchange in EXCHANGES:
        for row in rows_by_exchange.get(exchange, ()):
            item = classify(row, exchange, overrides)
            if not item.symbol or item.symbol in seen:
                continue
            seen.add(item.symbol)
            out.append(item)
    return out


# --------------------------------------------------------------------------------------------
# Point-in-time history: entries, exits and ticker changes
# --------------------------------------------------------------------------------------------


@dataclass
class Spell:
    """One continuous listing of a symbol across sampled snapshots."""

    symbol: str
    name: str
    layer: str
    first_seen: str
    last_seen: str
    last_market_cap_usd: float | None
    max_market_cap_usd: float | None
    n_snapshots: int = 1
    successor: str = ""  # new symbol when the exit looks like a ticker change
    exit_class: str = ""  # filled by `detect_exits`


def _name_key(name: str) -> str:
    """First two meaningful words of a company name, lowercased, for ticker-change matching."""
    words = re.findall(r"[a-z0-9]+", name.lower())
    stop = {"inc", "corp", "corporation", "the", "co", "company", "ltd", "plc", "common", "stock", "class", "a"}
    words = [w for w in words if w not in stop]
    return " ".join(words[:2])


def build_spells(
    snapshots: Sequence[tuple[str, Sequence[Listing]]],
    stable: Mapping[tuple[str, str], tuple[str, str]] | None = None,
) -> dict[str, Spell]:
    """Fold dated full snapshots (oldest first) into one spell per symbol ever in the universe.

    Presence is judged on the whole snapshot, whatever the layer: Nasdaq relabels industries, and a
    company whose label drifts out of the universe has not left the market. The spell's layer is the
    latest universe classification. A symbol that disappears and comes back keeps one spell; that
    absorbs screener glitches at the cost of merging rare real relistings.
    """
    def universe_layer(item: Listing) -> str | None:
        if stable is not None:
            hit = stable.get(stable_key(item))
            return hit[0] if hit else None
        return item.layer if item.in_universe else None

    ever = {item.symbol for _, listings in snapshots for item in listings if universe_layer(item)}
    spells: dict[str, Spell] = {}
    closed: dict[str, Spell] = {}
    prev_date = ""
    for date, listings in snapshots:
        for item in listings:
            if item.symbol not in ever:
                continue
            s = spells.get(item.symbol)
            if s is not None and s.last_seen != prev_date and _name_key(s.name) != _name_key(item.name):
                # Ticker reuse: the symbol came back after a gap under another name (CCXI was
                # ChemoCentryx, then a Churchill Capital SPAC). Close the old spell.
                closed[f"{s.symbol}@{s.first_seen}"] = s
                s = None
            if s is None:
                s = spells[item.symbol] = Spell(
                    item.symbol, item.name, item.layer, date, date, item.market_cap_usd, item.market_cap_usd, 0
                )
            s.last_seen = date
            s.name = item.name
            s.n_snapshots += 1
            layer = universe_layer(item)
            if layer:
                s.layer = layer
            if item.market_cap_usd:
                s.last_market_cap_usd = item.market_cap_usd
                s.max_market_cap_usd = max(s.max_market_cap_usd or 0.0, item.market_cap_usd)
        prev_date = date
    # A spell that only ever held non-universe rows (the SPAC that reused CCXI) is dropped.
    out = {**closed, **spells}
    return {k: v for k, v in out.items() if v.layer in LAYERS}


@dataclass(frozen=True)
class ExitRules:
    large_cap_usd: float = 3e8  # an unmatched exit above this is a candidate missing takeout
    small_cap_usd: float = 5e7  # below this an exit is most likely a failure or uplisting loss


SNAPSHOT_FIELDS = (
    "symbol", "name", "exchange", "sector", "industry", "country", "ipo_year",
    "market_cap_usd", "last_price_usd", "volume", "layer", "sublayer", "rule",
)


def read_snapshot_csv(path: str | Path, overrides: Mapping[str, Override] | None = None) -> list[Listing]:
    """Read a stored snapshot (`data/silver/listings/<date>.csv.gz`) and classify it with the current rules."""
    import gzip

    with gzip.open(path, "rt") as fh:
        rows = list(csv.DictReader(fh))
    raw: dict[str, list[dict]] = {ex: [] for ex in EXCHANGES}
    for r in rows:
        raw.setdefault(r["exchange"], []).append(
            {
                "symbol": r["symbol"], "name": r["name"], "sector": r["sector"], "industry": r["industry"],
                "country": r["country"], "ipoyear": r["ipo_year"], "marketCap": r["market_cap_usd"],
                "lastsale": r["last_price_usd"], "volume": r["volume"],
            }
        )
    return classify_snapshot(raw, overrides)


def detect_exits(
    spells: Mapping[str, Spell],
    last_snapshot: str,
    rules: ExitRules | None = None,
) -> list[Spell]:
    """Spells that end before the last snapshot, with a ticker-change check by name.

    `exit_class` is one of `ticker_change`, `exit_large`, `exit_mid`, `exit_small`. Matching to the
    takeout table happens in `match_exits_to_deals`.
    """
    rules = rules or ExitRules()
    starts_by_key: dict[str, list[Spell]] = {}
    for s in spells.values():
        starts_by_key.setdefault(_name_key(s.name), []).append(s)
    exits: list[Spell] = []
    for s in spells.values():
        if s.last_seen >= last_snapshot:
            continue
        twins = [
            t for t in starts_by_key.get(_name_key(s.name), [])
            if t.symbol != s.symbol and t.first_seen >= s.last_seen and t.first_seen <= _add_months(s.last_seen, 2)
        ]
        if twins and _name_key(s.name):
            s.successor = twins[0].symbol
            s.exit_class = "ticker_change"
        else:
            cap = s.last_market_cap_usd or 0.0
            if cap >= rules.large_cap_usd:
                s.exit_class = "exit_large"
            elif cap < rules.small_cap_usd:
                s.exit_class = "exit_small"
            else:
                s.exit_class = "exit_mid"
        exits.append(s)
    return sorted(exits, key=lambda x: (x.last_seen, x.symbol))


def _add_months(date: str, months: int) -> str:
    y, m = int(date[:4]), int(date[5:7])
    m += months
    y += (m - 1) // 12
    m = (m - 1) % 12 + 1
    return f"{y:04d}-{m:02d}-{date[8:10] or '01'}"


@dataclass(frozen=True)
class DealRef:
    deal_id: str
    ticker: str
    announced_on: str


@dataclass
class ExitMatch:
    spell: Spell
    deal_id: str = ""
    lag_months: int | None = None
    flags: list[str] = field(default_factory=list)


def match_exits_to_deals(
    exits: Iterable[Spell],
    deals: Iterable[DealRef],
    max_lag_months: int = 12,
    panel_start: str | None = None,
) -> list[ExitMatch]:
    """Match each exit to a takeout announced while the symbol was listed (ticker plus window).

    Tickers are reused (RXDX was Ignyta, then Prometheus), so the deal must be announced between
    the month before the spell's first sighting and the month after its last sighting.
    """
    by_ticker: dict[str, list[DealRef]] = {}
    for d in deals:
        by_ticker.setdefault(d.ticker.upper(), []).append(d)
    out: list[ExitMatch] = []
    for s in exits:
        m = ExitMatch(s)
        for d in by_ticker.get(s.symbol, []):
            # A fast tender offer can be announced and closed between two monthly snapshots, so the
            # window runs one month past the last sighting.
            # A company already listed when the panel starts may have announced its deal earlier.
            back = 12 if panel_start and s.first_seen <= panel_start else 1
            if _add_months(s.first_seen, -back) <= d.announced_on <= _add_months(s.last_seen, 1):
                lag = (int(s.last_seen[:4]) - int(d.announced_on[:4])) * 12 + int(s.last_seen[5:7]) - int(
                    d.announced_on[5:7]
                )
                if lag <= max_lag_months:
                    m.deal_id, m.lag_months = d.deal_id, lag
                    break
        if not m.deal_id and s.exit_class == "exit_large":
            m.flags.append("candidate_missing_deal")
        out.append(m)
    return out


def stable_layers(snapshots: Sequence[tuple[str, Sequence[Listing]]]) -> dict[tuple[str, str], tuple[str, str]]:
    """One layer per company: the most frequent universe layer across its snapshots.

    Nasdaq industry labels flicker (Translate Bio read "specialty chemicals" for part of 2021), so
    per-snapshot classification moves companies in and out of the denominator. Keyed on symbol and
    name key so a reused ticker (CCXI: ChemoCentryx, later a SPAC) is a separate company. A company
    is in the universe if at least a third of its snapshots classify it there.
    """
    seen: dict[tuple[str, str], int] = {}
    votes: dict[tuple[str, str], dict[tuple[str, str], int]] = {}
    for _, listings in snapshots:
        for item in listings:
            key = (item.symbol, _name_key(item.name))
            seen[key] = seen.get(key, 0) + 1
            if item.in_universe:
                tally = votes.setdefault(key, {})
                tally[(item.layer, item.sublayer)] = tally.get((item.layer, item.sublayer), 0) + 1
    out: dict[tuple[str, str], tuple[str, str]] = {}
    for key, tally in votes.items():
        (layer, sublayer), n = max(tally.items(), key=lambda kv: kv[1])
        if sum(tally.values()) * 3 >= seen[key]:
            out[key] = (layer, sublayer)
    return out


def stable_key(item: Listing) -> tuple[str, str]:
    return item.symbol, _name_key(item.name)


@dataclass(frozen=True)
class PanelCount:
    date: str
    layer: str
    cap_band: str
    n: int


def panel_counts(
    snapshots: Sequence[tuple[str, Sequence[Listing]]],
    stable: Mapping[tuple[str, str], tuple[str, str]] | None = None,
) -> list[PanelCount]:
    """Number of listed universe companies per snapshot, layer and cap band (the hazard denominator).

    With `stable` (from `stable_layers`), each company keeps one layer for its whole history.
    """
    out: list[PanelCount] = []
    for date, listings in snapshots:
        counts: dict[tuple[str, str], int] = {}
        for item in listings:
            if stable is not None:
                hit = stable.get(stable_key(item))
                layer = hit[0] if hit else None
            else:
                layer = item.layer if item.in_universe else None
            if layer:
                key = (layer, item.cap_band)
                counts[key] = counts.get(key, 0) + 1
        out.extend(PanelCount(date, layer, band, n) for (layer, band), n in sorted(counts.items()))
    return out
