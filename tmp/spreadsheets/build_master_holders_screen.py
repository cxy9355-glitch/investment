from __future__ import annotations

import json
import math
import re
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime
from io import StringIO
from pathlib import Path
from typing import Any

import pandas as pd
import requests
import yfinance as yf
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter


ROOT = Path(r"G:\Codex\个人\investment")
OUTPUT_XLSX = ROOT / "output" / "spreadsheet" / "巴芒_喜马拉雅_高瓴_历史持仓筛选_2026-04-16.xlsx"
CACHE_DIR = ROOT / "tmp" / "spreadsheets" / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

SEC_HEADERS = {
    "User-Agent": "research chuxiaoyu test@example.com",
    "Accept-Encoding": "gzip, deflate",
}
WEB_HEADERS = {
    "User-Agent": "Mozilla/5.0",
}
SEARCH_HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "X-Requested-With": "XMLHttpRequest",
}

HISTORY_START = pd.Timestamp("2015-01-01")
TOP_N = 200


@dataclass(frozen=True)
class ManagerEntity:
    group: str
    entity: str
    cik: str


MANAGERS = [
    ManagerEntity("巴芒系", "Berkshire Hathaway Inc", "0001067983"),
    ManagerEntity("巴芒系", "Daily Journal Corp", "0000783412"),
    ManagerEntity("喜马拉雅资本", "Himalaya Capital Management LLC", "0001709323"),
    ManagerEntity("高瓴资本", "HHLR Advisors, Ltd.", "0001762304"),
]


def cached_get_json(url: str, headers: dict[str, str], cache_key: str, sleep_s: float = 0.12) -> Any:
    cache_path = CACHE_DIR / f"{cache_key}.json"
    if cache_path.exists():
        return json.loads(cache_path.read_text(encoding="utf-8"))
    resp = requests.get(url, headers=headers, timeout=40)
    resp.raise_for_status()
    cache_path.write_text(resp.text, encoding="utf-8")
    time.sleep(sleep_s)
    return resp.json()


def cached_get_text(
    url: str,
    headers: dict[str, str],
    cache_key: str,
    method: str = "GET",
    data: dict[str, Any] | None = None,
    sleep_s: float = 0.12,
) -> str:
    suffix = "post" if method.upper() == "POST" else "txt"
    cache_path = CACHE_DIR / f"{cache_key}.{suffix}"
    if cache_path.exists():
        return cache_path.read_text(encoding="utf-8")
    if method.upper() == "POST":
        resp = requests.post(url, headers=headers, data=data, timeout=40)
    else:
        resp = requests.get(url, headers=headers, timeout=40)
    resp.raise_for_status()
    cache_path.write_text(resp.text, encoding="utf-8")
    time.sleep(sleep_s)
    return resp.text


def normalize_issuer(name: str) -> str:
    cleaned = re.sub(r"[^A-Z0-9]+", " ", name.upper()).strip()
    cleaned = re.sub(r"\bHLDGS\b", "HOLDINGS", cleaned)
    cleaned = re.sub(r"\bFINL\b", "FINANCIAL", cleaned)
    cleaned = re.sub(r"\bINTL\b", "INTERNATIONAL", cleaned)
    cleaned = re.sub(r"\bCOMMUNICATIONS INC DEL NEW\b", "COMMUNICATIONS", cleaned)
    stopwords = {
        "INC", "CORP", "CORPORATION", "CO", "COS", "PLC", "LTD", "LIMITED", "SA", "NV",
        "LP", "LLC", "DEL", "NEW", "HOLDINGS", "HOLDING", "GROUP", "CL", "CLASS",
        "SPONSORED", "ADR", "ADS", "ORD", "SHS", "THE",
    }
    tokens = [token for token in re.sub(r"\s+", " ", cleaned).split() if token not in stopwords]
    return " ".join(tokens)


