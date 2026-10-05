"""Evidence classes: every claim in the system declares how much we should trust it."""

from __future__ import annotations

from enum import StrEnum


class EvidenceClass(StrEnum):
    FACT = "fact"
    """Reported in a primary source (filing, regulator record, registry, audited number)."""

    MANAGEMENT_GUIDANCE = "management_guidance"
    """Company forecast or timeline (runway, readout window, PDUFA date, launch target)."""

    OWN_ASSUMPTION = "own_assumption"
    """Our modelling input or inference (probabilities, inferred readout windows)."""

    UNVERIFIED = "unverified"
    """Extracted or reported but not yet checked against a primary source."""
