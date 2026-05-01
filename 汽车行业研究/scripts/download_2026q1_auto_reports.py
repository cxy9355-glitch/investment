from __future__ import annotations

import csv
import re
import time
from dataclasses import dataclass
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "2026Q1季报原文" / "A股_CNINFO"
INDEX_PATH = ROOT / "2026Q1季报原文" / "report_index.csv"


@dataclass(frozen=True)
class Stock:
    code: str
    name: str
    segment: str
    h_code: str = ""


STOCKS: list[Stock] = [
    Stock("002594", "比亚迪", "乘用车", "01211"),
    Stock("601633", "长城汽车", "乘用车", "02333"),
    Stock("601238", "广汽集团", "乘用车", "02238"),
    Stock("000625", "长安汽车", "乘用车"),
    Stock("600104", "上汽集团", "乘用车"),
    Stock("601127", "赛力斯", "乘用车"),
    Stock("600418", "江淮汽车", "乘用车"),
    Stock("600733", "北汽蓝谷", "乘用车"),
    Stock("000572", "海马汽车", "乘用车"),
    Stock("000980", "众泰汽车", "乘用车"),
    Stock("000550", "江铃汽车", "商用车"),
    Stock("000800", "一汽解放", "商用车"),
    Stock("000951", "中国重汽", "商用车", "03808"),
    Stock("600006", "东风汽车", "商用车"),
    Stock("600066", "宇通客车", "商用车"),
    Stock("600166", "福田汽车", "商用车"),
    Stock("600375", "汉马科技", "商用车"),
    Stock("600686", "金龙汽车", "商用车"),
    Stock("000868", "安凯客车", "商用车"),
    Stock("000957", "中通客车", "商用车"),
    Stock("301039", "中集车辆", "商用车", "01839"),
    Stock("000338", "潍柴动力", "动力总成", "02338"),
    Stock("600660", "福耀玻璃", "汽车玻璃", "03606"),
    Stock("600741", "华域汽车", "汽车零部件"),
    Stock("600699", "均胜电子", "汽车电子"),
    Stock("000581", "威孚高科", "动力总成"),
    Stock("000887", "中鼎股份", "汽车零部件"),
    Stock("000559", "万向钱潮", "汽车零部件"),
    Stock("002048", "宁波华翔", "汽车零部件"),
    Stock("002050", "三花智控", "热管理"),
    Stock("002126", "银轮股份", "热管理"),
    Stock("002284", "亚太股份", "制动系统"),
    Stock("002406", "远东传动", "汽车零部件"),
    Stock("002472", "双环传动", "传动系统"),
    Stock("002536", "飞龙股份", "热管理"),
    Stock("002590", "万安科技", "制动系统"),
    Stock("002662", "京威股份", "汽车零部件"),
    Stock("002906", "华阳集团", "汽车电子"),
    Stock("002920", "德赛西威", "智能座舱/智驾"),
    Stock("300100", "双林股份", "汽车零部件"),
    Stock("300258", "精锻科技", "传动系统"),
    Stock("300304", "云意电气", "汽车电子"),
    Stock("300432", "富临精工", "汽车零部件"),
    Stock("300580", "贝斯特", "汽车零部件"),
    Stock("300680", "隆盛科技", "汽车零部件"),
    Stock("301181", "标榜股份", "热管理"),
    Stock("301215", "中汽股份", "汽车服务"),
    Stock("601689", "拓普集团", "汽车零部件"),
    Stock("603009", "北特科技", "汽车零部件"),
    Stock("603035", "常熟汽饰", "内外饰"),
    Stock("603089", "正裕工业", "汽车零部件"),
    Stock("603179", "新泉股份", "内外饰"),
    Stock("603197", "保隆科技", "汽车电子"),
    Stock("603305", "旭升集团", "汽车零部件"),
    Stock("603306", "华懋科技", "汽车零部件"),
    Stock("603319", "湘油泵", "动力总成"),
    Stock("603358", "华达科技", "汽车零部件"),
    Stock("603596", "伯特利", "制动系统"),
    Stock("603730", "岱美股份", "内外饰"),
    Stock("603786", "科博达", "汽车电子"),
    Stock("603997", "继峰股份", "座椅/内饰"),
    Stock("605128", "上海沿浦", "座椅/内饰"),
    Stock("605133", "嵘泰股份", "汽车零部件"),
    Stock("605333", "沪光股份", "线束"),
    Stock("688533", "上声电子", "汽车电子"),
]


