from __future__ import annotations

from pathlib import Path
import re

import pandas as pd
from pypdf import PdfReader


BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "raw" / "official"
DATA_DIR = BASE_DIR / "data"
OUT_CSV = DATA_DIR / "A股可比公司_2024_2025_核心数据.csv"
OUT_MD = DATA_DIR / "A股可比公司_说明.md"


REPORTS = [
    {
        "市场": "A股",
        "代码": "603156.SH",
        "公司": "养元饮品",
        "年度": 2024,
        "官方文件类型": "2024年年度报告",
        "官方来源": RAW_DIR / "A股_603156.SH_养元饮品_2024_年报全文.pdf",
    },
    {
        "市场": "A股",
        "代码": "603156.SH",
        "公司": "养元饮品",
        "年度": 2025,
        "官方文件类型": "2025年第三季度报告",
        "官方来源": RAW_DIR / "A股_603156.SH_养元饮品_2025_Q3_季度报告.pdf",
    },
    {
        "市场": "A股",
        "代码": "000848.SZ",
        "公司": "承德露露",
        "年度": 2024,
        "官方文件类型": "2024年年度报告",
        "官方来源": RAW_DIR / "A股_000848.SZ_承德露露_2024_年报全文.pdf",
    },
    {
        "市场": "A股",
        "代码": "000848.SZ",
        "公司": "承德露露",
        "年度": 2025,
        "官方文件类型": "2025年第三季度报告",
        "官方来源": RAW_DIR / "A股_000848.SZ_承德露露_2025_Q3_季度报告.pdf",
    },
    {
        "市场": "A股",
        "代码": "603711.SH",
        "公司": "香飘飘",
        "年度": 2024,
        "官方文件类型": "2024年年度报告",
        "官方来源": RAW_DIR / "A股_603711.SH_香飘飘_2024_年报全文.pdf",
    },
    {
        "市场": "A股",
        "代码": "603711.SH",
        "公司": "香飘飘",
        "年度": 2025,
        "官方文件类型": "2025年第三季度报告",
        "官方来源": RAW_DIR / "A股_603711.SH_香飘飘_2025_Q3_季度报告.pdf",
    },
    {
        "市场": "A股",
        "代码": "605337.SH",
        "公司": "李子园",
        "年度": 2024,
        "官方文件类型": "2024年年度报告",
        "官方来源": RAW_DIR / "A股_605337.SH_李子园_2024_年报全文.pdf",
    },
    {
        "市场": "A股",
        "代码": "605337.SH",
        "公司": "李子园",
        "年度": 2025,
        "官方文件类型": "2025年第三季度报告",
        "官方来源": RAW_DIR / "A股_605337.SH_李子园_2025_Q3_季度报告.pdf",
    },
    {
        "市场": "A股",
        "代码": "300997.SZ",
        "公司": "欢乐家",
        "年度": 2024,
        "官方文件类型": "2024年年度报告",
        "官方来源": RAW_DIR / "A股_300997.SZ_欢乐家_2024_年报全文.pdf",
    },
    {
        "市场": "A股",
        "代码": "300997.SZ",
        "公司": "欢乐家",
        "年度": 2025,
        "官方文件类型": "2025年年度报告",
        "官方来源": RAW_DIR / "A股_300997.SZ_欢乐家_2025_年报全文.pdf",
    },
]


