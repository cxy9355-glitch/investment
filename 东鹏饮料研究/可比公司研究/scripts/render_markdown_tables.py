from __future__ import annotations

from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"


RAW_COLUMNS = [
    "市场",
    "代码",
    "公司",
    "年度",
    "币种",
    "营业收入",
    "毛利",
    "归母净利润",
    "经营活动现金流量净额",
    "购建长期资产支付的现金",
    "货币资金",
    "存货",
    "总资产",
    "总负债",
    "归母权益",
    "官方文件类型",
]

RATIO_COLUMNS = [
    "市场",
    "代码",
    "公司",
    "年度",
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
]

INT_COLUMNS = {
    "营业收入",
    "毛利",
    "归母净利润",
    "经营活动现金流量净额",
    "购建长期资产支付的现金",
    "货币资金",
    "存货",
    "总资产",
    "总负债",
    "归母权益",
}

PCT_COLUMNS = {
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
    "资本开支/收入",
}

X_COLUMNS = {
    "流动比率",
    "现金比率",
    "经营现金流/归母净利润",
}


def format_value(column: str, value: object) -> str:
    if pd.isna(value):
        return "-"
    if column in INT_COLUMNS:
        return f"{int(round(float(value))):,}"
    if column in PCT_COLUMNS:
        return f"{float(value) * 100:.1f}%"
    if column in X_COLUMNS:
        return f"{float(value):.2f}x"
    return str(value)


def format_table(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    formatted = df[columns].copy()
    for column in columns:
        formatted[column] = formatted[column].map(lambda x, c=column: format_value(c, x))
    return formatted


def write_markdown(csv_name: str, md_name: str, title: str) -> None:
    csv_path = DATA_DIR / csv_name
    md_path = DATA_DIR / md_name
    df = pd.read_csv(csv_path)
    df = df.sort_values(["市场", "代码", "年度"], kind="stable").reset_index(drop=True)

    raw_table = format_table(df, RAW_COLUMNS).to_markdown(index=False)
    ratio_table = format_table(df, RATIO_COLUMNS).to_markdown(index=False)

    content = "\n".join(
        [
            f"# {title}",
            "",
            "## 基础财务数据",
            "",
            raw_table,
            "",
            "## 关键比率",
            "",
            ratio_table,
            "",
            "## 说明",
            "",
            "- 本文件为手机阅读友好的 Markdown 版，原始结构化数据仍保留在同名 CSV 中。",
            "- 比率类指标统一保留到 1 位小数，倍数类指标保留到 2 位。",
        ]
    )
    md_path.write_text(content, encoding="utf-8")


def main() -> None:
    write_markdown(
        "A股可比公司_2024_2025_核心数据.csv",
        "A股可比公司_2024_2025_核心数据.md",
        "A股可比公司 2024-2025 核心数据",
    )
    write_markdown(
        "H股可比公司_2024_2025_核心数据.csv",
        "H股可比公司_2024_2025_核心数据.md",
        "H股可比公司 2024-2025 核心数据",
    )
    write_markdown(
        "美股可比公司_2024_2025_核心数据.csv",
        "美股可比公司_2024_2025_核心数据.md",
        "美股可比公司 2024-2025 核心数据",
    )
    write_markdown(
        "饮料可比公司_横向对比数据表_第一版.csv",
        "饮料可比公司_横向对比数据表_第一版.md",
        "饮料可比公司横向对比数据表",
    )


if __name__ == "__main__":
    main()
