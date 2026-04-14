const dataBundle = window.__SPREAD_DATA__;

if (!dataBundle || !Array.isArray(dataBundle.records)) {
  throw new Error("Missing spread data bundle.");
}

const svg = document.getElementById("mainChart");
const tooltip = document.getElementById("chartTooltip");
const rangeSwitch = document.getElementById("rangeSwitch");
const legendSwitches = document.getElementById("legendSwitches");

const state = {
  range: "3Y",
  visible: {
    dividendYield: true,
    treasuryYield: true,
    spread: true
  },
  activeDate: dataBundle.meta.latest.date
};

const seriesCatalog = [
  { key: "dividendYield", label: "指数股息率", color: "#0d6665", className: "series-dividend" },
  { key: "treasuryYield", label: "10Y 国债利率", color: "#c78b2e", className: "series-treasury" },
  { key: "spread", label: "股债息差", color: "#b45843", className: "series-spread" }
];

function parseDate(value) {
  return new Date(`${value}T00:00:00+08:00`);
}

function formatPercent(value, digits = 2) {
  return `${Number(value).toFixed(digits)}%`;
}

function formatNumber(value, digits = 2) {
  return Number(value).toFixed(digits);
}

function formatDate(value) {
  const date = parseDate(value);
  const month = `${date.getMonth() + 1}`.padStart(2, "0");
  const day = `${date.getDate()}`.padStart(2, "0");
  return `${date.getFullYear()}-${month}-${day}`;
}

function getRangeLabel(range) {
  if (range === "1Y") {
    return "近1年";
  }
  if (range === "3Y") {
    return "近3年";
  }
  return "全部样本";
}

function calculateMidrankPercentile(records, key, targetValue) {
  const values = records
    .map((item) => item[key])
    .filter((value) => Number.isFinite(value));

  if (!values.length || !Number.isFinite(targetValue)) {
    return null;
  }

  let lowerCount = 0;
  let equalCount = 0;
  for (const value of values) {
    if (value < targetValue) {
      lowerCount += 1;
    } else if (value === targetValue) {
      equalCount += 1;
    }
  }

  return ((lowerCount + (equalCount / 2)) / values.length) * 100;
}

function getFilteredRecords() {
  const records = dataBundle.records;
  const latest = parseDate(records[records.length - 1].date);

  if (state.range === "ALL") {
    return records;
  }

  const boundary = new Date(latest);
  if (state.range === "1Y") {
    boundary.setFullYear(boundary.getFullYear() - 1);
  } else {
    boundary.setFullYear(boundary.getFullYear() - 3);
  }

  return records.filter((item) => parseDate(item.date) >= boundary);
}

function getActiveRecord(records) {
  return records.find((item) => item.date === state.activeDate) || records[records.length - 1];
}

function buildHeroMeta() {
  const meta = dataBundle.meta;
  document.getElementById("heroMeta").innerHTML = `
    <div class="hero-meta-card">
      <p class="eyebrow">数据区间</p>
      <strong>${meta.dateRange.start} ~ ${meta.dateRange.end}</strong>
    </div>
    <div class="hero-meta-card">
      <p class="eyebrow">当前息差分位</p>
      <strong>${formatPercent(meta.spreadPercentile, 2)}</strong>
    </div>
    <div class="hero-meta-card">
      <p class="eyebrow">最新指数点位</p>
      <strong>${formatNumber(meta.latest.closePoint, 2)}</strong>
    </div>
  `;
}

function buildLegend() {
  legendSwitches.innerHTML = "";
  for (const series of seriesCatalog) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `legend-chip ${state.visible[series.key] ? "is-active" : ""}`;
    button.textContent = series.label;
    button.style.boxShadow = `inset 0 0 0 1px ${series.color}22`;
    button.style.background = state.visible[series.key] ? series.color : "rgba(255,255,255,0.76)";
    button.style.color = state.visible[series.key] ? "#fff8f0" : "#142127";
    button.addEventListener("click", () => {
      state.visible[series.key] = !state.visible[series.key];
      buildLegend();
      render();
    });
    legendSwitches.appendChild(button);
  }
}

