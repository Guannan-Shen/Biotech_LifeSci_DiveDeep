"""Listing classification, point-in-time exits, ETF holdings parsers and takeout case studies (D-038 to D-041)."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from biotech_divedeep.connectors.etf_holdings import (
    ibb_rule_proxy,
    membership,
    parse_ishares_csv,
    parse_ssga_rows,
    xbi_rule_proxy,
)
from biotech_divedeep.connectors.listings import (
    LAYERS,
    DealRef,
    Override,
    build_spells,
    cap_band,
    classify,
    classify_snapshot,
    detect_exits,
    load_overrides,
    match_exits_to_deals,
    panel_counts,
    stable_layers,
)
from biotech_divedeep.models.takeout import load_deals
from biotech_divedeep.models.takeout_case import (
    CaseSignal,
    Process,
    load_catalog,
    load_process,
    load_signals,
    signal_rates,
    summarize_process,
    window_of,
)

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "data" / "reference"
FIX = Path(__file__).resolve().parent / "fixtures" / "etf"


def row(symbol, name, industry, sector="Health Care", cap="500000000", country="United States"):
    return {"symbol": symbol, "name": name, "industry": industry, "sector": sector, "marketCap": cap,
            "country": country, "lastsale": "$10.00", "volume": "1000", "ipoyear": ""}


# --- classification ---------------------------------------------------------------------------


def test_industry_default_and_rescue_and_exclusion():
    pharma = "Biotechnology: Pharmaceutical Preparations"
    assert classify(row("ABCD", "Abcd Therapeutics Inc.", pharma), "nasdaq").layer == "therapeutics"
    dx_label = "Biotechnology: In Vitro & In Vivo Diagnostic Substances"
    dx = classify(row("NTLA", "Intellia Therapeutics Inc", dx_label), "nasdaq")
    assert (dx.layer, dx.rule) == ("therapeutics", "name_rescue")
    care = classify(row("ELV", "Elevance Health Inc. Common Stock", "Medical Specialities"), "nyse")
    assert care.layer == "excluded"
    tobacco = classify(row("MO", "Altria Group Inc.", " Medicinal Chemicals and Botanical Products "), "nyse")
    assert tobacco.layer == "excluded"
    # Industrial specialties counts as medtech only inside the Health Care sector.
    assert classify(row("ISRG", "Intuitive Surgical", "Industrial Specialties"), "nasdaq").layer == "medtech"
    masco = row("MAS", "Masco Corporation", "Industrial Specialties", sector="Industrials")
    assert classify(masco, "nyse").layer == "excluded"


def test_non_common_spac_and_blank_industry():
    pharma = "Biotechnology: Pharmaceutical Preparations"
    assert classify(row("ABCDW", "Abcd Therapeutics Warrants", pharma), "nasdaq").rule == "non_common"
    assert classify(row("GXGX", "GX Acquisiton Corp. Class A", pharma), "nasdaq").layer == "excluded"
    assert classify(row("FACT", "Freedom Acquisition I Corp. Class A", pharma), "nyse").layer == "excluded"
    fresh = classify(row("RYZB", "RayzeBio Inc. Common Stock", "", sector=""), "nasdaq")
    assert (fresh.layer, fresh.rule) == ("therapeutics", "blank_industry_name")
    assert classify(row("XYZ", "Xyz Holdings", "", sector=""), "nasdaq").layer == "excluded"


def test_override_wins_and_override_file_is_valid():
    ov = {"TMO": Override("TMO", "tools", "tools_diversified", "test")}
    item = classify(row("TMO", "Thermo Fisher", "Industrial Machinery/Components", sector="Industrials"), "nyse", ov)
    assert (item.layer, item.rule) == ("tools", "override")
    overrides = load_overrides(REF / "lifesci_layer_overrides.csv")
    assert overrides["TMO"].layer == "tools" and overrides["UNH"].layer == "excluded"


def test_cap_bands_match_takeout_priors():
    assert cap_band(2.99e8) == "micro_under_0.3"
    assert cap_band(3e8) == "small_0.3_to_2"
    assert cap_band(2e9) == "mid_2_to_10"
    assert cap_band(2.6e10) == "mega_over_25"
    assert cap_band(None) == "unknown"


def test_snapshot_dedupes_dual_listings():
    snap = {"nasdaq": [row("ABCD", "Abcd Therapeutics", "Biotechnology: Pharmaceutical Preparations")],
            "nyse": [row("ABCD", "Abcd Therapeutics", "Biotechnology: Pharmaceutical Preparations")]}
    assert len(classify_snapshot(snap)) == 1


# --- history: spells, exits, ticker reuse, stable layers ---------------------------------------


def snap(*rows_):
    return classify_snapshot({"nasdaq": list(rows_)})


PHARMA = "Biotechnology: Pharmaceutical Preparations"


def test_exit_ticker_change_and_ticker_reuse():
    s1 = snap(row("AAA", "Alpha Therapeutics", PHARMA, cap="5e8"), row("BBB", "Beta Bio Pharma", PHARMA, cap="1e9"),
              row("CCC", "Gamma Therapeutics", PHARMA, cap="2e9"))
    # Beta changes ticker, Gamma is bought and leaves.
    s2 = snap(row("AAA", "Alpha Therapeutics", PHARMA, cap="5e8"), row("BBX", "Beta Bio Pharma", PHARMA, cap="1e9"))
    # CCC is later reused by an unrelated blank-check company.
    s3 = snap(row("AAA", "Alpha Therapeutics", PHARMA, cap="5e8"), row("BBX", "Beta Bio Pharma", PHARMA, cap="1e9"),
              row("CCC", "Churchill Capital Corp XI", "Blank Checks", sector="Finance", cap="0"))
    snaps = [("2024-01-01", s1), ("2024-02-01", s2), ("2024-03-01", s3)]
    stable = stable_layers(snaps)
    spells = build_spells(snaps, stable)
    exits = {s.symbol: s for s in detect_exits(spells, "2024-03-01")}
    assert exits["BBB"].exit_class == "ticker_change" and exits["BBB"].successor == "BBX"
    assert exits["CCC"].exit_class == "exit_large" and exits["CCC"].last_seen == "2024-01-01"
    assert "AAA" not in exits
    matches = match_exits_to_deals(
        exits.values(), [DealRef("TK-2024-99", "CCC", "2024-01-20"), DealRef("TK-2019-99", "CCC", "2019-05-01")]
    )
    by = {m.spell.symbol: m for m in matches}
    assert by["CCC"].deal_id == "TK-2024-99"  # the 2019 deal on the same ticker is outside the window


def test_stable_layer_absorbs_label_flicker():
    good = row("TBIO", "Translate Bio Inc.", "Biotechnology: Biological Products (No Diagnostic Substances)")
    flicker = row("TBIO", "Translate Bio Inc.", "Specialty Chemicals", sector="Industrials")
    snaps = [("2021-02-01", snap(good)), ("2021-03-01", snap(flicker)), ("2021-04-01", snap(good))]
    stable = stable_layers(snaps)
    counts = panel_counts(snaps, stable)
    assert [c.n for c in counts if c.layer == "therapeutics"] == [1, 1, 1]
    assert [c.n for c in panel_counts(snaps) if c.layer == "therapeutics"] == [1, 1]  # per-snapshot drops a month


# --- ETF holdings -----------------------------------------------------------------------------


def test_ishares_fixture():
    hold = parse_ishares_csv((FIX / "ishares_ibb_sample.csv").read_text(encoding="utf-8"), "IBB")
    assert [h.ticker for h in hold] == ["VRTX", "GILD", "PCRX"]  # the cash row is dropped
    assert hold[0].as_of == "2026-10-08" and hold[0].weight_pct == pytest.approx(8.12)
    assert membership(hold)["PCRX"] == {"IBB": pytest.approx(0.10)}


def test_ssga_rows():
    rows = [
        ["Fund Name:", "State Street SPDR S&P Biotech ETF"],
        ["Ticker Symbol:", "XBI"],
        ["Holdings:", "As of 08-Oct-2026"],
        [None],
        ["Name", "Ticker", "Identifier", "SEDOL", "Weight", "Sector", "Shares Held", "Local Currency"],
        ["SOLENO THERAPEUTICS INC", "SLNO", "834203309", "BYXN1L1", 1.2, "Health Care", 1000000, "USD"],
        ["ARCELLX INC", "ACLX", "03940C100", "BP2MJV4", "0.95", "Health Care", "800,000", "USD"],
        [None],
        ["Past performance is not a guarantee of future results."],
    ]
    hold = parse_ssga_rows(rows, "XBI")
    assert [h.ticker for h in hold] == ["SLNO", "ACLX"]
    assert hold[0].as_of == "2026-10-08" and hold[1].shares == 800000


def test_rule_proxies():
    assert ibb_rule_proxy("nasdaq", "therapeutics", 3e8)
    assert not ibb_rule_proxy("nyse", "therapeutics", 3e9)
    assert xbi_rule_proxy("VRTX", "United States", "therapeutics", "large_pharma", 1e11)  # GICS biotech
    assert not xbi_rule_proxy("LLY", "United States", "therapeutics", "large_pharma", 1e12)  # GICS pharma
    assert not xbi_rule_proxy("ARGX", "Netherlands", "therapeutics", "", 5e10)


# --- takeout case studies ---------------------------------------------------------------------


def test_windows_and_likelihood_ratio():
    assert window_of(400) == "W1_2y_to_1y"
    assert window_of(90) == "W3_3m_to_1w"
    assert window_of(1) == "W4_last_week"
    sig = [
        CaseSignal("C1", "case", "AAA", "2026-01-01", "C1", "2025-06-01", "day", "", "unverified", ""),
        CaseSignal("C1", "case", "AAA", "2026-01-01", "B5", "2025-12-31", "day", "", "unverified", ""),  # W4
        CaseSignal("C2", "case", "BBB", "2026-01-01", "C1", "2025-03-01", "day", "", "unverified", ""),
        CaseSignal("C1", "control", "XXX", "2026-01-01", "C1", "2025-05-01", "day", "", "unverified", ""),
    ]
    companies = [("C1", "case", "AAA"), ("C2", "case", "BBB"), ("C1", "control", "XXX"),
                 ("C1", "control", "YYY"), ("C2", "control", "ZZZ"), ("C2", "control", "WWW")]
    rates = {r.code: r for r in signal_rates(sig, companies)}
    assert "B5" not in rates  # last-week signals are reactions, not setup
    r = rates["C1"]
    assert (r.cases_with, r.n_cases, r.controls_with, r.n_controls) == (2, 2, 1, 4)
    assert r.likelihood_ratio == pytest.approx((2.5 / 3) / (1.5 / 5))


def test_process_summary():
    rows = [
        Process("D1", "A", "2026-07-06", "2026-03-14", "buyer", None, None, 1, 78.0, 85.0, "unverified", ""),
        Process("D2", "B", "2026-01-07", None, "target", 16, None, None, None, 14.0, "unverified", ""),
    ]
    s = summarize_process(rows)
    assert s.median_process_days == 114 and s.share_buyer_initiated == 0.5 and s.share_single_bidder == 1.0
    assert s.median_price_uplift == pytest.approx(85 / 78 - 1)


def test_case_reference_tables_are_consistent():
    catalog = load_catalog(ROOT / "config" / "takeout_signals.yaml")
    signals = load_signals(REF / "takeout_case_signals.csv", catalog)
    process = load_process(REF / "takeout_case_process.csv")
    deals = {d.deal_id: d for d in load_deals(REF / "biotech_takeouts.csv")}
    for s in signals:
        assert deals[s.case_id].announced_on == s.t0, s
        if s.role == "case":
            assert deals[s.case_id].target_ticker == s.ticker, s
    for p in process:
        assert deals[p.deal_id].target_ticker == p.ticker
    with open(REF / "takeout_case_controls.csv", newline="") as fh:
        for r in csv.DictReader(fh):
            assert deals[r["case_id"]].target_ticker == r["target_ticker"]
            assert r["control_ticker"] not in {d.target_ticker for d in deals.values() if d.announced_on[:4] >= "2025"}


# --- reference outputs ------------------------------------------------------------------------


def test_universe_and_exit_tables():
    with open(REF / "us_lifesci_universe.csv", newline="") as fh:
        uni = list(csv.DictReader(fh))
    assert len(uni) > 800 and {r["layer"] for r in uni} <= set(LAYERS)
    assert len({r["symbol"] for r in uni}) == len(uni)
    with open(REF / "lifesci_listing_exits.csv", newline="") as fh:
        exits = list(csv.DictReader(fh))
    deal_ids = {d.deal_id for d in load_deals(REF / "biotech_takeouts.csv")}
    assert all(r["matched_deal_id"] in deal_ids for r in exits if r["matched_deal_id"])
    with open(REF / "takeout_base_rates_2021_2026.csv", newline="") as fh:
        rates = {r["cap_band"]: float(r["hazard_mean"]) for r in csv.DictReader(fh)}
    assert rates["micro_under_0.3"] < rates["small_0.3_to_2"] < rates["mid_2_to_10"]
