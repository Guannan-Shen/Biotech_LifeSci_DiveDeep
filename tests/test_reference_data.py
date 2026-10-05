import csv
from pathlib import Path

REF = Path(__file__).resolve().parents[1] / "data" / "reference"
TIERS = {"D1", "D2", "D3", "D4", "D5"}
STATUSES = {"open", "corroborated", "partially_corroborated", "refuted"}
CLAIM_TYPES = {
    "efficacy_evidence",
    "safety",
    "manufacturing",
    "regulatory_process",
    "governance",
    "financial",
    "technology_readiness",
}


def read(name: str) -> list[dict[str, str]]:
    with open(REF / name, newline="") as fh:
        return list(csv.DictReader(fh))


def test_dissent_register_is_well_formed():
    rows = read("dissent_register.csv")
    assert rows
    ids = [r["dissent_id"] for r in rows]
    assert len(ids) == len(set(ids))
    for row in rows:
        assert row["tier"] in TIERS, row["dissent_id"]
        assert row["status"] in STATUSES, row["dissent_id"]
        assert row["claim_type"] in CLAIM_TYPES, row["dissent_id"]
        assert row["ticker"] and row["claim"], row["dissent_id"]


def test_other_reference_tables_parse():
    assert len(read("ai_discovery_cycle_times.csv")) == 11
    assert len(read("specialist_concentration_snapshot.csv")) == 20
