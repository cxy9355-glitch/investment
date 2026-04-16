import {
  createLinePath,
  formatCurrency,
  formatNumber,
  formatPercent,
  getQueryParam,
  loadJson
} from "./utils.js";

const code = getQueryParam("code");

const nodes = {
  stockTitle: document.getElementById("stockTitle"),
  stockSub: document.getElementById("stockSub"),
  detailUpdatedAt: document.getElementById("detailUpdatedAt"),
  detailMetrics: document.getElementById("detailMetrics"),
  methodComparison: document.getElementById("methodComparison"),
  candidateReason: document.getElementById("candidateReason"),
  sourceInfo: document.getElementById("sourceInfo"),
  detailChart: document.getElementById("detailChart")
};

function renderMetrics(detail) {
  const metrics = [
    ["PE(TTM)", formatNumber(detail.snapshot.peTtm, 2)],
    ["PE 历史分位", formatPercent(detail.snapshot.pePercentile, 2)],
    ["PB", formatNumber(detail.snapshot.pb, 2)],
    ["ROE", formatPercent(detail.snapshot.roe, 2)],
    ["ROA", formatPercent(detail.snapshot.roa, 2)],
    ["最新基金家数", detail.snapshot.latestFundCount ?? "--"]
  ];
  nodes.detailMetrics.innerHTML = metrics
    .map(
      ([label, value]) => `
      <article class="summary-card">
        <p class="eyebrow">${label}</p>
        <h3>${value}</h3>
      </article>
    `
    )
    .join("");
}

function renderComparison(detail) {
  const items = [
    {
      label: "占总股本比例",
      value: detail.methodologies["float-ratio"]
    },
    {
      label: "池内占比",
      value: detail.methodologies["pool-share"]
    }
  ];
  nodes.methodComparison.innerHTML = items
    .map(
      ({ label, value }) => `
      <div class="comparison-item">
        <strong>${label} · 排名 #${value.rank}</strong>
        <div>当前：${formatPercent(value.currentValue, 2)}</div>
        <div>累计：${formatPercent(value.cumulativeValue, 2)}</div>
        <div>均值：${formatPercent(value.averageValue, 2)}</div>
        <div>峰值：${formatPercent(value.peakValue, 2)}</div>
      </div>
    `
    )
    .join("");
}

function renderReason(detail) {
  nodes.candidateReason.innerHTML = `
    <div>${detail.methodologies["pool-share"].candidateReason || "暂无池内口径候选理由。"}</div>
    <div>${detail.methodologies["float-ratio"].candidateReason || "暂无占总股本比例口径候选理由。"}</div>
  `;
}

function renderSource(detail, methodology) {
  nodes.sourceInfo.innerHTML = `
    <div>最新财报期：${detail.snapshot.latestReportDate || "--"}</div>
    <div>最新持仓市值：${formatCurrency(detail.snapshot.latestHoldValue)}</div>
    <div>当前更新：${methodology.updatedAt}</div>
    <div>说明：站点为静态发布快照，详细定义见方法说明页。</div>
  `;
}

function renderChart(detail) {
  const svg = nodes.detailChart;
  const width = 1000;
  const height = 420;
  const padding = { top: 36, right: 28, bottom: 54, left: 56 };
  const floatValues = detail.series.map((item) => item.totalsharesRatio);
  const poolValues = detail.series.map((item) => item.poolShare);
  const allValues = [...floatValues, ...poolValues];
  const min = Math.min(...allValues);
  const max = Math.max(...allValues);
  const innerWidth = width - padding.left - padding.right;
  const innerHeight = height - padding.top - padding.bottom;
  const yRange = max - min || 1;

  const yTicks = 4;
  const grid = Array.from({ length: yTicks + 1 }, (_, index) => {
    const ratio = index / yTicks;
    const value = max - yRange * ratio;
    const y = padding.top + innerHeight * ratio;
    return `
      <line x1="${padding.left}" y1="${y}" x2="${width - padding.right}" y2="${y}" stroke="rgba(23,37,53,0.12)" />
      <text x="${padding.left - 10}" y="${y + 4}" text-anchor="end" fill="#68788c" font-size="12">${value.toFixed(2)}%</text>
    `;
  }).join("");

  const xLabels = detail.series.filter((_, index) => index % Math.max(Math.floor(detail.series.length / 6), 1) === 0)
    .map((item, index, list) => {
      const pointIndex = detail.series.findIndex((entry) => entry.date === item.date);
      const x = padding.left + (innerWidth * pointIndex) / Math.max(detail.series.length - 1, 1);
      return `<text x="${x}" y="${height - 16}" text-anchor="${index === 0 ? "start" : index === list.length - 1 ? "end" : "middle"}" fill="#68788c" font-size="12">${item.date}</text>`;
    })
    .join("");

  svg.innerHTML = `
    <rect x="0" y="0" width="${width}" height="${height}" fill="transparent"></rect>
    ${grid}
    <path d="${createLinePath(floatValues, width, height, padding)}" fill="none" stroke="#123b65" stroke-width="3"></path>
    <path d="${createLinePath(poolValues, width, height, padding)}" fill="none" stroke="#0d6665" stroke-width="3"></path>
    ${xLabels}
    <text x="${padding.left}" y="22" fill="#172535" font-size="14">蓝线：占总股本比例 · 绿线：池内占比</text>
  `;
}

async function bootstrap() {
  if (!code) {
    nodes.stockTitle.textContent = "缺少股票代码";
    nodes.stockSub.textContent = "请从主看板进入，或在 URL 后拼接 ?code=600519 这类参数。";
    return;
  }
  const [detail, methodology] = await Promise.all([
    loadJson(`./data/stocks/${code}.json`),
    loadJson("./data/metadata/methodology.json")
  ]);
  document.title = `${detail.identity.name} ${detail.identity.code} - 股票详情`;
  nodes.stockTitle.textContent = `${detail.identity.name} ${detail.identity.code}`;
  nodes.stockSub.textContent = `池内占比排名 #${detail.methodologies["pool-share"].rank} · 占总股本比例排名 #${detail.methodologies["float-ratio"].rank}`;
  nodes.detailUpdatedAt.textContent = `数据更新：${methodology.updatedAt}`;
  renderMetrics(detail);
  renderComparison(detail);
  renderReason(detail);
  renderSource(detail, methodology);
  renderChart(detail);
}

bootstrap().catch((error) => {
  nodes.stockTitle.textContent = "载入失败";
  nodes.stockSub.textContent = error.message;
});