def load_submission_rows(cik: str) -> list[dict[str, Any]]:
    main = cached_get_json(
        f"https://data.sec.gov/submissions/CIK{cik}.json",
        headers=SEC_HEADERS,
        cache_key=f"sec_submissions_{cik}",
    )
    chunks = [main["filings"]["recent"]]
    for entry in main["filings"].get("files", []):
        payload = cached_get_json(
            f"https://data.sec.gov/submissions/{entry['name']}",
            headers=SEC_HEADERS,
            cache_key=entry["name"].replace(".json", ""),
        )
        chunks.append(payload)

    rows: list[dict[str, Any]] = []
    for chunk in chunks:
        forms = chunk["form"]
        filing_dates = chunk["filingDate"]
        accession_numbers = chunk["accessionNumber"]
        report_dates = chunk.get("reportDate", [""] * len(forms))
        for form, filing_date, accession_number, report_date in zip(forms, filing_dates, accession_numbers, report_dates):
            if form not in {"13F-HR", "13F-HR/A"}:
                continue
            if pd.Timestamp(report_date) < HISTORY_START:
                continue
            rows.append(
                {
                    "form": form,
                    "filing_date": filing_date,
                    "report_date": report_date,
                    "accession_number": accession_number,
                }
            )
    deduped: dict[str, dict[str, Any]] = {}
    for row in rows:
        key = row["report_date"]
        prev = deduped.get(key)
        if not prev or (row["filing_date"], row["form"]) > (prev["filing_date"], prev["form"]):
            deduped[key] = row
    return sorted(deduped.values(), key=lambda x: x["report_date"])


def choose_info_table_file(cik: str, accession_number: str) -> str | None:
    accession_no_dash = accession_number.replace("-", "")
    payload = cached_get_json(
        f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession_no_dash}/index.json",
        headers=SEC_HEADERS,
        cache_key=f"sec_index_{cik}_{accession_no_dash}",
    )
    names = [item["name"] for item in payload["directory"]["item"]]
    xml_candidates = [
        name
        for name in names
        if name.lower().endswith(".xml")
        and "primary_doc" not in name.lower()
        and "index" not in name.lower()
        and not name.lower().startswith("xsl")
    ]
    if not xml_candidates:
        return None
    preferred = sorted(
        xml_candidates,
        key=lambda name: (
            0 if "info" in name.lower() else 1,
            0 if "13f" in name.lower() else 1,
            len(name),
        ),
    )
    return preferred[0]


def parse_information_table(cik: str, accession_number: str) -> list[dict[str, Any]]:
    xml_name = choose_info_table_file(cik, accession_number)
    if not xml_name:
        return []
    accession_no_dash = accession_number.replace("-", "")
    xml_text = cached_get_text(
        f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession_no_dash}/{xml_name}",
        headers=SEC_HEADERS,
        cache_key=f"sec_info_{cik}_{accession_no_dash}_{xml_name.replace('.', '_')}",
    )
    ns = {"n": "http://www.sec.gov/edgar/document/thirteenf/informationtable"}
    root = ET.fromstring(xml_text)
    rows: list[dict[str, Any]] = []
    for node in root.findall("n:infoTable", ns):
        issuer = (node.findtext("n:nameOfIssuer", default="", namespaces=ns) or "").strip()
        title_class = (node.findtext("n:titleOfClass", default="", namespaces=ns) or "").strip()
        cusip = (node.findtext("n:cusip", default="", namespaces=ns) or "").strip()
        value = node.findtext("n:value", default="", namespaces=ns) or "0"
        shares = node.findtext("n:shrsOrPrnAmt/n:sshPrnamt", default="", namespaces=ns) or "0"
        share_type = (node.findtext("n:shrsOrPrnAmt/n:sshPrnamtType", default="", namespaces=ns) or "").strip()
        put_call = (node.findtext("n:putCall", default="", namespaces=ns) or "").strip()
        discretion = (node.findtext("n:investmentDiscretion", default="", namespaces=ns) or "").strip()
        rows.append(
            {
                "issuer_name": issuer,
                "issuer_norm": normalize_issuer(issuer),
                "title_class": title_class,
                "cusip": cusip,
                "value_usd_thousand": float(value or 0),
                "shares": float(shares or 0),
                "share_type": share_type,
                "put_call": put_call,
                "investment_discretion": discretion,
            }
        )
    return rows


