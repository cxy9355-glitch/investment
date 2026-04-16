import { formatNumber, formatPercent, loadJson } from "./utils.js";

const state = {
  methodology: "pool-share",
  sortKey: "rank",
  sortDirection: "asc",
  filters: {
    search: "",
    candidateOnly: false,
    peMax: null,
    pbMax: null,
    roeMin: null,
    currentValueMin: null
  },
  rankings: {},
  summary: null,
  metadata: null
};

const nodes = {
  methodSwitch: document.getElementById("methodSwitch"),
  methodDescription: document.getElementById("methodDescription"),
  updatedAt: document.getElementById("updatedAt"),
  tableBody: document.getElementById("tableBody"),
  resultSummary: document.getElementById("resultSummary"),
  featuredList: document.getElementById("featuredList")
};

function bindFilters() {
  document.getElementById("searchInput").addEventListener("input", (event) => {
    state.filters.search = event.target.value.trim().toLowerCase();
    render();
  });
  document.getElementById("candidateFilter").addEventListener("change", (event) => {
    state.filters.candidateOnly = event.target.value === "only";
    render();
  });
  document.getElementById("peFilter").addEventListener("input", (event) => {
    state.filters.peMax = event.target.value ? Number(event.target.value) : null;
    render();
  });
  document.getElementById("pbFilter").addEventListener("input", (event) => {
    state.filters.pbMax = event.target.value ? Number(event.target.value) : null;
    render();
  });
  document.getElementById("roeFilter").addEventListener("input", (event) => {
    state.filters.roeMin = event.target.value ? Number(event.target.value) : null;
    render();
  });
  document.getElementById("currentValueFilter").addEventListener("input", (event) => {
    state.filters.currentValueMin = event.target.value ? Number(event.target.value) : null;
    render();
  });
  document.getElementById("resetFilters").addEventListener("click", () => {
    document.getElementById("searchInput").value = "";
    document.getElementById("candidateFilter").value = "all";
    document.getElementById("peFilter").value = "";
    document.getElementById("pbFilter").value = "";
    document.getElementById("roeFilter").value = "";
    document.getElementById("currentValueFilter").value = "";
    state.filters = {
      search: "",
      candidateOnly: false,
      peMax: null,
      pbMax: null,
      roeMin: null,
      currentValueMin: null
    };
    render();
  });

  document.querySelectorAll("th[data-sort]").forEach((header) => {
    header.addEventListener("click", () => {
      const key = header.dataset.sort;
      if (state.sortKey === key) {
        state.sortDirection = state.sortDirection === "desc" ? "asc" : "desc";
      } else {
        state.sortKey = key;
        state.sortDirection = key === "name" ? "asc" : "desc";
      }
      render();
    });
  });
}

function renderMethodSwitch() {
  const definitions = state.metadata.definitions;
  nodes.methodSwitch.innerHTML = definitions
    .map(
      (item) => `
      <button type="button" class="method-pill ${state.methodology === item.key ? "is-active" : ""}" data-key="${item.key}">
        <strong>${item.label}</strong>
        <p>${item.summary}</p>
      </button>
    `
    )
    .join("");
  nodes.methodDescription.textContent = definitions.find(
    (item) => item.key === state.methodology
  )?.detail ?? "";
  nodes.methodSwitch.querySelectorAll("[data-key]").forEach((button) => {
    button.addEventListener("click", () => {
      state.methodology = button.dataset.key;
      state.sortKey = "rank";
      state.sortDirection = "asc";
      render();
    });
  });
}