FIELD_PATTERNS = {
    "营业收入": ["营业收入"],
    "营业成本": ["营业成本"],
    "销售费用": ["销售费用"],
    "管理费用": ["管理费用"],
    "研发费用": ["研发费用"],
    "财务费用": ["财务费用"],
    "营业利润": ["营业利润（亏损以“－”号填列）", "营业利润（亏损以“-”号填列）", "营业利润"],
    "利润总额": ["利润总额（亏损总额以“－”号填列）", "利润总额（亏损总额以“-”号填列）", "利润总额"],
    "归母净利润": [
        "归属于母公司股东的净利润（净亏损以“－”号填列）",
        "归属于母公司股东的净利润（净亏损以“-”号填列）",
        "归属于母公司所有者的净利润（净亏损以“－”号填列）",
        "归属于母公司所有者的净利润（净亏损以“-”号填列）",
        "归属于上市公司股东的净利润（净亏损以“－”号填列）",
        "归属于上市公司股东的净利润（净亏损以“-”号填列）",
        "归属于母公司股东的净利润",
        "归属于母公司所有者的净利润",
        "归属于上市公司股东的净利润",
    ],
    "经营活动现金流量净额": ["经营活动产生的现金流量净额"],
    "购建长期资产支付的现金": [
        "购建固定资产、无形资产和其他长期资产支付的现金",
        "购建固定资产、无形资产和其他长期资产所支付的现金",
        "购建长期资产支付的现金",
    ],
    "货币资金": ["货币资金"],
    "存货": ["存货"],
    "流动资产合计": ["流动资产合计"],
    "固定资产": ["固定资产"],
    "无形资产": ["无形资产"],
    "总资产": ["资产总计", "总资产"],
    "短期借款": ["短期借款"],
    "长期借款": ["长期借款"],
    "流动负债合计": ["流动负债合计"],
    "总负债": ["负债合计", "总负债"],
    "归母权益": [
        "归属于母公司所有者权益（或股东权益）合计",
        "归属于母公司所有者权益合计",
        "归属于母公司股东权益合计",
        "归属于上市公司股东权益合计",
        "归属于母公司股东的权益合计",
        "所有者权益（或股东权益）合计",
    ],
}


def flex(label: str) -> str:
    """把中文标签转成允许任意空白的正则。"""
    return r"\s*".join(re.escape(ch) for ch in label)


def parse_number(value: str) -> float:
    return float(value.replace(",", ""))


def first_page_with_any(pages: list[str], keywords: list[str]) -> int:
    for keyword in keywords:
        for idx, text in enumerate(pages):
            if keyword in text:
                return idx
    raise ValueError(f"未找到章节：{keywords[0]}")


def cut_parent_statements(text: str) -> str:
    """截断母公司报表，避免把合并报表后面的母公司行混进来。"""
    for marker in ["母公司资产负债表", "母公司利润表", "母公司现金流量表"]:
        pos = text.find(marker)
        if pos != -1:
            return text[:pos]
    return text


def extract_section_text(pages: list[str], start_keywords: list[str], end_keywords: list[str] | None) -> str:
    start_idx = first_page_with_any(pages, start_keywords)
    section = "\n".join(pages[start_idx:]) if end_keywords is None else "\n".join(
        pages[start_idx:first_page_with_any(pages, end_keywords) + 1]
    )
    return cut_parent_statements(section)


def extract_value(text: str, patterns: list[str], zero_if_missing: bool = False) -> float:
    for pat in patterns:
        m = re.search(flex(pat), text)
        if m:
            tail = text[m.end() : m.end() + 220]
            for token in re.findall(r"[\-]?\d[\d,]*\.?\d*", tail):
                clean = token.replace(",", "").replace("-", "")
                if "." in token or len(clean) > 3:
                    return parse_number(token)
    if zero_if_missing:
        return 0.0
    raise ValueError(f"未找到字段：{patterns[0]}")


def extract_pair_value(text: str, patterns: list[str], zero_if_missing: bool = False) -> tuple[float, float]:
    for pat in patterns:
        m = re.search(flex(pat), text)
        if m:
            tail = text[m.end() : m.end() + 300]
            values: list[float] = []
            for token in re.findall(r"[\-]?\d[\d,]*\.?\d*", tail):
                clean = token.replace(",", "").replace("-", "")
                if "." in token or len(clean) > 3:
                    values.append(parse_number(token))
                    if len(values) == 2:
                        return values[0], values[1]
    if zero_if_missing:
        return 0.0, 0.0
    raise ValueError(f"未找到双列字段：{patterns[0]}")


