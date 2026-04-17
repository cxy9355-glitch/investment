from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def resolve_paths() -> tuple[Path, Path]:
    base_dir = Path(__file__).resolve().parent
    workspace_root = base_dir.parents[2]
    repo_root = base_dir.parents[1]

    root_input = workspace_root / "tmp" / "fund_analysis"
    repo_input = repo_root / "tmp" / "fund_analysis"
    input_dir = root_input if root_input.exists() else repo_input
    output_dir = base_dir / "data"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "rankings").mkdir(exist_ok=True)
    (output_dir / "stocks").mkdir(exist_ok=True)
    (output_dir / "metadata").mkdir(exist_ok=True)
    return input_dir, output_dir


def load_metrics(input_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    valuation_parts = []
    for name in [
        "valuation_metrics_top180.csv",
        "valuation_metrics_181_300.csv",
        "valuation_metrics_pool_missing.csv",
    ]:
        path = input_dir / name
        if path.exists():
            part = pd.read_csv(path, dtype={"stock_code": str})
            part["stock_code"] = part["stock_code"].str.zfill(6)
            valuation_parts.append(part)
    valuation = pd.concat(valuation_parts, ignore_index=True).drop_duplicates(
        "stock_code", keep="last"
    )

    financial_parts = []
    for name in [
        "financial_metrics_top180.csv",
        "financial_metrics_181_300.csv",
        "financial_metrics_pool_missing.csv",
    ]:
        path = input_dir / name
        if path.exists():
            part = pd.read_csv(path, dtype={"stock_code": str, "SECURITY_CODE": str})
            if "stock_code" not in part.columns:
                part["stock_code"] = part["SECURITY_CODE"]
            part["stock_code"] = part["stock_code"].str.zfill(6)
            financial_parts.append(part)
    financial = pd.concat(financial_parts, ignore_index=True).drop_duplicates(
        "stock_code", keep="last"
    )
    return valuation, financial


def compute_rankings(all_hold: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, str]:
    latest_date = str(all_hold["date"].max())
    latest_rows = (
        all_hold[all_hold["date"] == latest_date]
        .copy()
        .rename(
            columns={
                "totalshares_ratio": "latest_totalshares_ratio",
                "pool_share": "latest_pool_share",
                "hold_fund_count": "latest_hold_fund_count",
                "hold_value": "latest_hold_value",
            }
        )
    )
    latest_rows = latest_rows[
        [
            "stock_code",
            "latest_totalshares_ratio",
            "latest_pool_share",
            "latest_hold_fund_count",
            "latest_hold_value",
        ]
    ]

    totalshares_rank = (
        all_hold.groupby(["stock_code", "stock_name"], as_index=False)
        .agg(
            appearances=("date", "nunique"),
            years=("date", lambda s: len({x[:4] for x in s})),
            first_date=("date", "min"),
            last_date=("date", "max"),
            cumulative_value=("totalshares_ratio", "sum"),
            average_value=("totalshares_ratio", "mean"),
            peak_value=("totalshares_ratio", "max"),
        )
        .merge(latest_rows, on="stock_code", how="left")
        .sort_values(["cumulative_value", "average_value"], ascending=[False, False])
        .reset_index(drop=True)
    )
    totalshares_rank["rank"] = totalshares_rank.index + 1

    pool_rank = (
        all_hold.groupby(["stock_code", "stock_name"], as_index=False)
        .agg(
            appearances=("date", "nunique"),
            years=("date", lambda s: len({x[:4] for x in s})),
            first_date=("date", "min"),
            last_date=("date", "max"),
            cumulative_value=("pool_share", "sum"),
            average_value=("pool_share", "mean"),
            peak_value=("pool_share", "max"),
        )
        .merge(latest_rows, on="stock_code", how="left")
        .sort_values(["cumulative_value", "average_value"], ascending=[False, False])
        .reset_index(drop=True)
    )
    pool_rank["rank"] = pool_rank.index + 1
    return totalshares_rank, pool_rank, latest_date


def apply_candidate_logic(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["valuation_score"] = df[["pe_ttm_percentile", "pb_percentile"]].mean(axis=1)
    df["is_st"] = df["stock_name"].astype(str).str.contains("ST", na=False)
    
    # Calculate ROE TTM from PB and PE_TTM, fallback to ROEJQ if missing
    df["ROE_TTM"] = (df["pb"] / df["pe_ttm"] * 100).fillna(df["ROEJQ"])
    
    # Calculate ROA TTM (ROE_TTM * Equity/Assets), fallback to ZZCJLL if missing
    df["ROA_TTM"] = (df["ROE_TTM"] * (1 - df["ZCFZL"].fillna(0) / 100)).fillna(df["ZZCJLL"])
    
    # Calculate ROIC Annualized
    months = pd.to_datetime(df["REPORT_DATE"]).dt.month
    df["annual_factor"] = 12.0 / months.where(months.isin([3, 6, 9, 12]), 12.0)
    df["ROIC_ANNUAL"] = df["ROIC"].fillna(0) * df["annual_factor"]
    
    df["candidate"] = (
        (~df["is_st"])
        & (df["appearances"] >= 20)
        & (df["latest_hold_fund_count"] >= 30)
        & (df["ROE_TTM"].fillna(0) >= 8)
        & (df["ROA_TTM"].fillna(0) >= 3)
    )
    return df


def build_reason(row: pd.Series, methodology_key: str) -> str:
    parts: list[str] = []
    if pd.notna(row.get("valuation_score")) and row["valuation_score"] <= 15:
        parts.append("估值处历史偏低区间")
    if methodology_key == "pool-share":
        if pd.notna(row.get("latest_pool_share")) and row["latest_pool_share"] >= 1:
            parts.append("当前在公募持仓池内占比高")
        if pd.notna(row.get("average_value")) and row["average_value"] >= 0.5:
            parts.append("长期机构配置集中度高")
    else:
        if pd.notna(row.get("latest_totalshares_ratio")) and row["latest_totalshares_ratio"] >= 5:
            parts.append("当前机构持股深度高")
        if pd.notna(row.get("average_value")) and row["average_value"] >= 10:
            parts.append("长期持股比例深")
    if pd.notna(row.get("ROE_TTM")) and row["ROE_TTM"] >= 15:
        parts.append("ROE(TTM)较高")
    elif pd.notna(row.get("ROE_TTM")) and row["ROE_TTM"] >= 10:
        parts.append("ROE(TTM)稳定")
    if pd.notna(row.get("ROA_TTM")) and row["ROA_TTM"] >= 8:
        parts.append("ROA(TTM)较好")
    return "；".join(parts)


def write_json(path: Path, payload: object) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def ensure_row(obj: pd.Series | pd.DataFrame) -> pd.Series:
    if isinstance(obj, pd.DataFrame):
        return obj.iloc[0]
    return obj


def main() -> None:
    input_dir, output_dir = resolve_paths()
    all_hold = pd.read_csv(input_dir / "fund_hold_all.csv", dtype={"stock_code": str})
    all_hold["stock_code"] = all_hold["stock_code"].str.zfill(6)
    quarter_sum = (
        all_hold.groupby("date", as_index=False)["hold_value"]
        .sum()
        .rename(columns={"hold_value": "quarter_total_hold_value"})
    )
    all_hold = all_hold.merge(quarter_sum, on="date", how="left")
    all_hold["pool_share"] = (
        all_hold["hold_value"] / all_hold["quarter_total_hold_value"] * 100
    )

    valuation, financial = load_metrics(input_dir)
    totalshares_rank, pool_rank, latest_date = compute_rankings(all_hold)

    financial_keep = [
        "stock_code",
        "REPORT_DATE",
        "SECUCODE",
        "ROEJQ",
        "ZZCJLL",
        "ROIC",
        "ZCFZL",
        "XSMLL",
        "XSJLL",
    ]
    totalshares_rank = apply_candidate_logic(
        totalshares_rank.merge(valuation, on="stock_code", how="left").merge(
            financial[financial_keep], on="stock_code", how="left"
        )
    )
    pool_rank = apply_candidate_logic(
        pool_rank.merge(valuation, on="stock_code", how="left").merge(
            financial[financial_keep], on="stock_code", how="left"
        )
    )

    universe = sorted(
        set(totalshares_rank.head(300)["stock_code"]).union(
            set(pool_rank.head(300)["stock_code"])
        )
    )

    methodologies = {
        "float-ratio": {
            "label": "占总股本比例",
            "description": "机构在这只股票里持有得有多深",
            "current_field": "latest_totalshares_ratio",
        },
        "pool-share": {
            "label": "池内占比",
            "description": "机构把整个公募持仓池的仓位集中给了谁",
            "current_field": "latest_pool_share",
        },
    }

    for key, meta in methodologies.items():
        source = totalshares_rank if key == "float-ratio" else pool_rank
        rows = source.head(300).copy()
        rows["current_value"] = rows[meta["current_field"]]
        rows["candidate_reason"] = rows.apply(lambda r: build_reason(r, key), axis=1)
        payload = {
            "methodology": {
                "key": key,
                "label": meta["label"],
                "description": meta["description"],
                "latestQuarter": latest_date,
                "universeCount": int(len(rows)),
            },
            "rows": [],
        }
        for _, row in rows.iterrows():
            payload["rows"].append(
                {
                    "rank": int(row["rank"]),
                    "code": row["stock_code"],
                    "name": row["stock_name"],
                    "appearances": int(row["appearances"]),
                    "years": int(row["years"]),
                    "currentValue": round(float(row["current_value"]), 6)
                    if pd.notna(row["current_value"])
                    else None,
                    "cumulativeValue": round(float(row["cumulative_value"]), 6),
                    "averageValue": round(float(row["average_value"]), 6),
                    "peakValue": round(float(row["peak_value"]), 6),
                    "latestFundCount": int(row["latest_hold_fund_count"])
                    if pd.notna(row["latest_hold_fund_count"])
                    else None,
                    "latestHoldValue": round(float(row["latest_hold_value"]), 2)
                    if pd.notna(row["latest_hold_value"])
                    else None,
                    "peTtm": round(float(row["pe_ttm"]), 2)
                    if pd.notna(row["pe_ttm"])
                    else None,
                    "pePercentile": round(float(row["pe_ttm_percentile"]), 4)
                    if pd.notna(row["pe_ttm_percentile"])
                    else None,
                    "pb": round(float(row["pb"]), 2) if pd.notna(row["pb"]) else None,
                    "pbPercentile": round(float(row["pb_percentile"]), 4)
                    if pd.notna(row["pb_percentile"])
                    else None,
                    "valuationScore": round(float(row["valuation_score"]), 4)
                    if pd.notna(row["valuation_score"])
                    else None,
                    "roe": round(float(row["ROE_TTM"]), 2) if pd.notna(row.get("ROE_TTM")) else None,
                    "roa": round(float(row["ROA_TTM"]), 2) if pd.notna(row.get("ROA_TTM")) else None,
                    "roic": round(float(row["ROIC_ANNUAL"]), 2) if pd.notna(row.get("ROIC_ANNUAL")) else None,
                    "grossMargin": round(float(row["XSMLL"]), 2)
                    if pd.notna(row["XSMLL"])
                    else None,
                    "netMargin": round(float(row["XSJLL"]), 2)
                    if pd.notna(row["XSJLL"])
                    else None,
                    "latestReportDate": row["REPORT_DATE"] if pd.notna(row["REPORT_DATE"]) else None,
                    "candidate": bool(row["candidate"]),
                    "candidateReason": row["candidate_reason"],
                }
            )
        write_json(output_dir / "rankings" / f"{key}.json", payload)

    detail_totalshares = totalshares_rank.set_index("stock_code")
    detail_pool = pool_rank.set_index("stock_code")
    time_series = {
        code: all_hold[all_hold["stock_code"] == code].sort_values("date").copy()
        for code in universe
    }
    for code in universe:
        base_row = ensure_row(
            detail_pool.loc[code] if code in detail_pool.index else detail_totalshares.loc[code]
        )
        ts = time_series[code]
        total_row = ensure_row(detail_totalshares.loc[code])
        pool_row = ensure_row(detail_pool.loc[code])
        detail_payload = {
            "identity": {
                "code": code,
                "name": str(base_row["stock_name"]),
                "secucode": str(base_row["SECUCODE"]) if pd.notna(base_row.get("SECUCODE")) else None,
            },
            "snapshot": {
                "peTtm": round(float(base_row["pe_ttm"]), 2) if pd.notna(base_row["pe_ttm"]) else None,
                "pePercentile": round(float(base_row["pe_ttm_percentile"]), 4)
                if pd.notna(base_row["pe_ttm_percentile"])
                else None,
                "pb": round(float(base_row["pb"]), 2) if pd.notna(base_row["pb"]) else None,
                "pbPercentile": round(float(base_row["pb_percentile"]), 4)
                if pd.notna(base_row["pb_percentile"])
                else None,
                "valuationScore": round(float(base_row["valuation_score"]), 4)
                if pd.notna(base_row["valuation_score"])
                else None,
                "roe": round(float(base_row["ROE_TTM"]), 2) if pd.notna(base_row.get("ROE_TTM")) else None,
                "roa": round(float(base_row["ROA_TTM"]), 2) if pd.notna(base_row.get("ROA_TTM")) else None,
                "roic": round(float(base_row["ROIC_ANNUAL"]), 2) if pd.notna(base_row.get("ROIC_ANNUAL")) else None,
                "grossMargin": round(float(base_row["XSMLL"]), 2)
                if pd.notna(base_row["XSMLL"])
                else None,
                "netMargin": round(float(base_row["XSJLL"]), 2)
                if pd.notna(base_row["XSJLL"])
                else None,
                "latestFundCount": int(base_row["latest_hold_fund_count"])
                if pd.notna(base_row["latest_hold_fund_count"])
                else None,
                "latestHoldValue": round(float(base_row["latest_hold_value"]), 2)
                if pd.notna(base_row["latest_hold_value"])
                else None,
                "latestReportDate": base_row["REPORT_DATE"]
                if pd.notna(base_row.get("REPORT_DATE"))
                else None,
            },
            "methodologies": {
                "float-ratio": {
                    "rank": int(total_row["rank"]),
                    "currentValue": round(float(total_row["latest_totalshares_ratio"]), 6),
                    "cumulativeValue": round(float(total_row["cumulative_value"]), 6),
                    "averageValue": round(float(total_row["average_value"]), 6),
                    "peakValue": round(float(total_row["peak_value"]), 6),
                    "candidateReason": build_reason(total_row, "float-ratio"),
                },
                "pool-share": {
                    "rank": int(pool_row["rank"]),
                    "currentValue": round(float(pool_row["latest_pool_share"]), 6),
                    "cumulativeValue": round(float(pool_row["cumulative_value"]), 6),
                    "averageValue": round(float(pool_row["average_value"]), 6),
                    "peakValue": round(float(pool_row["peak_value"]), 6),
                    "candidateReason": build_reason(pool_row, "pool-share"),
                },
            },
            "series": [
                {
                    "date": row["date"],
                    "holdValue": round(float(row["hold_value"]), 2),
                    "fundCount": int(row["hold_fund_count"]),
                    "totalsharesRatio": round(float(row["totalshares_ratio"]), 6),
                    "poolShare": round(float(row["pool_share"]), 6),
                }
                for _, row in ts.iterrows()
            ],
        }
        write_json(output_dir / "stocks" / f"{code}.json", detail_payload)

    methodology_payload = {
        "updatedAt": latest_date,
        "definitions": [
            {
                "key": "float-ratio",
                "label": "占总股本比例",
                "summary": "机构在这只股票里持有得有多深。",
                "detail": "某季度某股票的公募持股数占该股票总股本的比例，用来观察机构对单只股票的持股深度。",
            },
            {
                "key": "pool-share",
                "label": "池内占比",
                "summary": "机构把整个公募持仓池的仓位集中给了谁。",
                "detail": "某季度某股票的公募持仓市值占当季全部公募股票持仓总市值的比例，用来观察机构配置集中度。",
            },
        ],
        "candidateRule": "非ST；出现季度数>=20；最新持有基金家数>=30；ROE>=8%；ROA/总资产净利率>=3%；再结合估值历史分位观察候选优先级。",
        "limitations": [
            "当前公开免费聚合数据稳定覆盖的是 A 股公募持仓，不是完整 AH 双市场逐股聚合结果。",
            "估值历史分位来自百度股市通公开序列，财务指标来自东方财富 F10 主要指标。",
            "站点数据来自已验证的研究中间表，属于静态发布快照，不是实时行情服务。",
        ],
    }
    write_json(output_dir / "metadata" / "methodology.json", methodology_payload)

    summary_payload = {
        "updatedAt": latest_date,
        "featuredCodes": ["600519", "300750", "300308", "000858", "000651"],
        "methodologies": [
            {
                "key": "float-ratio",
                "label": "占总股本比例",
                "topCode": totalshares_rank.iloc[0]["stock_code"],
                "topName": totalshares_rank.iloc[0]["stock_name"],
                "topCurrentValue": round(float(totalshares_rank.iloc[0]["latest_totalshares_ratio"]), 6),
                "universeCount": 300,
            },
            {
                "key": "pool-share",
                "label": "池内占比",
                "topCode": pool_rank.iloc[0]["stock_code"],
                "topName": pool_rank.iloc[0]["stock_name"],
                "topCurrentValue": round(float(pool_rank.iloc[0]["latest_pool_share"]), 6),
                "universeCount": 300,
            },
        ],
    }
    write_json(output_dir / "dashboard-summary.json", summary_payload)


if __name__ == "__main__":
    main()
