from __future__ import annotations

from pathlib import Path

import pandas as pd

import build_long_hold_core_dataset as core


ROOT = core.ROOT
WORKBOOK_PATH = core.WORKBOOK_PATH
OUTPUT_XLSX = ROOT / "机构持仓研究" / "长期持有全池数据集_2026-04-17.xlsx"


def load_full_pool_reference() -> pd.DataFrame:
    valuation = pd.read_excel(WORKBOOK_PATH, sheet_name="估值总表")
    cols = [
        "代码",
        "中文公司名",
        "英文公司名",
        "市场",
        "当前持有机构",
        "覆盖机构数",
        "出现季度数",
        "最近出现",
        "深研候选",
        "候选理由",
    ]
    ref = valuation[cols].copy()
    ref = ref.rename(columns={"代码": "ticker"})
    ref = ref.dropna(subset=["ticker"]).drop_duplicates(subset=["ticker"], keep="first").reset_index(drop=True)
    ref["sample_reason"] = ref.apply(
        lambda r: "当前深研候选"
        if str(r.get("深研候选", "")).strip() in {"是", "True", "true", "1"}
        else (r.get("候选理由") if pd.notna(r.get("候选理由")) else "全池研究样本"),
        axis=1,
    )
    return ref


def write_workbook(ref: pd.DataFrame, holdings: pd.DataFrame, annual: pd.DataFrame) -> None:
    coverage = (
        ref[["ticker", "中文公司名", "英文公司名", "市场", "当前持有机构", "覆盖机构数", "出现季度数", "最近出现", "深研候选", "候选理由"]]
        .copy()
    )
    hold_cov = holdings.groupby("ticker", as_index=False).agg(
        持仓历史行数=("ticker", "size"),
        持仓覆盖实体数=("manager_entity", "nunique"),
        最新持仓报告期=("report_date", "max"),
    )
    annual_tmp = annual.copy()
    annual_tmp["有效财年标记"] = annual_tmp["fiscal_year"].notna().astype(int)
    annual_cov = annual_tmp.groupby("ticker", as_index=False).agg(
        年度记录行数=("ticker", "size"),
        有效财年行数=("有效财年标记", "sum"),
        首个财年=("fiscal_year", "min"),
        最新财年=("fiscal_year", "max"),
        年度source_status=("source_status", lambda s: " | ".join(sorted(set(str(x) for x in s if pd.notna(x)))[:6])),
    )
    annual_cov["是否有有效财年数据"] = annual_cov["有效财年行数"] > 0
    coverage = coverage.merge(hold_cov, on="ticker", how="left").merge(annual_cov, on="ticker", how="left")

    with pd.ExcelWriter(OUTPUT_XLSX, engine="openpyxl") as writer:
        coverage.to_excel(writer, sheet_name="全池覆盖说明", index=False)
        holdings.to_excel(writer, sheet_name="实体级持仓历史", index=False)
        annual.to_excel(writer, sheet_name="年度经营质量", index=False)


def main() -> None:
    ref = load_full_pool_reference()
    holdings = core.build_core_holdings_history(ref)
    annual = core.build_annual_operating_quality(ref)
    write_workbook(ref, holdings, annual)
    print(f"saved: {OUTPUT_XLSX}")


if __name__ == "__main__":
    main()
