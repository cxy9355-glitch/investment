from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

import build_master_holders_screen as base


ROOT = base.ROOT
OUTPUT_XLSX = ROOT / "机构持仓研究" / "长期持有核心样本数据集_2026-04-17.xlsx"
WORKBOOK_PATH = ROOT / "机构持仓研究" / "巴芒_喜马拉雅_高瓴_历史持仓筛选_2026-04-17.xlsx"

CORE_SAMPLE = [
    ("AAPL", "美股长期核心仓，作为跨机构长期持有正样本"),
    ("AMZN", "美股平台型龙头，作为当前仍持有的代表样本"),
    ("BABA", "中概 ADR，且当前持有主体存在实体级差异"),
    ("CHTR", "巴芒系长期持有的高热度样本"),
    ("KHC", "高热度但当前经营质量存在争议的样本"),
    ("MCO", "高质量金融信息服务公司，作为长期持有正样本"),
    ("OXY", "能源样本，便于比较当前仍持有与经营波动"),
    ("PDD", "中概成长样本，当前仍被多家机构持有"),
    ("TSM", "ADR 半导体龙头，检验 20-F / IFRS 覆盖"),
    ("WB", "已退出的中概 ADR 样本"),
    ("BZ", "中概 ADR，作为当前不在仓但经营较强的样本"),
    ("TME", "中概 ADR，检验 IFRS 口径的年度字段"),
]

ANNUAL_FORMS = {"10-K", "10-K/A", "20-F", "20-F/A", "40-F", "40-F/A"}

CONCEPT_MAP = {
    "revenue": [
        ("us-gaap", "Revenues"),
        ("us-gaap", "SalesRevenueNet"),
        ("us-gaap", "RevenueFromContractWithCustomerExcludingAssessedTax"),
        ("us-gaap", "RevenueFromContractWithCustomerIncludingAssessedTax"),
        ("ifrs-full", "Revenue"),
        ("ifrs-full", "RevenueFromContractsWithCustomers"),
        ("ifrs-full", "RevenueFromSaleOfGoods"),
        ("ifrs-full", "RevenueFromRenderingOfTelecommunicationServices"),
        ("ifrs-full", "RevenueFromRenderingOfAdvertisingServices"),
    ],
    "gross_profit": [
        ("us-gaap", "GrossProfit"),
        ("ifrs-full", "GrossProfit"),
    ],
    "net_income": [
        ("us-gaap", "NetIncomeLoss"),
        ("us-gaap", "ProfitLoss"),
        ("ifrs-full", "ProfitLoss"),
    ],
    "assets": [
        ("us-gaap", "Assets"),
        ("ifrs-full", "Assets"),
    ],
    "equity": [
        ("us-gaap", "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"),
        ("us-gaap", "StockholdersEquity"),
        ("ifrs-full", "Equity"),
    ],
    "liabilities": [
        ("us-gaap", "Liabilities"),
        ("ifrs-full", "Liabilities"),
    ],
    "shares_outstanding": [
        ("us-gaap", "CommonStockSharesOutstanding"),
        ("dei", "EntityCommonStockSharesOutstanding"),
    ],
    "cfo": [
        ("us-gaap", "NetCashProvidedByUsedInOperatingActivities"),
        ("us-gaap", "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations"),
        ("ifrs-full", "CashFlowsFromUsedInOperatingActivities"),
    ],
    "capex": [
        ("us-gaap", "PaymentsToAcquirePropertyPlantAndEquipment"),
        ("ifrs-full", "PurchaseOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities"),
    ],
}


def _score_annual_candidate(df: pd.DataFrame) -> tuple[int, int, float]:
    if df.empty:
        return (0, 0, 0.0)
    latest_year = int(df["fiscal_year"].max())
    median_abs = float(df["value"].abs().median()) if "value" in df.columns else 0.0
    return (len(df), latest_year, median_abs)


