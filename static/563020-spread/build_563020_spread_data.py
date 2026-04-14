#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""构建 563020 股息率与国债利率静态数据包。

当前脚本聚焦两件事：
1. 用中债官方接口拉取近 10 年中国 10 年期国债收益率。
2. 读取 H30269 股息率数据源，并标准化为页面需要的结构。

股息率数据源支持四种输入：
- 当前仓库里的 563020_spread_data.js
- 理杏仁页面导出的 pageData JSON
- 理杏仁的 dyr.js 原始脚本
- 乐咕乐股网页在浏览器上下文中加载的 index-basic 接口

这样做的目的，是把“数据抓取”和“页面消费”拆开。只要能拿到任一
H30269 原始数据文件，就能稳定重建页面数据包。
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import pathlib
import re
import statistics
from dataclasses import dataclass
from typing import Iterable
from urllib.parse import urlencode

import requests


ROOT = pathlib.Path(__file__).resolve().parent
DEFAULT_OUTPUT = ROOT / "563020_spread_data.js"
DEFAULT_EXISTING_BUNDLE = ROOT / "563020_spread_data.js"
CHINABOND_REFERER = (
    "https://indices.chinabond.com.cn/cbweb-mn/indices/single_index_query?locale=zh_CN"
)
CHINABOND_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
    ),
    "X-Requested-With": "XMLHttpRequest",
    "Referer": CHINABOND_REFERER,
}
CHINABOND_10Y_CURVE_ID = "2c9081e50a2f9606010a3068cae70001"
JS_ASSIGN_RE = re.compile(r"window\.__SPREAD_DATA__\s*=\s*(\{.*\})\s*;\s*$", re.S)
PAGE_DATA_RE = re.compile(r"window\.pageData\s*=\s*(\{.*\})\s*;\s*$", re.S)


@dataclass(frozen=True)
class DividendRecord:
    date: str
    dividend_yield: float
    close_point: float | None
    percentile: float | None


@dataclass(frozen=True)
class TreasuryRecord:
    date: str
    treasury_yield: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="构建 563020 股债息差静态数据")
    parser.add_argument(
        "--source",
        choices=["existing-bundle", "page-data-json", "lixinger-js", "legulegu-browser"],
        default="existing-bundle",
        help="H30269 股息率输入源类型",
    )
    parser.add_argument(
        "--input",
        type=pathlib.Path,
        default=DEFAULT_EXISTING_BUNDLE,
        help="输入文件路径",
    )
    parser.add_argument(
        "--output",
        type=pathlib.Path,
        default=DEFAULT_OUTPUT,
        help="输出 JS 文件路径",
    )
    parser.add_argument(
        "--start-date",
        default="2016-01-01",
        help="国债历史起始日期，格式 YYYY-MM-DD",
    )
    parser.add_argument(
        "--end-date",
        default=dt.date.today().isoformat(),
        help="国债历史结束日期，格式 YYYY-MM-DD",
    )
    return parser.parse_args()