def build_holdings_detail() -> pd.DataFrame:
    all_rows: list[dict[str, Any]] = []
    for manager in MANAGERS:
        filing_rows = load_submission_rows(manager.cik)
        print(f"{manager.entity}: filings={len(filing_rows)}")
        for filing in filing_rows:
            info_rows = parse_information_table(manager.cik, filing["accession_number"])
            if not info_rows:
                continue
            chunk = pd.DataFrame(info_rows)
            if chunk.empty:
                continue
            chunk = (
                chunk.groupby(["issuer_name", "issuer_norm", "title_class", "cusip", "share_type", "put_call", "investment_discretion"], as_index=False)
                .agg({"value_usd_thousand": "sum", "shares": "sum"})
            )
            chunk["group"] = manager.group
            chunk["manager_entity"] = manager.entity
            chunk["manager_cik"] = manager.cik
            chunk["report_date"] = filing["report_date"]
            chunk["filing_date"] = filing["filing_date"]
            chunk["form"] = filing["form"]
            chunk["accession_number"] = filing["accession_number"]
            all_rows.extend(chunk.to_dict("records"))
    detail = pd.DataFrame(all_rows)
    detail["report_date"] = pd.to_datetime(detail["report_date"])
    detail["filing_date"] = pd.to_datetime(detail["filing_date"])
    detail = detail.sort_values(["group", "manager_entity", "report_date", "value_usd_thousand"], ascending=[True, True, True, False])
    return detail


def search_companies_marketcap(query: str) -> list[dict[str, Any]]:
    text = cached_get_text(
        "https://companiesmarketcap.com/search.do",
        headers=SEARCH_HEADERS,
        cache_key=f"cmc_search_{re.sub(r'[^A-Za-z0-9]+', '_', query)[:80]}",
        method="POST",
        data={"query": query},
        sleep_s=0.05,
    )
    return json.loads(text)


def choose_search_match(results: list[dict[str, Any]], issuer_norm: str, title_class: str) -> dict[str, Any] | None:
    if not results:
        return None
    filtered = [item for item in results if item.get("type") == "stock"]
    if not filtered:
        return None
    issuer_tokens = set(issuer_norm.split())
    best: tuple[float, dict[str, Any]] | None = None
    for item in filtered:
        name_norm = normalize_issuer(item.get("name", ""))
        name_tokens = set(name_norm.split())
        overlap = len(issuer_tokens & name_tokens) / max(1, len(issuer_tokens))
        score = overlap
        score -= 0.08 * max(0, len(name_tokens - issuer_tokens))
        score -= 0.12 * max(0, len(issuer_tokens - name_tokens))
        if title_class.upper().startswith("ADS") or "ADR" in title_class.upper():
            if "." not in item.get("identifier", "") and item.get("identifier", "").isupper():
                score += 0.25
        identifier = item.get("identifier", "")
        if "." in identifier or any(ch.isdigit() for ch in identifier):
            score -= 0.35
        elif identifier.isupper() and 1 <= len(identifier) <= 5:
            score += 0.15
        if best is None or score > best[0]:
            best = (score, item)
    return best[1] if best and best[0] >= 0.3 else filtered[0]


def extract_current_ratio(html: str, ratio_label: str) -> float | None:
    patterns = [
        rf"{ratio_label} ratio as of .*?<span class=\"background-ya\">([^<]+)</span>",
        rf"current price-to-{ratio_label.lower()} ratio .*?<strong>([^<]+)</strong>",
    ]
    for pattern in patterns:
        match = re.search(pattern, html, re.S | re.I)
        if match:
            try:
                return float(match.group(1).replace(",", ""))
            except ValueError:
                return None
    return None


def extract_history_table(html: str) -> list[float]:
    try:
        tables = pd.read_html(StringIO(html))
    except ValueError:
        return []
    for table in tables:
        cols = [str(col).strip().lower() for col in table.columns]
        if "year" in cols[0] and any("ratio" in col for col in cols):
            ratio_col = next(col for col in table.columns if "ratio" in str(col).lower())
            values = pd.to_numeric(table[ratio_col], errors="coerce").dropna().tolist()
            return [float(v) for v in values if pd.notna(v)]
    return []