function buildBenchmarks() {
  const { p20, p50, p80 } = dataBundle.meta.spreadQuantiles;
  document.getElementById("benchmarkGrid").innerHTML = `
    <div class="benchmark-item">
      <span>20% 分位</span>
      <strong>${formatPercent(p20, 2)}</strong>
    </div>
    <div class="benchmark-item">
      <span>50% 分位</span>
      <strong>${formatPercent(p50, 2)}</strong>
    </div>
    <div class="benchmark-item">
      <span>80% 分位</span>
      <strong>${formatPercent(p80, 2)}</strong>
    </div>
  `;
}

function buildNotes() {
  const noteList = document.getElementById("noteList");
  noteList.innerHTML = dataBundle.meta.notes.map((item) => `<li>${item}</li>`).join("");

  const sourcesList = document.getElementById("sourcesList");
  sourcesList.innerHTML = dataBundle.meta.sources.map((item) => `
    <div class="source-item">
      <strong>${item.label}</strong>
      <a href="${item.url}" target="_blank" rel="noreferrer">${item.url}</a>
    </div>
  `).join("");
}

function updateReadout(record, currentRangeRecords) {
  const rangeLabel = getRangeLabel(state.range);
  const rangePercentile = calculateMidrankPercentile(currentRangeRecords, "dividendYield", record.dividendYield);
  const fullSamplePercentile = record.dividendYieldPercentile;

  document.getElementById("readoutDate").textContent = formatDate(record.date);
  document.getElementById("readoutList").innerHTML = `
    <div class="readout-row"><dt>指数股息率</dt><dd>${formatPercent(record.dividendYield, 2)}</dd></div>
    <div class="readout-row"><dt>10Y 国债利率</dt><dd>${formatPercent(record.treasuryYield, 2)}</dd></div>
    <div class="readout-row"><dt>股债息差</dt><dd>${formatPercent(record.spread, 2)}</dd></div>
    <div class="readout-row"><dt>${rangeLabel}股息率分位</dt><dd>${formatPercent(rangePercentile, 2)}</dd></div>
    <div class="readout-row"><dt>全样本股息率分位</dt><dd>${formatPercent(fullSamplePercentile, 2)}</dd></div>
    <div class="readout-row"><dt>指数点位</dt><dd>${formatNumber(record.closePoint, 2)}</dd></div>
  `;

  document.getElementById("dividendYieldValue").textContent = formatPercent(record.dividendYield, 2);
  document.getElementById("dividendYieldSub").textContent = `${dataBundle.meta.seriesLabel}`;
  document.getElementById("treasuryYieldValue").textContent = formatPercent(record.treasuryYield, 2);
  document.getElementById("treasuryYieldSub").textContent = "中国 10 年期国债收益率";
  document.getElementById("spreadValue").textContent = formatPercent(record.spread, 2);
  document.getElementById("spreadSub").textContent = `全样本分位 ${formatPercent(dataBundle.meta.spreadPercentile, 2)}`;
  document.getElementById("dividendPercentileValue").textContent = formatPercent(rangePercentile, 2);
  document.getElementById("dividendPercentileSub").textContent = `${rangeLabel}口径；全样本 ${formatPercent(fullSamplePercentile, 2)}`;
}

function createSvgNode(tag, attrs = {}) {
  const node = document.createElementNS("http://www.w3.org/2000/svg", tag);
  Object.entries(attrs).forEach(([key, value]) => {
    node.setAttribute(key, value);
  });
  return node;
}