function getFilteredRows() {
  const rows = state.rankings[state.methodology]?.rows ?? [];
  return rows.filter((row) => {
    if (state.filters.search) {
      const haystack = `${row.name} ${row.code}`.toLowerCase();
      if (!haystack.includes(state.filters.search)) {
        return false;
      }
    }
    if (state.filters.candidateOnly && !row.candidate) {
      return false;
    }
    if (state.filters.peMax !== null && (row.pePercentile ?? Infinity) > state.filters.peMax) {
      return false;
    }
    if (state.filters.pbMax !== null && (row.pbPercentile ?? Infinity) > state.filters.pbMax) {
      return false;
    }
    if (state.filters.roeMin !== null && (row.roe ?? -Infinity) < state.filters.roeMin) {
      return false;
    }
    if (
      state.filters.currentValueMin !== null &&
      (row.currentValue ?? -Infinity) < state.filters.currentValueMin
    ) {
      return false;
    }
    return true;
  });
}

function sortRows(rows) {
  const multiplier = state.sortDirection === "desc" ? -1 : 1;
  return [...rows].sort((left, right) => {
    const a = left[state.sortKey];
    const b = right[state.sortKey];
    if (state.sortKey === "name") {
      return left.name.localeCompare(right.name, "zh-CN") * multiplier;
    }
    if (typeof a === "boolean" || typeof b === "boolean") {
      return (Number(a) - Number(b)) * multiplier;
    }
    return ((a ?? -Infinity) - (b ?? -Infinity)) * multiplier;
  });
}

function renderTable(rows) {
  nodes.tableBody.innerHTML = rows
    .map(
      (row) => `
      <tr data-code="${row.code}">
        <td>${row.rank}</td>
        <td class="stock-cell"><strong>${row.name}</strong><span>${row.code}</span></td>
        <td>${formatPercent(row.currentValue, 2)}</td>
        <td>${formatPercent(row.cumulativeValue, 2)}</td>
        <td>${formatPercent(row.pePercentile, 2)}</td>
        <td>${formatPercent(row.pbPercentile, 2)}</td>
        <td>${formatPercent(row.roe, 2)}</td>
        <td>${formatPercent(row.roa, 2)}</td>
        <td>${formatPercent(row.roic, 2)}</td>
        <td>${formatPercent(row.grossMargin, 2)}</td>
        <td>${formatPercent(row.netMargin, 2)}</td>
        <td>${row.latestFundCount ?? "--"}</td>
        <td>${row.candidate ? '<span class="tag tag-positive">候选</span>' : '<span class="tag tag-neutral">观察</span>'}</td>
        <td>查看 ></td>
      </tr>
    `
    )
    .join("");

  nodes.tableBody.querySelectorAll("tr[data-code]").forEach((row) => {
    row.addEventListener("click", () => {
      window.location.href = `./stock.html?code=${row.dataset.code}`;
    });
  });
}

function renderFeatured() {
  nodes.featuredList.innerHTML = state.summary.featuredCodes
    .map((code) => {
      const row =
        state.rankings["pool-share"].rows.find((item) => item.code === code) ||
        state.rankings["float-ratio"].rows.find((item) => item.code === code);
      if (!row) {
        return "";
      }
      return `
        <a class="featured-link" href="./stock.html?code=${code}">
          <strong>${row.name}</strong>
          <span>${code}</span>
        </a>
      `;
    })
    .join("");
}

function render() {
  renderMethodSwitch();
  const rows = sortRows(getFilteredRows());
  renderTable(rows);
  nodes.resultSummary.textContent = `当前方法：${state.rankings[state.methodology].methodology.label} · 共 ${rows.length} 条结果`;
  nodes.updatedAt.textContent = `数据更新：${state.summary.updatedAt}`;
}

async function bootstrap() {
  const [summary, metadata, floatRatio, poolShare] = await Promise.all([
    loadJson("./data/dashboard-summary.json"),
    loadJson("./data/metadata/methodology.json"),
    loadJson("./data/rankings/float-ratio.json"),
    loadJson("./data/rankings/pool-share.json")
  ]);
  state.summary = summary;
  state.metadata = metadata;
  state.rankings = {
    "float-ratio": floatRatio,
    "pool-share": poolShare
  };
  renderFeatured();
  bindFilters();
  render();
}

bootstrap().catch((error) => {
  nodes.resultSummary.textContent = `载入失败：${error.message}`;
});
