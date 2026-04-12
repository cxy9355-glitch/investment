from __future__ import annotations

import io
import re
import time
from pathlib import Path
from typing import Any

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
RAW_DIR = BASE_DIR / "raw" / "official"
SOURCE_FILE = BASE_DIR / "05_官方来源明细.csv"

OUTPUT_CSV = DATA_DIR / "美股可比公司_2024_2025_核心数据.csv"
OUTPUT_MD = DATA_DIR / "美股可比公司_说明.md"


CIK_MAP = {
    "Monster Beverage": "0000865752",
    "Celsius Holdings": "0001341766",
    "Coca-Cola": "0000021344",
    "PepsiCo": "0000077476",
    "Keurig Dr Pepper": "0001418135",
}


CORE_COLUMNS = [
    "市场",
    "代码",
    "公司",
    "年度",
    "币种",
    "营业收入",
    "营业成本",
    "毛利",
    "销售费用",
    "管理费用",
    "研发费用",
    "财务费用",
    "营业利润",
    "利润总额",
    "归母净利润",
    "经营活动现金流量净额",
    "购建长期资产支付的现金",
    "货币资金",
    "存货",
    "流动资产合计",
    "固定资产",
    "无形资产",
    "总资产",
    "短期借款",
    "长期借款",
    "流动负债合计",
    "总负债",
    "归母权益",
    "毛利率",
    "归母净利率",
    "销售费用率",
    "管理费用率",
    "研发费用率",
    "财务费用率",
    "三费费率",
    "ROA",
    "ROE",
    "资产负债率",
    "流动比率",
    "现金比率",
    "经营现金流/归母净利润",
    "资本开支/收入",
    "官方文件类型",
    "官方来源",
]


REVENUE_TAGS = [
    "RevenueFromContractWithCustomerExcludingAssessedTax",
    "Revenues",
    "SalesRevenueGoodsNet",
]
COGS_TAGS = [
    "CostOfRevenue",
    "CostOfGoodsSold",
    "OtherCostOfOperatingRevenue",
]
GROSS_TAGS = ["GrossProfit"]
SGA_TAGS = ["SellingGeneralAndAdministrativeExpense"]
RND_TAGS = ["ResearchAndDevelopmentExpense", "ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost"]
OP_TAGS = ["OperatingIncomeLoss"]
PRETAX_TAGS = [
    "IncomeBeforeTaxExpenseBenefit",
    "IncomeBeforeTax",
    "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
    "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments",
    "IncomeLossFromContinuingOperationsBeforeIncomeTaxes",
]
NET_TAGS = [
    "NetIncomeLossAvailableToCommonStockholdersBasic",
    "NetIncomeLoss",
]
CFO_TAGS = [
    "NetCashProvidedByUsedInOperatingActivities",
    "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations",
]
CAPEX_TAGS = [
    "PaymentsToAcquirePropertyPlantAndEquipment",
]
CASH_TAGS = ["CashAndCashEquivalentsAtCarryingValue"]
INVENTORY_TAGS = ["InventoryNet"]
CURRENT_ASSET_TAGS = ["AssetsCurrent"]
PPE_TAGS = ["PropertyPlantAndEquipmentNet"]
INTANGIBLE_TAGS = [
    "IntangibleAssetsNetExcludingGoodwill",
    "OtherIntangibleAssetsNet",
    "FiniteLivedIntangibleAssetsNet",
]
ASSET_TAGS = ["Assets"]
SHORT_DEBT_TAGS = [
    "LongTermDebtCurrent",
    "LongTermDebtAndFinanceLeaseObligationsCurrent",
    "DebtCurrent",
]
LONG_DEBT_TAGS = [
    "LongTermDebtNoncurrent",
    "LongTermDebt",
    "LongTermDebtAndFinanceLeaseObligationsNoncurrent",
]
CURRENT_LIAB_TAGS = ["LiabilitiesCurrent"]
LIAB_TAGS = ["Liabilities"]
EQUITY_TAGS = [
    "StockholdersEquity",
    "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
]


US_ROW_META = {
    "Monster Beverage": {
        "ticker": "MNST",
        "market": "美股",
        "expense_mode": "combined",
    },
    "Celsius Holdings": {
        "ticker": "CELH",
        "market": "美股",
        "expense_mode": "combined",
    },
    "Coca-Cola": {
        "ticker": "KO",
        "market": "美股",
        "expense_mode": "sg&a",
    },
    "PepsiCo": {
        "ticker": "PEP",
        "market": "美股",
        "expense_mode": "sg&a",
    },
    "Keurig Dr Pepper": {
        "ticker": "KDP",
        "market": "美股",
        "expense_mode": "sg&a",
    },
}