function getChartContext(records) {
  const width = 1120;
  const height = 560;
  const margin = { top: 36, right: 70, bottom: 54, left: 72 };
  const times = records.map((item) => parseDate(item.date).getTime());
  const xMin = Math.min(...times);
  const xMax = Math.max(...times);

  const visibleKeys = seriesCatalog.filter((series) => state.visible[series.key]).map((series) => series.key);
  const values = records.flatMap((item) => visibleKeys.map((key) => item[key]));
  if (state.visible.spread) {
    values.push(
      dataBundle.meta.spreadQuantiles.p20,
      dataBundle.meta.spreadQuantiles.p50,
      dataBundle.meta.spreadQuantiles.p80
    );
  }

  const rawMin = Math.min(...values);
  const rawMax = Math.max(...values);
  const padding = Math.max((rawMax - rawMin) * 0.12, 0.2);
  const yMin = rawMin - padding;
  const yMax = rawMax + padding;

  const xScale = (value) => {
    const innerWidth = width - margin.left - margin.right;
    return margin.left + ((value - xMin) / (xMax - xMin || 1)) * innerWidth;
  };

  const yScale = (value) => {
    const innerHeight = height - margin.top - margin.bottom;
    return height - margin.bottom - ((value - yMin) / (yMax - yMin || 1)) * innerHeight;
  };

  return { width, height, margin, xMin, xMax, yMin, yMax, xScale, yScale };
}

function buildLinePath(records, key, xScale, yScale) {
  return records
    .map((item, index) => `${index === 0 ? "M" : "L"} ${xScale(parseDate(item.date).getTime()).toFixed(2)} ${yScale(item[key]).toFixed(2)}`)
    .join(" ");
}

function buildSpreadArea(records, xScale, yScale, bottom) {
  if (!records.length) {
    return "";
  }
  const topPath = records
    .map((item, index) => `${index === 0 ? "M" : "L"} ${xScale(parseDate(item.date).getTime()).toFixed(2)} ${yScale(item.spread).toFixed(2)}`)
    .join(" ");
  const last = records[records.length - 1];
  const first = records[0];
  return `${topPath} L ${xScale(parseDate(last.date).getTime()).toFixed(2)} ${bottom.toFixed(2)} L ${xScale(parseDate(first.date).getTime()).toFixed(2)} ${bottom.toFixed(2)} Z`;
}

