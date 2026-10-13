from dataclasses import replace
from datetime import date
from pathlib import Path

from biotech_divedeep.connectors.sec_ownership import (
    parse_form4_xml,
    parse_form144_xml,
    parse_sec_date,
    read_13f_dataset,
    read_insider_dataset,
)
from biotech_divedeep.signals.fund_flow import (
    fund_skill,
    issuer_quarters,
    latest_positions,
    normalize_issuer,
    position_changes,
    terciles,
)
from biotech_divedeep.signals.insider import (
    classify,
    classify_all,
    cluster_events,
    collapse_joint_filers,
    group_buy_keys,
    line_key,
    role,
    routine_flags,
    stake_fraction,
)

FIX = Path(__file__).resolve().parent / "fixtures" / "sec_ownership"


def _lines():
    return collapse_joint_filers(read_insider_dataset(FIX / "insider_ds"))


def test_parse_sec_date_formats():
    assert parse_sec_date("31-MAR-2024") == date(2024, 3, 31)
    assert parse_sec_date("2024-03-31") == date(2024, 3, 31)
    assert parse_sec_date("02/28/2024") == date(2024, 2, 28)
    assert parse_sec_date("") is None


def test_insider_dataset_join_and_joint_filers():
    raw = read_insider_dataset(FIX / "insider_ds")
    assert len(raw) == 5  # Form 3 dropped; the fund and its GP both report the same sale
    lines = collapse_joint_filers(raw)
    assert len(lines) == 4
    fund = next(t for t in lines if t.code == "S" and t.is_ten_pct)
    assert fund.issuer_cik == "111111" and fund.ticker == "EXBO" and fund.available_at == date(2024, 3, 5)
    assert fund.value == 5_000_000 and abs(stake_fraction(fund) - 0.1) < 1e-12
    assert role(fund) == "ten_pct_owner"
    ceo = next(t for t in lines if t.owner_name == "Doe Jane" and t.code == "S")
    assert role(ceo) == "ceo_cfo" and ceo.plan_10b5_1


def test_classes_and_events():
    lines = _lines()
    classes = classify_all(lines)
    by_code = {t.code + ("_plan" if t.plan_10b5_1 else ""): classes[line_key(t)] for t in lines}
    assert by_code["S"] == "open_market_sale"
    assert by_code["S_plan"] == "plan_sale"
    assert by_code["F_plan"] == "tax_withholding"
    assert by_code["P"] == "open_market_buy"
    routine = routine_flags(lines)
    assert set(routine.values()) == {"unclassified"}
    events = cluster_events(lines, classes, routine)
    assert [(e.direction, e.trigger_date, e.any_ten_pct) for e in events] == [("sell", date(2024, 3, 5), True)]
    # The USD 220k director buy fires only with a lower size floor.
    small = cluster_events(lines, classes, routine, min_value=100_000)
    assert {e.direction for e in small} == {"sell", "buy"}
    # A sale of less than the stake floor never fires, whatever its value.
    assert cluster_events(lines, classes, routine, min_stake=0.5) == []


def test_offering_participation_rules():
    buy = next(t for t in _lines() if t.code == "P")
    assert classify(buy, financing_dates=[date(2024, 3, 8)]) == "offering_participation"
    assert classify(buy, financing_dates=[date(2024, 4, 30)]) == "open_market_buy"
    fund_buy = replace(buy, accession="X-2", owner_cik="222222", is_ten_pct=True, is_director=False)
    keys = group_buy_keys([buy, fund_buy])
    assert classify(buy, group_keys=keys) == "offering_participation"
    assert group_buy_keys([buy]) == set()


def test_routine_vs_opportunistic():
    base = next(t for t in _lines() if t.code == "P")

    def at(year: int, month: int, acc: str):
        return replace(base, accession=acc, trans_date=date(year, month, 10), available_at=date(year, month, 12))

    march = [at(2021, 3, "a"), at(2022, 3, "b"), at(2023, 3, "c"), at(2024, 3, "d")]
    assert routine_flags(march)[("d", base.owner_cik)] == "routine"
    jan = [at(2021, 1, "a"), at(2022, 1, "b"), at(2023, 1, "c"), at(2024, 3, "d")]
    assert routine_flags(jan)[("d", base.owner_cik)] == "opportunistic"
    short = [at(2023, 3, "c"), at(2024, 3, "d")]
    assert routine_flags(short)[("d", base.owner_cik)] == "unclassified"


def test_form4_and_form144_xml():
    rows = parse_form4_xml((FIX / "form4.xml").read_bytes(), "acc-x", date(2024, 3, 6))
    assert len(rows) == 1
    t = rows[0]
    assert (t.ticker, t.code, t.shares, t.price, t.shares_after) == ("EXBO", "S", 10000, 12.0, 90000)
    assert t.plan_10b5_1 and t.is_officer and role(t) == "ceo_cfo"
    n = parse_form144_xml((FIX / "form144.xml").read_bytes(), "acc-y", date(2024, 2, 27))
    assert len(n) == 1
    assert n[0].shares == 400000 and n[0].approx_sale_date == date(2024, 2, 28) and n[0].issuer_cik == "111111"
    assert n[0].seller == "Sample Fund LP"


def test_13f_positions_changes_and_aggregates():
    h = read_13f_dataset(FIX / "f13_ds", filer_ciks=["0000999999"])
    assert {x.filer_cik for x in h} == {"999999"}
    assert not any(x.cusip == "30000D101" for x in h)  # principal amount rows skipped
    pos = latest_positions(h)
    q1, q2 = pos[("999999", date(2024, 3, 31))], pos[("999999", date(2024, 6, 30))]
    assert q1 == {"30000A101": (1_000_000, date(2024, 5, 14)), "30000B101": (500_000, date(2024, 5, 14))}
    assert q2 == {"30000A101": (2_500_000, date(2024, 8, 20)), "30000C101": (100_000, date(2024, 8, 20))}
    kinds = {c.cusip: c.kind for c in position_changes(pos)}
    assert kinds == {"30000A101": "add", "30000B101": "exit", "30000C101": "new"}
    agg = {q.cusip: q for q in issuer_quarters(position_changes(pos), {"999999"})}
    assert agg["30000A101"].holders == 1 and agg["30000A101"].net_buyers == 1
    assert agg["30000B101"].exits == 1 and agg["30000B101"].available_at == date(2024, 8, 20)


def test_fund_skill_is_point_in_time_and_shrunk():
    outcomes = [(date(2023, 1, 1), 0.5)] * 3 + [(date(2025, 1, 1), -0.5)] * 3
    s = fund_skill(outcomes, as_of=date(2024, 1, 1))
    assert s.n == 3 and s.raw_mean == 0.5
    assert 0 < s.mean < 0.05  # three lucky picks barely move a 5-point prior
    assert fund_skill([], as_of=date(2024, 1, 1)).mean == 0.0
    t = terciles({"a": -0.02, "b": 0.0, "c": 0.03})
    assert t == {"a": "bottom", "b": "middle", "c": "top"}


def test_normalize_issuer():
    assert normalize_issuer("Example Bio, Inc.") == normalize_issuer("EXAMPLE BIO INC") == "EXAMPLE BIO"
