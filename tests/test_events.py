from datetime import UTC, datetime, timedelta

import pytest

from biotech_divedeep.core.events import Event, Source, known_at
from biotech_divedeep.core.evidence import EvidenceClass

T0 = datetime(2026, 8, 6, 20, 5, tzinfo=UTC)


def make(source_id: str = "0001-26-000001", available: datetime = T0, **kw) -> Event:
    return Event(
        source=Source.EDGAR,
        source_id=source_id,
        event_type="quarterly_results",
        available_at=available,
        observed_at=kw.pop("observed", available + timedelta(days=60)),
        evidence_class=EvidenceClass.FACT,
        tickers=("pacb",),
        **kw,
    )


def test_event_id_is_deterministic_and_ignores_observation_time():
    a = make()
    b = make(observed=T0 + timedelta(days=1))
    assert a.event_id == b.event_id
    assert a.event_id != make(source_id="other").event_id


def test_tickers_uppercased():
    assert make().tickers == ("PACB",)


def test_naive_timestamps_rejected():
    with pytest.raises(ValueError, match="timezone"):
        make(available=datetime(2026, 8, 6), observed=datetime(2026, 9, 1))


def test_observed_before_available_rejected():
    with pytest.raises(ValueError, match="precedes"):
        make(observed=T0 - timedelta(seconds=1))


def test_known_at_filters_future_events_and_sorts():
    early, late = make("a", T0), make("b", T0 + timedelta(days=10))
    assert known_at([late, early], T0 + timedelta(days=1)) == [early]
    assert known_at([late, early], T0 + timedelta(days=10)) == [early, late]