def fetch_all_cninfo_q1_announcements() -> dict[str, list[dict[str, object]]]:
    url = "http://www.cninfo.com.cn/new/hisAnnouncement/query"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "http://www.cninfo.com.cn/new/commonUrl/pageOfSearch?url=disclosure/list/search",
    }
    by_code: dict[str, list[dict[str, object]]] = {}
    page_num = 1
    page_size = 30
    while True:
        data = {
            "pageNum": str(page_num),
            "pageSize": str(page_size),
            "column": "szse",
            "tabName": "fulltext",
            "plate": "",
            "stock": "",
            "searchkey": "",
            "secid": "",
            "category": "category_yjdbg_szsh",
            "trade": "",
            "seDate": "2026-04-01~2026-05-01",
            "sortName": "",
            "sortType": "",
            "isHLtitle": "true",
        }
        response = requests.post(url, data=data, headers=headers, timeout=60)
        response.raise_for_status()
        payload = response.json()
        announcements = payload.get("announcements") or []
        if not announcements:
            break
        for item in announcements:
            code = str(item.get("secCode") or "").strip()
            if code:
                by_code.setdefault(code, []).append(item)
        total = int(payload.get("totalRecordNum") or 0)
        if page_num * page_size >= total:
            break
        page_num += 1
        time.sleep(0.15)
    return by_code


def safe_name(text: str) -> str:
    return re.sub(r'[<>:"/\\|?*]+', "_", text).strip()


def fetch_cninfo_report(stock: Stock, announcements_by_code: dict[str, list[dict[str, object]]]) -> dict[str, str]:
    rows = announcements_by_code.get(stock.code, [])
    if not rows:
        return {"status": "missing", "note": "CNINFO未检索到2026Q1一季报"}

    rows = [
        item
        for item in rows
        if "2026" in str(item.get("announcementTitle") or "")
        and re.search("一季度|第一季度", str(item.get("announcementTitle") or ""))
    ]
    if not rows:
        return {"status": "missing", "note": "仅检索到非2026Q1标题"}

    row = sorted(rows, key=lambda item: int(item.get("announcementTime") or 0), reverse=True)[0]
    announcement_id = str(row.get("announcementId") or "")
    title = str(row.get("announcementTitle") or "")
    adjunct_url = str(row.get("adjunctUrl") or "")
    date_match = re.search(r"finalpage/(\d{4}-\d{2}-\d{2})/", adjunct_url)
    announcement_date = date_match.group(1) if date_match else ""
    if not announcement_id or not announcement_date:
        return {"status": "error", "note": "公告记录缺少announcementId或adjunctUrl日期"}

    pdf_url = f"http://static.cninfo.com.cn/{adjunct_url}"
    source_url = (
        "http://www.cninfo.com.cn/new/disclosure/detail"
        f"?stockCode={stock.code}&announcementId={announcement_id}"
        f"&orgId={row.get('orgId')}&announcementTime={announcement_date}"
    )
    file_name = safe_name(f"{stock.code}_{stock.name}_{title}_{announcement_date}.PDF")
    local_path = OUT_DIR / file_name
    download_pdf(pdf_url, local_path)
    return {
        "status": "downloaded",
        "title": title,
        "announcement_date": announcement_date,
        "announcement_id": announcement_id,
        "source_url": source_url,
        "pdf_url": pdf_url,
        "local_path": str(local_path.relative_to(ROOT)),
        "note": "",
    }


def download_pdf(url: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "http://www.cninfo.com.cn/",
    }
    response = requests.get(url, headers=headers, timeout=60)
    response.raise_for_status()
    if not response.content.startswith(b"%PDF"):
        raise RuntimeError(f"not a pdf response: {url}")
    path.write_bytes(response.content)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    announcements_by_code = fetch_all_cninfo_q1_announcements()
    records: list[dict[str, str]] = []
    for idx, stock in enumerate(STOCKS, 1):
        print(f"[{idx}/{len(STOCKS)}] {stock.code} {stock.name}")
        base = {
            "a_code": stock.code,
            "h_code": stock.h_code,
            "name": stock.name,
            "segment": stock.segment,
        }
        try:
            result = fetch_cninfo_report(stock, announcements_by_code)
        except Exception as exc:
            result = {"status": "error", "note": repr(exc)}
        records.append({**base, **result})
        time.sleep(0.25)

    fieldnames = [
        "a_code",
        "h_code",
        "name",
        "segment",
        "status",
        "title",
        "announcement_date",
        "announcement_id",
        "source_url",
        "pdf_url",
        "local_path",
        "note",
    ]
    with INDEX_PATH.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    downloaded = sum(item["status"] == "downloaded" for item in records)
    print(f"downloaded={downloaded}, total={len(records)}, index={INDEX_PATH}")


if __name__ == "__main__":
    main()
