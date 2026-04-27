import json
import ast
from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent.parent
WORKBOOK = ROOT / "机构持仓研究" / "巴芒_喜马拉雅_高瓴_长期持有审美分类总表_2026-04-17.xlsx"
FULL_DATASET = ROOT / "机构持仓研究" / "长期持有全池数据集_2026-04-17_可比清理版.xlsx"
CASE_SCRIPT = ROOT / "tmp" / "spreadsheets" / "seed_long_hold_case_intake.py"
OUTPUT_JSON = Path(__file__).resolve().parent / "data.json"
REQUIRED_FIELDS = [
    "代码",
    "中文公司名",
    "英文公司名",
    "市场",
    "当前持有机构",
    "当前持有状态",
    "持有持续性分数",
    "持有持续性分位",
    "经营持续性分数",
    "经营持续性分位",
    "分类结果",
    "观察原因",
]

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


def split_tags(value) -> list[str]:
    if pd.isna(value) or value is None:
        return []
    return [tag.strip() for tag in str(value).split("|") if tag and tag.strip()]


def load_manual_tickers() -> set[str]:
    if not CASE_SCRIPT.exists():
        return set()
    module = ast.parse(CASE_SCRIPT.read_text(encoding="utf-8"))
    for node in module.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "CASE_DATA":
                    payload = ast.literal_eval(node.value)
                    return {str(key) for key in payload.keys()}
    return set()


def load_judgement_maps() -> tuple[dict[str, dict], dict[str, dict], list[dict], set[str]]:
    if not FULL_DATASET.exists():
        return {}, {}, [], set()
    research = pd.read_excel(FULL_DATASET, sheet_name="research_judgement")
    tags = pd.read_excel(FULL_DATASET, sheet_name="tag_dictionary")
    manual_tickers = load_manual_tickers()

    tag_options = []
    tag_lookup = {}
    for record in tags.to_dict(orient="records"):
        item = {
            "name": normalize_value(record.get("tag_name")),
            "group": normalize_value(record.get("tag_group")),
            "definition": normalize_value(record.get("definition")),
            "status": normalize_value(record.get("status")),
        }
        if item["name"]:
            tag_options.append(item)
            tag_lookup[item["name"]] = item

    judgement_by_company_id: dict[str, dict] = {}
    judgement_by_ticker: dict[str, dict] = {}
    for record in research.to_dict(orient="records"):
        ticker = normalize_value(record.get("ticker"))
        company_id = normalize_value(record.get("company_id"))
        has_judgement = any(
            normalize_value(record.get(field))
            for field in ["entry_summary", "hold_summary", "exit_summary", "degradation_summary", "evidence_refs"]
        )
        case_source = "manual" if ticker in manual_tickers else ("auto" if has_judgement else "empty")
        review_status = {"manual": "人工已审", "auto": "自动草稿", "empty": "暂无判断"}[case_source]
        confidence_values = [
            normalize_value(record.get(field))
            for field in ["entry_confidence", "hold_confidence", "exit_confidence", "degradation_confidence"]
            if normalize_value(record.get(field)) is not None
        ]
        judgement = {
            "caseSource": case_source,
            "reviewStatus": review_status,
            "managerScope": normalize_value(record.get("manager_scope")),
            "version": normalize_value(record.get("judgement_version")),
            "caseType": normalize_value(record.get("case_type")),
            "entryTags": split_tags(record.get("entry_tags")),
            "entrySummary": normalize_value(record.get("entry_summary")),
            "entryConfidence": normalize_value(record.get("entry_confidence")),
            "holdTags": split_tags(record.get("hold_tags")),
            "holdSummary": normalize_value(record.get("hold_summary")),
            "holdConfidence": normalize_value(record.get("hold_confidence")),
            "exitTags": split_tags(record.get("exit_tags")),
            "exitSummary": normalize_value(record.get("exit_summary")),
            "exitConfidence": normalize_value(record.get("exit_confidence")),
            "degradationTags": split_tags(record.get("degradation_tags")),
            "degradationSummary": normalize_value(record.get("degradation_summary")),
            "degradationConfidence": normalize_value(record.get("degradation_confidence")),
            "degradationNature": normalize_value(record.get("degradation_nature")),
            "exitHindsight": normalize_value(record.get("exit_hindsight")),
            "evidenceRefs": normalize_value(record.get("evidence_refs")),
            "lastReviewedAt": normalize_value(record.get("last_reviewed_at")),
            "hasJudgement": has_judgement,
            "confidenceMin": min(confidence_values) if confidence_values else None,
            "confidenceMax": max(confidence_values) if confidence_values else None,
            "allTags": sorted(
                {
                    *split_tags(record.get("entry_tags")),
                    *split_tags(record.get("hold_tags")),
                    *split_tags(record.get("exit_tags")),
                    *split_tags(record.get("degradation_tags")),
                }
            ),
        }
        if company_id:
            judgement_by_company_id[company_id] = judgement
        if ticker:
            judgement_by_ticker[str(ticker)] = judgement
    return judgement_by_company_id, judgement_by_ticker, tag_options, manual_tickers

