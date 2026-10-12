"""Parsers for SEC ownership data: Form 4 transactions, Form 13F holdings, Form 144 notices.

Three routes, all offline-testable (H18 part B, H4):

1. **Insider Transactions Data Sets** (sec.gov, quarterly ZIPs of Forms 3, 4 and 5 as TSV tables:
   SUBMISSION, REPORTINGOWNER, NONDERIV_TRANS, FOOTNOTES and others). `read_insider_dataset`
   joins them into one row per non-derivative transaction.
2. **Form 4 XML** (`ownershipDocument`) for single filings fetched from EDGAR, e.g. the current
   quarter before its data set is published. `parse_form4_xml`.
3. **Form 13F Data Sets** (quarterly ZIPs: SUBMISSION, COVERPAGE, INFOTABLE). `read_13f_dataset`.
   Form 144 notices (electronic on EDGAR since 2023) parse with `parse_form144_xml`.

Point-in-time: every record carries the filing date as `available_at`. The transaction date
(Form 4) and the period of report (13F) are kept but never used to order information.

Column names follow the SEC data set readme files. The readers look columns up by name and
tolerate missing optional ones (the 10b5-1 checkbox column exists only from 2023 onward).
Network access is not done here; `scripts/ownership_flow.py` downloads on the local machine.
"""

from __future__ import annotations

import csv
import io
import re
import zipfile
from collections import defaultdict
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from xml.etree import ElementTree as ET

csv.field_size_limit(10**8)

_DATE_FORMATS = ("%d-%b-%Y", "%Y-%m-%d", "%m/%d/%Y", "%Y%m%d")


def parse_sec_date(text: str | None) -> date | None:
    """SEC data sets write dates as 31-MAR-2024; XML uses 2024-03-31."""
    if not text:
        return None
    t = text.strip()[:11]
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(t.title() if "-" in t and t[2:3] == "-" else t, fmt).date()
        except ValueError:
            continue
    return None


def _num(text: str | None) -> float | None:
    if text is None:
        return None
    t = str(text).replace(",", "").strip()
    if not t:
        return None
    try:
        return float(t)
    except ValueError:
        return None


def _truthy(text: str | None) -> bool:
    return str(text or "").strip().lower() in {"1", "true", "y", "yes", "x"}


@dataclass(frozen=True)
class InsiderTxn:
    """One non-derivative line of a Form 4 (or 5)."""

    accession: str
    available_at: date  # filing date
    trans_date: date | None
    form: str
    issuer_cik: str
    issuer_name: str
    ticker: str
    owner_cik: str
    owner_name: str
    is_director: bool
    is_officer: bool
    is_ten_pct: bool
    officer_title: str
    code: str  # P, S, A, M, F, G, J, C, X, D, ...
    shares: float | None
    price: float | None
    acq_disp: str  # A or D
    shares_after: float | None
    direct: str  # D or I
    plan_10b5_1: bool  # checkbox (2023+) or a footnote naming Rule 10b5-1
    footnote_text: str = ""

    @property
    def value(self) -> float | None:
        return self.shares * self.price if self.shares is not None and self.price is not None else None


def _open_tables(source: Path) -> dict[str, Iterator[dict[str, str]]]:
    """Map upper-case table name (SUBMISSION, ...) to a DictReader over a ZIP or a directory."""
    tables: dict[str, Iterator[dict[str, str]]] = {}
    if source.is_dir():
        for p in source.iterdir():
            if p.suffix.lower() == ".tsv":
                fh = open(p, newline="", encoding="utf-8", errors="replace")
                tables[p.stem.upper()] = csv.DictReader(fh, delimiter="\t", quoting=csv.QUOTE_NONE)
        return tables
    zf = zipfile.ZipFile(source)
    for name in zf.namelist():
        if name.lower().endswith(".tsv"):
            fh = io.TextIOWrapper(zf.open(name), encoding="utf-8", errors="replace", newline="")
            tables[Path(name).stem.upper()] = csv.DictReader(fh, delimiter="\t", quoting=csv.QUOTE_NONE)
    return tables


def _relationship(text: str) -> tuple[bool, bool, bool]:
    t = text.lower().replace(" ", "")
    return "director" in t, "officer" in t, "tenpercentowner" in t or "10%owner" in t