def load_reference_lookup() -> pd.DataFrame:
    valuation = pd.read_excel(WORKBOOK_PATH, sheet_name="估值总表")
    sample_df = pd.DataFrame(CORE_SAMPLE, columns=["ticker", "sample_reason"])
    ref = sample_df.merge(
        valuation[["代码", "中文公司名", "英文公司名", "市场"]],
        left_on="ticker",
        right_on="代码",
        how="left",
    ).drop(columns=["代码"])
    return ref


def build_core_holdings_history(ref: pd.DataFrame) -> pd.DataFrame:
    detail = base.build_holdings_detail()
    detail = detail[
        detail["put_call"].fillna("").eq("")
        & ~detail["title_class"].str.upper().fillna("").str.contains("CALL|PUT|NOTE|DEBT|WARRANT|RIGHT")
    ].copy()

    issuer_level = (
        detail.groupby(["issuer_name", "issuer_norm"], as_index=False)
        .agg(title_class=("title_class", lambda s: " | ".join(sorted(set(s.dropna()))[:4])))
    )

    mappings = []
    for row in issuer_level.itertuples(index=False):
        results = base.search_companies_marketcap(row.issuer_name)
        match = base.choose_search_match(results, row.issuer_norm, row.title_class or "")
        mappings.append(
            {
                "issuer_name": row.issuer_name,
                "issuer_norm": row.issuer_norm,
                "ticker": match.get("identifier") if isinstance(match, dict) else None,
            }
        )
    mapping_df = pd.DataFrame(mappings)
    detail = detail.merge(mapping_df, on=["issuer_name", "issuer_norm"], how="left")
    detail = detail[detail["ticker"].isin(ref["ticker"])].copy()
    detail["value_usd"] = detail["value_usd_thousand"] * 1000

    totals = (
        detail.groupby(["manager_entity", "report_date"], as_index=False)
        .agg(entity_total_value_usd_thousand=("value_usd_thousand", "sum"))
    )
    detail = detail.merge(totals, on=["manager_entity", "report_date"], how="left")
    detail["position_weight"] = detail["value_usd_thousand"] / detail["entity_total_value_usd_thousand"]

    grouped = (
        detail.groupby(["manager_entity", "group", "manager_cik", "ticker", "report_date"], as_index=False)
        .agg(
            filing_date=("filing_date", "max"),
            form=("form", "last"),
            accession_number=("accession_number", "last"),
            value_usd_thousand=("value_usd_thousand", "sum"),
            value_usd=("value_usd", "sum"),
            shares=("shares", "sum"),
            position_weight=("position_weight", "sum"),
            issuer_name_raw=("issuer_name", lambda s: " | ".join(sorted(set(s))[:6])),
            title_class=("title_class", lambda s: " | ".join(sorted(set(s))[:4])),
            cusip=("cusip", lambda s: " | ".join(sorted(set(x for x in s if x))[:4])),
        )
    )
    grouped = grouped.merge(ref, on="ticker", how="left")
    grouped = grouped.sort_values(["manager_entity", "ticker", "report_date"]).reset_index(drop=True)
    grouped["is_first_seen"] = grouped.groupby(["manager_entity", "ticker"]).cumcount().eq(0)

    latest_dates = grouped.groupby("manager_entity")["report_date"].transform("max")
    grouped["is_current"] = grouped["report_date"].eq(latest_dates)
    grouped["source"] = "SEC 13F"
    grouped["value_unit"] = "USD"
    grouped["position_weight_unit"] = "ratio"
    grouped["source_status"] = "official"
    grouped["quarters_held_by_entity"] = grouped.groupby(["manager_entity", "ticker"])["report_date"].transform("nunique")
    grouped["years_held_by_entity"] = grouped.groupby(["manager_entity", "ticker"])["report_date"].transform(lambda s: s.dt.year.nunique())

    return grouped[
        [
            "ticker",
            "中文公司名",
            "英文公司名",
            "市场",
            "sample_reason",
            "group",
            "manager_entity",
            "manager_cik",
            "report_date",
            "filing_date",
            "form",
            "accession_number",
            "value_usd_thousand",
            "value_usd",
            "shares",
            "position_weight",
            "is_first_seen",
            "is_current",
            "quarters_held_by_entity",
            "years_held_by_entity",
            "issuer_name_raw",
            "title_class",
            "cusip",
            "source",
            "value_unit",
            "position_weight_unit",
            "source_status",
        ]
    ]


