from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(r"G:\Codex\个人\investment")
SOURCE_SCREEN = ROOT / "机构持仓研究" / "巴芒_喜马拉雅_高瓴_历史持仓筛选_2026-04-17.xlsx"
SOURCE_FULL = ROOT / "机构持仓研究" / "长期持有全池数据集_2026-04-17.xlsx"

OUTPUT_SCREEN = ROOT / "机构持仓研究" / "巴芒_喜马拉雅_高瓴_历史持仓筛选_2026-04-17_可比清理版.xlsx"
OUTPUT_FULL = ROOT / "机构持仓研究" / "长期持有全池数据集_2026-04-17_可比清理版.xlsx"

CORE_FIELDS = ["revenue", "net_income", "assets", "equity", "liabilities"]
MIN_COMPLETE_YEARS = 3


def load_inputs() -> tuple[dict[str, pd.DataFrame], pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    screen_sheets = {
        name: pd.read_excel(SOURCE_SCREEN, sheet_name=name)
        for name in ["口径说明", "历史热度原榜", "估值总表", "深研候选"]
    }
    coverage = pd.read_excel(SOURCE_FULL, sheet_name="全池覆盖说明")
    holdings = pd.read_excel(SOURCE_FULL, sheet_name="实体级持仓历史")
    annual = pd.read_excel(SOURCE_FULL, sheet_name="年度经营质量")
    return screen_sheets, coverage, holdings, annual


def build_holding_metrics(holdings: pd.DataFrame) -> pd.DataFrame:
    metrics = (
        holdings.groupby("ticker", as_index=False)
        .agg(
            持仓覆盖实体数=("manager_entity", "nunique"),
            持仓历史行数=("ticker", "size"),
            首次持仓报告期=("report_date", "min"),
            最新持仓报告期=("report_date", "max"),
            平均持仓权重=("position_weight", "mean"),
            峰值持仓权重=("position_weight", "max"),
            当前持仓行数=("is_current", lambda s: int(s.fillna(False).sum())),
        )
    )
    return metrics


def build_annual_metrics(annual: pd.DataFrame) -> pd.DataFrame:
    annual = annual.copy()
    annual["有效财年标记"] = annual["fiscal_year"].notna()
    annual["核心字段完整"] = annual[CORE_FIELDS].notna().all(axis=1) & annual["有效财年标记"]
    metrics = (
        annual.groupby("ticker", as_index=False)
        .agg(
            年度记录行数=("ticker", "size"),
            有效财年行数=("有效财年标记", "sum"),
            核心完整财年行数=("核心字段完整", "sum"),
            首个有效财年=("fiscal_year", "min"),
            最新有效财年=("fiscal_year", "max"),
            年度source_status=("source_status", lambda s: " | ".join(sorted(set(str(x) for x in s if pd.notna(x)))[:6])),
        )
    )
    return metrics


def classify_missing_row(row: pd.Series) -> tuple[str, str]:
    quarters = int(row.get("出现季度数") or 0)
    max_weight = float(row.get("峰值持仓权重") or 0)
    current = str(row.get("当前是否仍持有") or "").strip() in {"是", "True", "true", "1"}
    deep = str(row.get("深研候选") or "").strip() in {"是", "True", "true", "1"}
    last_date = pd.to_datetime(row.get("最新持仓报告期"), errors="coerce")

    if quarters >= 8:
        return "keep_case", "无有效财年数据，但出现季度数较高，保留为历史持仓案例"
    if max_weight >= 0.05:
        return "keep_case", "无有效财年数据，但峰值持仓权重较高，保留为高关注历史案例"
    if quarters <= 4 and max_weight < 0.01 and (not current) and (not deep):
        return "drop", "无有效财年数据，且持仓季度少、权重低、非当前持有，研究价值偏低"
    if pd.notna(last_date) and last_date >= pd.Timestamp("2024-01-01") and max_weight >= 0.01:
        return "manual_review", "无有效财年数据，但持仓较新且权重不低，保留人工复核"
    return "manual_review", "无有效财年数据，信号介于保留与剔除之间，保留人工复核"


def build_decision_table(
    screen_sheets: dict[str, pd.DataFrame],
    coverage: pd.DataFrame,
    holdings: pd.DataFrame,
    annual: pd.DataFrame,
) -> pd.DataFrame:
    valuation = screen_sheets["估值总表"].copy()
    valuation = valuation.drop_duplicates(subset=["代码"], keep="first").reset_index(drop=True)
    hold_metrics = build_holding_metrics(holdings)
    annual_metrics = build_annual_metrics(annual)

    df = valuation.merge(hold_metrics, left_on="代码", right_on="ticker", how="left").drop(columns=["ticker"])
    df = df.merge(annual_metrics, left_on="代码", right_on="ticker", how="left").drop(columns=["ticker"])

    df["是否有有效财年数据"] = df["有效财年行数"].fillna(0).gt(0)
    df["是否满足主池完整度"] = df["核心完整财年行数"].fillna(0).ge(MIN_COMPLETE_YEARS)

    decisions = []
    reasons = []
    for row in df.itertuples(index=False):
        row_s = pd.Series(row._asdict())
        if bool(row_s["是否有有效财年数据"]):
            decisions.append("has_valid_annual")
            if bool(row_s["是否满足主池完整度"]):
                reasons.append(f"具有有效财年数据，且核心完整财年行数 >= {MIN_COMPLETE_YEARS}")
            else:
                reasons.append(f"具有有效财年数据，但核心完整财年行数 < {MIN_COMPLETE_YEARS}，暂不进入可比主池")
        else:
            decision, reason = classify_missing_row(row_s)
            decisions.append(decision)
            reasons.append(reason)
    df["判定结果"] = decisions
    df["判定原因"] = reasons
    return df


def build_summary(decisions: pd.DataFrame) -> pd.DataFrame:
    comparable = decisions[decisions["是否满足主池完整度"]].copy()
    kept_cases = decisions[~decisions["是否有有效财年数据"] & decisions["判定结果"].isin(["keep_case", "manual_review"])].copy()
    dropped = decisions[decisions["判定结果"].eq("drop")].copy()
    limited = decisions[decisions["是否有有效财年数据"] & ~decisions["是否满足主池完整度"]].copy()

    rows = [
        ("原始研究池ticker数", int(decisions["代码"].nunique())),
        ("可比主池ticker数", int(comparable["代码"].nunique())),
        ("保留缺数案例数", int(kept_cases["代码"].nunique())),
        ("低价值剔除数", int(dropped["代码"].nunique())),
        ("有限财年覆盖观察样本数", int(limited["代码"].nunique())),
        ("主池完整度阈值", MIN_COMPLETE_YEARS),
    ]
    return pd.DataFrame(rows, columns=["指标", "值"])


def write_pruned_screen_workbook(screen_sheets: dict[str, pd.DataFrame], decisions: pd.DataFrame) -> None:
    comparable_tickers = set(decisions[decisions["是否满足主池完整度"]]["代码"])
    missing_keep = decisions[~decisions["是否有有效财年数据"] & decisions["判定结果"].isin(["keep_case", "manual_review"])].copy()
    dropped = decisions[decisions["判定结果"].eq("drop")].copy()
    limited = decisions[decisions["是否有有效财年数据"] & ~decisions["是否满足主池完整度"]].copy()
    summary = build_summary(decisions)

    scope_note = pd.DataFrame(
        [
            ["清理口径", f"可比主池要求核心完整财年行数 >= {MIN_COMPLETE_YEARS}"],
            ["缺数案例处理", "无有效财年数据样本不直接并入主池；保留案例与人工复核样本单列输出"],
            ["低价值剔除", "仅对无有效财年数据且持仓信号弱的低价值样本执行剔除"],
        ],
        columns=["口径项", "说明"],
    )
    caliber = pd.concat([screen_sheets["口径说明"], scope_note], ignore_index=True)

    with pd.ExcelWriter(OUTPUT_SCREEN, engine="openpyxl") as writer:
        caliber.to_excel(writer, sheet_name="口径说明", index=False)
        screen_sheets["历史热度原榜"][screen_sheets["历史热度原榜"]["代码"].isin(comparable_tickers)].to_excel(writer, sheet_name="历史热度原榜", index=False)
        screen_sheets["估值总表"][screen_sheets["估值总表"]["代码"].isin(comparable_tickers)].to_excel(writer, sheet_name="估值总表", index=False)
        screen_sheets["深研候选"][screen_sheets["深研候选"]["代码"].isin(comparable_tickers)].to_excel(writer, sheet_name="深研候选", index=False)
        decisions.to_excel(writer, sheet_name="缺数样本判定", index=False)
        missing_keep.to_excel(writer, sheet_name="保留缺数案例", index=False)
        limited.to_excel(writer, sheet_name="有限财年覆盖样本", index=False)
        dropped.to_excel(writer, sheet_name="剔除名单", index=False)
        summary.to_excel(writer, sheet_name="重核验摘要", index=False)


def write_pruned_full_workbook(coverage: pd.DataFrame, holdings: pd.DataFrame, annual: pd.DataFrame, decisions: pd.DataFrame) -> None:
    comparable_tickers = set(decisions[decisions["是否满足主池完整度"]]["代码"])
    missing_keep = decisions[~decisions["是否有有效财年数据"] & decisions["判定结果"].isin(["keep_case", "manual_review"])].copy()
    dropped = decisions[decisions["判定结果"].eq("drop")].copy()
    limited = decisions[decisions["是否有有效财年数据"] & ~decisions["是否满足主池完整度"]].copy()
    summary = build_summary(decisions)

    annual = annual.copy()
    annual["核心字段完整"] = annual[CORE_FIELDS].notna().all(axis=1) & annual["fiscal_year"].notna()

    pruned_coverage = decisions.copy()
    pruned_holdings = holdings[holdings["ticker"].isin(comparable_tickers)].copy()
    pruned_annual = annual[annual["ticker"].isin(comparable_tickers) & annual["核心字段完整"]].copy()

    validation_rows = [
        ("主池coverage ticker数", int(pruned_coverage[pruned_coverage["是否满足主池完整度"]]["代码"].nunique())),
        ("主池持仓历史 ticker数", int(pruned_holdings["ticker"].nunique())),
        ("主池年度经营质量 ticker数", int(pruned_annual["ticker"].nunique())),
        ("主池年度经营质量缺核心字段行数", int((~pruned_annual["核心字段完整"]).sum())),
    ]
    validation = pd.DataFrame(validation_rows, columns=["核验项", "值"])

    with pd.ExcelWriter(OUTPUT_FULL, engine="openpyxl") as writer:
        pruned_coverage.to_excel(writer, sheet_name="可比池覆盖说明", index=False)
        pruned_holdings.to_excel(writer, sheet_name="实体级持仓历史_可比池", index=False)
        pruned_annual.to_excel(writer, sheet_name="年度经营质量_可比池", index=False)
        missing_keep.to_excel(writer, sheet_name="保留缺数案例", index=False)
        limited.to_excel(writer, sheet_name="有限财年覆盖样本", index=False)
        dropped.to_excel(writer, sheet_name="剔除名单", index=False)
        summary.to_excel(writer, sheet_name="重核验摘要", index=False)
        validation.to_excel(writer, sheet_name="数据一致性核验", index=False)


def main() -> None:
    screen_sheets, coverage, holdings, annual = load_inputs()
    decisions = build_decision_table(screen_sheets, coverage, holdings, annual)
    write_pruned_screen_workbook(screen_sheets, decisions)
    write_pruned_full_workbook(coverage, holdings, annual, decisions)
    print(f"saved: {OUTPUT_SCREEN}")
    print(f"saved: {OUTPUT_FULL}")


if __name__ == "__main__":
    main()