def load_panel_data() -> dict:
    df = pd.read_excel(WORKBOOK, sheet_name="分类总表")
    judgement_by_company_id, judgement_by_ticker, tag_options, _manual_tickers = load_judgement_maps()
    missing = [field for field in REQUIRED_FIELDS if field not in df.columns]
    if missing:
        raise ValueError(f"分类总表缺少四象限面板必需字段: {', '.join(missing)}")
    records = []
    for record in df.to_dict(orient="records"):
        current_holder = normalize_value(record.get("当前持有机构"))
        current_status = normalize_value(record.get("当前持有状态"))
        market = normalize_value(record.get("市场"))
        ticker = normalize_value(record.get("代码"))
        company_id = f"{market}|{ticker}" if market and ticker else None
        judgement = judgement_by_company_id.get(company_id) or judgement_by_ticker.get(str(ticker))
        item = {
            "companyId": company_id,
            "ticker": ticker,
            "name": normalize_value(record.get("中文公司名")),
            "englishName": normalize_value(record.get("英文公司名")),
            "market": market,
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
            "judgement": judgement or {
                "caseSource": "empty",
                "reviewStatus": "暂无判断",
                "managerScope": None,
                "version": None,
                "caseType": normalize_value(record.get("分类结果")),
                "entryTags": [],
                "entrySummary": None,
                "entryConfidence": None,
                "holdTags": [],
                "holdSummary": None,
                "holdConfidence": None,
                "exitTags": [],
                "exitSummary": None,
                "exitConfidence": None,
                "degradationTags": [],
                "degradationSummary": None,
                "degradationConfidence": None,
                "degradationNature": None,
                "exitHindsight": None,
                "evidenceRefs": None,
                "lastReviewedAt": None,
                "hasJudgement": False,
                "confidenceMin": None,
                "confidenceMax": None,
                "allTags": [],
            },
        }
        item["isObservation"] = item["category"] == "观察区"
        item["isCurrent"] = bool(current_holder) and str(current_holder).strip() != ""
        records.append(item)

    categories = [x for x in df["分类结果"].dropna().astype(str).unique().tolist()]
    markets = [x for x in df["市场"].dropna().astype(str).unique().tolist()]
    judgement_statuses = ["人工已审", "自动草稿", "暂无判断"]
    return {
        "generatedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "workbookPath": "机构持仓研究/巴芒_喜马拉雅_高瓴_长期持有审美分类总表_2026-04-17.xlsx",
        "judgementWorkbookPath": "机构持仓研究/长期持有全池数据集_2026-04-17_可比清理版.xlsx",
        "records": records,
        "categories": categories,
        "markets": markets,
        "judgementStatuses": judgement_statuses,
        "tagOptions": tag_options,
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