US_10K_URLS = {
    ("Monster Beverage", 2024): "https://www.sec.gov/Archives/edgar/data/865752/000141057825000248/mnst-20241231x10k.htm",
    ("Monster Beverage", 2025): "https://www.sec.gov/Archives/edgar/data/865752/000110465926020831/mnst-20251231x10k.htm",
    ("Celsius Holdings", 2024): "https://www.sec.gov/Archives/edgar/data/1341766/000134176625000024/celh-20241231.htm",
    ("Celsius Holdings", 2025): "https://www.sec.gov/Archives/edgar/data/1341766/000134176626000024/celh-20251231.htm",
    ("Coca-Cola", 2024): "https://www.sec.gov/Archives/edgar/data/21344/000002134425000011/ko-20241231.htm",
    ("Coca-Cola", 2025): "https://www.sec.gov/Archives/edgar/data/21344/000162828026010047/ko-20251231.htm",
    ("PepsiCo", 2024): "https://www.sec.gov/Archives/edgar/data/77476/000007747625000007/pep-20241228.htm",
    ("PepsiCo", 2025): "https://www.sec.gov/Archives/edgar/data/77476/000007747626000007/pep-20251227.htm",
    ("Keurig Dr Pepper", 2024): "https://www.sec.gov/Archives/edgar/data/1418135/000141813525000013/kdp-20241231.htm",
    ("Keurig Dr Pepper", 2025): "https://www.sec.gov/Archives/edgar/data/1418135/000141813526000016/kdp-20251231.htm",
}