def read_insider_dataset(source: Path) -> list[InsiderTxn]:
    """Join SUBMISSION, REPORTINGOWNER, NONDERIV_TRANS and FOOTNOTES of one quarterly data set.

    A filing with several reporting owners (a fund and its general partner, say) yields one row
    per owner and transaction; `signals.insider` collapses owners that share an accession.
    """
    t = _open_tables(source)
    subs: dict[str, dict[str, str]] = {}
    for r in t.get("SUBMISSION", iter(())):
        if (r.get("DOCUMENT_TYPE") or "").strip() in {"4", "4/A", "5", "5/A"}:
            subs[r["ACCESSION_NUMBER"]] = r
    owners: dict[str, list[dict[str, str]]] = defaultdict(list)
    for r in t.get("REPORTINGOWNER", iter(())):
        if r["ACCESSION_NUMBER"] in subs:
            owners[r["ACCESSION_NUMBER"]].append(r)
    notes: dict[str, list[str]] = defaultdict(list)
    for r in t.get("FOOTNOTES", iter(())):
        if r["ACCESSION_NUMBER"] in subs:
            notes[r["ACCESSION_NUMBER"]].append(r.get("FOOTNOTE_TXT") or "")
    out: list[InsiderTxn] = []
    for r in t.get("NONDERIV_TRANS", iter(())):
        acc = r["ACCESSION_NUMBER"]
        sub = subs.get(acc)
        if sub is None:
            continue
        fn = " ".join(notes.get(acc, []))
        plan = _truthy(sub.get("AFF10B5ONE")) or bool(re.search(r"10b5-1", fn, re.I))
        filed = parse_sec_date(sub.get("FILING_DATE"))
        if filed is None:
            continue
        for o in owners.get(acc, [{}]):
            d, off, ten = _relationship(o.get("RPTOWNER_RELATIONSHIP") or "")
            out.append(
                InsiderTxn(
                    accession=acc,
                    available_at=filed,
                    trans_date=parse_sec_date(r.get("TRANS_DATE")),
                    form=(sub.get("DOCUMENT_TYPE") or "").strip(),
                    issuer_cik=(sub.get("ISSUERCIK") or "").strip().lstrip("0"),
                    issuer_name=(sub.get("ISSUERNAME") or "").strip(),
                    ticker=(sub.get("ISSUERTRADINGSYMBOL") or "").strip().upper(),
                    owner_cik=(o.get("RPTOWNERCIK") or "").strip().lstrip("0"),
                    owner_name=(o.get("RPTOWNERNAME") or "").strip(),
                    is_director=d,
                    is_officer=off,
                    is_ten_pct=ten,
                    officer_title=(o.get("RPTOWNER_TITLE") or "").strip(),
                    code=(r.get("TRANS_CODE") or "").strip().upper(),
                    shares=_num(r.get("TRANS_SHARES")),
                    price=_num(r.get("TRANS_PRICEPERSHARE")),
                    acq_disp=(r.get("TRANS_ACQUIRED_DISP_CD") or "").strip().upper(),
                    shares_after=_num(r.get("SHRS_OWND_FOLWNG_TRANS")),
                    direct=(r.get("DIRECT_INDIRECT_OWNERSHIP") or "").strip().upper(),
                    plan_10b5_1=plan,
                    footnote_text=fn[:500],
                )
            )
    return out


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _find(el: ET.Element | None, path: str) -> ET.Element | None:
    """Namespace-agnostic path lookup (`a/b/c`)."""
    cur = el
    for part in path.split("/"):
        if cur is None:
            return None
        cur = next((c for c in cur if _local(c.tag) == part), None)
    return cur


def _text(el: ET.Element | None, path: str) -> str:
    node = _find(el, path)
    if node is None:
        return ""
    val = _find(node, "value")
    return ((val.text if val is not None else node.text) or "").strip()


def parse_form4_xml(xml: str | bytes, accession: str, filed: date) -> list[InsiderTxn]:
    """Non-derivative transactions of one `ownershipDocument` (Form 4 primary XML)."""
    root = ET.fromstring(xml)
    issuer = _find(root, "issuer")
    fn = " ".join((f.text or "") for f in root.iter() if _local(f.tag) == "footnote")
    plan = _truthy(_text(root, "aff10b5One")) or bool(re.search(r"10b5-1", fn, re.I))
    owners = [c for c in root if _local(c.tag) == "reportingOwner"] or [ET.Element("reportingOwner")]
    table = _find(root, "nonDerivativeTable")
    rows = [c for c in table if _local(c.tag) == "nonDerivativeTransaction"] if table is not None else []
    out: list[InsiderTxn] = []
    for o in owners:
        rel = _find(o, "reportingOwnerRelationship")
        for tx in rows:
            out.append(
                InsiderTxn(
                    accession=accession,
                    available_at=filed,
                    trans_date=parse_sec_date(_text(tx, "transactionDate")),
                    form=_text(root, "documentType") or "4",
                    issuer_cik=_text(issuer, "issuerCik").lstrip("0"),
                    issuer_name=_text(issuer, "issuerName"),
                    ticker=_text(issuer, "issuerTradingSymbol").upper(),
                    owner_cik=_text(o, "reportingOwnerId/rptOwnerCik").lstrip("0"),
                    owner_name=_text(o, "reportingOwnerId/rptOwnerName"),
                    is_director=_truthy(_text(rel, "isDirector")),
                    is_officer=_truthy(_text(rel, "isOfficer")),
                    is_ten_pct=_truthy(_text(rel, "isTenPercentOwner")),
                    officer_title=_text(rel, "officerTitle"),
                    code=_text(tx, "transactionCoding/transactionCode").upper(),
                    shares=_num(_text(tx, "transactionAmounts/transactionShares")),
                    price=_num(_text(tx, "transactionAmounts/transactionPricePerShare")),
                    acq_disp=_text(tx, "transactionAmounts/transactionAcquiredDisposedCode").upper(),
                    shares_after=_num(_text(tx, "postTransactionAmounts/sharesOwnedFollowingTransaction")),
                    direct=_text(tx, "ownershipNature/directOrIndirectOwnership").upper(),
                    plan_10b5_1=plan,
                    footnote_text=fn[:500],
                )
            )
    return out


