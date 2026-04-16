export async function loadJson(path) {
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(`Failed to load ${path}`);
  }
  return response.json();
}

export function formatNumber(value, digits = 2) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "--";
  }
  return Number(value).toLocaleString("zh-CN", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits
  });
}

export function formatPercent(value, digits = 2) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "--";
  }
  return `${formatNumber(value, digits)}%`;
}

export function formatCurrency(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "--";
  }
  const number = Number(value);
  if (Math.abs(number) >= 1e8) {
    return `${formatNumber(number / 1e8, 2)} 亿元`;
  }
  return `${number.toLocaleString("zh-CN", { maximumFractionDigits: 0 })} 元`;
}

export function getQueryParam(key) {
  const params = new URLSearchParams(window.location.search);
  return params.get(key);
}

export function createLinePath(values, width, height, padding) {
  if (!values.length) {
    return "";
  }
  const min = Math.min(...values);
  const max = Math.max(...values);
  const innerWidth = width - padding.left - padding.right;
  const innerHeight = height - padding.top - padding.bottom;
  const yRange = max - min || 1;
  return values
    .map((value, index) => {
      const x = padding.left + (innerWidth * index) / Math.max(values.length - 1, 1);
      const y = padding.top + innerHeight - ((value - min) / yRange) * innerHeight;
      return `${index === 0 ? "M" : "L"} ${x.toFixed(2)} ${y.toFixed(2)}`;
    })
    .join(" ");
}
