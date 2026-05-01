from __future__ import annotations

import csv
import re
import time
from dataclasses import dataclass
from pathlib import Path

import requests
from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "2026Q1季报原文" / "整车公司_Sina原文"
INDEX_PATH = ROOT / "2026Q1季报原文" / "整车公司_report_index.csv"


@dataclass(frozen=True)
class VehicleCompany:
    code: str
    name: str
    segment: str
    h_code: str = ""


VEHICLE_COMPANIES: list[VehicleCompany] = [
    VehicleCompany("002594", "比亚迪", "乘用车", "01211"),
    VehicleCompany("601633", "长城汽车", "乘用车", "02333"),
    VehicleCompany("601238", "广汽集团", "乘用车", "02238"),
    VehicleCompany("000625", "长安汽车", "乘用车"),
    VehicleCompany("600104", "上汽集团", "乘用车"),
    VehicleCompany("601127", "赛力斯", "乘用车"),
    VehicleCompany("600418", "江淮汽车", "乘用车"),
    VehicleCompany("600733", "北汽蓝谷", "乘用车"),
    VehicleCompany("000572", "海马汽车", "乘用车"),
    VehicleCompany("000980", "众泰汽车", "乘用车"),
    VehicleCompany("000550", "江铃汽车", "商用车"),
    VehicleCompany("000800", "一汽解放", "商用车"),
    VehicleCompany("000951", "中国重汽", "商用车", "03808"),
    VehicleCompany("600006", "东风汽车", "商用车"),
    VehicleCompany("600066", "宇通客车", "商用车"),
    VehicleCompany("600166", "福田汽车", "商用车"),
    VehicleCompany("600375", "汉马科技", "商用车"),
    VehicleCompany("600686", "金龙汽车", "商用车"),
    VehicleCompany("000868", "安凯客车", "商用车"),
    VehicleCompany("000957", "中通客车", "商用车"),
    VehicleCompany("301039", "中集车辆", "商用车", "01839"),
]


HEADERS = {"User-Agent": "Mozilla/5.0"}


def safe_name(text: str) -> str:
    return re.sub(r'[<>:"/\\|?*]+', "_", text).strip()


def fetch_html(url: str, encoding: str = "gb18030") -> str:
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    response.encoding = encoding
    return response.text


def find_quarter_detail(code: str) -> tuple[str, str] | None:
    url = f"https://money.finance.sina.com.cn/corp/go.php/vCB_AllBulletin/stockid/{code}.phtml"
    html = fetch_html(url)
    pattern = re.compile(
        rf"/corp/view/vCB_AllBulletinDetail\.php\?stockid={code}&id=(\d+)'.*?>(.*?)</a>",
        re.S,
    )
    matches = []
    for bulletin_id, raw_title in pattern.findall(html):
        title = re.sub(r"<.*?>", "", raw_title).strip()
        if "2026" not in title:
            continue
        if not re.search(r"一季度|第一季度", title):
            continue
        matches.append((bulletin_id, title))
    return matches[0] if matches else None


def parse_detail(detail_url: str) -> tuple[str, str, str, str]:
    html = fetch_html(detail_url)
    soup = BeautifulSoup(html, "html.parser")
    content = soup.find(id="content")
    if content is None:
        raise RuntimeError("detail content not found")
    pdf_match = re.search(r"href='([^']+\.PDF)'", html, re.I)
    pdf_url = pdf_match.group(1) if pdf_match else ""
    date_match = re.search(r"公告日期[:：]\s*(\d{4}-\d{2}-\d{2})", html)
    announcement_date = date_match.group(1) if date_match else ""
    text = content.get_text("\n", strip=True)
    return pdf_url, text, html, announcement_date


def download_binary(url: str, path: Path) -> None:
    response = requests.get(url, headers=HEADERS, timeout=60)
    response.raise_for_status()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(response.content)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, str]] = []
    for idx, company in enumerate(VEHICLE_COMPANIES, 1):
        print(f"[{idx}/{len(VEHICLE_COMPANIES)}] {company.code} {company.name}")
        record = {
            "a_code": company.code,
            "h_code": company.h_code,
            "name": company.name,
            "segment": company.segment,
            "status": "missing",
            "title": "",
            "announcement_date": "",
            "sina_detail_url": "",
            "pdf_url": "",
            "pdf_path": "",
            "html_path": "",
            "txt_path": "",
            "note": "未在新浪公司公告页检索到2026Q1整车原文",
        }
        try:
            detail = find_quarter_detail(company.code)
            if detail is None:
                records.append(record)
                continue
            bulletin_id, title = detail
            detail_url = (
                "https://money.finance.sina.com.cn/corp/view/"
                f"vCB_AllBulletinDetail.php?id={bulletin_id}&stockid={company.code}"
            )
            pdf_url, text, html, date = parse_detail(detail_url)
            base_name = safe_name(f"{company.code}_{company.name}_{title}_{date}")
            pdf_path = OUT_DIR / f"{base_name}.pdf"
            html_path = OUT_DIR / f"{base_name}.html"
            txt_path = OUT_DIR / f"{base_name}.txt"
            if pdf_url:
                download_binary(pdf_url, pdf_path)
            html_path.write_text(html, encoding="utf-8")
            txt_path.write_text(text, encoding="utf-8")
            record.update(
                {
                    "status": "downloaded" if pdf_url else "text_only",
                    "title": title,
                    "announcement_date": date,
                    "sina_detail_url": detail_url,
                    "pdf_url": pdf_url,
                    "pdf_path": str(pdf_path.relative_to(ROOT)) if pdf_url else "",
                    "html_path": str(html_path.relative_to(ROOT)),
                    "txt_path": str(txt_path.relative_to(ROOT)),
                    "note": "" if pdf_url else "详情页可访问，但未解析到PDF链接",
                }
            )
        except Exception as exc:
            record["status"] = "error"
            record["note"] = repr(exc)
        records.append(record)
        time.sleep(0.2)

    with INDEX_PATH.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "a_code",
                "h_code",
                "name",
                "segment",
                "status",
                "title",
                "announcement_date",
                "sina_detail_url",
                "pdf_url",
                "pdf_path",
                "html_path",
                "txt_path",
                "note",
            ],
        )
        writer.writeheader()
        writer.writerows(records)

    downloaded = sum(item["status"] == "downloaded" for item in records)
    print(f"downloaded={downloaded}, total={len(records)}")


if __name__ == "__main__":
    main()
