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
    ("企业软件平台", "entry", "买入逻辑建立在企业软件安装基础、数据库或关键IT基础设施地位上。"),
    ("成熟产品现金牛", "entry", "买入逻辑建立在成熟产品组合的稳定现金流和利润释放能力上。"),
    ("内容与线上娱乐", "entry", "买入逻辑建立在内容、社区、游戏、媒体或线上娱乐消费场景上。"),
    ("金融基础设施", "entry", "买入逻辑建立在支付、清算、经纪、托管或金融市场基础设施地位上。"),
    ("工业基础设施", "entry", "买入逻辑建立在工业设备、基础设施、能源供给或关键工程体系上。"),
    ("半导体硬件", "entry", "买入逻辑建立在芯片、半导体制造、硬件平台或电子供应链地位上。"),
    ("消费品牌渠道", "entry", "买入逻辑建立在消费品牌、线下渠道、服务网络或零售运营能力上。"),
    ("能源转型叙事", "entry", "买入逻辑建立在新能源、电气化或能源结构变化带来的长期需求上。"),
    ("轻资产模式", "entry", "资本开支较轻，增长更多依赖网络、软件或标准化复制。"),
    ("行业寡头", "entry", "所处行业集中度高，头部公司份额与议价能力明显。"),
    ("高增长渗透", "entry", "买入逻辑建立在行业渗透率提升和收入高增长预期上。"),
    ("周期复苏", "entry", "买入逻辑建立在行业从低谷修复、景气回升与利润弹性释放上。"),
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
    "KO": {
        "entry_tags": "品牌与定价权|现金流稳定",
        "entry_summary": "可口可乐的买入逻辑非常经典：全球品牌资产、渠道体系和定价权共同支撑长期稳定现金流。它更像消费行业里最接近债券替代品的复利资产。",
        "entry_confidence": 0.89,
        "hold_tags": "现金流稳定|品牌与定价权|回购分红友好|核心仓位",
        "hold_summary": "长期持有主要依赖品牌粘性、全球分销网络和持续分红回购。即使增长不快，确定性本身就是长期持有理由。",
        "hold_confidence": 0.91,
        "exit_tags": "",
        "exit_summary": "",
        "exit_confidence": None,
        "degradation_tags": "",
        "degradation_summary": "",
        "degradation_confidence": None,
        "degradation_nature": "",
        "exit_hindsight": "不适用",
    },
    "BABA": {
        "entry_tags": "平台网络效应|高增长渗透|长期增长空间",
        "entry_summary": "阿里巴巴被长期买入的核心在于中国电商平台网络效应、商家生态和云业务带来的第二成长曲线。它本质上是平台型龙头与数字基础设施的结合体。",
        "entry_confidence": 0.81,
        "hold_tags": "平台网络效应|现金流稳定|长期增长空间",
        "hold_summary": "持续持有依赖电商生态沉淀下来的平台优势和较强现金流，哪怕宏观波动和监管扰动存在，核心商业地位仍然足够强。",
        "hold_confidence": 0.78,
        "exit_tags": "",
        "exit_summary": "",
        "exit_confidence": None,
        "degradation_tags": "",
        "degradation_summary": "",
        "degradation_confidence": None,
        "degradation_nature": "",
        "exit_hindsight": "不适用",
    },
    "DASH": {
        "entry_tags": "平台网络效应|高增长渗透",
        "entry_summary": "DoorDash 的买入逻辑来自本地生活配送平台的网络效应和渗透率提升空间。机构押注的是平台规模扩大后利润结构持续改善。",
        "entry_confidence": 0.74,
        "hold_tags": "长期增长空间|平台网络效应",
        "hold_summary": "被继续持有阶段，市场相信配送平台的订单密度、广告和新业务扩展可以逐步转化成更高质量的盈利。",
        "hold_confidence": 0.69,
        "exit_tags": "组合集中度让位|估值波动承受度",
        "exit_summary": "DoorDash 没有被继续长期拿住，更像是高估值成长平台在兑现节奏不稳时被组合让位，而不是简单的商业模式失效。",
        "exit_confidence": 0.61,
        "degradation_tags": "竞争加剧|盈利兑现不足",
        "degradation_summary": "DASH 落入退化象限，关键在于平台虽有规模优势，但盈利和资本回报的兑现仍不够扎实，竞争与补贴属性也削弱了经营持续性。",
        "degradation_confidence": 0.79,
        "degradation_nature": "成长兑现不足",
        "exit_hindsight": "后续需结合利润兑现节奏再判断是否卖早",
    },
    "SNOW": {
        "entry_tags": "高增长渗透|企业软件平台|长期增长空间",
        "entry_summary": "Snowflake 的买入逻辑建立在云数据平台的高增长渗透和企业软件平台属性上。机构押注的是数据基础设施地位和长期高利润空间。",
        "entry_confidence": 0.78,
        "hold_tags": "长期增长空间|企业软件平台",
        "hold_summary": "持续持有主要基于产品粘性和企业客户扩张空间，市场曾认为其高毛利平台特征最终会转成优质利润结构。",
        "hold_confidence": 0.71,
        "exit_tags": "估值波动承受度|组合集中度让位",
        "exit_summary": "Snowflake 没有被长期拿住，较大概率与高估值软件股回调后机构风险偏好下降有关，而不是需求完全消失。",
        "exit_confidence": 0.63,
        "degradation_tags": "盈利兑现不足|竞争加剧",
        "degradation_summary": "SNOW 进入退化象限，更多是因为高毛利并未同步兑现成高质量净利和资本回报，云数据赛道竞争也让长期盈利假设打了折扣。",
        "degradation_confidence": 0.8,
        "degradation_nature": "高估值成长回落",
        "exit_hindsight": "是否卖出正确，需要后续观察利润兑现能否持续改善",
    },
    "ORCL": {
        "entry_tags": "企业软件平台|高转换成本|现金流稳定",
        "entry_summary": "甲骨文的买入逻辑更偏成熟企业软件平台：数据库和企业软件安装基础深，客户转换成本高，现金流长期稳定。",
        "entry_confidence": 0.77,
        "hold_tags": "现金流稳定|高转换成本",
        "hold_summary": "如果从经营质量看，Oracle 具备长期持有条件，尤其是软件维护收入和企业客户锁定让其利润韧性很强。",
        "hold_confidence": 0.73,
        "exit_tags": "非核心仓位|能力圈边缘",
        "exit_summary": "ORCL 没有被长期拿住，较可能是机构并未把它视作高确信度核心仓位，而不是因为软件平台本身经营质量差。",
        "exit_confidence": 0.58,
        "degradation_tags": "",
        "degradation_summary": "",
        "degradation_confidence": None,
        "degradation_nature": "",
        "exit_hindsight": "从经营韧性看，未长期持有有复盘价值",
    },
    "BIIB": {
        "entry_tags": "成熟产品现金牛|创新药叙事",
        "entry_summary": "渤健的买入逻辑兼具成熟生物药现金流和创新药管线预期，属于医药里兼顾盈利能力与研发可选性的资产。",
        "entry_confidence": 0.72,
        "hold_tags": "现金流稳定|长期增长空间",
        "hold_summary": "从经营角度看，BIIB 具备较好的利润与现金流基础，只是它的长期空间更多依赖管线和新产品兑现。",
        "hold_confidence": 0.68,
        "exit_tags": "非核心仓位|能力圈边缘",
        "exit_summary": "没有被长期拿住，更像是医药研究深度与组合优先级问题，而不是现有业务完全不值得长期持有。",
        "exit_confidence": 0.57,
        "degradation_tags": "",
        "degradation_summary": "",
        "degradation_confidence": None,
        "degradation_nature": "",
        "exit_hindsight": "是否错过后续修复，需要和同类医药样本再比",
    },
    "WFC": {
        "entry_tags": "成熟产品现金牛|高资本回报",
        "entry_summary": "富国银行的买入逻辑偏向传统金融里的低估值与资本回报修复，核心资产仍是存贷款与零售银行网络。对长期价值资金而言，它更像成熟现金牛的修复型持仓。",
        "entry_confidence": 0.73,
        "hold_tags": "现金流稳定|核心仓位",
        "hold_summary": "被继续长期持有主要依赖银行业务的规模优势、盈利恢复能力和资本回报预期。对 Daily Journal 这类集中持仓主体来说，它更像高权重金融底仓。",
        "hold_confidence": 0.71,
        "exit_tags": "",
        "exit_summary": "",
        "exit_confidence": None,
        "degradation_tags": "",
        "degradation_summary": "",
        "degradation_confidence": None,
        "degradation_nature": "",
        "exit_hindsight": "不适用",
    },
    "PDD": {
        "entry_tags": "平台网络效应|高增长渗透|高资本回报",
        "entry_summary": "拼多多的买入逻辑是中国电商平台网络效应叠加高效率变现模型，属于平台龙头里少见同时兼具高增长和高资本回报的资产。",
        "entry_confidence": 0.86,
        "hold_tags": "平台网络效应|现金流稳定|长期增长空间",
        "hold_summary": "长期持有依赖商家生态、低价心智和平台流量优势，同时财务上已经表现出很强的盈利与现金流能力。",
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
    "AXP": {
        "entry_tags": "品牌与定价权|高转换成本|高资本回报",
        "entry_summary": "美国运通的买入逻辑来自高端卡品牌、商户与会员体系带来的双边优势，以及很强的资本回报能力。它是支付与消费金融结合的高质量资产。",
        "entry_confidence": 0.84,
        "hold_tags": "现金流稳定|品牌与定价权|核心仓位",
        "hold_summary": "持续持有依赖会员生态、品牌溢价和稳定的信用卡业务利润。它更像被长期资金反复验证过的金融消费复利股。",
        "hold_confidence": 0.86,
        "exit_tags": "",
        "exit_summary": "",
        "exit_confidence": None,
        "degradation_tags": "",
        "degradation_summary": "",
        "degradation_confidence": None,
        "degradation_nature": "",
        "exit_hindsight": "不适用",
    },
    "MDLZ": {
        "entry_tags": "品牌与定价权|现金流稳定",
        "entry_summary": "亿滋的买入逻辑围绕全球零食品牌组合、分销能力和消费品提价权展开，属于稳定现金流和全球品牌力兼备的成熟消费资产。",
        "entry_confidence": 0.81,
        "hold_tags": "现金流稳定|品牌与定价权|回购分红友好",
        "hold_summary": "长期持有依赖品牌组合的韧性、全球渠道和稳健的现金回收。它虽然不是高增长资产，但很符合长期持有的质量标准。",
        "hold_confidence": 0.8,
        "exit_tags": "",
        "exit_summary": "",
        "exit_confidence": None,
        "degradation_tags": "",
        "degradation_summary": "",
        "degradation_confidence": None,
        "degradation_nature": "",
        "exit_hindsight": "不适用",
    },
    "KHC": {
        "entry_tags": "品牌与定价权|成熟产品现金牛",
        "entry_summary": "卡夫亨氏的买入逻辑在于成熟食品品牌组合和现金流能力，属于典型的传统消费现金牛思路。它更依赖品牌资产和成本纪律，而不是增长弹性。",
        "entry_confidence": 0.76,
        "hold_tags": "现金流稳定|核心仓位",
        "hold_summary": "之所以还能长期拿住，更多是因为成熟品牌组合仍能提供可预期现金流，而且在某些机构组合里承担防御性角色。",
        "hold_confidence": 0.72,
        "exit_tags": "",
        "exit_summary": "",
        "exit_confidence": None,
        "degradation_tags": "",
        "degradation_summary": "",
        "degradation_confidence": None,
        "degradation_nature": "",
        "exit_hindsight": "不适用",
    },
    "YSG": {
        "entry_tags": "品牌与定价权|高增长渗透",
        "entry_summary": "逸仙电商最初的买入逻辑来自新消费美妆品牌叙事、线上渠道红利和快速增长预期。它本质上是品牌成长故事，而不是已成熟的消费复利资产。",
        "entry_confidence": 0.68,
        "hold_tags": "长期增长空间",
        "hold_summary": "被继续持有阶段，市场主要仍在等待品牌矩阵和渠道扩张转化成更稳的利润结构，而不是依赖已验证的高质量财务表现。",
        "hold_confidence": 0.61,
        "exit_tags": "组合集中度让位|盈利兑现不足",
        "exit_summary": "一旦品牌成长没有兑现为可持续利润，像 YSG 这样的新消费标的就很容易被组合让位，难形成长期核心仓位。",
        "exit_confidence": 0.64,
        "degradation_tags": "竞争加剧|盈利兑现不足",
        "degradation_summary": "YSG 退化的核心在于美妆品牌竞争激烈、营销投入高、利润兑现弱。增长故事存在，但经营持续性没有同步成形。",
        "degradation_confidence": 0.82,
        "degradation_nature": "品牌成长兑现不足",
        "exit_hindsight": "从经营结果看，长期持有难度较高",
    },
    "BBIO": {
        "entry_tags": "创新药叙事|高增长渗透",
        "entry_summary": "BridgeBio 的买入逻辑是典型创新药平台叙事：多管线布局和潜在商业化机会带来高赔率想象空间。它的核心吸引力来自未来，而非当期盈利。",
        "entry_confidence": 0.69,
        "hold_tags": "长期增长空间",
        "hold_summary": "继续持有更多是押注研发兑现和商业化突破，而不是因为它已经表现出稳定高质量经营。",
        "hold_confidence": 0.63,
        "exit_tags": "组合集中度让位|盈利兑现不足",
        "exit_summary": "当研发兑现节奏弱于预期、财务质量持续承压时，这类生物科技标的通常难以继续留在高优先级仓位中。",
        "exit_confidence": 0.66,
        "degradation_tags": "研发投入吞噬利润|单产品依赖|盈利兑现不足",
        "degradation_summary": "BBIO 的退化主要来自创新药平台常见问题：研发和商业化投入重、利润极不稳定、单项目成败对经营影响过大。",
        "degradation_confidence": 0.86,
        "degradation_nature": "研发驱动型承压",
        "exit_hindsight": "从财务兑现角度看，退出并不难理解",
    },
    "KNSA": {
        "entry_tags": "创新药叙事|高增长渗透",
        "entry_summary": "Kiniksa 的买入逻辑仍然是创新药成长叙事，关注点在产品推进、商业化放量和研发兑现可能性上。",
        "entry_confidence": 0.67,
        "hold_tags": "长期增长空间",
        "hold_summary": "被持有阶段更像是等待产品与商业化成果兑现，而不是依靠已经成熟的盈利能力。",
        "hold_confidence": 0.62,
        "exit_tags": "非核心仓位|盈利兑现不足",
        "exit_summary": "一旦商业化进展和财务兑现不够强，这类仓位往往难升级为长期核心持仓。",
        "exit_confidence": 0.58,
        "degradation_tags": "研发投入吞噬利润|盈利兑现不足",
        "degradation_summary": "KNSA 落入退化象限，核心在于研发型公司常见的利润和现金流承压，经营质量尚不足以支撑长期复利逻辑。",
        "degradation_confidence": 0.8,
        "degradation_nature": "商业化兑现不足",
        "exit_hindsight": "从长期持有框架看，保持谨慎是合理的",
    },
    "DAL": {
        "entry_tags": "周期复苏|高增长渗透",
        "entry_summary": "达美航空的买入逻辑更像周期复苏交易：航空需求恢复、票价修复和利润弹性释放。它不是典型长期高质量资产，而是对行业修复的押注。",
        "entry_confidence": 0.72,
        "hold_tags": "长期增长空间",
        "hold_summary": "继续持有阶段主要是在等待航空出行修复兑现，而不是依赖强护城河和稳定资本回报。",
        "hold_confidence": 0.59,
        "exit_tags": "组合集中度让位|估值波动承受度",
        "exit_summary": "周期修复逻辑一旦不再足够顺畅，航空股通常很难继续占据长期资金的高权重位置。",
        "exit_confidence": 0.62,
        "degradation_tags": "周期性波动|竞争加剧",
        "degradation_summary": "DAL 的经营持续性弱点主要来自航空业天然的高周期性、高固定成本和竞争压力，利润质量难以长期稳定在高位。",
        "degradation_confidence": 0.84,
        "degradation_nature": "强周期型",
        "exit_hindsight": "从长期持有框架看，航空股更适合阶段性而非长期核心仓位",
    },
    "UXIN": {
        "entry_tags": "平台网络效应|高增长渗透",
        "entry_summary": "优信的买入逻辑是二手车平台/渠道升级叙事，机构押注的是行业渗透和平台规模效应的放大。",
        "entry_confidence": 0.63,
        "hold_tags": "长期增长空间",
        "hold_summary": "被继续持有主要因为市场仍对二手车线上化和平台化有期待，而不是因为经营质量已经稳定。",
        "hold_confidence": 0.56,
        "exit_tags": "",
        "exit_summary": "",
        "exit_confidence": None,
        "degradation_tags": "竞争加剧|盈利兑现不足",
        "degradation_summary": "UXIN 的退化更像平台成长故事未能转成稳定盈利，低利润率和经营脆弱性使其难以进入长期复利范式。",
        "degradation_confidence": 0.8,
        "degradation_nature": "平台成长兑现不足",
        "exit_hindsight": "仍在持有，后续要重点观察兑现质量",
    },
    "KMI": {
        "entry_tags": "成熟产品现金牛|现金流稳定",
        "entry_summary": "Kinder Morgan 的买入逻辑偏向稳定管道资产与分红现金流，属于能源基础设施里的成熟现金牛思路。",
        "entry_confidence": 0.72,
        "hold_tags": "现金流稳定",
        "hold_summary": "如果从经营角度看，KMI 的长期持有理由在于管道资产现金流可预期、盈利弹性不如上游资源股但稳定性更强。",
        "hold_confidence": 0.69,
        "exit_tags": "非核心仓位|能力圈边缘",
        "exit_summary": "没有被长期拿住，更可能是仓位优先级和偏好问题，而不是基础设施现金流逻辑失效。",
        "exit_confidence": 0.6,
        "degradation_tags": "",
        "degradation_summary": "",
        "degradation_confidence": None,
        "degradation_nature": "",
        "exit_hindsight": "从经营稳定性看，有一定复盘价值",
    },
    "RPRX": {
        "entry_tags": "成熟产品现金牛|高资本回报",
        "entry_summary": "Royalty Pharma 的买入逻辑在于版税流模式带来的轻资产、高现金回收和相对分散的药品敞口。它本质上是医药里的现金流平台。",
        "entry_confidence": 0.76,
        "hold_tags": "现金流稳定|长期增长空间",
        "hold_summary": "从经营角度看，RPRX 具备较好的长期持有条件，原因在于轻资产结构和版税现金流的稳定性。",
        "hold_confidence": 0.73,
        "exit_tags": "非核心仓位|能力圈边缘",
        "exit_summary": "没有被长期拿住，较可能与医药覆盖和持仓优先级有关，而非商业模式本身质量不足。",
        "exit_confidence": 0.61,
        "degradation_tags": "",
        "degradation_summary": "",
        "degradation_confidence": None,
        "degradation_nature": "",
        "exit_hindsight": "作为高质量医药现金流资产，值得后续再复盘",
    },
    "DLO": {
        "entry_tags": "高增长渗透|轻资产模式",
        "entry_summary": "DLocal 的买入逻辑来自跨境支付渗透率提升和轻资产平台模式，属于高增长金融基础设施叙事。",
        "entry_confidence": 0.71,
        "hold_tags": "长期增长空间|高资本回报",
        "hold_summary": "如果从经营角度看，DLO 兼具增长空间和较好的利润率，具备成为长期高质量资产的潜力。",
        "hold_confidence": 0.69,
        "exit_tags": "非核心仓位|估值波动承受度",
        "exit_summary": "没有被长期拿住，较可能与成长型金融科技标的波动较大、仓位容易被压低有关。",
        "exit_confidence": 0.58,
        "degradation_tags": "",
        "degradation_summary": "",
        "degradation_confidence": None,
        "degradation_nature": "",
        "exit_hindsight": "后续要看它是否能从高增长资产走向高质量复利资产",
    },
    "LAMR": {
        "entry_tags": "行业寡头|高转换成本",
        "entry_summary": "Lamar 的买入逻辑在于户外广告的区域寡头特征和广告位资源的长期稀缺性。它是典型的地方性护城河资产。",
        "entry_confidence": 0.78,
        "hold_tags": "现金流稳定|高转换成本",
        "hold_summary": "从经营角度看，LAMR 很像可以长期拿住的基础设施型媒体资产，现金流和资产属性都比较稳。",
        "hold_confidence": 0.76,
        "exit_tags": "非核心仓位|组合集中度让位",
        "exit_summary": "没有被长期拿住，更像是晚近才进入组合的边缘仓位，还没来得及成为真正的长期核心持仓。",
        "exit_confidence": 0.56,
        "degradation_tags": "",
        "degradation_summary": "",
        "degradation_confidence": None,
        "degradation_nature": "",
        "exit_hindsight": "从经营属性看，有继续跟踪价值",
    },
    "ALLE": {
        "entry_tags": "品牌与定价权|高转换成本",
        "entry_summary": "Allegion 的买入逻辑在于安防与门锁产品的品牌、渠道和替换成本优势，属于工业消费交叉地带的稳定资产。",
        "entry_confidence": 0.74,
        "hold_tags": "现金流稳定|高转换成本",
        "hold_summary": "从经营质量看，ALLE 具备不错的利润率和客户粘性，属于典型可以长期持有但不一定会被高度关注的好公司。",
        "hold_confidence": 0.71,
        "exit_tags": "非核心仓位|组合集中度让位",
        "exit_summary": "没有被长期拿住，更多像是因为仓位建立较晚且不够核心，而不是经营质量出了问题。",
        "exit_confidence": 0.57,
        "degradation_tags": "",
        "degradation_summary": "",
        "degradation_confidence": None,
        "degradation_nature": "",
        "exit_hindsight": "偏向被忽略的高质量样本",
    },
    "MCK": {
        "entry_tags": "成熟产品现金牛|现金流稳定",
        "entry_summary": "McKesson 的买入逻辑偏向医药分销平台的规模和现金流属性，属于成熟但利润率不高的稳定业务。",
        "entry_confidence": 0.7,
        "hold_tags": "现金流稳定",
        "hold_summary": "如果要形成长期持有理由，主要依赖分销平台规模和经营稳定性，但它缺少更强的高质量护城河特征。",
        "hold_confidence": 0.58,
        "exit_tags": "非核心仓位|组合集中度让位",
        "exit_summary": "最终没有被长期拿住，说明这种低利润率分销资产很难在高标准长期组合里占据核心位置。",
        "exit_confidence": 0.65,
        "degradation_tags": "",
        "degradation_summary": "",
        "degradation_confidence": None,
        "degradation_nature": "",
        "exit_hindsight": "在本框架里更像一般性稳定资产，而非优质复利资产",
    },
    "NKTX": {
        "entry_tags": "创新药叙事|高增长渗透",
        "entry_summary": "Nkarta 的买入逻辑是早期创新药和细胞治疗平台叙事，核心吸引力在于研发想象空间而不是当前财务质量。",
        "entry_confidence": 0.64,
        "hold_tags": "长期增长空间",
        "hold_summary": "这类公司若被持有，通常也是因为潜在平台价值和研发成功概率，而不是因为已经形成稳定经营质量。",
        "hold_confidence": 0.53,
        "exit_tags": "非核心仓位|盈利兑现不足",
        "exit_summary": "当研发兑现和资本市场环境都不友好时，这类仓位通常会快速失去优先级。",
        "exit_confidence": 0.68,
        "degradation_tags": "研发投入吞噬利润|单产品依赖",
        "degradation_summary": "NKTX 进入弱质/陷阱象限，主要是因为研发投入重、商业化远、单平台成败影响大，经营持续性几乎没有建立起来。",
        "degradation_confidence": 0.86,
        "degradation_nature": "早期研发型脆弱样本",
        "exit_hindsight": "从长期持有框架看，谨慎是合理的",
    },
    "TXG": {
        "entry_tags": "实验室工具平台|高增长渗透",
        "entry_summary": "10x Genomics 的买入逻辑来自前沿科研工具平台和高成长渗透叙事，市场一度期待其成为高质量生命科学工具公司。",
        "entry_confidence": 0.72,
        "hold_tags": "长期增长空间",
        "hold_summary": "被持有阶段更多是押注科研工具平台潜力，而不是因为其经营质量已经稳定成熟。",
        "hold_confidence": 0.58,
        "exit_tags": "非核心仓位|估值波动承受度",
        "exit_summary": "当高成长工具股的兑现节奏放缓、估值承压时，这类仓位很难继续被抱住。",
        "exit_confidence": 0.67,
        "degradation_tags": "竞争加剧|盈利兑现不足",
        "degradation_summary": "TXG 的弱点在于高成长平台叙事没有转成稳定盈利，竞争和需求波动共同拉低了经营持续性。",
        "degradation_confidence": 0.81,
        "degradation_nature": "高成长工具平台回落",
        "exit_hindsight": "更像成长叙事失速，而非护城河完全消失",
    },
    "HIPO": {
        "entry_tags": "高增长渗透|轻资产模式",
        "entry_summary": "Hippo 的买入逻辑来自保险科技平台叙事，市场原本期待技术和渠道效率能够重塑保险承保与分销。",
        "entry_confidence": 0.63,
        "hold_tags": "长期增长空间",
        "hold_summary": "这类公司如果被持有，主要是押注模式创新和成长空间，而不是基于已经形成的稳健盈利。",
        "hold_confidence": 0.49,
        "exit_tags": "非核心仓位|盈利兑现不足",
        "exit_summary": "一旦业务模式没有兑现出盈利质量，保险科技这类高叙事资产通常会迅速失去持有价值。",
        "exit_confidence": 0.73,
        "degradation_tags": "竞争加剧|盈利兑现不足",
        "degradation_summary": "HIPO 进入弱质/陷阱象限，说明模式创新没有顺利转化成稳定承保盈利和现金流，经营持续性明显不足。",
        "degradation_confidence": 0.83,
        "degradation_nature": "保险科技叙事失速",
        "exit_hindsight": "从当前结果看，未长期持有是合理的",
    },
    "TCRX": {
        "entry_tags": "创新药叙事|高增长渗透",
        "entry_summary": "TScan Therapeutics 的买入逻辑仍然是早期创新药平台叙事，核心来自研发潜力与远期商业化预期。",
        "entry_confidence": 0.62,
        "hold_tags": "长期增长空间",
        "hold_summary": "被持有阶段更多是围绕研发故事，而不是建立在已经验证的财务质量上。",
        "hold_confidence": 0.48,
        "exit_tags": "非核心仓位|盈利兑现不足",
        "exit_summary": "研发兑现不确定、亏损持续的情况下，这类早期生物科技样本通常只会停留在边缘试仓层面。",
        "exit_confidence": 0.74,
        "degradation_tags": "研发投入吞噬利润|单产品依赖",
        "degradation_summary": "TCRX 落入弱质/陷阱象限，主要因为公司仍停留在高研发消耗、低财务可见度阶段，经营持续性尚未建立。",
        "degradation_confidence": 0.88,
        "degradation_nature": "早期研发型脆弱样本",
        "exit_hindsight": "在长期持有框架下，谨慎是必要的",
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


def keyword_tags(name: str) -> str:
    text = name.lower()
    if any(word in text for word in ["berkshire", "johnson & johnson", "sanofi", "organon"]):
        return "成熟产品现金牛|现金流稳定"
    if any(word in text for word in ["pharma", "therapeutics", "biotech", "biosciences", "immuno", "apellis", "argenx", "cytokinetics", "geron", "moderna", "novavax", "organon", "sarepta", "sanofi"]):
        return "创新药叙事|高增长渗透"
    if any(word in text for word in ["software", "cadence", "salesforce", "sentinelone", "oracle"]):
        return "企业软件平台|高转换成本"
    if any(word in text for word in ["semiconductor", "broadcom", "arista", "tsmc", "taiwan semiconductor", "wolfspeed"]):
        return "半导体硬件|高资本回报"
    if any(word in text for word in ["microsoft", "meta", "baidu", "netease", "shopify", "coupang"]):
        return "平台网络效应|高资本回报|长期增长空间"
    if any(word in text for word in ["bilibili", "iqiyi", "weibo", "playtika", "roblox", "new york times", "yalla"]):
        return "内容与线上娱乐|平台网络效应"
    if any(word in text for word in ["sirius"]):
        return "内容与线上娱乐|现金流稳定"
    if any(word in text for word in ["bank", "financial", "paypal", "futu", "mellon", "mastercard", "visa", "verisign"]):
        return "金融基础设施|行业寡头"
    if any(word in text for word in ["marsh", "mclennan"]):
        return "行业寡头|现金流稳定"
    if any(word in text for word in ["restaurant", "beauty", "beverage", "food", "krispy", "vipshop", "pg ", "procter", "ulta", "beyond meat", "yatsen", "h world", "melco"]):
        return "消费品牌渠道|品牌与定价权"
    if any(word in text for word in ["coupang"]):
        return "高增长渗透|消费品牌渠道"
    if any(word in text for word in ["zto", "liberty latin"]):
        return "行业寡头|长期增长空间"
    if any(word in text for word in ["sunrun", "constellation energy"]):
        return "能源转型叙事|高增长渗透"
    if any(word in text for word in ["vnet"]):
        return "工业基础设施|高增长渗透"
    if any(word in text for word in ["gold", "barrick", "energy", "ge ", "trane", "lennar", "constellation"]):
        return "工业基础设施|周期复苏"
    return "高资本回报|现金流稳定"


def build_auto_payload(row: pd.Series) -> dict[str, object]:
    ticker = str(row["代码"])
    cn_name = str(row["中文公司名"])
    en_name = str(row["英文公司名"])
    name = f"{cn_name} {en_name}"
    category = str(row["分类结果"])
    current_status = str(row.get("当前持有状态", ""))
    base_tags = keyword_tags(name)
    is_current = "当前在仓" in current_status

    if category == "长期赢家":
        return {
            "entry_tags": base_tags,
            "entry_summary": f"{cn_name} 的入池逻辑来自已经验证过的高质量经营特征：长期盈利能力、现金流质量或行业地位相对突出，因此在全池里被归为长期赢家。",
            "entry_confidence": 0.68,
            "hold_tags": "现金流稳定|长期增长空间" + ("|核心仓位" if is_current else ""),
            "hold_summary": f"{cn_name} 被持续研究的重点是经营质量能否长期维持。当前分类显示其持有持续性和经营持续性都处在较高区间，适合作为正面样本继续拆解。",
            "hold_confidence": 0.66,
            "exit_tags": "" if is_current else "组合集中度让位|非核心仓位",
            "exit_summary": "" if is_current else f"{cn_name} 当前不在仓，初步按组合取舍或非核心仓位处理；是否属于卖出误判，需要后续案例复盘再确认。",
            "exit_confidence": None if is_current else 0.45,
            "degradation_tags": "",
            "degradation_summary": "",
            "degradation_confidence": None,
            "degradation_nature": "",
            "exit_hindsight": "当前仍持有，暂不评价退出对错" if is_current else "需后续复盘退出后经营表现",
        }
    if category == "经营优秀但未被长期拿住":
        return {
            "entry_tags": base_tags,
            "entry_summary": f"{cn_name} 的经营持续性较强，买入逻辑更多来自质量、回报或行业地位，而不是短期交易机会。",
            "entry_confidence": 0.62,
            "hold_tags": "现金流稳定|长期增长空间",
            "hold_summary": f"从经营数据看，{cn_name} 具备继续研究的质量基础；但持有持续性偏低，说明它没有被机构稳定沉淀为长期核心仓位。",
            "hold_confidence": 0.58,
            "exit_tags": "非核心仓位|组合集中度让位",
            "exit_summary": f"{cn_name} 未被长期拿住，当前先归因为仓位优先级、组合约束或机构能力圈边界，而不是经营质量明显恶化。",
            "exit_confidence": 0.5,
            "degradation_tags": "",
            "degradation_summary": "",
            "degradation_confidence": None,
            "degradation_nature": "",
            "exit_hindsight": "从经营质量看，后续需要重点复盘是否卖早",
        }
    if category == "审美失效/退化案例":
        return {
            "entry_tags": base_tags,
            "entry_summary": f"{cn_name} 曾经具备被机构关注的成长、周期或平台叙事，因此进入持仓池；但这类逻辑对兑现质量要求较高。",
            "entry_confidence": 0.58,
            "hold_tags": "长期增长空间",
            "hold_summary": f"{cn_name} 的持有持续性不低，说明机构曾愿意给它时间验证逻辑；问题在于经营持续性没有同步维持在高位。",
            "hold_confidence": 0.56,
            "exit_tags": "" if is_current else "盈利兑现不足|组合集中度让位",
            "exit_summary": "" if is_current else f"{cn_name} 当前不在仓，初步判断退出与经营质量兑现不足或组合重新排序有关。",
            "exit_confidence": None if is_current else 0.55,
            "degradation_tags": "盈利兑现不足|竞争加剧",
            "degradation_summary": f"{cn_name} 落入退化象限，核心含义是历史持有偏好和当前经营持续性不匹配；后续研究应重点核实利润、现金流或竞争格局为何变弱。",
            "degradation_confidence": 0.68,
            "degradation_nature": "经营兑现不足",
            "exit_hindsight": "需后续结合退化原因判断退出是否正确",
        }
    return {
        "entry_tags": base_tags,
        "entry_summary": f"{cn_name} 曾进入机构持仓池，但当前经营质量或持续性不足，暂按弱质/陷阱样本处理。",
        "entry_confidence": 0.52,
        "hold_tags": "长期增长空间",
        "hold_summary": f"{cn_name} 的持有基础较弱，更多来自远期故事或阶段性机会，尚未形成稳定复利型持有理由。",
        "hold_confidence": 0.45,
        "exit_tags": "" if is_current else "非核心仓位|盈利兑现不足",
        "exit_summary": "" if is_current else f"{cn_name} 未形成长期持有，初步看是因为经营质量、兑现确定性或仓位重要性不足。",
        "exit_confidence": None if is_current else 0.6,
        "degradation_tags": "盈利兑现不足|竞争加剧",
        "degradation_summary": f"{cn_name} 在当前框架中属于负面样本，后续研究重点是识别买入时的叙事与实际经营质量之间的偏差。",
        "degradation_confidence": 0.72,
        "degradation_nature": "质量不足或叙事落空",
        "exit_hindsight": "在长期持有框架下，需要作为负面样本保留",
    }


def build_case_payloads(classification: pd.DataFrame) -> dict[str, dict[str, object]]:
    eligible = classification[~classification["分类结果"].isin(["观察区", "未进入分类样本"])].copy()
    generated = {
        str(row["代码"]): build_auto_payload(row)
        for _, row in eligible.iterrows()
        if str(row["代码"]) not in CASE_DATA
    }
    generated.update(CASE_DATA)
    return generated


def update_research_judgement(workbook: Path) -> tuple[int, int]:
    research = pd.read_excel(workbook, sheet_name="research_judgement")
    holdings = pd.read_excel(workbook, sheet_name="holding_timeline")
    annual = pd.read_excel(workbook, sheet_name="operating_timeline")
    classification = pd.read_excel(workbook, sheet_name="classification_snapshot")
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
    case_payloads = build_case_payloads(classification)
    for ticker, payload in case_payloads.items():
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
