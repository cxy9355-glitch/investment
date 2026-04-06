from __future__ import annotations

import math
import re
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import font_manager
from pypdf import PdfReader


BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "raw" / "official"
DATA_DIR = BASE_DIR / "data"
CHART_DIR = BASE_DIR / "charts"


SOURCE_CONFIG = {
    2020: {
        "source_type": "A股招股说明书",
        "pdf": RAW_DIR / "A股招股说明书_2021-05-14.pdf",
        "scale": 10000.0,
        "pages": {
            "balance": [353, 354],
            "income": [355],
            "cashflow": [356, 357],
        },
        "value_count": 3,
        "column_order": [2020, 2019, 2018],
    },
    2021: {
        "source_type": "年度报告",
        "pdf": RAW_DIR / "2021年年度报告.pdf",
        "scale": 1.0,
        "pages": {
            "balance": [106, 107, 108],
            "income": [110, 111, 112],
            "cashflow": [114, 115, 116],
        },
        "value_count": 2,
        "column_order": [2021, 2020],
    },
    2022: {
        "source_type": "年度报告",
        "pdf": RAW_DIR / "2022年年度报告.pdf",
        "scale": 1.0,
        "pages": {
            "balance": [103, 104, 105],
            "income": [107, 108, 109],
            "cashflow": [110, 111, 112],
        },
        "value_count": 2,
        "column_order": [2022, 2021],
    },
    2023: {
        "source_type": "年度报告",
        "pdf": RAW_DIR / "2023年年度报告.pdf",
        "scale": 1.0,
        "pages": {
            "balance": [113, 114, 115],
            "income": [117, 118, 119],
            "cashflow": [120, 121, 122],
        },
        "value_count": 2,
        "column_order": [2023, 2022],
    },
    2024: {
        "source_type": "年度报告",
        "pdf": RAW_DIR / "2024年年度报告.pdf",
        "scale": 1.0,
        "pages": {
            "balance": [122, 123, 124],
            "income": [126, 127, 128],
            "cashflow": [130, 131, 132],
        },
        "value_count": 2,
        "column_order": [2024, 2023],
    },
}


BALANCE_PATTERNS = {
    "货币资金": [r"货币资金"],
    "交易性金融资产": [r"交易性金融资产"],
    "应收账款": [r"应收账款"],
    "预付款项": [r"预付款项"],
    "其他应收款": [r"其他应收款"],
    "存货": [r"存货"],
    "一年内到期的非流动资产": [r"一年内到期的非流动资产"],
    "其他流动资产": [r"其他流动资产"],
    "流动资产合计": [r"流动资产合计"],
    "债权投资": [r"债权投资"],
    "其他非流动金融资产": [r"其他非流动金融资产"],
    "固定资产": [r"固定资产"],
    "在建工程": [r"在建工程"],
    "使用权资产": [r"使用权资产"],
    "无形资产": [r"无形资产"],
    "长期待摊费用": [r"长期待摊费用"],
    "递延所得税资产": [r"递延所得税资产"],
    "其他非流动资产": [r"其他非流动资产"],
    "非流动资产合计": [r"非流动资产合计"],
    "资产总计": [r"资产总计"],
    "短期借款": [r"短期借款"],
    "应付票据": [r"应付票据"],
    "应付账款": [r"应付账款"],
    "合同负债": [r"合同负债"],
    "应付职工薪酬": [r"应付职工薪酬"],
    "应交税费": [r"应交税费"],
    "其他应付款": [r"其他应付款"],
    "一年内到期的非流动负债": [r"一年内到期的非流动负债"],
    "其他流动负债": [r"其他流动负债"],
    "流动负债合计": [r"流动负债合计"],
    "长期借款": [r"长期借款"],
    "租赁负债": [r"租赁负债"],
    "递延收益": [r"递延收益"],
    "递延所得税负债": [r"递延所得税负债"],
    "非流动负债合计": [r"非流动负债合计"],
    "负债合计": [r"负债合计"],
    "股本": [r"实收资本（或股本）", r"股本/实收资本"],
    "资本公积": [r"资本公积"],
    "其他综合收益": [r"其他综合收益"],
    "盈余公积": [r"盈余公积"],
    "未分配利润": [r"未分配利润"],
    "归母权益合计": [r"归属于母公司所有者权益（或股东权益）合计", r"所有者权益合计"],
    "少数股东权益": [r"少数股东权益"],
    "权益合计": [r"所有者权益（或股东权益）合计", r"所有者权益合计"],
}


