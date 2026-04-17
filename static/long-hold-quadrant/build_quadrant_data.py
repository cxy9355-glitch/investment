import json
import math
from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent.parent
WORKBOOK = ROOT / "机构持仓研究" / "巴芒_喜马拉雅_高瓴_长期持有审美分类总表_2026-04-17.xlsx"
OUTPUT_JSON = Path(__file__).resolve().parent / "data.json"

def normalize_value(value):
    if pd.isna(value):
        return None
    if isinstance(value, (pd.Timestamp, datetime)):
        return value.strftime("%Y-%m-%d")
    if hasattr(value, "item"):
        try:
            value = value.item()
        except Exception:
            pass
    return value

def load_panel_data() -> dict:
    df = pd.read_excel(WORKBOOK, sheet_name="分类总表")
    records = []
    for record in df.to_dict(orient="records"):
        current_holder = normalize_value(record.get("当前持有机构"))
        current_status = normalize_value(record.get("当前持有状态"))
        item = {
            "ticker": normalize_value(record.get("代码")),
            "name": normalize_value(record.get("中文公司名")),
            "englishName": normalize_value(record.get("英文公司名")),
            "market": normalize_value(record.get("市场")),
            "category": normalize_value(record.get("分类结果")),
            "observationReason": normalize_value(record.get("观察原因")),
            "currentHolder": current_holder,
            "currentStatus": current_status,
            "holdingScore": normalize_value(record.get("持有持续性分数")),
            "holdingPercentile": normalize_value(record.get("持有持续性分位")),
            "operatingScore": normalize_value(record.get("经营持续性分数")),
            "operatingPercentile": normalize_value(record.get("经营持续性分位")),
            "coverageInstitutions": normalize_value(record.get("覆盖机构数")),
            "quartersHeld": normalize_value(record.get("出现季度数")),
            "yearsHeld": normalize_value(record.get("覆盖年份数")),
            "currentHolderCount": normalize_value(record.get("当前持有机构数")),
            "avgWeight": normalize_value(record.get("平均持仓权重")),
            "peakWeight": normalize_value(record.get("峰值持仓权重")),
            "validYears": normalize_value(record.get("有效财年行数")),
            "completeYears": normalize_value(record.get("核心完整财年行数")),
            "latestReport": normalize_value(record.get("最新财报期")),
            "roe5y": normalize_value(record.get("5年平均ROE")),
            "roa5y": normalize_value(record.get("5年平均ROA")),
            "grossMargin5y": normalize_value(record.get("5年平均毛利率")),
            "netMargin5y": normalize_value(record.get("5年平均净利率")),
            "fcfMargin5y": normalize_value(record.get("5年平均FCF利润率")),
            "debtToEquity5y": normalize_value(record.get("5年平均Debt/Equity")),
            "meetsComparablePool": bool(record.get("是否满足主池完整度")) if record.get("是否满足主池完整度") is not None else None,
        }
        item["isObservation"] = item["category"] == "观察区"
        item["isCurrent"] = bool(current_holder) and str(current_holder).strip() != ""
        records.append(item)

    categories = [x for x in df["分类结果"].dropna().astype(str).unique().tolist()]
    markets = [x for x in df["市场"].dropna().astype(str).unique().tolist()]
    return {
        "generatedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "workbookPath": "机构持仓研究/巴芒_喜马拉雅_高瓴_长期持有审美分类总表_2026-04-17.xlsx",
        "records": records,
        "categories": categories,
        "markets": markets,
    }

def main():
    if not WORKBOOK.exists():
        print(f"Warning: Workbook not found: {WORKBOOK}")
        return

    data = load_panel_data()
    OUTPUT_JSON.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    print(f"Successfully wrote data to {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
