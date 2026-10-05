"""Load and validate the watchlist universe (config/universe.yaml)."""

from __future__ import annotations

from datetime import date
from enum import StrEnum
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

DEFAULT_PATH = Path(__file__).resolve().parents[2] / "config" / "universe.yaml"


class Archetype(StrEnum):
    CLINICAL_BINARY = "clinical_binary"
    LAUNCH = "launch"
    COMMERCIAL_PHARMA = "commercial_pharma"
    TOOLS = "tools"
    SOFTWARE = "software"
    DX_DATA = "dx_data"
    AI_PLATFORM = "ai_platform"


class Role(StrEnum):
    WATCHLIST = "watchlist"
    SCREEN_ONLY = "screen_only"


class SizeBucket(StrEnum):
    MICRO = "micro"  # < 300M
    SMALL = "small"  # 300M to 2B
    MID = "mid"  # 2B to 10B
    LARGE = "large"  # >= 10B


def size_bucket(market_cap_usd: float) -> SizeBucket:
    if market_cap_usd < 300e6:
        return SizeBucket.MICRO
    if market_cap_usd < 2e9:
        return SizeBucket.SMALL
    if market_cap_usd < 10e9:
        return SizeBucket.MID
    return SizeBucket.LARGE


class Snapshot(BaseModel):
    model_config = ConfigDict(frozen=True)

    as_of: date
    source: str
    price: float = Field(gt=0)
    market_cap_usd: float = Field(gt=0)


class Company(BaseModel):
    model_config = ConfigDict(frozen=True)

    ticker: str
    name: str
    role: Role
    archetypes: tuple[Archetype, ...] = Field(min_length=1)
    cik: str | None = None
    thesis_note: str = ""
    snapshot: Snapshot | None = None

    @field_validator("ticker")
    @classmethod
    def _upper(cls, value: str) -> str:
        return value.strip().upper()

    @field_validator("cik")
    @classmethod
    def _ten_digit_cik(cls, value: str | None) -> str | None:
        if value is not None and not (len(value) == 10 and value.isdigit()):
            raise ValueError(f"CIK must be 10 zero-padded digits, got {value!r}")
        return value

    @property
    def size_bucket(self) -> SizeBucket | None:
        return size_bucket(self.snapshot.market_cap_usd) if self.snapshot else None


class Benchmark(BaseModel):
    model_config = ConfigDict(frozen=True)

    ticker: str
    name: str
    role: str


class Universe(BaseModel):
    model_config = ConfigDict(frozen=True)

    companies: tuple[Company, ...]
    benchmarks: tuple[Benchmark, ...]

    @model_validator(mode="after")
    def _unique_tickers(self) -> Universe:
        tickers = [c.ticker for c in self.companies]
        dupes = sorted({t for t in tickers if tickers.count(t) > 1})
        if dupes:
            raise ValueError(f"duplicate tickers: {dupes}")
        return self

    def by_ticker(self, ticker: str) -> Company:
        ticker = ticker.upper()
        for company in self.companies:
            if company.ticker == ticker:
                return company
        raise KeyError(ticker)

    def with_role(self, role: Role) -> list[Company]:
        return [c for c in self.companies if c.role == role]

    def with_archetype(self, archetype: Archetype) -> list[Company]:
        return [c for c in self.companies if archetype in c.archetypes]


def load_universe(path: Path | str = DEFAULT_PATH) -> Universe:
    raw = yaml.safe_load(Path(path).read_text())
    defaults = raw.get("snapshot_defaults", {})
    companies = []
    for entry in raw["companies"]:
        entry = dict(entry)
        if "snapshot" in entry:
            entry["snapshot"] = {**defaults, **entry["snapshot"]}
        companies.append(entry)
    return Universe(companies=companies, benchmarks=raw.get("benchmarks", []))
