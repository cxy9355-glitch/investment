from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse
import re

import pandas as pd
import requests


BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "raw" / "official"
SOURCE_FILE = BASE_DIR / "05_官方来源明细.csv"


def safe_name(value: str) -> str:
    value = re.sub(r"[\\\\/:*?\"<>|]", "_", value)
    value = re.sub(r"\s+", "_", value.strip())
    return value


def infer_suffix(url: str) -> str:
    path = urlparse(url).path.lower()
    if path.endswith(".pdf"):
        return ".pdf"
    if path.endswith(".htm") or path.endswith(".html"):
        return ".html"
    return ".txt"


def should_download(url: str) -> bool:
    if not url.startswith(("http://", "https://")):
        return False
    path = urlparse(url).path.lower()
    return path.endswith(".pdf") or path.endswith(".htm") or path.endswith(".html")


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(SOURCE_FILE)

    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "Codex Investment Research contact research@example.com",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf,*/*;q=0.8",
        }
    )

    for _, row in df.iterrows():
        url = str(row["官方来源"])
        if not should_download(url):
            continue

        suffix = infer_suffix(url)
        filename = f'{row["市场"]}_{row["代码"]}_{row["公司"]}_{int(row["年度"])}_{row["文件类型"]}{suffix}'
        target = RAW_DIR / safe_name(filename)
        if target.exists():
            print(f"skip {target.name}")
            continue

        try:
            response = session.get(url, timeout=60)
            response.raise_for_status()
            target.write_bytes(response.content)
            print(f"saved {target}")
        except Exception as exc:
            print(f"failed {url} -> {exc}")


if __name__ == "__main__":
    main()