def read_text(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def load_existing_bundle(path: pathlib.Path) -> list[DividendRecord]:
    content = read_text(path)
    match = JS_ASSIGN_RE.search(content)
    if not match:
        raise ValueError(f"无法从现有数据包解析 JSON: {path}")
    payload = json.loads(match.group(1))
    records: list[DividendRecord] = []
    for item in payload["records"]:
        records.append(
            DividendRecord(
                date=item["date"],
                dividend_yield=float(item["dividendYield"]),
                close_point=float(item["closePoint"]) if item.get("closePoint") is not None else None,
                percentile=float(item["dividendYieldPercentile"])
                if item.get("dividendYieldPercentile") is not None
                else None,
            )
        )
    return records


def load_page_data_json(path: pathlib.Path) -> list[DividendRecord]:
    payload = json.loads(read_text(path))
    return normalize_lixinger_page_data(payload)


def load_lixinger_js(path: pathlib.Path) -> list[DividendRecord]:
    content = read_text(path)
    match = PAGE_DATA_RE.search(content)
    if not match:
        raise ValueError(f"无法从理杏仁 JS 脚本解析 pageData: {path}")
    payload = json.loads(match.group(1))
    return normalize_lixinger_page_data(payload)


def normalize_lixinger_page_data(payload: dict) -> list[DividendRecord]:
    info = payload["priceMetricsChartInfo"]
    records: list[DividendRecord] = []
    for item in info["priceMetricsList"]:
        date = item["date"][:10]
        dyr = item["dyr"]["mcw"] * 100
        close_point = item.get("cp")
        percentile = (
            item.get("statistics", {})
            .get("dyr", {})
            .get("mcw", {})
            .get("cvpos")
        )
        records.append(
            DividendRecord(
                date=date,
                dividend_yield=round(float(dyr), 4),
                close_point=float(close_point) if close_point is not None else None,
                percentile=round(float(percentile) * 100, 4)
                if percentile is not None
                else None,
            )
        )
    records.sort(key=lambda item: item.date)
    return records


def load_legulegu_browser() -> list[DividendRecord]:
    """通过浏览器上下文读取乐咕乐股接口响应。

    乐咕乐股的匿名接口直接用 requests 往往只返回空体，但页面自身加载时会
    正常拿到 JSON。这里直接监听浏览器网络响应，拿到与页面一致的原始数据。
    当前选用 addDvTtm，原因是它与仓库现有 2023-2026 序列重合度最高，
    且口径上对应“加权股息率(TTM)”，更接近原页面的市值加权展示。
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError("缺少 playwright，无法使用 legulegu-browser 数据源") from exc

    url = "https://www.legulegu.com/stockdata/index-basic?indexCode=h30269.CSI"
    payload_holder: dict[str, str | None] = {"body": None}

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})

        def handle_response(response) -> None:
            if "api/stockdata/index-basic" in response.url and payload_holder["body"] is None:
                payload_holder["body"] = response.text()

        page.on("response", handle_response)
        page.goto(url, wait_until="networkidle", timeout=120000)
        page.wait_for_timeout(3000)
        browser.close()

    if not payload_holder["body"]:
        raise RuntimeError("未能从乐咕乐股页面捕获 index-basic 接口响应")

    payload = json.loads(payload_holder["body"])
    records: list[DividendRecord] = []
    for item in payload["data"]:
        value = item.get("addDvTtm")
        if value in (None, ""):
            continue
        records.append(
            DividendRecord(
                date=item["date"],
                dividend_yield=round(float(value), 4),
                close_point=float(item["close"]) if item.get("close") is not None else None,
                percentile=round(float(item["dvTtmQuantile"]) * 100, 4)
                if item.get("dvTtmQuantile") is not None
                else None,
            )
        )
    records.sort(key=lambda item: item.date)
    return records


def fetch_treasury_history(start_date: str, end_date: str) -> list[TreasuryRecord]:
    params = {
        "bjlx": "no",
        "dcq": "10,10y;",
        "startTime": start_date,
        "endTime": end_date,
        "qxlx": "0,",
        "yqqxN": "N",
        "yqqxK": "K",
        "par": "0",
        "ycDefIds": CHINABOND_10Y_CURVE_ID,
        "locale": "zh_CN",
    }
    url = (
        "https://indices.chinabond.com.cn/cbweb-mn/yc/queryYz?"
        + urlencode(params)
    )
    response = requests.post(url, headers=CHINABOND_HEADERS, timeout=30)
    response.raise_for_status()
    payload = response.json()
    if not payload or "seriesData" not in payload[0]:
        raise ValueError("中债接口返回结构异常")

    records: list[TreasuryRecord] = []
    for timestamp_ms, value in payload[0]["seriesData"]:
        date = dt.datetime.fromtimestamp(timestamp_ms / 1000, dt.UTC).date().isoformat()
        records.append(TreasuryRecord(date=date, treasury_yield=float(value)))
    records.sort(key=lambda item: item.date)
    return records


def align_records(
    dividend_records: Iterable[DividendRecord],
    treasury_records: Iterable[TreasuryRecord],
) -> list[dict]:
    treasury_map = {item.date: item for item in treasury_records}
    aligned: list[dict] = []
    for dividend in dividend_records:
        treasury = treasury_map.get(dividend.date)
        if treasury is None:
            continue
        spread = dividend.dividend_yield - treasury.treasury_yield
        aligned.append(
            {
                "date": dividend.date,
                "dividendYield": round(dividend.dividend_yield, 3),
                "treasuryYield": round(treasury.treasury_yield, 3),
                "spread": round(spread, 3),
                "closePoint": round(dividend.close_point, 2) if dividend.close_point is not None else None,
                "dividendYieldPercentile": dividend.percentile,
            }
        )
    return aligned


def compute_quantile(values: list[float], percentile: float) -> float:
    if not values:
        return math.nan
    if len(values) == 1:
        return values[0]
    ordered = sorted(values)
    idx = (len(ordered) - 1) * percentile
    lower = math.floor(idx)
    upper = math.ceil(idx)
    if lower == upper:
        return ordered[lower]
    weight = idx - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def calculate_midrank_percentile(values: list[float], target: float) -> float:
    lower_count = 0
    equal_count = 0
    for value in values:
        if value < target:
            lower_count += 1
        elif value == target:
            equal_count += 1
    return ((lower_count + equal_count / 2) / len(values)) * 100


def build_meta(records: list[dict], source_type: str) -> dict:
    if not records:
        raise ValueError("没有可用的重叠记录，无法构建页面数据包")
    spread_values = [item["spread"] for item in records]
    dividend_values = [item["dividendYield"] for item in records]
    latest = records[-1]
    latest_dividend_percentile = latest.get("dividendYieldPercentile")
    if latest_dividend_percentile is None:
        latest_dividend_percentile = calculate_midrank_percentile(
            dividend_values, latest["dividendYield"]
        )
        latest["dividendYieldPercentile"] = round(latest_dividend_percentile, 2)

    if source_type == "legulegu-browser":
        series_label = "中证红利低波动指数(H30269)加权股息率(TTM)"
        source_label = "乐咕乐股 H30269 加权股息率(TTM)"
        source_url = "https://www.legulegu.com/stockdata/index-basic?indexCode=h30269.CSI"
        notes = [
            "563020 跟踪中证红利低波动指数(H30269)。页面股息率当前取自乐咕乐股的加权股息率(TTM)口径。",
            "息差 = 指数股息率 - 中国 10 年期国债收益率。两条序列按重叠交易日对齐。",
            "10 年期国债收益率来自中债官方曲线接口；当前公开可稳定抓取的 H30269 日度股息率历史起点约为 2021-04-15。",
        ]
    else:
        series_label = "中证红利低波动指数(H30269)股息率，市值加权口径"
        source_label = "理杏仁 H30269 股息率（市值加权）"
        source_url = "https://www.lixinger.com/equity/index/detail/csi/H30269/1730269/fundamental/valuation/dyr?metrics-type=mcw"
        notes = [
            "563020 跟踪中证红利低波动指数(H30269)。页面中的股息率使用更贴近 ETF 整体暴露的市值加权口径。",
            "息差 = 指数股息率 - 中国 10 年期国债收益率。两条序列按重叠交易日对齐。",
            "国债收益率来自中债官方曲线接口；股息率数据可由理杏仁页面导出的 pageData 或现有数据包重建。",
        ]

    return {
        "title": "563020 红利低波 vs 10Y 国债利率",
        "seriesLabel": series_label,
        "productLabel": "易方达中证红利低波动ETF(563020)",
        "dateRange": {"start": records[0]["date"], "end": records[-1]["date"]},
        "latest": latest,
        "spreadPercentile": round(
            calculate_midrank_percentile(spread_values, latest["spread"]), 2
        ),
        "spreadQuantiles": {
            "p20": round(compute_quantile(spread_values, 0.2), 4),
            "p50": round(statistics.median(spread_values), 4),
            "p80": round(compute_quantile(spread_values, 0.8), 4),
        },
        "sources": [
            {
                "label": source_label,
                "url": source_url,
            },
            {
                "label": "中债 10 年期国债收益率曲线（官方接口）",
                "url": "https://indices.chinabond.com.cn/cbweb-mn/indices/single_index_query?locale=zh_CN",
            },
            {
                "label": "中证指数 H30269 官方 factsheet",
                "url": "https://oss-ch.csindex.com.cn/static/html/csindex/public/uploads/indices/detail/files/zh_CN/H30269factsheet.pdf",
            },
        ],
        "notes": notes,
    }


def write_bundle(path: pathlib.Path, meta: dict, records: list[dict]) -> None:
    payload = {"meta": meta, "records": records}
    serialized = json.dumps(payload, ensure_ascii=False, separators=(",", ": "))
    path.write_text(
        "window.__SPREAD_DATA__ = " + serialized + ";\n",
        encoding="utf-8",
    )


def main() -> None:
    args = parse_args()
    if args.source == "existing-bundle":
        dividend_records = load_existing_bundle(args.input)
    elif args.source == "page-data-json":
        dividend_records = load_page_data_json(args.input)
    elif args.source == "legulegu-browser":
        dividend_records = load_legulegu_browser()
    else:
        dividend_records = load_lixinger_js(args.input)

    treasury_records = fetch_treasury_history(args.start_date, args.end_date)
    records = align_records(dividend_records, treasury_records)
    meta = build_meta(records, args.source)
    write_bundle(args.output, meta, records)
    print(
        json.dumps(
            {
                "output": str(args.output),
                "recordCount": len(records),
                "dateRange": meta["dateRange"],
                "latest": meta["latest"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