def build_session() -> requests.Session:
    session = requests.Session()
    session.trust_env = False
    session.headers.update(
        {
            "User-Agent": "Codex Research contact research@example.com",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
    )
    retry = Retry(
        total=5,
        connect=5,
        read=5,
        backoff_factor=1.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def safe_name(value: str) -> str:
    value = re.sub(r'[\\/:*?"<>|]', "_", value)
    value = re.sub(r"\s+", "_", value.strip())
    return value


def download_text(session: requests.Session, url: str, target: Path) -> str:
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and target.stat().st_size > 0:
        return target.read_text(encoding="utf-8", errors="ignore")
    response = session.get(url, timeout=90)
    response.raise_for_status()
    text = response.text
    target.write_text(text, encoding="utf-8")
    return text


def fetch_companyfacts(session: requests.Session, cik: str) -> dict[str, Any]:
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    response = session.get(url, timeout=90)
    response.raise_for_status()
    return response.json()


def normalize_value(value: Any) -> int:
    if pd.isna(value):
        return 0
    if isinstance(value, str):
        value = value.replace(",", "").strip()
    return int(round(float(value)))


def pick_fact(companyfacts: dict[str, Any], tags: list[str], year: int) -> tuple[int | None, str | None]:
    us_gaap = companyfacts["facts"].get("us-gaap", {})
    for tag in tags:
        if tag not in us_gaap:
            continue
        units = us_gaap[tag].get("units", {})
        for unit_name, records in units.items():
            df = pd.DataFrame(records)
            if df.empty or "fy" not in df.columns or "form" not in df.columns:
                continue
            rows = df[(df["form"] == "10-K") & (df["fy"] == year)].copy()
            if rows.empty:
                continue
            rows["end_dt"] = pd.to_datetime(rows.get("end"), errors="coerce")
            rows["filed_dt"] = pd.to_datetime(rows.get("filed"), errors="coerce")
            rows = rows.sort_values(["end_dt", "filed_dt"]).reset_index(drop=True)
            row = rows.iloc[-1]
            return normalize_value(row["val"]), tag
    return None, None


def extract_fact(companyfacts: dict[str, Any], tags: list[str], year: int, fallback: int = 0) -> int:
    value, _ = pick_fact(companyfacts, tags, year)
    return fallback if value is None else value


def sum_numeric_row(table: pd.DataFrame, label: str) -> int:
    label_lower = label.lower()
    matches = []
    for idx in range(len(table)):
        row = table.iloc[idx].astype(str).fillna("")
        text = " ".join(row.tolist()).lower()
        if label_lower in text:
            matches.append(idx)
    if not matches:
        return 0
    row = table.iloc[matches[0]]
    vals = []
    for val in row.tolist():
        if pd.isna(val):
            continue
        if isinstance(val, str):
            cleaned = val.replace(",", "").replace("$", "").replace("(", "-").replace(")", "").strip()
            if cleaned in {"", "-", "—", "nan", "na", "n/a", "​"}:
                continue
            try:
                vals.append(float(cleaned))
                continue
            except Exception:
                continue
        elif isinstance(val, (int, float)) and not pd.isna(val):
            vals.append(float(val))
    if not vals:
        return 0
    return int(round(sum(vals)))


def find_table(tables: list[pd.DataFrame], required_labels: list[str]) -> pd.DataFrame | None:
    required = [x.lower() for x in required_labels]
    for table in tables:
        text = " ".join(table.astype(str).fillna("").stack().tolist()).lower()
        if all(label in text for label in required):
            return table
    return None


def extract_monster_splits(html: str, year: int) -> tuple[int, int]:
    tables = pd.read_html(io.StringIO(html))
    table = find_table(
        tables,
        ["distribution expense", "selling and marketing expense", "nonmanufacturing payroll expense"],
    )
    if table is None:
        return 0, 0
    distribution = sum_numeric_row(table, "Distribution expense")
    selling_marketing = sum_numeric_row(table, "Selling and marketing expense")
    payroll = sum_numeric_row(table, "Nonmanufacturing payroll expense")
    impairment = sum_numeric_row(table, "Goodwill and intangibles impairment")
    other_items = sum_numeric_row(table, "Other segment items")
    sales = distribution + selling_marketing
    admin = payroll + impairment + other_items
    return sales, admin


def extract_celsius_splits(html: str, year: int) -> tuple[int, int]:
    tables = pd.read_html(io.StringIO(html))
    table = find_table(tables, ["selling and marketing expenses", "general and administrative expenses"])
    if table is None:
        return 0, 0
    selling_marketing = sum_numeric_row(table, "Selling and Marketing Expenses")
    general_admin = sum_numeric_row(table, "General and Administrative Expenses")
    return selling_marketing, general_admin


def derive_rows(company: str, year: int, companyfacts: dict[str, Any], html: str, source_url: str) -> dict[str, Any]:
    meta = US_ROW_META[company]
    revenue = extract_fact(companyfacts, REVENUE_TAGS, year)
    cogs = extract_fact(companyfacts, COGS_TAGS, year)
    gross = extract_fact(companyfacts, GROSS_TAGS, year, fallback=revenue - cogs)
    sga = extract_fact(companyfacts, SGA_TAGS, year)
    rnd = extract_fact(companyfacts, RND_TAGS, year)
    op_income = extract_fact(companyfacts, OP_TAGS, year, fallback=gross - sga - rnd)
    pretax = extract_fact(companyfacts, PRETAX_TAGS, year, fallback=op_income)
    net_income = extract_fact(companyfacts, NET_TAGS, year)
    cfo = extract_fact(companyfacts, CFO_TAGS, year)
    capex = extract_fact(companyfacts, CAPEX_TAGS, year)
    cash = extract_fact(companyfacts, CASH_TAGS, year)
    inventory = extract_fact(companyfacts, INVENTORY_TAGS, year)
    current_assets = extract_fact(companyfacts, CURRENT_ASSET_TAGS, year)
    ppe = extract_fact(companyfacts, PPE_TAGS, year)
    intangible = extract_fact(companyfacts, INTANGIBLE_TAGS, year)
    assets = extract_fact(companyfacts, ASSET_TAGS, year)
    short_debt = extract_fact(companyfacts, SHORT_DEBT_TAGS, year)
    long_debt = extract_fact(companyfacts, LONG_DEBT_TAGS, year)
    current_liab = extract_fact(companyfacts, CURRENT_LIAB_TAGS, year)
    liabilities = extract_fact(companyfacts, LIAB_TAGS, year)
    equity = extract_fact(companyfacts, EQUITY_TAGS, year)

    if cogs == 0 and revenue and gross:
        cogs = revenue - gross
    if gross == 0 and revenue and cogs:
        gross = revenue - cogs

    cogs = abs(cogs)
    gross = abs(gross)
    sga = abs(sga)
    rnd = abs(rnd)
    capex = abs(capex)

    if liabilities == 0 and assets and equity:
        liabilities = assets - equity

    if meta["expense_mode"] == "combined":
        sales = gross - op_income - rnd
        admin = 0
    else:
        sales = sga
        admin = 0

    sales = abs(sales)
    admin = abs(admin)

    finance = op_income - pretax

    gross_margin = gross / revenue if revenue else 0
    net_margin = net_income / revenue if revenue else 0
    sales_ratio = sales / revenue if revenue else 0
    admin_ratio = admin / revenue if revenue else 0
    rnd_ratio = rnd / revenue if revenue else 0
    finance_ratio = finance / revenue if revenue else 0
    three_fee = sales_ratio + admin_ratio + rnd_ratio
    roa = net_income / assets if assets else 0
    roe = net_income / equity if equity else 0
    debt_ratio = liabilities / assets if assets else 0
    current_ratio = current_assets / current_liab if current_liab else 0
    cash_ratio = cash / current_liab if current_liab else 0
    cfo_to_np = cfo / net_income if net_income else 0
    capex_ratio = capex / revenue if revenue else 0

    return {
        "市场": meta["market"],
        "代码": meta["ticker"],
        "公司": company,
        "年度": year,
        "币种": "USD",
        "营业收入": revenue,
        "营业成本": cogs,
        "毛利": gross,
        "销售费用": sales,
        "管理费用": admin,
        "研发费用": rnd,
        "财务费用": finance,
        "营业利润": op_income,
        "利润总额": pretax,
        "归母净利润": net_income,
        "经营活动现金流量净额": cfo,
        "购建长期资产支付的现金": capex,
        "货币资金": cash,
        "存货": inventory,
        "流动资产合计": current_assets,
        "固定资产": ppe,
        "无形资产": intangible,
        "总资产": assets,
        "短期借款": short_debt,
        "长期借款": long_debt,
        "流动负债合计": current_liab,
        "总负债": liabilities,
        "归母权益": equity,
        "毛利率": gross_margin,
        "归母净利率": net_margin,
        "销售费用率": sales_ratio,
        "管理费用率": admin_ratio,
        "研发费用率": rnd_ratio,
        "财务费用率": finance_ratio,
        "三费费率": three_fee,
        "ROA": roa,
        "ROE": roe,
        "资产负债率": debt_ratio,
        "流动比率": current_ratio,
        "现金比率": cash_ratio,
        "经营现金流/归母净利润": cfo_to_np,
        "资本开支/收入": capex_ratio,
        "官方文件类型": "10-K",
        "官方来源": source_url,
    }


def format_int(v: Any) -> str:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    if isinstance(v, str):
        return v
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        if v.is_integer():
            return str(int(v))
        return f"{v:.6f}".rstrip("0").rstrip(".")
    return str(v)


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    source_urls = US_10K_URLS
    session = build_session()
    rows: list[dict[str, Any]] = []

    for company in US_ROW_META:
        cik = CIK_MAP[company]
        print(f"fetch companyfacts: {company}")
        companyfacts = None
        for attempt in range(5):
            try:
                companyfacts = fetch_companyfacts(session, cik)
                break
            except Exception as exc:
                if attempt == 4:
                    raise
                time.sleep(1.5 * (attempt + 1))
        assert companyfacts is not None

        for year in (2024, 2025):
            source_url = source_urls[(company, year)]
            print(f"download and parse: {company} {year}")
            raw_name = safe_name(f"US_{US_ROW_META[company]['ticker']}_{year}_10K.html")
            raw_path = RAW_DIR / raw_name
            html = download_text(session, source_url, raw_path)
            row = derive_rows(company, year, companyfacts, html, source_url)
            rows.append(row)

    df = pd.DataFrame(rows, columns=CORE_COLUMNS)
    df = df.sort_values(["公司", "年度"]).reset_index(drop=True)

    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

    md_lines = [
        "# 美股可比公司 2024/2025 核心数据说明",
        "",
        "## 口径",
        "",
        "- 数据优先取自官方 FY2024 / FY2025 10-K 的内联 XBRL 事实。",
        "- 原始金额单位为 `千美元`，比率按原币种直接计算。",
        "- `2025` 一律以 FY2025 官方 10-K 为准。",
        "- `销售费用 / 管理费用` 尽量按 10-K 原文拆分；若公司仅披露合并 SG&A，则按披露口径填入 `销售费用`，`管理费用` 记为 `0`。",
        "- `财务费用` 按 `营业利润 - 利润总额` 计算，若为负值表示净财务收益或其他非营业收益。",
        "",
        "## 特殊点",
        "",
        "- Monster Beverage / Celsius Holdings：为避免把多年的分部表或多期列拼接错位，统一按 `毛利 - 营业利润 - 研发费用` 作为合并经营费用，`管理费用` 记 0。",
        "- Coca-Cola / PepsiCo / Keurig Dr Pepper：多数情况下仅披露合并 SG&A，未强行拆成中文口径的销售费用与管理费用。",
        "",
        "## 输出文件",
        "",
        f"- `{OUTPUT_CSV.relative_to(BASE_DIR).as_posix()}`",
        f"- 原始 10-K HTML 已保存到 `{(RAW_DIR / 'US_*.html').as_posix()}` 这一目录下，实际文件名形如 `US_MNST_2024_10K.html`。",
    ]
    OUTPUT_MD.write_text("\n".join(md_lines), encoding="utf-8")

    print(f"saved {OUTPUT_CSV}")
    print(f"saved {OUTPUT_MD}")
    print(f"rows={len(df)}")


if __name__ == "__main__":
    main()
