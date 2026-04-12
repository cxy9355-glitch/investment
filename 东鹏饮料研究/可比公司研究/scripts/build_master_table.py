from __future__ import annotations

from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = BASE_DIR.parents[0]
DATA_DIR = BASE_DIR / "data"
TEMPLATE_FILE = BASE_DIR / "04_横向对比数据表_模板.csv"
OUTPUT_CSV = DATA_DIR / "饮料可比公司_横向对比数据表_第一版.csv"
OUTPUT_XLSX = DATA_DIR / "饮料可比公司_横向对比数据表_第一版.xlsx"


def read_template_columns() -> list[str]:
    return list(pd.read_csv(TEMPLATE_FILE, nrows=0).columns)


def value_from_table(table: pd.DataFrame, item: str, year: str) -> float | None:
    matched = table.loc[table["项目"] == item, year]
    if matched.empty:
        return None
    value = matched.iloc[0]
    if pd.isna(value):
        return None
    return float(value)


def pct(value: float | None) -> float | None:
    if value is None or pd.isna(value):
        return None
    return float(value)


def build_eastroc_rows(columns: list[str]) -> pd.DataFrame:
    key_df = pd.read_csv(
        ROOT_DIR / "东鹏饮料研究" / "data" / "东鹏饮料_关键指标_2020_2025.csv"
    )
    key_df["年份"] = key_df["年份"].astype(int)

    income_2024 = pd.read_csv(
        ROOT_DIR / "东鹏饮料研究" / "data" / "东鹏饮料_合并利润表_2020_2024_元.csv"
    )
    balance_2024 = pd.read_csv(
        ROOT_DIR / "东鹏饮料研究" / "data" / "东鹏饮料_合并资产负债表_2020_2024_元.csv"
    )
    cashflow_2024 = pd.read_csv(
        ROOT_DIR / "东鹏饮料研究" / "data" / "东鹏饮料_合并现金流量表_2020_2024_元.csv"
    )

    income_2025 = pd.read_csv(
        ROOT_DIR / "东鹏饮料研究" / "data" / "东鹏饮料_2025_HKEX_IFRS_合并利润表_元.csv"
    )
    balance_2025 = pd.read_csv(
        ROOT_DIR / "东鹏饮料研究" / "data" / "东鹏饮料_2025_HKEX_IFRS_合并资产负债表_元.csv"
    )
    cashflow_2025 = pd.read_csv(
        ROOT_DIR / "东鹏饮料研究" / "data" / "东鹏饮料_2025_HKEX_IFRS_合并现金流量表_元.csv"
    )

    rows: list[dict[str, object]] = []
    for year in (2024, 2025):
        key = key_df.loc[key_df["年份"] == year].iloc[0]
        if year == 2024:
            y = str(year)
            row = {
                "市场": "A股",
                "代码": "605499.SH",
                "公司": "东鹏饮料",
                "年度": year,
                "币种": "人民币",
                "营业收入": value_from_table(income_2024, "营业收入", y),
                "营业成本": value_from_table(income_2024, "营业成本", y),
                "毛利": float(key["毛利"]),
                "销售费用": value_from_table(income_2024, "销售费用", y),
                "管理费用": value_from_table(income_2024, "管理费用", y),
                "研发费用": value_from_table(income_2024, "研发费用", y),
                "财务费用": value_from_table(income_2024, "财务费用", y),
                "营业利润": value_from_table(income_2024, "营业利润", y),
                "利润总额": value_from_table(income_2024, "利润总额", y),
                "归母净利润": value_from_table(income_2024, "归母净利润", y),
                "经营活动现金流量净额": value_from_table(cashflow_2024, "经营活动现金流量净额", y),
                "购建长期资产支付的现金": value_from_table(cashflow_2024, "购建长期资产支付的现金", y),
                "货币资金": value_from_table(balance_2024, "货币资金", y),
                "存货": value_from_table(balance_2024, "存货", y),
                "流动资产合计": value_from_table(balance_2024, "流动资产合计", y),
                "固定资产": value_from_table(balance_2024, "固定资产", y),
                "无形资产": value_from_table(balance_2024, "无形资产", y),
                "总资产": value_from_table(balance_2024, "资产总计", y),
                "短期借款": value_from_table(balance_2024, "短期借款", y),
                "长期借款": value_from_table(balance_2024, "长期借款", y),
                "流动负债合计": value_from_table(balance_2024, "流动负债合计", y),
                "总负债": value_from_table(balance_2024, "负债合计", y),
                "归母权益": value_from_table(balance_2024, "归母权益合计", y),
                "毛利率": pct(key["毛利率"]),
                "归母净利率": pct(key["归母净利率"]),
                "销售费用率": pct(key["销售费用率"]),
                "管理费用率": pct(key["管理费用率"]),
                "研发费用率": pct(key["研发费用率"]),
                "财务费用率": pct(key["财务费用率"]),
                "三费费率": pct(key["三费费率"]),
                "ROA": pct(key["ROA"]),
                "ROE": pct(key["ROE"]),
                "资产负债率": pct(key["资产负债率"]),
                "流动比率": float(key["流动比率"]),
                "现金比率": float(key["现金比率"]),
                "经营现金流/归母净利润": float(key["经营现金流/归母净利润"]),
                "资本开支/收入": float(key["资本开支/收入"]),
                "官方文件类型": "年度报告",
                "官方来源": str(ROOT_DIR / "东鹏饮料研究" / "raw" / "official" / "2024年年度报告.pdf"),
            }
        else:
            y = str(year)
            row = {
                "市场": "A股",
                "代码": "605499.SH",
                "公司": "东鹏饮料",
                "年度": year,
                "币种": "人民币",
                "营业收入": value_from_table(income_2025, "营业收入", y),
                "营业成本": value_from_table(income_2025, "销售成本", y),
                "毛利": value_from_table(income_2025, "毛利", y),
                "销售费用": value_from_table(income_2025, "分销及销售费用", y),
                "管理费用": value_from_table(income_2025, "管理费用", y),
                "研发费用": value_from_table(income_2025, "研发费用", y),
                "财务费用": value_from_table(income_2025, "财务成本", y),
                "营业利润": value_from_table(income_2025, "税前利润", y),
                "利润总额": value_from_table(income_2025, "税前利润", y),
                "归母净利润": value_from_table(income_2025, "归母净利润", y),
                "经营活动现金流量净额": value_from_table(cashflow_2025, "经营活动现金流量净额", y),
                "购建长期资产支付的现金": (
                    (value_from_table(cashflow_2025, "购置固定资产支付的现金", y) or 0.0)
                    + (value_from_table(cashflow_2025, "购置无形资产支付的现金", y) or 0.0)
                    + (value_from_table(cashflow_2025, "使用权资产前期付款", y) or 0.0)
                ),
                "货币资金": value_from_table(balance_2025, "现金及现金等价物", y),
                "存货": value_from_table(balance_2025, "存货", y),
                "流动资产合计": value_from_table(balance_2025, "流动资产合计", y),
                "固定资产": value_from_table(balance_2025, "固定资产", y),
                "无形资产": value_from_table(balance_2025, "无形资产", y),
                "总资产": value_from_table(balance_2025, "资产总计", y),
                "短期借款": value_from_table(balance_2025, "借款", y),
                "长期借款": None,
                "流动负债合计": value_from_table(balance_2025, "流动负债合计", y),
                "总负债": value_from_table(balance_2025, "负债合计", y),
                "归母权益": value_from_table(balance_2025, "归母权益", y),
                "毛利率": pct(key["毛利率"]),
                "归母净利率": pct(key["归母净利率"]),
                "销售费用率": pct(key["销售费用率"]),
                "管理费用率": pct(key["管理费用率"]),
                "研发费用率": pct(key["研发费用率"]),
                "财务费用率": pct(key["财务费用率"]),
                "三费费率": pct(key["三费费率"]),
                "ROA": pct(key["ROA"]),
                "ROE": pct(key["ROE"]),
                "资产负债率": pct(key["资产负债率"]),
                "流动比率": float(key["流动比率"]),
                "现金比率": float(key["现金比率"]),
                "经营现金流/归母净利润": float(key["经营现金流/归母净利润"]),
                "资本开支/收入": float(key["资本开支/收入"]),
                "官方文件类型": "年度报告/HKEX年报",
                "官方来源": str(ROOT_DIR / "东鹏饮料研究" / "raw" / "official" / "2025年度业绩公告_HKEX_2026-03-30.pdf"),
            }

        normalized = {column: row.get(column) for column in columns}
        rows.append(normalized)

    return pd.DataFrame(rows, columns=columns)


def load_market_file(path: Path, columns: list[str]) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=columns)
    df = pd.read_csv(path)
    for column in columns:
        if column not in df.columns:
            df[column] = None
    return df[columns]


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    columns = read_template_columns()

    frames = [
        build_eastroc_rows(columns),
        load_market_file(DATA_DIR / "A股可比公司_2024_2025_核心数据.csv", columns),
        load_market_file(DATA_DIR / "H股可比公司_2024_2025_核心数据.csv", columns),
        load_market_file(DATA_DIR / "美股可比公司_2024_2025_核心数据.csv", columns),
    ]

    result = pd.concat(frames, ignore_index=True)
    result = result.sort_values(["市场", "代码", "年度"], kind="stable").reset_index(drop=True)
    result.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    with pd.ExcelWriter(OUTPUT_XLSX, engine="openpyxl") as writer:
        result.to_excel(writer, index=False, sheet_name="横向对比")


if __name__ == "__main__":
    main()
