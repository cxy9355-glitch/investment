from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd


ROOT = Path(r"G:\Codex\个人\investment")
WORKBOOK = ROOT / "机构持仓研究" / "长期持有全池数据集_2026-04-17_可比清理版.xlsx"
TODAY = date(2026, 4, 25).isoformat()

ENTITY_SHORT = {
    "Berkshire Hathaway Inc": "BRK",
    "Himalaya Capital Management LLC": "Himalaya",
    "HHLR Advisors, Ltd.": "HHLR",
    "Daily Journal Corp": "DJCO",
}

TAG_DEFINITIONS = [
    ("平台网络效应", "entry", "平台越大越强，新增用户或商户会强化既有竞争优势。"),
    ("品牌与定价权", "entry", "品牌心智和议价能力强，能够较稳定地把成本压力转嫁给客户。"),
    ("高资本回报", "entry", "买入逻辑建立在长期高ROIC/ROE或强资本效率之上。"),
    ("轻资产模式", "entry", "资本开支较轻，增长更多依赖网络、软件或标准化复制。"),
    ("行业寡头", "entry", "所处行业集中度高，头部公司份额与议价能力明显。"),
    ("高增长渗透", "entry", "买入逻辑建立在行业渗透率提升和收入高增长预期上。"),
    ("资源品杠杆", "entry", "买入逻辑高度依赖商品价格、储量质量或行业供给约束。"),
    ("创新药叙事", "entry", "买入逻辑建立在创新药管线、单品放量或平台型研发能力上。"),
    ("实验室工具平台", "entry", "买入逻辑建立在科研/诊断工具平台的标准化与整合能力上。"),
    ("算力基础设施", "entry", "买入逻辑建立在AI/算力基础设施的核心供给地位上。"),
    ("中国消费连锁", "entry", "买入逻辑建立在中国消费连锁经营、门店复制和品牌渗透上。"),
    ("现金流稳定", "hold", "持续持有依赖稳健现金流和较强可预见性。"),
    ("用户粘性强", "hold", "用户留存、生态锁定或使用习惯让需求具有较强惯性。"),
    ("回购分红友好", "hold", "持续持有受到回购、分红或股东回报纪律支撑。"),
    ("高转换成本", "hold", "客户迁移成本高，使得收入留存和议价能力更稳。"),
    ("核心仓位", "hold", "被机构当作重要持仓而非边缘试仓。"),
    ("长期增长空间", "hold", "即使短期波动，机构仍相信中长期空间足够大。"),
    ("资产负债表修复", "hold", "持有逻辑部分依赖去杠杆、债务改善或资本结构优化。"),
    ("组合集中度让位", "exit", "没有被长期持有，更多是组合集中度或仓位取舍结果。"),
    ("非核心仓位", "exit", "曾持有但仓位轻、时间短，不构成长期核心配置。"),
    ("能力圈边缘", "exit", "未被长期持有可能与机构能力圈、偏好范围或研究深度有关。"),
    ("估值波动承受度", "exit", "未被长期持有与估值抬升或波动容忍度不足有关。"),
    ("周期性波动", "degradation", "经营持续性受宏观或商品周期影响明显。"),
    ("内容成本压力", "degradation", "内容或获客成本高企，持续压缩盈利质量。"),
    ("竞争加剧", "degradation", "行业竞争恶化，使利润率和份额承压。"),
    ("盈利兑现不足", "degradation", "收入故事存在，但利润、现金流或回报没有同步兑现。"),
    ("研发投入吞噬利润", "degradation", "研发和商业化投入过大，长期压制净利与自由现金流。"),
    ("单产品依赖", "degradation", "经营质量高度依赖少数产品、管线或单一商业化路径。"),
]