INCOME_PATTERNS = {
    "营业收入": [r"一、营业总收入", r"一、营业收入"],
    "营业成本": [r"营业成本"],
    "税金及附加": [r"税金及附加"],
    "销售费用": [r"销售费用"],
    "管理费用": [r"管理费用"],
    "研发费用": [r"研发费用"],
    "财务费用": [r"财务费用"],
    "其他收益": [r"其他收益"],
    "投资收益": [r"投资收益"],
    "公允价值变动收益": [r"公允价值变动收益"],
    "信用减值损失": [r"信用减值损失"],
    "资产减值损失": [r"资产减值损失"],
    "资产处置收益": [r"资产处置收益"],
    "营业利润": [r"二、营业利润", r"营业利润"],
    "营业外收入": [r"营业外收入"],
    "营业外支出": [r"营业外支出"],
    "利润总额": [r"三、利润总额", r"利润总额"],
    "所得税费用": [r"所得税费用"],
    "净利润": [r"五、净利润", r"四、净利润", r"净利润"],
    "归母净利润": [r"归属于母公司股东的净利润", r"归属于母公司所有者的净利润"],
    "少数股东损益": [r"少数股东损益"],
    "综合收益总额": [r"七、综合收益总额", r"六、综合收益总额", r"综合收益总额"],
    "归母综合收益总额": [r"归属于母公司所有者的综合收益总额"],
    "基本每股收益": [r"基本每股收益"],
    "稀释每股收益": [r"稀释每股收益"],
}


CASHFLOW_PATTERNS = {
    "销售商品提供劳务收到的现金": [r"销售商品、提供劳务收到的现金"],
    "收到的税费返还": [r"收到的税费返还"],
    "收到其他与经营活动有关的现金": [r"收到其他与经营活动有关的现金"],
    "经营活动现金流入小计": [r"经营活动现金流入小计"],
    "购买商品接受劳务支付的现金": [r"购买商品、接受劳务支付的现金"],
    "支付给职工及为职工支付的现金": [r"支付给职工及为职工支付的现金", r"支付给职工以及为职工支付的现金"],
    "支付的各项税费": [r"支付的各项税费"],
    "支付其他与经营活动有关的现金": [r"支付其他与经营活动有关的现金"],
    "经营活动现金流量净额": [r"经营活动产生的现金流量净额"],
    "收回投资收到的现金": [r"收回投资收到的现金"],
    "取得投资收益收到的现金": [r"取得投资收益收到的现金"],
    "投资活动现金流入小计": [r"投资活动现金流入小计"],
    "购建长期资产支付的现金": [r"购建固定资产、无形资产和其他长期资产支付的现金"],
    "投资支付的现金": [r"投资支付的现金"],
    "投资活动现金流量净额": [r"投资活动产生的现金流量净额"],
    "吸收投资收到的现金": [r"吸收投资收到的现金"],
    "取得借款收到的现金": [r"取得借款收到的现金"],
    "分配股利及偿付利息支付的现金": [r"分配股利及偿付利息支付的现金", r"分配股利、利润或偿付利息支付的现金"],
    "筹资活动现金流量净额": [r"筹资活动产生的现金流量净额"],
    "汇率变动影响": [r"汇率变动对现金及现金等价物的影响"],
    "现金净增加额": [r"现金及现金等价物净增加额", r"现金及现金等价物净增加额"],
    "期初现金及现金等价物余额": [r"期初现金及现金等价物余额"],
    "期末现金及现金等价物余额": [r"期末现金及现金等价物余额"],
}