def percentile_rank(current: float | None, history_values: list[float]) -> float | None:
    if current is None:
        return None
    valid = [v for v in history_values if v is not None and pd.notna(v) and not math.isinf(v)]
    if not valid:
        return None
    less_or_equal = sum(1 for v in valid if v <= current)
    return less_or_equal / len(valid)


def fetch_valuation_metrics(ticker: str, slug: str) -> dict[str, Any]:
    pe_html = cached_get_text(
        f"https://companiesmarketcap.com/{slug}/pe-ratio/",
        headers=WEB_HEADERS,
        cache_key=f"cmc_pe_{slug}",
        sleep_s=0.05,
    )
    pb_html = cached_get_text(
        f"https://companiesmarketcap.com/{slug}/pb-ratio/",
        headers=WEB_HEADERS,
        cache_key=f"cmc_pb_{slug}",
        sleep_s=0.05,
    )
    pe_current = extract_current_ratio(pe_html, "P/E")
    pb_current = extract_current_ratio(pb_html, "P/B")
    pe_history = extract_history_table(pe_html)
    pb_history = extract_history_table(pb_html)

    return {
        "ticker": ticker,
        "cmc_slug": slug,
        "pe_ttm": pe_current,
        "pb_ttm": pb_current,
        "pe_hist_years": len(pe_history),
        "pb_hist_years": len(pb_history),
        "pe_hist_percentile": percentile_rank(pe_current, [v for v in pe_history if v > 0]),
        "pb_hist_percentile": percentile_rank(pb_current, [v for v in pb_history if v > 0]),
    }


def fetch_yahoo_metrics(ticker: str) -> dict[str, Any]:
    cache_path = CACHE_DIR / f"yf_{ticker.replace('.', '_')}.json"
    if cache_path.exists():
        payload = json.loads(cache_path.read_text(encoding="utf-8"))
    else:
        yf_ticker = yf.Ticker(ticker)
        payload = {
            "info": yf_ticker.info,
            "fast": dict(yf_ticker.fast_info),
        }
        cache_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        time.sleep(0.05)

    info = payload["info"]
    fast = payload["fast"]

    def pct_value(value: Any) -> float | None:
        if value is None or (isinstance(value, float) and math.isnan(value)):
            return None
        if abs(value) > 1.5:
            return float(value) / 100
        return float(value)

    return {
        "ticker": ticker,
        "company_name_market": info.get("longName"),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "country": info.get("country"),
        "currency": info.get("currency"),
        "current_price": fast.get("lastPrice"),
        "market_cap_usd": info.get("marketCap"),
        "roe": pct_value(info.get("returnOnEquity")),
        "roa": pct_value(info.get("returnOnAssets")),
        "dividend_yield": pct_value(info.get("dividendYield")),
        "gross_margin": pct_value(info.get("grossMargins")),
        "operating_margin": pct_value(info.get("operatingMargins")),
        "net_margin": pct_value(info.get("profitMargins")),
        "debt_to_equity": info.get("debtToEquity"),
        "revenue_growth": pct_value(info.get("revenueGrowth")),
        "earnings_growth": pct_value(info.get("earningsGrowth")),
        "current_ratio": info.get("currentRatio"),
        "quick_ratio": info.get("quickRatio"),
    }