def load_sec_ticker_map() -> dict[str, str]:
    payload = base.cached_get_json(
        "https://www.sec.gov/files/company_tickers.json",
        headers=base.SEC_HEADERS,
        cache_key="sec_company_tickers",
    )
    return {item["ticker"]: str(item["cik_str"]).zfill(10) for item in payload.values()}


def fetch_companyfacts(cik: str) -> dict[str, Any]:
    return base.cached_get_json(
        f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json",
        headers=base.SEC_HEADERS,
        cache_key=f"sec_companyfacts_{cik}",
        sleep_s=0.05,
    )


def pick_unit(units_map: dict[str, list[dict[str, Any]]]) -> str | None:
    if "USD" in units_map:
        return "USD"
    if "CNY" in units_map:
        return "CNY"
    if "TWD" in units_map:
        return "TWD"
    if "shares" in units_map:
        return "shares"
    return next(iter(units_map.keys()), None)


def extract_annual_concept(companyfacts: dict[str, Any], field_name: str) -> pd.DataFrame:
    candidates: list[pd.DataFrame] = []
    for taxonomy, concept in CONCEPT_MAP[field_name]:
        rows: list[dict[str, Any]] = []
        concept_block = companyfacts.get("facts", {}).get(taxonomy, {}).get(concept)
        if not concept_block:
            continue
        units_map = concept_block.get("units", {})
        unit = pick_unit(units_map)
        if unit is None:
            continue
        for item in units_map[unit]:
            form = item.get("form")
            if form not in ANNUAL_FORMS:
                continue
            fy = item.get("fy")
            if fy is None:
                end = item.get("end")
                if not end:
                    continue
                fy = pd.Timestamp(end).year
            fp = item.get("fp")
            if fp not in {None, "FY"}:
                continue
            rows.append(
                {
                    "fiscal_year": int(fy),
                    "value": item.get("val"),
                    "unit": unit,
                    "form": form,
                    "filed": item.get("filed"),
                    "end": item.get("end"),
                    "taxonomy": taxonomy,
                    "concept": concept,
                }
            )
        if not rows:
            continue
        df = pd.DataFrame(rows)
        df["filed"] = pd.to_datetime(df["filed"])
        df = df.sort_values(["fiscal_year", "filed"], ascending=[True, False]).drop_duplicates(subset=["fiscal_year"], keep="first")
        candidates.append(df)
    if not candidates:
        return pd.DataFrame(columns=["fiscal_year", "value", "unit", "form", "filed", "end", "taxonomy", "concept"])
    candidates = sorted(candidates, key=_score_annual_candidate, reverse=True)
    merged = pd.concat(candidates, ignore_index=True)
    merged = merged.sort_values(["fiscal_year", "filed"], ascending=[True, False]).drop_duplicates(subset=["fiscal_year"], keep="first")
    return merged.reset_index(drop=True)


