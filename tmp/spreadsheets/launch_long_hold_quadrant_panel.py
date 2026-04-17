from __future__ import annotations

import argparse
import json
import socket
import threading
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd


ROOT = Path(r"G:\Codex\个人\investment")
WORKBOOK = ROOT / "机构持仓研究" / "巴芒_喜马拉雅_高瓴_长期持有审美分类总表_2026-04-17.xlsx"
HTML_PATH = ROOT / "机构持仓研究" / "长期持有审美四象限面板.html"


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


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
        "workbookPath": str(WORKBOOK),
        "records": records,
        "categories": categories,
        "markets": markets,
    }


class PanelHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path in {"/", "/index.html"}:
            self._send_html()
            return
        if parsed.path == "/data":
            self._send_json()
            return
        self.send_error(404, "Not Found")

    def log_message(self, format, *args):
        return

    def _send_html(self):
        content = HTML_PATH.read_text(encoding="utf-8")
        encoded = content.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _send_json(self):
        payload = json.dumps(load_panel_data(), ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def serve(port: int, open_browser: bool) -> None:
    server = ThreadingHTTPServer(("127.0.0.1", port), PanelHandler)
    url = f"http://127.0.0.1:{port}/"
    print(f"Quadrant panel running at: {url}")
    print(f"Workbook source: {WORKBOOK}")
    if open_browser:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping quadrant panel server...")
    finally:
        server.server_close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Launch long-hold quadrant panel")
    parser.add_argument("--port", type=int, default=0, help="Port to bind. Default: auto")
    parser.add_argument("--no-open", action="store_true", help="Do not open browser automatically")
    args = parser.parse_args()

    if not WORKBOOK.exists():
        raise FileNotFoundError(f"Workbook not found: {WORKBOOK}")
    if not HTML_PATH.exists():
        raise FileNotFoundError(f"HTML template not found: {HTML_PATH}")

    port = args.port or find_free_port()
    serve(port, open_browser=not args.no_open)


if __name__ == "__main__":
    main()