NO_SCALE_ITEMS = {"基本每股收益", "稀释每股收益"}


def configure_matplotlib_fonts() -> None:
    candidates = ["Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "Source Han Sans SC", "Arial Unicode MS"]
    available = {font.name for font in font_manager.fontManager.ttflist}
    selected = next((name for name in candidates if name in available), None)
    if selected:
        plt.rcParams["font.sans-serif"] = [selected, "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False


def clean_text(text: str) -> str:
    text = re.sub(r"东鹏饮料（集团）股份有限公司\s*\d{4}\s*年年度报告", " ", text)
    text = re.sub(r"东鹏饮料（集团）股份有限公司\s*首次公开发行股票招股说明书", " ", text)
    text = re.sub(r"\d+\s*/\s*\d+", " ", text)
    text = re.sub(r"单位[:：]?\s*元\s*币种[:：]?\s*人民币", " ", text)
    text = re.sub(r"单位[:：]?\s*万元", " ", text)
    text = re.sub(r"编制单位[:：]?\s*东鹏饮料（集团）股份有限公司", " ", text)
    text = re.sub(r"主管会计工作负责人[:：].+?会计机构负责人[:：].+?(?=母公司|合并现金流量表|$)", " ", text)
    text = re.sub(r"公司负责人[:：].+?(?=母公司|合并现金流量表|$)", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def read_pages(pdf_path: Path, pages: list[int]) -> str:
    reader = PdfReader(str(pdf_path))
    text = " ".join((reader.pages[p - 1].extract_text() or "") for p in pages)
    return clean_text(text)


def parse_value(raw: str | None, scale: float) -> float | None:
    if raw is None:
        return None
    raw = raw.strip()
    if raw in {"-", "--", ""}:
        return 0.0
    return float(raw.replace(",", "")) * scale


def fuzzy_label(label: str) -> str:
    chars = [re.escape(ch) for ch in label if not ch.isspace()]
    return r"\s*".join(chars)


def build_pattern(label_pattern: str, count: int) -> re.Pattern[str]:
    num = r"(-?[\d,]+\.\d+|-{1,2})"
    body = r"\s+".join([num] * count)
    gap = r".*?"
    return re.compile(fuzzy_label(label_pattern) + gap + body, re.S)


def extract_row(text: str, item_name: str, label_patterns: list[str], count: int, scale: float) -> list[float | None]:
    item_scale = 1.0 if item_name in NO_SCALE_ITEMS else scale
    for label in label_patterns:
        pattern = build_pattern(label, count)
        match = pattern.search(text)
        if match:
            return [parse_value(item, item_scale) for item in match.groups()]
    return [None] * count


def extract_statement(config: dict, statement: str, pattern_map: dict[str, list[str]]) -> pd.DataFrame:
    text = read_pages(config["pdf"], config["pages"][statement])
    count = config["value_count"]
    data: list[dict[str, float | int | str | None]] = []
    for line_item, labels in pattern_map.items():
        values = extract_row(text, line_item, labels, count, config["scale"])
        row: dict[str, float | int | str | None] = {"项目": line_item}
        for idx, year in enumerate(config["column_order"][:count]):
            row[str(year)] = values[idx]
        data.append(row)
    return pd.DataFrame(data)


def year_statement_frames() -> tuple[dict[int, pd.DataFrame], dict[int, pd.DataFrame], dict[int, pd.DataFrame]]:
    balance_frames: dict[int, pd.DataFrame] = {}
    income_frames: dict[int, pd.DataFrame] = {}
    cashflow_frames: dict[int, pd.DataFrame] = {}
    for year, config in SOURCE_CONFIG.items():
        balance_frames[year] = extract_statement(config, "balance", BALANCE_PATTERNS)
        income_frames[year] = extract_statement(config, "income", INCOME_PATTERNS)
        cashflow_frames[year] = extract_statement(config, "cashflow", CASHFLOW_PATTERNS)
    return balance_frames, income_frames, cashflow_frames


def merge_frames(frames: dict[int, pd.DataFrame], years: list[int]) -> pd.DataFrame:
    merged: pd.DataFrame | None = None
    for year in years:
        current = frames[year][["项目", str(year)]].copy()
        merged = current if merged is None else merged.merge(current, on="项目", how="outer")
    assert merged is not None
    return merged


def series_map(df: pd.DataFrame) -> dict[str, dict[int, float | None]]:
    result: dict[str, dict[int, float | None]] = {}
    for _, row in df.iterrows():
        result[str(row["项目"])] = {int(col): (None if pd.isna(row[col]) else float(row[col])) for col in df.columns if col != "项目"}
    return result


def safe_div(a: float | None, b: float | None) -> float | None:
    if a is None or b in (None, 0):
        return None
    return a / b


def average(a: float | None, b: float | None) -> float | None:
    if a is None or b is None:
        return None
    return (a + b) / 2


def compute_ratios(balance_df: pd.DataFrame, income_df: pd.DataFrame, cashflow_df: pd.DataFrame, years: list[int]) -> pd.DataFrame:
    bmap = series_map(balance_df)
    imap = series_map(income_df)
    cmap = series_map(cashflow_df)
    rows = []
    for year in years:
        revenue = imap["营业收入"][year]
        cost = imap["营业成本"][year]
        gross_profit = None if revenue is None or cost is None else revenue - cost
        parent_np = imap["归母净利润"][year] if imap["归母净利润"][year] is not None else imap["净利润"][year]
        total_assets = bmap["资产总计"][year]
        total_liabilities = bmap["负债合计"][year]
        parent_equity = bmap["归母权益合计"][year] if bmap["归母权益合计"][year] is not None else bmap["权益合计"][year]
        prev_year = year - 1
        avg_assets = average(total_assets, bmap["资产总计"].get(prev_year))
        avg_equity = average(parent_equity, bmap["归母权益合计"].get(prev_year, bmap["权益合计"].get(prev_year)))
        row = {
            "年份": year,
            "营业收入": revenue,
            "毛利": gross_profit,
            "归母净利润": parent_np,
            "经营活动现金流量净额": cmap["经营活动现金流量净额"][year],
            "购建长期资产支付的现金": cmap["购建长期资产支付的现金"][year],
            "总资产": total_assets,
            "总负债": total_liabilities,
            "归母权益": parent_equity,
            "毛利率": safe_div(gross_profit, revenue),
            "归母净利率": safe_div(parent_np, revenue),
            "销售费用率": safe_div(imap["销售费用"][year], revenue),
            "管理费用率": safe_div(imap["管理费用"][year], revenue),
            "研发费用率": safe_div(imap["研发费用"][year], revenue),
            "财务费用率": safe_div(imap["财务费用"][year], revenue),
            "三费费率": safe_div(
                (imap["销售费用"][year] or 0.0) + (imap["管理费用"][year] or 0.0) + (imap["研发费用"][year] or 0.0),
                revenue,
            ),
            "ROA": safe_div(parent_np, avg_assets),
            "ROE": safe_div(parent_np, avg_equity),
            "资产负债率": safe_div(total_liabilities, total_assets),
            "流动比率": safe_div(bmap["流动资产合计"][year], bmap["流动负债合计"][year]),
            "现金比率": safe_div(bmap["货币资金"][year], bmap["流动负债合计"][year]),
            "经营现金流/归母净利润": safe_div(cmap["经营活动现金流量净额"][year], parent_np),
            "资本开支/收入": safe_div(cmap["购建长期资产支付的现金"][year], revenue),
        }
        rows.append(row)
    return pd.DataFrame(rows)


def apply_manual_adjustments(balance_df: pd.DataFrame, income_df: pd.DataFrame, cashflow_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    b = balance_df.copy()
    i = income_df.copy()
    c = cashflow_df.copy()

    def set_value(df: pd.DataFrame, item: str, year: int, value: float) -> None:
        df.loc[df["项目"] == item, str(year)] = value

    def get_value(df: pd.DataFrame, item: str, year: int) -> float | None:
        series = df.loc[df["项目"] == item, str(year)]
        if series.empty or pd.isna(series.iloc[0]):
            return None
        return float(series.iloc[0])

    for year in [2020, 2021, 2022, 2023, 2024]:
        current_liab = get_value(b, "流动负债合计", year)
        noncurrent_liab = get_value(b, "非流动负债合计", year)
        parent_equity = get_value(b, "归母权益合计", year)
        total_assets = get_value(b, "资产总计", year)
        total_liabilities = None
        if current_liab is not None and noncurrent_liab is not None:
            total_liabilities = current_liab + noncurrent_liab
            set_value(b, "负债合计", year, total_liabilities)
        if total_assets is not None and total_liabilities is not None:
            computed_total_equity = total_assets - total_liabilities
            set_value(b, "权益合计", year, computed_total_equity)
            if parent_equity is not None:
                minority_equity = computed_total_equity - parent_equity
                if abs(minority_equity) < 1000:
                    minority_equity = 0.0
                set_value(b, "少数股东权益", year, minority_equity)
            else:
                set_value(b, "归母权益合计", year, computed_total_equity)
                set_value(b, "少数股东权益", year, 0.0)

        np_total = get_value(i, "净利润", year)
        np_parent = get_value(i, "归母净利润", year)
        if np_total is not None and np_parent is not None:
            set_value(i, "少数股东损益", year, np_total - np_parent)

    set_value(b, "其他综合收益", 2020, 0.0)
    set_value(b, "其他综合收益", 2021, 0.0)

    absorb_values = {
        2020: 0.0,
        2021: 1851262700.0,
        2022: 0.0,
        2023: 0.0,
        2024: 4056480.0,
    }
    fx_values = {
        2020: 0.0,
        2021: 0.0,
        2022: -15123032.52,
        2023: -28557118.63,
        2024: 31721563.28,
    }
    for year, value in absorb_values.items():
        set_value(c, "吸收投资收到的现金", year, value)
    for year, value in fx_values.items():
        set_value(c, "汇率变动影响", year, value)

    return b, i, c


def to_yi(series: pd.Series) -> pd.Series:
    return series / 100000000.0


def save_chart_revenue_profit(ratio_df: pd.DataFrame) -> None:
    plt.figure(figsize=(10, 6))
    plt.plot(ratio_df["年份"], to_yi(ratio_df["营业收入"]), marker="o", label="营业收入(亿元)")
    plt.plot(ratio_df["年份"], to_yi(ratio_df["归母净利润"]), marker="o", label="归母净利润(亿元)")
    plt.title("东鹏饮料 2020-2024 营收与归母净利润")
    plt.xlabel("年份")
    plt.ylabel("亿元")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(CHART_DIR / "01_营收与归母净利润.png", dpi=200)
    plt.close()


def save_chart_margins(ratio_df: pd.DataFrame) -> None:
    plt.figure(figsize=(10, 6))
    for col in ["毛利率", "归母净利率", "ROA", "ROE"]:
        plt.plot(ratio_df["年份"], ratio_df[col] * 100, marker="o", label=col)
    plt.title("东鹏饮料 2020-2024 盈利能力与回报率")
    plt.xlabel("年份")
    plt.ylabel("%")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(CHART_DIR / "02_盈利能力与回报率.png", dpi=200)
    plt.close()


def save_chart_expenses(ratio_df: pd.DataFrame) -> None:
    plt.figure(figsize=(10, 6))
    for col in ["销售费用率", "管理费用率", "研发费用率", "财务费用率", "三费费率"]:
        plt.plot(ratio_df["年份"], ratio_df[col] * 100, marker="o", label=col)
    plt.title("东鹏饮料 2020-2024 费用率趋势")
    plt.xlabel("年份")
    plt.ylabel("%")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(CHART_DIR / "03_费用率趋势.png", dpi=200)
    plt.close()


def save_chart_balance_quality(ratio_df: pd.DataFrame) -> None:
    plt.figure(figsize=(10, 6))
    for col in ["资产负债率", "流动比率", "现金比率", "经营现金流/归母净利润"]:
        plt.plot(ratio_df["年份"], ratio_df[col] * 100 if col == "资产负债率" else ratio_df[col], marker="o", label=col)
    plt.title("东鹏饮料 2020-2024 偿债与现金质量")
    plt.xlabel("年份")
    plt.ylabel("倍 / %")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(CHART_DIR / "04_偿债与现金质量.png", dpi=200)
    plt.close()


def format_amount(v: float | None) -> str:
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return ""
    return f"{v / 100000000:.2f}"


def format_ratio(v: float | None) -> str:
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return ""
    return f"{v * 100:.2f}%"


def write_markdown(balance_df: pd.DataFrame, income_df: pd.DataFrame, cashflow_df: pd.DataFrame, ratio_df: pd.DataFrame) -> None:
    source_rows = [
        ["A股招股说明书", "2021-05-14", "A股招股书回溯的 2018-2020 审计财务报表", "raw/official/A股招股说明书_2021-05-14.pdf"],
        ["2021 年年度报告", "2022-02-28", "2021 年合并报表", "raw/official/2021年年度报告.pdf"],
        ["2022 年年度报告", "2023-04-22", "2022 年合并报表", "raw/official/2022年年度报告.pdf"],
        ["2023 年年度报告", "2024-04-15", "2023 年合并报表", "raw/official/2023年年度报告.pdf"],
        ["2024 年年度报告", "2025-03-08", "2024 年合并报表", "raw/official/2024年年度报告.pdf"],
        ["港股招股说明书", "2026-01-26", "港股 IPO 招股说明书，已下载留档", "raw/official/港股招股说明书_2026-01-26.pdf"],
    ]
    source_df = pd.DataFrame(source_rows, columns=["资料", "日期", "用途", "本地路径"])

    balance_display_rows = [
        "货币资金",
        "交易性金融资产",
        "应收账款",
        "预付款项",
        "其他应收款",
        "存货",
        "一年内到期的非流动资产",
        "其他流动资产",
        "流动资产合计",
        "债权投资",
        "其他非流动金融资产",
        "固定资产",
        "在建工程",
        "使用权资产",
        "无形资产",
        "长期待摊费用",
        "递延所得税资产",
        "其他非流动资产",
        "非流动资产合计",
        "资产总计",
        "短期借款",
        "应付票据",
        "应付账款",
        "合同负债",
        "应付职工薪酬",
        "应交税费",
        "其他应付款",
        "一年内到期的非流动负债",
        "其他流动负债",
        "流动负债合计",
        "长期借款",
        "租赁负债",
        "递延收益",
        "递延所得税负债",
        "非流动负债合计",
        "负债合计",
        "股本",
        "资本公积",
        "其他综合收益",
        "盈余公积",
        "未分配利润",
        "归母权益合计",
        "少数股东权益",
        "权益合计",
    ]
    income_display_rows = [
        "营业收入",
        "营业成本",
        "税金及附加",
        "销售费用",
        "管理费用",
        "研发费用",
        "财务费用",
        "其他收益",
        "投资收益",
        "营业利润",
        "营业外收入",
        "营业外支出",
        "利润总额",
        "所得税费用",
        "净利润",
        "归母净利润",
        "少数股东损益",
        "综合收益总额",
        "归母综合收益总额",
        "基本每股收益",
        "稀释每股收益",
    ]
    cashflow_display_rows = [
        "销售商品提供劳务收到的现金",
        "收到的税费返还",
        "收到其他与经营活动有关的现金",
        "经营活动现金流入小计",
        "购买商品接受劳务支付的现金",
        "支付给职工及为职工支付的现金",
        "支付的各项税费",
        "支付其他与经营活动有关的现金",
        "经营活动现金流量净额",
        "收回投资收到的现金",
        "取得投资收益收到的现金",
        "投资活动现金流入小计",
        "购建长期资产支付的现金",
        "投资支付的现金",
        "投资活动现金流量净额",
        "吸收投资收到的现金",
        "取得借款收到的现金",
        "分配股利及偿付利息支付的现金",
        "筹资活动现金流量净额",
        "汇率变动影响",
        "现金净增加额",
        "期初现金及现金等价物余额",
        "期末现金及现金等价物余额",
    ]

    balance_md = balance_df[balance_df["项目"].isin(balance_display_rows)].copy()
    income_md = income_df[income_df["项目"].isin(income_display_rows)].copy()
    cashflow_md = cashflow_df[cashflow_df["项目"].isin(cashflow_display_rows)].copy()
    balance_md["项目"] = pd.Categorical(balance_md["项目"], categories=balance_display_rows, ordered=True)
    income_md["项目"] = pd.Categorical(income_md["项目"], categories=income_display_rows, ordered=True)
    cashflow_md["项目"] = pd.Categorical(cashflow_md["项目"], categories=cashflow_display_rows, ordered=True)
    balance_md = balance_md.sort_values("项目")
    income_md = income_md.sort_values("项目")
    cashflow_md = cashflow_md.sort_values("项目")
    ratio_md = ratio_df.copy()

    for frame in [balance_md, income_md, cashflow_md]:
        for col in frame.columns:
            if col != "项目":
                frame[col] = frame[col].map(format_amount)
    for col in ["营业收入", "毛利", "归母净利润", "经营活动现金流量净额", "购建长期资产支付的现金", "总资产", "总负债", "归母权益"]:
        ratio_md[col] = ratio_md[col].map(format_amount)
    for col in ["毛利率", "归母净利率", "销售费用率", "管理费用率", "研发费用率", "财务费用率", "三费费率", "ROA", "ROE", "资产负债率"]:
        ratio_md[col] = ratio_md[col].map(format_ratio)
    for col in ["流动比率", "现金比率", "经营现金流/归母净利润", "资本开支/收入"]:
        ratio_md[col] = ratio_md[col].map(lambda x: "" if x is None or pd.isna(x) else f"{x:.2f}")

    for col in ["2020", "2021", "2022", "2023", "2024"]:
        for item in ["基本每股收益", "稀释每股收益"]:
            raw_value = income_df.loc[income_df["项目"] == item, col]
            if not raw_value.empty and not pd.isna(raw_value.iloc[0]):
                income_md.loc[income_md["项目"] == item, col] = f"{float(raw_value.iloc[0]):.4f}"
            else:
                income_md.loc[income_md["项目"] == item, col] = ""

    lines = [
        "# 东鹏饮料 2020-2024 财务数据底表",
        "",
        "## 口径说明",
        "",
        "- 公司主体：东鹏饮料（集团）股份有限公司。",
        "- 时间范围：2020-2024 共 5 个完整会计年度。",
        "- 2020 年数据来自 A 股招股说明书中的经审计合并报表；2021-2024 年数据来自对应年度年报合并报表。",
        "- 港股招股说明书已下载留档，但本版 5 年趋势主表未混入港股招股书中的 2025 年九个月口径，以避免年度与期间口径混杂。",
        "- 截至 2026-04-06，未检索到东鹏饮料 2025 年年度报告正式 PDF 的官方披露链接，因此本版年报底表截至 2024 年。",
        "- 三表金额展示单位为“亿元人民币”，CSV 明细保留原始“元”口径。",
        "- ROA = 归母净利润 / 平均总资产；ROE = 归母净利润 / 平均归母权益。",
        "",
        "## 已下载官方资料",
        "",
        source_df.to_markdown(index=False),
        "",
        "## 合并资产负债表",
        "",
        balance_md.to_markdown(index=False),
        "",
        "## 合并利润表",
        "",
        income_md.to_markdown(index=False),
        "",
        "## 合并现金流量表",
        "",
        cashflow_md.to_markdown(index=False),
        "",
        "## 关键财务指标",
        "",
        ratio_md.to_markdown(index=False),
        "",
        "## 图表",
        "",
        "### 营收与归母净利润",
        "",
        "![营收与归母净利润](charts/01_营收与归母净利润.png)",
        "",
        "### 盈利能力与回报率",
        "",
        "![盈利能力与回报率](charts/02_盈利能力与回报率.png)",
        "",
        "### 费用率趋势",
        "",
        "![费用率趋势](charts/03_费用率趋势.png)",
        "",
        "### 偿债与现金质量",
        "",
        "![偿债与现金质量](charts/04_偿债与现金质量.png)",
        "",
    ]
    (BASE_DIR / "东鹏饮料_2020_2024财务数据底表.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    configure_matplotlib_fonts()

    years = [2020, 2021, 2022, 2023, 2024]
    balance_frames, income_frames, cashflow_frames = year_statement_frames()

    balance_df = merge_frames(balance_frames, years)
    income_df = merge_frames(income_frames, years)
    cashflow_df = merge_frames(cashflow_frames, years)
    balance_df, income_df, cashflow_df = apply_manual_adjustments(balance_df, income_df, cashflow_df)

    ratio_df = compute_ratios(balance_df, income_df, cashflow_df, years)
    prev_assets_2019 = float(balance_frames[2020].loc[balance_frames[2020]["项目"] == "资产总计", "2019"].iloc[0])
    prev_equity_2019 = float(balance_frames[2020].loc[balance_frames[2020]["项目"] == "归母权益合计", "2019"].iloc[0])
    ratio_df.loc[ratio_df["年份"] == 2020, "ROA"] = 812063500.0 / ((4361286400.0 + prev_assets_2019) / 2)
    ratio_df.loc[ratio_df["年份"] == 2020, "ROE"] = 812063500.0 / ((1913253400.0 + prev_equity_2019) / 2)

    balance_df.to_csv(DATA_DIR / "东鹏饮料_合并资产负债表_2020_2024_元.csv", index=False, encoding="utf-8-sig")
    income_df.to_csv(DATA_DIR / "东鹏饮料_合并利润表_2020_2024_元.csv", index=False, encoding="utf-8-sig")
    cashflow_df.to_csv(DATA_DIR / "东鹏饮料_合并现金流量表_2020_2024_元.csv", index=False, encoding="utf-8-sig")
    ratio_df.to_csv(DATA_DIR / "东鹏饮料_关键指标_2020_2024.csv", index=False, encoding="utf-8-sig")

    with pd.ExcelWriter(DATA_DIR / "东鹏饮料_财务数据与指标_2020_2024.xlsx") as writer:
        balance_df.to_excel(writer, sheet_name="合并资产负债表", index=False)
        income_df.to_excel(writer, sheet_name="合并利润表", index=False)
        cashflow_df.to_excel(writer, sheet_name="合并现金流量表", index=False)
        ratio_df.to_excel(writer, sheet_name="关键指标", index=False)

    save_chart_revenue_profit(ratio_df)
    save_chart_margins(ratio_df)
    save_chart_expenses(ratio_df)
    save_chart_balance_quality(ratio_df)
    write_markdown(balance_df, income_df, cashflow_df, ratio_df)


if __name__ == "__main__":
    main()