CASE_DATA = {
    "AAPL": {
        "entry_tags": "品牌与定价权|高资本回报",
        "entry_summary": "苹果被长期买入的核心不是单一硬件销量，而是品牌定价权叠加生态闭环带来的高资本回报。对长期资金而言，它兼具消费品护城河和平台型现金流特征。",
        "entry_confidence": 0.87,
        "hold_tags": "现金流稳定|用户粘性强|回购分红友好|核心仓位",
        "hold_summary": "持续持有依赖的是稳健自由现金流、用户粘性和持续回购。即使增速放缓，生态锁定与资本回收能力仍足以支撑核心仓位。",
        "hold_confidence": 0.89,
        "exit_tags": "",
        "exit_summary": "",
        "exit_confidence": None,
        "degradation_tags": "",
        "degradation_summary": "",
        "degradation_confidence": None,
        "degradation_nature": "",
        "exit_hindsight": "不适用",
    },
    "GOOG": {
        "entry_tags": "平台网络效应|高资本回报|长期增长空间",
        "entry_summary": "谷歌的买入逻辑来自搜索与广告平台的网络效应，以及极强的现金创造能力。云和AI又给了机构第二成长曲线的想象空间。",
        "entry_confidence": 0.82,
        "hold_tags": "现金流稳定|平台网络效应|核心仓位",
        "hold_summary": "长期持有主要依靠搜索入口的稳定性、高利润广告业务和持续扩展的云平台。它更像能自我强化的数字基础设施资产。",
        "hold_confidence": 0.84,
        "exit_tags": "",
        "exit_summary": "",
        "exit_confidence": None,
        "degradation_tags": "",
        "degradation_summary": "",
        "degradation_confidence": None,
        "degradation_nature": "",
        "exit_hindsight": "不适用",
    },
    "V": {
        "entry_tags": "平台网络效应|轻资产模式|高资本回报",
        "entry_summary": "Visa 的买入逻辑很清晰：支付清算网络具备双边网络效应，商业模式轻资产且资本回报极高。它天然适合长期复利型资金。",
        "entry_confidence": 0.9,
        "hold_tags": "现金流稳定|高转换成本|回购分红友好",
        "hold_summary": "持续持有依赖支付网络的高转换成本、全球交易量增长和优秀股东回报纪律。业务稳定性与利润结构都非常适合长期拿住。",
        "hold_confidence": 0.9,
        "exit_tags": "",
        "exit_summary": "",
        "exit_confidence": None,
        "degradation_tags": "",
        "degradation_summary": "",
        "degradation_confidence": None,
        "degradation_nature": "",
        "exit_hindsight": "不适用",
    },
    "MCO": {
        "entry_tags": "行业寡头|高转换成本|高资本回报",
        "entry_summary": "穆迪被买入的核心在于评级业务的行业寡头格局，以及数据与分析业务的高附加值。它兼具高转换成本和高资本回报。",
        "entry_confidence": 0.86,
        "hold_tags": "现金流稳定|行业寡头|长期增长空间",
        "hold_summary": "长期持有依赖评级业务的制度地位和分析业务的持续扩展。即使信用周期波动，整体商业模式仍能维持很强的现金流质量。",
        "hold_confidence": 0.83,
        "exit_tags": "",
        "exit_summary": "",
        "exit_confidence": None,
        "degradation_tags": "",
        "degradation_summary": "",
        "degradation_confidence": None,
        "degradation_nature": "",
        "exit_hindsight": "不适用",
    },
    "OXY": {
        "entry_tags": "资源品杠杆|资产负债表修复|高增长渗透",
        "entry_summary": "西方石油更像宏观与资产重估下注：油气资源质量、行业供给约束和去杠杆预期共同构成买入理由。它不是典型稳定复利股，而是资源周期中的高赔率选择。",
        "entry_confidence": 0.75,
        "hold_tags": "现金流稳定|资产负债表修复|核心仓位",
        "hold_summary": "之所以还能被继续持有，是因为高油价阶段的现金流、回购空间和债务改善仍然有吸引力。机构显然把它当成阶段性核心暴露，而不是纯交易仓位。",
        "hold_confidence": 0.73,
        "exit_tags": "",
        "exit_summary": "",
        "exit_confidence": None,
        "degradation_tags": "周期性波动|盈利兑现不足",
        "degradation_summary": "OXY 在经营持续性上掉队，关键不是公司失去经营能力，而是资源品公司的盈利质量天然受油价周期牵引。高峰期之外，回报和稳定性都明显弱于长期赢家口径。",
        "degradation_confidence": 0.8,
        "degradation_nature": "强周期型",
        "exit_hindsight": "仍在持有，暂不评价退出对错",
    },
    "SE": {
        "entry_tags": "高增长渗透|平台网络效应|长期增长空间",
        "entry_summary": "Sea 的买入逻辑来自东南亚互联网平台的高增长渗透叙事：电商、游戏和金融业务一度被视作区域级平台组合。它符合成长型机构偏好的长期空间故事。",
        "entry_confidence": 0.73,
        "hold_tags": "长期增长空间|平台网络效应",
        "hold_summary": "被继续持有的理由主要是区域龙头地位和用户规模优势，市场曾相信其能把增长转化成更稳定的现金流与盈利结构。",
        "hold_confidence": 0.68,
        "exit_tags": "组合集中度让位|估值波动承受度",
        "exit_summary": "在盈利兑现弱于预期、波动放大的阶段，Sea 更像被从组合中让位出去，而不是天然适合长期核心持有的资产。",
        "exit_confidence": 0.58,
        "degradation_tags": "竞争加剧|盈利兑现不足",
        "degradation_summary": "Sea 的退化主要体现在高增长叙事没有同步转成稳定盈利，电商竞争与游戏业务回落共同压缩了经营持续性。",
        "degradation_confidence": 0.82,
        "degradation_nature": "成长兑现不足",
        "exit_hindsight": "需后续结合卖出后经营改善情况再复盘",
    },
    "IQ": {
        "entry_tags": "高增长渗透|平台网络效应",
        "entry_summary": "爱奇艺最初的买入逻辑是中国长视频平台的流量入口和会员增长空间。它本质上是内容平台叙事，而非现金流型复利资产。",
        "entry_confidence": 0.68,
        "hold_tags": "长期增长空间",
        "hold_summary": "持续持有阶段更多是在等待订阅增长、广告恢复和内容生态改善兑现，而不是依靠已经成型的高质量财务结构。",
        "hold_confidence": 0.61,
        "exit_tags": "组合集中度让位|盈利兑现不足",
        "exit_summary": "当内容平台逻辑迟迟不能转成更稳健利润时，这类标的更容易被成长型组合剔除，持有纪律也更难长期维持。",
        "exit_confidence": 0.62,
        "degradation_tags": "内容成本压力|竞争加剧|盈利兑现不足",
        "degradation_summary": "爱奇艺的经营持续性走弱主要来自内容成本长期偏高、竞争格局不友好，以及利润和现金流改善不够稳。它更像叙事型平台，而不是成熟护城河资产。",
        "degradation_confidence": 0.84,
        "degradation_nature": "结构性承压",
        "exit_hindsight": "从经营质量角度看，退出并非明显误判",
    },
    "LEGN": {
        "entry_tags": "创新药叙事|高增长渗透",
        "entry_summary": "Legend Biotech 被买入的核心是创新药商业化与管线兑现预期，属于典型的生物科技成长叙事。机构押注的是产品放量和平台价值提升。",
        "entry_confidence": 0.71,
        "hold_tags": "长期增长空间",
        "hold_summary": "继续持有说明机构仍然相信核心产品和商业化路径具备长期空间，但这类逻辑更多依赖未来兑现，而非当前财务质量。",
        "hold_confidence": 0.67,
        "exit_tags": "",
        "exit_summary": "",
        "exit_confidence": None,
        "degradation_tags": "研发投入吞噬利润|单产品依赖|盈利兑现不足",
        "degradation_summary": "LEGN 的退化并不一定意味着产业逻辑失效，而是当前财务表现仍受研发投入和商业化节奏压制。对长期持有框架来说，这会显著拖累经营持续性评分。",
        "degradation_confidence": 0.83,
        "degradation_nature": "商业化兑现不足",
        "exit_hindsight": "仍在持有，暂不评价退出对错",
    },
    "TMO": {
        "entry_tags": "实验室工具平台|高转换成本|高资本回报",
        "entry_summary": "赛默飞世尔的买入理由非常标准：实验室工具平台具备高转换成本、强整合能力和长期高质量回报。它是典型的高质量经营资产。",
        "entry_confidence": 0.84,
        "hold_tags": "现金流稳定|高转换成本",
        "hold_summary": "如果从经营本身看，TMO 完全具备长期持有条件，需求韧性、平台整合和现金流都比较扎实。",
        "hold_confidence": 0.79,
        "exit_tags": "非核心仓位|组合集中度让位",
        "exit_summary": "TMO 没有被长期拿住，更像是研究覆盖和仓位优先级问题，而不是经营质量不行。它在机构组合里更像短期试仓或阶段性配置。",
        "exit_confidence": 0.63,
        "degradation_tags": "",
        "degradation_summary": "",
        "degradation_confidence": None,
        "degradation_nature": "",
        "exit_hindsight": "从经营质量看，未长期持有可能偏保守",
    },
    "REGN": {
        "entry_tags": "创新药叙事|高资本回报",
        "entry_summary": "再生元被买入的逻辑是高质量创新药资产：研发兑现能力强、利润率高、资本回报优秀。它属于经营端明显好于一般医药公司的标的。",
        "entry_confidence": 0.8,
        "hold_tags": "现金流稳定|长期增长空间",
        "hold_summary": "如果仅从经营质量看，REGN 具备长期持有条件，利润率、资产负债表和研发转化都很强。",
        "hold_confidence": 0.77,
        "exit_tags": "非核心仓位|能力圈边缘",
        "exit_summary": "再生元没有被长期拿住，较大概率与机构医药覆盖深度和组合优先级有关，而不是公司本身失去质量。",
        "exit_confidence": 0.57,
        "degradation_tags": "",
        "degradation_summary": "",
        "degradation_confidence": None,
        "degradation_nature": "",
        "exit_hindsight": "从后验经营表现看，未长期持有值得后续重点复盘",
    },
    "NVDA": {
        "entry_tags": "算力基础设施|高增长渗透",
        "entry_summary": "英伟达的买入逻辑围绕算力基础设施和AI/加速计算需求扩张展开，属于高景气、高弹性、高波动并存的成长资产。",
        "entry_confidence": 0.82,
        "hold_tags": "长期增长空间",
        "hold_summary": "从经营端看，NVDA 的技术领先和需求爆发完全足以支撑长期持有，但这种标的对波动承受和产业理解要求也更高。",
        "hold_confidence": 0.74,
        "exit_tags": "估值波动承受度|非核心仓位",
        "exit_summary": "没有被长期拿住，更像是高波动成长股在机构组合中的常见命运：仓位轻、持有短、难以跨周期抱住。",
        "exit_confidence": 0.66,
        "degradation_tags": "",
        "degradation_summary": "",
        "degradation_confidence": None,
        "degradation_nature": "",
        "exit_hindsight": "从后验结果看，卖出纪律可能低估了长期复利空间",
    },
    "YUMC": {
        "entry_tags": "中国消费连锁|现金流稳定",
        "entry_summary": "百胜中国的买入逻辑是中国消费连锁龙头，具备标准化复制能力、品牌资产和相对稳健的现金流。它不是高弹性故事，更像稳健消费运营资产。",
        "entry_confidence": 0.74,
        "hold_tags": "现金流稳定|长期增长空间",
        "hold_summary": "如果从经营角度看，YUMC 具备较强的长期经营韧性，门店复制、供应链和品牌心智都支持持续经营质量。",
        "hold_confidence": 0.71,
        "exit_tags": "非核心仓位|组合集中度让位",
        "exit_summary": "没有被长期拿住，大概率不是因为经营崩坏，而是因为它在机构组合里不够稀缺，容易让位给更高赔率或更高确信度的标的。",
        "exit_confidence": 0.59,
        "degradation_tags": "",
        "degradation_summary": "",
        "degradation_confidence": None,
        "degradation_nature": "",
        "exit_hindsight": "是否错过稳定复利，需要后续和其他消费样本再比",
    },
}