def pick_stock_universe(detail: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    current_rows = []
    for entity, group_df in detail.groupby("manager_entity"):
        latest_report = group_df["report_date"].max()
        current_rows.append(group_df[group_df["report_date"] == latest_report])
    current_holdings = pd.concat(current_rows, ignore_index=True)

    summary = (
        detail.groupby(["issuer_name", "issuer_norm"], as_index=False)
        .agg(
            groups_ever=("group", lambda s: ", ".join(sorted(set(s)))),
            entities_ever=("manager_entity", lambda s: ", ".join(sorted(set(s)))),
            first_report_date=("report_date", "min"),
            last_report_date=("report_date", "max"),
            quarters_held=("report_date", "nunique"),
            total_value_usd_thousand=("value_usd_thousand", "sum"),
        )
    )

    current_summary = (
        current_holdings.groupby(["issuer_name", "issuer_norm"], as_index=False)
        .agg(
            groups_current=("group", lambda s: ", ".join(sorted(set(s)))),
            entities_current=("manager_entity", lambda s: ", ".join(sorted(set(s)))),
            latest_value_usd_thousand=("value_usd_thousand", "sum"),
        )
    )
    summary = summary.merge(current_summary, how="left", on=["issuer_name", "issuer_norm"])
    summary["is_current_any"] = summary["groups_current"].notna()
    return summary, current_holdings


def safe_avg(values: list[float | None]) -> float | None:
    valid = [v for v in values if v is not None and pd.notna(v)]
    return sum(valid) / len(valid) if valid else None


def format_sheet(ws, df: pd.DataFrame, freeze_cell: str = "A2") -> None:
    ws.freeze_panes = freeze_cell
    header_fill = PatternFill("solid", fgColor="1F4E78")
    header_font = Font(color="FFFFFF", bold=True)
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
    for idx, col in enumerate(df.columns, start=1):
        if len(df):
            sample_len = df[col].map(lambda x: len(str(x)) if pd.notna(x) else 0).quantile(0.9)
        else:
            sample_len = 10
        width = min(24, max(10, int(max(len(str(col)), sample_len)) + 2))
        ws.column_dimensions[get_column_letter(idx)].width = width


def write_workbook(candidates: pd.DataFrame, all_summary: pd.DataFrame, current_holdings: pd.DataFrame, detail: pd.DataFrame) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "候选池_排序"
    for row in [candidates.columns.tolist(), *candidates.replace({pd.NA: None}).to_records(index=False).tolist()]:
        ws.append(list(row))
    format_sheet(ws, candidates)

    ws2 = wb.create_sheet("全量标的池")
    for row in [all_summary.columns.tolist(), *all_summary.replace({pd.NA: None}).to_records(index=False).tolist()]:
        ws2.append(list(row))
    format_sheet(ws2, all_summary)

    ws3 = wb.create_sheet("当前持仓")
    for row in [current_holdings.columns.tolist(), *current_holdings.replace({pd.NA: None}).to_records(index=False).tolist()]:
        ws3.append(list(row))
    format_sheet(ws3, current_holdings)

    ws4 = wb.create_sheet("历史13F明细")
    detail_out = detail.copy()
    detail_out["report_date"] = detail_out["report_date"].dt.date
    detail_out["filing_date"] = detail_out["filing_date"].dt.date
    for row in [detail_out.columns.tolist(), *detail_out.replace({pd.NA: None}).to_records(index=False).tolist()]:
        ws4.append(list(row))
    format_sheet(ws4, detail_out)

    wb.save(OUTPUT_XLSX)


def main() -> None:
    detail = build_holdings_detail()
    detail = detail[
        detail["put_call"].fillna("").eq("")
        & ~detail["title_class"].str.upper().fillna("").str.contains("CALL|PUT|NOTE|DEBT|WARRANT|RIGHT")
    ].copy()
    summary, current_holdings = pick_stock_universe(detail)

    search_payloads = []
    for row in summary.itertuples(index=False):
        results = search_companies_marketcap(row.issuer_name)
        match = choose_search_match(results, row.issuer_norm, "")
        search_payloads.append(
            {
                "issuer_name": row.issuer_name,
                "issuer_norm": row.issuer_norm,
                "cmc_match": match,
            }
        )
    match_df = pd.DataFrame(search_payloads)
    summary = summary.merge(match_df, on=["issuer_name", "issuer_norm"], how="left")
    summary["ticker"] = summary["cmc_match"].map(lambda x: x.get("identifier") if isinstance(x, dict) else None)
    summary["cmc_slug"] = summary["cmc_match"].map(lambda x: x.get("url") if isinstance(x, dict) else None)
    summary["cmc_type"] = summary["cmc_match"].map(lambda x: x.get("type") if isinstance(x, dict) else None)
    summary = summary[summary["cmc_type"].eq("stock") & summary["ticker"].notna() & summary["cmc_slug"].notna()].copy()
    summary = summary.drop(columns=["cmc_match"])
    detail_mapped = detail.merge(
        summary[["issuer_name", "issuer_norm", "ticker", "cmc_slug"]],
        on=["issuer_name", "issuer_norm"],
        how="inner",
    )
    current_holdings = current_holdings.merge(
        summary[["issuer_name", "issuer_norm", "ticker", "cmc_slug"]],
        on=["issuer_name", "issuer_norm"],
        how="left",
    )

    ticker_hist = (
        detail_mapped.groupby(["ticker", "cmc_slug"], as_index=False)
        .agg(
            issuer_name=("issuer_name", lambda s: " | ".join(sorted(set(s))[:4])),
            groups_ever=("group", lambda s: ", ".join(sorted(set(s)))),
            entities_ever=("manager_entity", lambda s: ", ".join(sorted(set(s)))),
            first_report_date=("report_date", "min"),
            last_report_date=("report_date", "max"),
            quarters_held=("report_date", "nunique"),
            total_value_usd_thousand=("value_usd_thousand", "sum"),
        )
    )
    ticker_current = (
        current_holdings.dropna(subset=["ticker"])
        .groupby(["ticker", "cmc_slug"], as_index=False)
        .agg(
            groups_current=("group", lambda s: ", ".join(sorted(set(s)))),
            entities_current=("manager_entity", lambda s: ", ".join(sorted(set(s)))),
            latest_value_usd_thousand=("value_usd_thousand", "sum"),
        )
    )
    summary = ticker_hist.merge(ticker_current, on=["ticker", "cmc_slug"], how="left")
    summary["is_current_any"] = summary["groups_current"].notna()

    valuation_rows = []
    for row in summary[["ticker", "cmc_slug"]].drop_duplicates().itertuples(index=False):
        try:
            valuation_rows.append(fetch_valuation_metrics(row.ticker, row.cmc_slug))
            print(f"valuation ok: {row.ticker}")
        except Exception as exc:
            print(f"valuation failed: {row.ticker} {type(exc).__name__}")
    valuation_df = pd.DataFrame(valuation_rows)

    all_summary = summary.merge(valuation_df, on=["ticker", "cmc_slug"], how="left")
    all_summary["valuation_score"] = all_summary.apply(
        lambda r: safe_avg([r.get("pe_hist_percentile"), r.get("pb_hist_percentile")]),
        axis=1,
    )
    all_summary["bar_mung_current"] = all_summary["groups_current"].fillna("").str.contains("巴芒系")
    all_summary["himalaya_current"] = all_summary["groups_current"].fillna("").str.contains("喜马拉雅资本")
    all_summary["hillhouse_current"] = all_summary["groups_current"].fillna("").str.contains("高瓴资本")

    candidate_cols = [
        "ticker", "company_name_market", "sector", "industry", "country",
        "pe_ttm", "pe_hist_percentile", "pb_ttm", "pb_hist_percentile", "valuation_score",
        "roe", "roa", "dividend_yield", "gross_margin", "operating_margin", "net_margin",
        "debt_to_equity", "revenue_growth", "earnings_growth", "current_ratio", "quick_ratio",
        "current_price", "market_cap_usd", "groups_ever", "groups_current", "entities_ever", "entities_current",
        "first_report_date", "last_report_date", "quarters_held", "latest_value_usd_thousand",
        "bar_mung_current", "himalaya_current", "hillhouse_current", "issuer_name", "cmc_slug",
    ]
    ranked = all_summary[all_summary["valuation_score"].notna()].sort_values(
        ["valuation_score", "pe_hist_percentile", "pb_hist_percentile", "latest_value_usd_thousand"],
        ascending=[True, True, True, False],
    )
    selected = ranked.head(TOP_N)[["ticker"]].drop_duplicates()
    yahoo_rows = []
    for row in selected.itertuples(index=False):
        try:
            yahoo_rows.append(fetch_yahoo_metrics(row.ticker))
            print(f"yahoo ok: {row.ticker}")
        except Exception as exc:
            print(f"yahoo failed: {row.ticker} {type(exc).__name__}")
    yahoo_df = pd.DataFrame(yahoo_rows)
    ranked = ranked.merge(yahoo_df, on="ticker", how="left")
    candidates = ranked[candidate_cols].head(TOP_N).reset_index(drop=True)
    candidates.insert(0, "sort_rank", range(1, len(candidates) + 1))

    write_workbook(candidates, all_summary, current_holdings, detail)
    print(f"saved: {OUTPUT_XLSX}")


if __name__ == "__main__":
    main()