def build_annual_operating_quality(ref: pd.DataFrame) -> pd.DataFrame:
    ticker_map = load_sec_ticker_map()
    all_rows: list[dict[str, Any]] = []
    for row in ref.itertuples(index=False):
        cik = ticker_map.get(row.ticker)
        if not cik:
            all_rows.append(
                {
                    "ticker": row.ticker,
                    "中文公司名": row.中文公司名,
                    "英文公司名": row.英文公司名,
                    "市场": row.市场,
                    "sample_reason": row.sample_reason,
                    "source_status": "missing_cik",
                }
            )
            continue

        facts = fetch_companyfacts(cik)
        extracted = {field: extract_annual_concept(facts, field) for field in CONCEPT_MAP}
        years = sorted({int(y) for df in extracted.values() for y in df.get("fiscal_year", [])})
        if not years:
            all_rows.append(
                {
                    "ticker": row.ticker,
                    "中文公司名": row.中文公司名,
                    "英文公司名": row.英文公司名,
                    "市场": row.市场,
                    "sample_reason": row.sample_reason,
                    "source_status": "no_companyfacts_annual_data",
                    "companyfacts_cik": cik,
                }
            )
            continue

        for fiscal_year in years:
            record: dict[str, Any] = {
                "ticker": row.ticker,
                "中文公司名": row.中文公司名,
                "英文公司名": row.英文公司名,
                "市场": row.市场,
                "sample_reason": row.sample_reason,
                "companyfacts_cik": cik,
                "fiscal_year": fiscal_year,
                "source_status": "official_or_missing",
            }
            currency = None
            forms = []
            for field, df in extracted.items():
                hit = df[df["fiscal_year"].eq(fiscal_year)]
                if hit.empty:
                    record[field] = None
                    record[f"{field}_source_concept"] = None
                    record[f"{field}_source_form"] = None
                    record[f"{field}_source_filed"] = None
                    continue
                item = hit.iloc[0]
                record[field] = item["value"]
                record[f"{field}_source_concept"] = f"{item['taxonomy']}:{item['concept']}"
                record[f"{field}_source_form"] = item["form"]
                record[f"{field}_source_filed"] = item["filed"].date()
                forms.append(item["form"])
                if currency is None and item["unit"] not in {"shares"}:
                    currency = item["unit"]
            record["currency"] = currency
            record["source_forms"] = " | ".join(sorted(set(forms)))

            revenue = record.get("revenue")
            gross_profit = record.get("gross_profit")
            net_income = record.get("net_income")
            assets = record.get("assets")
            equity = record.get("equity")
            liabilities = record.get("liabilities")
            cfo = record.get("cfo")
            capex = record.get("capex")

            if liabilities is None and assets is not None and equity is not None:
                liabilities = assets - equity
                record["liabilities"] = liabilities
                record["liabilities_source_concept"] = "derived:assets_minus_equity"
                record["liabilities_source_form"] = record.get("assets_source_form") or record.get("equity_source_form")
                record["liabilities_source_filed"] = record.get("assets_source_filed") or record.get("equity_source_filed")

            if equity is None and assets is not None and liabilities is not None:
                equity = assets - liabilities
                record["equity"] = equity
                record["equity_source_concept"] = "derived:assets_minus_liabilities"
                record["equity_source_form"] = record.get("assets_source_form") or record.get("liabilities_source_form")
                record["equity_source_filed"] = record.get("assets_source_filed") or record.get("liabilities_source_filed")

            record["gross_margin"] = gross_profit / revenue if revenue not in {None, 0} and gross_profit is not None else None
            record["net_margin"] = net_income / revenue if revenue not in {None, 0} and net_income is not None else None
            record["roe"] = net_income / equity if equity not in {None, 0} and net_income is not None else None
            record["roa"] = net_income / assets if assets not in {None, 0} and net_income is not None else None
            record["debt_to_equity"] = liabilities / equity if equity not in {None, 0} and liabilities is not None else None
            record["fcf"] = cfo - capex if cfo is not None and capex is not None else None
            record["fcf_margin"] = record["fcf"] / revenue if revenue not in {None, 0} and record["fcf"] is not None else None

            all_rows.append(record)

    annual = pd.DataFrame(all_rows)
    if "fiscal_year" in annual.columns:
        annual = annual.sort_values(["ticker", "fiscal_year"]).reset_index(drop=True)
    return annual


def write_workbook(ref: pd.DataFrame, holdings: pd.DataFrame, annual: pd.DataFrame) -> None:
    with pd.ExcelWriter(OUTPUT_XLSX, engine="openpyxl") as writer:
        ref.to_excel(writer, sheet_name="样本说明", index=False)
        holdings.to_excel(writer, sheet_name="实体级持仓历史", index=False)
        annual.to_excel(writer, sheet_name="年度经营质量", index=False)


def main() -> None:
    ref = load_reference_lookup()
    holdings = build_core_holdings_history(ref)
    annual = build_annual_operating_quality(ref)
    write_workbook(ref, holdings, annual)
    print(f"saved: {OUTPUT_XLSX}")


if __name__ == "__main__":
    main()