def quarter_label(value: object) -> str:
    ts = pd.to_datetime(value)
    quarter = (ts.month - 1) // 3 + 1
    return f"{ts.year}Q{quarter}"


def build_evidence_refs(ticker: str, holdings: pd.DataFrame, annual: pd.DataFrame) -> str:
    hs = holdings[holdings["ticker"] == ticker].copy()
    refs: list[str] = []
    if not hs.empty:
        spans = (
            hs.groupby("manager_entity")
            .agg(
                first_report=("report_date", "min"),
                last_report=("report_date", "max"),
                current=("is_current", "max"),
                accession_number=("accession_number", "last"),
            )
            .reset_index()
            .sort_values(["current", "last_report"], ascending=[False, False])
        )
        for row in spans.head(2).itertuples(index=False):
            entity = ENTITY_SHORT.get(row.manager_entity, row.manager_entity)
            refs.append(
                f"13F({entity}, {quarter_label(row.first_report)}-{quarter_label(row.last_report)}, {row.accession_number})"
            )
    aa = annual[annual["ticker"] == ticker].copy()
    if not aa.empty:
        latest = aa.sort_values("fiscal_year").iloc[-1]
        refs.append(f"Annual(FY{int(latest['fiscal_year'])}, {latest['source_forms']})")
    return "; ".join(refs)