@dataclass(frozen=True)
class Form144Notice:
    accession: str
    available_at: date
    issuer_cik: str
    issuer_name: str
    seller: str
    relationship: str
    shares: float | None
    market_value: float | None
    approx_sale_date: date | None


def parse_form144_xml(xml: str | bytes, accession: str, filed: date) -> list[Form144Notice]:
    """One notice per `securitiesInformation` block. Tags are matched by local name anywhere in
    the document, because the 144 schema nests issuer and seller fields differently across
    versions."""
    root = ET.fromstring(xml)

    def first(name: str, within: ET.Element = root) -> str:
        for el in within.iter():
            if _local(el.tag) == name and (el.text or "").strip():
                return el.text.strip()  # type: ignore[union-attr]
        return ""

    blocks = [el for el in root.iter() if _local(el.tag) == "securitiesInformation"] or [root]
    out = []
    for b in blocks:
        out.append(
            Form144Notice(
                accession=accession,
                available_at=filed,
                issuer_cik=first("issuerCik").lstrip("0"),
                issuer_name=first("issuerName"),
                seller=first("nameOfPersonForWhoseAccountTheSecuritiesAreToBeSold"),
                relationship=first("relationshipToIssuer"),
                shares=_num(first("noOfUnitsSold", b)),
                market_value=_num(first("aggregateMarketValue", b)),
                approx_sale_date=parse_sec_date(first("approxSaleDate", b)),
            )
        )
    return out


@dataclass(frozen=True)
class Holding13F:
    accession: str
    available_at: date  # 13F filing date
    period: date | None  # quarter end
    filer_cik: str
    filer_name: str
    issuer_name: str
    cusip: str
    value_usd: float | None
    shares: float | None
    put_call: str  # "" for the stock itself
    amendment_type: str  # "" for originals, RESTATEMENT or NEW HOLDINGS


def read_13f_dataset(source: Path, filer_ciks: Iterable[str] | None = None) -> list[Holding13F]:
    """INFOTABLE rows joined to SUBMISSION and COVERPAGE, optionally only for `filer_ciks`.

    VALUE is in US dollars from the 2023-01-03 filing period onward and in thousands before; the
    reader converts by filing date. Share rows only (SSHPRNAMTTYPE == SH); principal amounts of
    notes are skipped.
    """
    keep = {c.lstrip("0") for c in filer_ciks} if filer_ciks is not None else None
    t = _open_tables(source)
    subs: dict[str, dict[str, str]] = {}
    for r in t.get("SUBMISSION", iter(())):
        if not (r.get("SUBMISSIONTYPE") or "").startswith("13F-HR"):
            continue
        cik = (r.get("CIK") or "").strip().lstrip("0")
        if keep is not None and cik not in keep:
            continue
        subs[r["ACCESSION_NUMBER"]] = r
    cover: dict[str, dict[str, str]] = {}
    for r in t.get("COVERPAGE", iter(())):
        if r["ACCESSION_NUMBER"] in subs:
            cover[r["ACCESSION_NUMBER"]] = r
    out: list[Holding13F] = []
    for r in t.get("INFOTABLE", iter(())):
        acc = r["ACCESSION_NUMBER"]
        sub = subs.get(acc)
        if sub is None or (r.get("SSHPRNAMTTYPE") or "SH").strip().upper() != "SH":
            continue
        filed = parse_sec_date(sub.get("FILING_DATE"))
        if filed is None:
            continue
        cv = cover.get(acc, {})
        value = _num(r.get("VALUE"))
        if value is not None and filed < date(2023, 1, 3):
            value *= 1000.0
        out.append(
            Holding13F(
                accession=acc,
                available_at=filed,
                period=parse_sec_date(sub.get("PERIODOFREPORT") or cv.get("REPORTCALENDARORQUARTER")),
                filer_cik=(sub.get("CIK") or "").strip().lstrip("0"),
                filer_name=(cv.get("FILINGMANAGER_NAME") or "").strip(),
                issuer_name=(r.get("NAMEOFISSUER") or "").strip(),
                cusip=(r.get("CUSIP") or "").strip().upper(),
                value_usd=value,
                shares=_num(r.get("SSHPRNAMT")),
                put_call=(r.get("PUTCALL") or "").strip().upper(),
                amendment_type=(cv.get("AMENDMENTTYPE") or "").strip().upper()
                if _truthy(cv.get("ISAMENDMENT"))
                else "",
            )
        )
    return out
