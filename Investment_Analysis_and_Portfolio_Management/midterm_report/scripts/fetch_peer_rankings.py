#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import csv
import re
from urllib.parse import urlencode

import requests


BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_PATH = BASE_DIR / "analysis_outputs" / "tables" / "peer_ranking_summary.csv"

BASE_URL = "https://www.sitca.org.tw/ROC/Industry/IN240201.aspx"

FUNDS = [
    {
        "fund_name": "統一奔騰基金",
        "category": "股票型/投資國內/科技類",
        "class_code": "1110",
        "menu2": "1",
        "match_text": "統一奔騰基金",
    },
    {
        "fund_name": "野村成長基金",
        "category": "股票型/投資國內/一般股票型",
        "class_code": "1140",
        "menu2": "4",
        "match_text": "野村成長基金",
    },
    {
        "fund_name": "國泰台灣 ESG 永續高股息 ETF (00878)",
        "category": "股票型/投資國內/指數股票型/一般型ETF/高股息ETF",
        "class_code": "1161C",
        "menu2": "9",
        "match_text": "台灣ESG永續高股息ETF基金",
    },
]

WINDOWS = [
    ("1Y", "FCS_1Y", 3),
    ("3Y", "FCS_3Y", 5),
    ("5Y", "FCS_5Y", 6),
]

ROW_RE = re.compile(r'<tr class="DT(?:odd|even)">(.*?)</tr>', re.S)
TD_RE = re.compile(r'<td style="text-align:Left;">(.*?)</td>')
TAG_RE = re.compile(r"<[^>]+>")


def clean_html_text(value: str) -> str:
    return TAG_RE.sub("", value).replace("&nbsp;", " ").strip()


def extract_rows(url: str) -> list[tuple[str, list[str]]]:
    html = requests.get(url, timeout=20).text
    rows: list[tuple[str, list[str]]] = []
    for block in ROW_RE.findall(html):
        cells = TD_RE.findall(block)
        if not cells:
            continue
        name = clean_html_text(cells[0])
        values = [clean_html_text(cell) for cell in cells[1:]]
        if name:
            rows.append((name, values))
    return rows


def build_url(class_code: str, menu2: str, orderby: str) -> str:
    params = {
        "txtFCS_CLASS": class_code,
        "txtMONTH": "02",
        "txtNFC_MENU1": "1",
        "txtNFC_MENU2": menu2,
        "txtYEAR": "2026",
        "txtOrderby": orderby,
        "txtchkList": "",
    }
    return f"{BASE_URL}?{urlencode(params)}"


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, object]] = []

    for fund in FUNDS:
        for window, orderby, value_col_idx in WINDOWS:
            url = build_url(fund["class_code"], fund["menu2"], orderby)
            rows = extract_rows(url)
            total = len(rows)

            rank = None
            official_return = None
            for idx, (name, values) in enumerate(rows, start=1):
                if fund["match_text"] in name:
                    rank = idx
                    official_return = values[value_col_idx - 1]
                    break

            if rank is None:
                raise ValueError(f"Could not find {fund['fund_name']} in {url}")

            records.append(
                {
                    "fund_name": fund["fund_name"],
                    "category": fund["category"],
                    "observation_month": "2026-02",
                    "window": window,
                    "rank": rank,
                    "total_funds": total,
                    "percentile_pct": rank / total * 100.0,
                    "official_return_pct": official_return,
                    "source_url": url,
                }
            )

    with OUTPUT_PATH.open("w", encoding="utf-8", newline="") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=[
                "fund_name",
                "category",
                "observation_month",
                "window",
                "rank",
                "total_funds",
                "percentile_pct",
                "official_return_pct",
                "source_url",
            ],
        )
        writer.writeheader()
        writer.writerows(records)


if __name__ == "__main__":
    main()
