from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = BASE_DIR / "data" / "饮料可比公司_横向对比数据表_第一版.csv"
CHART_DIR = BASE_DIR / "charts"


def pct(series: pd.Series) -> pd.Series:
    return series.astype(float) * 100


def setup_chart(title: str, ylabel: str) -> None:
    plt.figure(figsize=(12, 7))
    plt.title(title, fontname="Microsoft YaHei", fontsize=14)
    plt.xlabel("年度", fontname="Microsoft YaHei")
    plt.ylabel(ylabel, fontname="Microsoft YaHei")
    plt.grid(True, axis="y", linestyle="--", alpha=0.3)


def save_chart(name: str) -> None:
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(CHART_DIR / name, dpi=160)
    plt.close()


def render_metric(df: pd.DataFrame, metric: str, title: str, ylabel: str, percent: bool = False) -> None:
    usable = df.dropna(subset=[metric]).copy()
    if usable.empty:
        return

    setup_chart(title, ylabel)
    for company, sub_df in usable.groupby("公司"):
        sub_df = sub_df.sort_values("年度")
        y = pct(sub_df[metric]) if percent else sub_df[metric].astype(float)
        plt.plot(sub_df["年度"], y, marker="o", linewidth=2, label=company)
    plt.legend(prop={"family": "Microsoft YaHei", "size": 9})


def main() -> None:
    df = pd.read_csv(DATA_FILE)

    render_metric(df, "营业收入", "可比公司营业收入", "营业收入")
    save_chart("01_营业收入.png")

    render_metric(df, "归母净利润", "可比公司归母净利润", "归母净利润")
    save_chart("02_归母净利润.png")

    render_metric(df, "毛利率", "可比公司毛利率", "毛利率（%）", percent=True)
    save_chart("03_毛利率.png")

    render_metric(df, "归母净利率", "可比公司归母净利率", "归母净利率（%）", percent=True)
    save_chart("04_归母净利率.png")

    render_metric(df, "ROE", "可比公司ROE", "ROE（%）", percent=True)
    save_chart("05_ROE.png")

    render_metric(df, "销售费用率", "可比公司销售费用率", "销售费用率（%）", percent=True)
    save_chart("06_销售费用率.png")


if __name__ == "__main__":
    main()