function renderChart(records) {
  const { width, height, margin, yMin, yMax, xScale, yScale } = getChartContext(records);
  const activeRecord = getActiveRecord(records);

  svg.innerHTML = "";
  const defs = createSvgNode("defs");
  const gradient = createSvgNode("linearGradient", { id: "spreadArea", x1: "0%", y1: "0%", x2: "0%", y2: "100%" });
  gradient.appendChild(createSvgNode("stop", { offset: "0%", "stop-color": "#b45843", "stop-opacity": "0.38" }));
  gradient.appendChild(createSvgNode("stop", { offset: "100%", "stop-color": "#b45843", "stop-opacity": "0" }));
  defs.appendChild(gradient);
  svg.appendChild(defs);

  for (let i = 0; i < 5; i += 1) {
    const value = yMin + ((yMax - yMin) / 4) * i;
    const y = yScale(value);
    svg.appendChild(createSvgNode("line", {
      x1: margin.left,
      x2: width - margin.right,
      y1: y,
      y2: y,
      class: "grid-line"
    }));
    const label = createSvgNode("text", { x: 16, y: y + 4, class: "grid-label" });
    label.textContent = `${value.toFixed(1)}%`;
    svg.appendChild(label);
  }

  const xTicks = 6;
  for (let i = 0; i <= xTicks; i += 1) {
    const index = Math.round((records.length - 1) * (i / xTicks));
    const record = records[index];
    const x = xScale(parseDate(record.date).getTime());
    const line = createSvgNode("line", {
      x1: x,
      x2: x,
      y1: margin.top,
      y2: height - margin.bottom,
      class: "grid-line"
    });
    line.setAttribute("stroke-dasharray", "3 8");
    svg.appendChild(line);

    const label = createSvgNode("text", { x: x, y: height - 18, "text-anchor": "middle", class: "axis-text" });
    label.textContent = record.date;
    svg.appendChild(label);
  }

  svg.appendChild(createSvgNode("line", {
    x1: margin.left,
    x2: width - margin.right,
    y1: height - margin.bottom,
    y2: height - margin.bottom,
    class: "axis-line"
  }));

  if (state.visible.spread) {
    const bottom = height - margin.bottom;
    const spreadArea = createSvgNode("path", {
      d: buildSpreadArea(records, xScale, yScale, bottom),
      class: "series-area"
    });
    svg.appendChild(spreadArea);

    [["p20", "20% 分位", "quantile-p20"], ["p50", "50% 分位", "quantile-p50"], ["p80", "80% 分位", "quantile-p80"]]
      .forEach(([key, labelText, className], idx) => {
        const y = yScale(dataBundle.meta.spreadQuantiles[key]);
        svg.appendChild(createSvgNode("line", {
          x1: margin.left,
          x2: width - margin.right,
          y1: y,
          y2: y,
          class: `quantile-line ${className}`
        }));
        const label = createSvgNode("text", {
          x: width - margin.right + 10,
          y: y + (idx === 1 ? -6 : 4),
          class: "quantile-label"
        });
        label.textContent = `${labelText} ${formatPercent(dataBundle.meta.spreadQuantiles[key], 2)}`;
        svg.appendChild(label);
      });
  }

  for (const series of seriesCatalog) {
    if (!state.visible[series.key]) {
      continue;
    }
    const path = createSvgNode("path", {
      d: buildLinePath(records, series.key, xScale, yScale),
      class: `series-line ${series.className}`
    });
    svg.appendChild(path);
  }

  const activeX = xScale(parseDate(activeRecord.date).getTime());
  svg.appendChild(createSvgNode("line", {
    x1: activeX,
    x2: activeX,
    y1: margin.top,
    y2: height - margin.bottom,
    class: "focus-line"
  }));

  for (const series of seriesCatalog) {
    if (!state.visible[series.key]) {
      continue;
    }
    svg.appendChild(createSvgNode("circle", {
      cx: activeX,
      cy: yScale(activeRecord[series.key]),
      r: 5.2,
      fill: series.color,
      class: "focus-dot"
    }));
  }

  const overlay = createSvgNode("rect", {
    x: margin.left,
    y: margin.top,
    width: width - margin.left - margin.right,
    height: height - margin.top - margin.bottom,
    fill: "transparent"
  });

  overlay.addEventListener("mousemove", (event) => {
    const box = svg.getBoundingClientRect();
    const ratio = (event.clientX - box.left) / box.width;
    const svgX = ratio * width;
    let closest = records[0];
    let bestDistance = Infinity;
    for (const item of records) {
      const distance = Math.abs(xScale(parseDate(item.date).getTime()) - svgX);
      if (distance < bestDistance) {
        bestDistance = distance;
        closest = item;
      }
    }
    state.activeDate = closest.date;
    render();
    positionTooltip(event, closest);
  });

  overlay.addEventListener("mouseleave", () => {
    state.activeDate = dataBundle.meta.latest.date;
    tooltip.classList.add("is-hidden");
    render();
  });

  svg.appendChild(overlay);
}

function positionTooltip(event, record) {
  const frame = svg.parentElement.getBoundingClientRect();
  const x = Math.min(event.clientX - frame.left + 16, frame.width - 210);
  const y = Math.max(event.clientY - frame.top - 24, 18);

  tooltip.innerHTML = `
    <p class="tooltip-date">${formatDate(record.date)}</p>
    <div class="tooltip-row"><span>指数股息率</span><strong>${formatPercent(record.dividendYield, 2)}</strong></div>
    <div class="tooltip-row"><span>10Y 国债利率</span><strong>${formatPercent(record.treasuryYield, 2)}</strong></div>
    <div class="tooltip-row"><span>股债息差</span><strong>${formatPercent(record.spread, 2)}</strong></div>
  `;
  tooltip.style.left = `${x}px`;
  tooltip.style.top = `${y}px`;
  tooltip.classList.remove("is-hidden");
}

function render() {
  const records = getFilteredRecords();
  const activeRecord = getActiveRecord(records);
  updateReadout(activeRecord, records);
  renderChart(records);
}

rangeSwitch.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-range]");
  if (!button) {
    return;
  }
  state.range = button.dataset.range;
  rangeSwitch.querySelectorAll("button").forEach((node) => {
    node.classList.toggle("is-active", node === button);
  });
  state.activeDate = getFilteredRecords().at(-1).date;
  render();
});

buildHeroMeta();
buildLegend();
buildBenchmarks();
buildNotes();
render();