def update_research_judgement(workbook: Path) -> tuple[int, int]:
    research = pd.read_excel(workbook, sheet_name="research_judgement")
    holdings = pd.read_excel(workbook, sheet_name="holding_timeline")
    annual = pd.read_excel(workbook, sheet_name="operating_timeline")
    target_columns = {
        "entry_tags",
        "entry_summary",
        "entry_confidence",
        "hold_tags",
        "hold_summary",
        "hold_confidence",
        "exit_tags",
        "exit_summary",
        "exit_confidence",
        "degradation_tags",
        "degradation_summary",
        "degradation_confidence",
        "degradation_nature",
        "exit_hindsight",
        "evidence_refs",
        "last_reviewed_at",
    }
    for column in target_columns:
        if column in research.columns:
            research[column] = research[column].astype("object")

    updated = 0
    used_tags: set[str] = set()
    for ticker, payload in CASE_DATA.items():
        mask = research["ticker"] == ticker
        if not mask.any():
            continue
        evidence_refs = build_evidence_refs(ticker, holdings, annual)
        for column, value in payload.items():
            research.loc[mask, column] = value
        research.loc[mask, "evidence_refs"] = evidence_refs
        research.loc[mask, "last_reviewed_at"] = TODAY
        updated += int(mask.sum())
        for field in ["entry_tags", "hold_tags", "exit_tags", "degradation_tags"]:
            tags = payload.get(field, "")
            if tags:
                used_tags.update(tag for tag in tags.split("|") if tag)

    tags_df = pd.read_excel(workbook, sheet_name="tag_dictionary")
    additions = [
        {
            "tag_name": tag_name,
            "tag_group": tag_group,
            "definition": definition,
            "status": "active",
            "notes": "首批案例入池使用",
        }
        for tag_name, tag_group, definition in TAG_DEFINITIONS
        if tag_name in used_tags
    ]
    merged_tags = pd.concat([tags_df, pd.DataFrame(additions)], ignore_index=True)
    if not merged_tags.empty:
        merged_tags = merged_tags.drop_duplicates(subset=["tag_name"], keep="last")
        merged_tags = merged_tags.sort_values(["tag_group", "tag_name"]).reset_index(drop=True)

    with pd.ExcelWriter(workbook, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
        research.to_excel(writer, sheet_name="research_judgement", index=False)
        merged_tags.to_excel(writer, sheet_name="tag_dictionary", index=False)
    return updated, len(merged_tags)


def main() -> None:
    updated, tag_count = update_research_judgement(WORKBOOK)
    print(f"updated research_judgement rows: {updated}")
    print(f"tag_dictionary rows: {tag_count}")


if __name__ == "__main__":
    main()
