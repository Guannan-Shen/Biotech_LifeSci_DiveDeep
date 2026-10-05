import pytest

from biotech_divedeep.models.rnpv import Stage, rnpv

CLINICAL = [
    Stage("phase1", cost=20, years=1.5, pos=0.6),
    Stage("phase2", cost=50, years=2.5, pos=0.3),
    Stage("phase3", cost=150, years=3, pos=0.6),
    Stage("filing", cost=5, years=1, pos=0.9),
]


def discovery(years: int) -> list[Stage]:
    return [Stage(f"discovery_y{i}", cost=10, years=1, pos=1.0) for i in range(years)]


def with_p2(pos: float) -> list[Stage]:
    return [s if s.name != "phase2" else Stage("phase2", 50, 2.5, pos) for s in CLINICAL]


def test_cumulative_pos_and_timeline():
    result = rnpv(discovery(4) + CLINICAL, launch_value=1000, discount_rate=0.10)
    assert result.cumulative_pos == pytest.approx(0.6 * 0.3 * 0.6 * 0.9)
    assert result.years_to_launch == pytest.approx(12.0)


def test_research_note_table_reproduces():
    """Numbers quoted in docs/research/ai_drug_discovery_cycle_times.md, section 3a."""
    expected = {1000: (-48.1, 13.0, 6.1, 9.1), 3000: (13.8, 26.0, 26.7, 40.1), 6000: (106.8, 45.5, 57.7, 86.5)}
    for value, (base, faster, p40, p45) in expected.items():
        b = rnpv(discovery(4) + CLINICAL, value, 0.10).rnpv
        assert b == pytest.approx(base, abs=0.05)
        assert rnpv(discovery(2) + CLINICAL, value, 0.10).rnpv - b == pytest.approx(faster, abs=0.05)
        assert rnpv(discovery(4) + with_p2(0.4), value, 0.10).rnpv - b == pytest.approx(p40, abs=0.05)
        assert rnpv(discovery(4) + with_p2(0.45), value, 0.10).rnpv - b == pytest.approx(p45, abs=0.05)


def test_invalid_pos_rejected():
    with pytest.raises(ValueError):
        Stage("x", cost=1, years=1, pos=1.2)
