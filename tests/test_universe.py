import pytest

from biotech_divedeep.universe import Archetype, Role, SizeBucket, Universe, load_universe, size_bucket


@pytest.fixture(scope="module")
def universe() -> Universe:
    return load_universe()


def test_universe_loads_watchlist_and_screen(universe):
    watch = {c.ticker for c in universe.with_role(Role.WATCHLIST)}
    assert {"PACB", "DNA", "QSI", "RXRX", "SDGR", "HROW", "ETON", "SLS", "REPL", "IOVA"} <= watch
    assert len(universe.with_role(Role.SCREEN_ONLY)) >= 20
    assert universe.benchmarks[0].ticker == "XBI"


def test_watchlist_entries_are_complete(universe):
    for company in universe.with_role(Role.WATCHLIST):
        assert company.cik is not None, company.ticker
        assert company.snapshot is not None, company.ticker
        assert company.snapshot.source.startswith("FMP"), company.ticker


def test_archetype_lookup(universe):
    tools = {c.ticker for c in universe.with_archetype(Archetype.TOOLS)}
    assert {"PACB", "ILMN", "TXG", "TWST", "QSI"} <= tools
    assert universe.by_ticker("iova").archetypes == (Archetype.LAUNCH,)


@pytest.mark.parametrize(
    ("cap", "bucket"),
    [(299e6, SizeBucket.MICRO), (300e6, SizeBucket.SMALL), (2e9, SizeBucket.MID), (10e9, SizeBucket.LARGE)],
)
def test_size_bucket_boundaries(cap, bucket):
    assert size_bucket(cap) == bucket


def test_duplicate_tickers_rejected():
    entry = {"ticker": "abc", "name": "A", "role": "watchlist", "archetypes": ["tools"]}
    with pytest.raises(ValueError, match="duplicate"):
        Universe(companies=[entry, {**entry, "ticker": "ABC"}], benchmarks=[])


def test_bad_cik_rejected():
    with pytest.raises(ValueError, match="CIK"):
        Universe(
            companies=[{"ticker": "A", "name": "A", "role": "watchlist", "archetypes": ["tools"], "cik": "1299130"}],
            benchmarks=[],
        )
