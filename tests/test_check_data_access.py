import importlib.util
import json
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_data_access.py"
spec = importlib.util.spec_from_file_location("check_data_access", SCRIPT)
cda = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = cda  # dataclasses resolve their module via sys.modules
spec.loader.exec_module(cda)

PAYLOADS = {
    "company_tickers": {"0": {"ticker": "PACB"}, "1": {"ticker": "MRLN"}},
    "submissions": {
        "name": "PACIFIC BIOSCIENCES",
        "filings": {"recent": {"form": ["10-Q"], "filingDate": ["2026-08-07"]}},
    },
    "companyfacts": {"entityName": "Merlin, Inc.", "facts": {"us-gaap": {"Cash": {}}}},
    "drugsfda": {"meta": {"results": {"total": 28000}, "last_updated": "2026-10-01"}},
    "version": {"apiVersion": "2.0.5", "dataTimestamp": "2026-10-04T09:00:00"},
    "studies": {"studies": [{"protocolSection": {"identificationModule": {"nctId": "NCT0", "briefTitle": "T"}}}]},
    "toptier_agencies": {"results": [{}, {}]},
}


def fake_fetch(url, headers):
    for key, payload in PAYLOADS.items():
        if key in url:
            return 200, json.dumps(payload).encode()
    raise AssertionError(url)


def test_all_sources_ok_returns_zero(monkeypatch, capsys):
    monkeypatch.setenv("SEC_USER_AGENT", "Test test@example.com")
    monkeypatch.delenv("X_BEARER_TOKEN", raising=False)
    monkeypatch.setattr(cda.time, "sleep", lambda s: None)
    assert cda.main([], fetcher=fake_fetch) == 0
    assert "7/7 reachable" in capsys.readouterr().out


def test_summary_counts_only_successes(monkeypatch, capsys):
    monkeypatch.setenv("SEC_USER_AGENT", "Test test@example.com")
    monkeypatch.delenv("X_BEARER_TOKEN", raising=False)
    monkeypatch.setattr(cda.time, "sleep", lambda s: None)

    def blocked(url, headers):
        raise OSError("Tunnel connection failed: 403")

    assert cda.main([], fetcher=blocked) == 1
    assert "0/7 reachable; 6 required source(s) failing" in capsys.readouterr().out


def test_missing_sec_user_agent_fails_without_network(monkeypatch):
    monkeypatch.delenv("SEC_USER_AGENT", raising=False)
    sec = cda.build_checks({})[0]
    result = cda.run_check(sec, fetcher=lambda u, h: (_ for _ in ()).throw(AssertionError("no fetch")))
    assert not result.ok and "SEC_USER_AGENT" in result.detail


def test_unexpected_shape_is_a_failure():
    check = cda.build_checks({"SEC_USER_AGENT": "x y@z"})[3]  # openFDA
    result = cda.run_check(check, fetcher=lambda u, h: (200, b'{"error": "blocked"}'))
    assert not result.ok and "KeyError" in result.detail