def extract_report(pdf_path: Path) -> dict[str, float]:
    reader = PdfReader(str(pdf_path))
    pages = [page.extract_text() or "" for page in reader.pages]
    bs_text = extract_section_text(pages, ["合并资产负债表"], ["合并利润表", "合并年初到报告期末利润表"])
    is_text = extract_section_text(
        pages,
        ["合并利润表", "合并年初到报告期末利润表", "合并利润及其他综合收益表"],
        ["合并现金流量表", "合并年初到报告期末现金流量表"],
    )
    cf_text = extract_section_text(
        pages,
        ["合并现金流量表", "合并年初到报告期末现金流量表"],
        None,
    )

    revenue = extract_value(is_text, FIELD_PATTERNS["营业收入"])
    cost = extract_value(is_text, FIELD_PATTERNS["营业成本"])
    gross_profit = revenue - cost

    return {
        "营业收入": revenue,
        "营业成本": cost,
        "毛利": gross_profit,
        "销售费用": extract_value(is_text, FIELD_PATTERNS["销售费用"]),
        "管理费用": extract_value(is_text, FIELD_PATTERNS["管理费用"]),
        "研发费用": extract_value(is_text, FIELD_PATTERNS["研发费用"]),
        "财务费用": extract_value(is_text, FIELD_PATTERNS["财务费用"]),
        "营业利润": extract_value(is_text, FIELD_PATTERNS["营业利润"]),
        "利润总额": extract_value(is_text, FIELD_PATTERNS["利润总额"]),
        "归母净利润": extract_value(is_text, FIELD_PATTERNS["归母净利润"]),
        "经营活动现金流量净额": extract_value(cf_text, FIELD_PATTERNS["经营活动现金流量净额"]),
        "购建长期资产支付的现金": extract_value(cf_text, FIELD_PATTERNS["购建长期资产支付的现金"]),
        "货币资金": extract_value(bs_text, FIELD_PATTERNS["货币资金"]),
        "存货": extract_value(bs_text, FIELD_PATTERNS["存货"]),
        "流动资产合计": extract_value(bs_text, FIELD_PATTERNS["流动资产合计"]),
        "固定资产": extract_value(bs_text, FIELD_PATTERNS["固定资产"]),
        "无形资产": extract_value(bs_text, FIELD_PATTERNS["无形资产"]),
        "总资产": extract_value(bs_text, FIELD_PATTERNS["总资产"]),
        "短期借款": extract_value(bs_text, FIELD_PATTERNS["短期借款"], zero_if_missing=True),
        "长期借款": extract_value(bs_text, FIELD_PATTERNS["长期借款"], zero_if_missing=True),
        "流动负债合计": extract_value(bs_text, FIELD_PATTERNS["流动负债合计"]),
        "总负债": extract_value(bs_text, FIELD_PATTERNS["总负债"]),
        "归母权益": extract_value(bs_text, FIELD_PATTERNS["归母权益"]),
        "资产总计_期末": extract_pair_value(bs_text, FIELD_PATTERNS["总资产"])[0],
        "资产总计_期初": extract_pair_value(bs_text, FIELD_PATTERNS["总资产"])[1],
        "归母权益_期末": extract_pair_value(bs_text, FIELD_PATTERNS["归母权益"])[0],
        "归母权益_期初": extract_pair_value(bs_text, FIELD_PATTERNS["归母权益"])[1],
    }


