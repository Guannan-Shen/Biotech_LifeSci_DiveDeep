"""The Event record: the common currency between connectors, calendars, models and backtests.

Point-in-time rule (docs/BLUEPRINT.md, section 5):
- `available_at` is the earliest moment the information was public. Backtests filter on it.
- `observed_at` is when this system fetched it. Used for audit only.
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterable
from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from biotech_divedeep.core.evidence import EvidenceClass


class Source(StrEnum):
    EDGAR = "edgar"
    FDA = "fda"
    CTGOV = "ctgov"
    COMPANY_IR = "company_ir"
    NEWSWIRE = "newswire"
    MARKET = "market"
    MANUAL = "manual"


class Event(BaseModel):
    model_config = ConfigDict(frozen=True)

    source: Source
    source_id: str = Field(min_length=1, description="Stable id within the source (accession, NCT+version, URL).")
    event_type: str = Field(min_length=1, description="Taxonomy in docs/framework/archetypes.md.")
    available_at: datetime
    observed_at: datetime
    evidence_class: EvidenceClass
    title: str = ""
    url: str | None = None
    tickers: tuple[str, ...] = ()
    cik: str | None = None
    asset_ids: tuple[str, ...] = ()
    nct_ids: tuple[str, ...] = ()
    payload: dict[str, Any] = Field(default_factory=dict)
    raw_ref: str | None = Field(default=None, description="Path of the raw snapshot this was parsed from.")

    @field_validator("available_at", "observed_at")
    @classmethod
    def _require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timestamps must be timezone-aware")
        return value

    @field_validator("tickers")
    @classmethod
    def _upper_tickers(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(t.upper() for t in value)

    @model_validator(mode="after")
    def _observed_after_available(self) -> Event:
        # We cannot observe information before it exists; this guards against swapped fields.
        if self.observed_at < self.available_at:
            raise ValueError("observed_at precedes available_at")
        return self

    @property
    def event_id(self) -> str:
        """Deterministic id, so re-fetching the same item never duplicates it."""
        key = f"{self.source.value}|{self.source_id}|{self.event_type}"
        return hashlib.sha256(key.encode()).hexdigest()[:16]

    def is_known_at(self, as_of: datetime) -> bool:
        return self.available_at <= as_of


def known_at(events: Iterable[Event], as_of: datetime) -> list[Event]:
    """Events a backtest is allowed to see at `as_of`, oldest first."""
    return sorted((e for e in events if e.is_known_at(as_of)), key=lambda e: e.available_at)