def build_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for report in REPORTS:
        pdf_path = report["官方来源"]
        if not pdf_path.exists():
            raise FileNotFoundError(f"缺少文件：{pdf_path}")
        metrics = extract_report(pdf_path)
        avg_assets = (metrics["资产总计_期末"] + metrics["资产总计_期初"]) / 2
        avg_equity = (metrics["归母权益_期末"] + metrics["归母权益_期初"]) / 2

        row = {
            "市场": report["市场"],
            "代码": report["代码"],
            "公司": report["公司"],
            "年度": report["年度"],
            "币种": "人民币",
            "营业收入": metrics["营业收入"],
            "营业成本": metrics["营业成本"],
            "毛利": metrics["毛利"],
            "销售费用": metrics["销售费用"],
            "管理费用": metrics["管理费用"],
            "研发费用": metrics["研发费用"],
            "财务费用": metrics["财务费用"],
            "营业利润": metrics["营业利润"],
            "利润总额": metrics["利润总额"],
            "归母净利润": metrics["归母净利润"],
            "经营活动现金流量净额": metrics["经营活动现金流量净额"],
            "购建长期资产支付的现金": metrics["购建长期资产支付的现金"],
            "货币资金": metrics["货币资金"],
            "存货": metrics["存货"],
            "流动资产合计": metrics["流动资产合计"],
            "固定资产": metrics["固定资产"],
            "无形资产": metrics["无形资产"],
            "总资产": metrics["总资产"],
            "短期借款": metrics["短期借款"],
            "长期借款": metrics["长期借款"],
            "流动负债合计": metrics["流动负债合计"],
            "总负债": metrics["总负债"],
            "归母权益": metrics["归母权益"],
            "毛利率": metrics["毛利"] / metrics["营业收入"] if metrics["营业收入"] else None,
            "归母净利率": metrics["归母净利润"] / metrics["营业收入"] if metrics["营业收入"] else None,
            "销售费用率": metrics["销售费用"] / metrics["营业收入"] if metrics["营业收入"] else None,
            "管理费用率": metrics["管理费用"] / metrics["营业收入"] if metrics["营业收入"] else None,
            "研发费用率": metrics["研发费用"] / metrics["营业收入"] if metrics["营业收入"] else None,
            "财务费用率": metrics["财务费用"] / metrics["营业收入"] if metrics["营业收入"] else None,
            "三费费率": (metrics["销售费用"] + metrics["管理费用"] + metrics["研发费用"]) / metrics["营业收入"] if metrics["营业收入"] else None,
            "ROA": metrics["归母净利润"] / avg_assets if avg_assets else None,
            "ROE": metrics["归母净利润"] / avg_equity if avg_equity else None,
            "资产负债率": metrics["总负债"] / metrics["总资产"] if metrics["总资产"] else None,
            "流动比率": metrics["流动资产合计"] / metrics["流动负债合计"] if metrics["流动负债合计"] else None,
            "现金比率": metrics["货币资金"] / metrics["流动负债合计"] if metrics["流动负债合计"] else None,
            "经营现金流/归母净利润": metrics["经营活动现金流量净额"] / metrics["归母净利润"] if metrics["归母净利润"] else None,
            "资本开支/收入": metrics["购建长期资产支付的现金"] / metrics["营业收入"] if metrics["营业收入"] else None,
            "官方文件类型": report["官方文件类型"],
            "官方来源": str(pdf_path),
        }
        rows.append(row)
    return rows


def write_markdown(rows: list[dict[str, object]]) -> None:
    by_company: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        by_company.setdefault(row["公司"], []).append(row)
    lines = [
        "# A股可比公司 2024-2025 核心数据说明",
        "",
        "## 口径说明",
        "",
        "- 2024 年使用各公司最新可得的年度报告全文。",
        "- 2025 年优先使用年度报告；若年度报告尚未获取，则使用最新完整官方披露口径（如季度报告）。",
        "- 三表字段均从合并报表提取；毛利按 `营业收入 - 营业成本` 计算。",
        "- `ROA` 与 `ROE` 采用期初期末平均资产/权益口径。",
        "",
        "## 2025 口径明细",
        "",
        "| 公司 | 2024 口径 | 2025 口径 |",
        "|:--|:--|:--|",
    ]
    for company, items in by_company.items():
        items = sorted(items, key=lambda x: x["年度"])
        lines.append(f"| {company} | {items[0]['官方文件类型']} | {items[1]['官方文件类型']} |")
    lines.extend(
        [
            "",
            "## 文件说明",
            "",
            "- 输出 CSV：`data/A股可比公司_2024_2025_核心数据.csv`",
            "- 每条记录的 `官方来源` 都写入了本地 PDF 路径，便于复核。",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    rows = build_rows()
    df = pd.DataFrame(rows)
    df = df[
        [
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
    ]
    df.to_csv(OUT_CSV, index=False, encoding="utf-8-sig", float_format="%.10f")
    write_markdown(rows)
    print(f"saved {OUT_CSV}")
    print(f"saved {OUT_MD}")


if __name__ == "__main__":
    main()
