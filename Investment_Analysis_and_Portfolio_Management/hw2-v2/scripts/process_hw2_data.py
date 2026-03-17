#!/usr/bin/env python3
from __future__ import annotations

import csv
import re
import zipfile
from collections import OrderedDict
from datetime import datetime, timedelta
from pathlib import Path
import xml.etree.ElementTree as ET


MAIN_NS = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
REL_NS = {"r": "http://schemas.openxmlformats.org/package/2006/relationships"}
DOC_REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
EXCEL_EPOCH = datetime(1899, 12, 30)

BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = BASE_DIR / "processed"

FACTOR_CODE = "Z9999"
FACTOR_NAME = "上市＋上櫃"

ASSET_CONFIG = [
    {
        "file": "安聯台灣智慧.xlsx",
        "asset_id": "allianz",
        "asset_name": "安聯台灣智慧",
        "security": "AGCVBED TT Equity",
    },
    {
        "file": "街口台灣5年.xlsx",
        "asset_id": "jko",
        "asset_name": "街口台灣5年",
        "security": "CHTAIFD TT Equity",
    },
    {
        "file": "0050_5Y.xlsx",
        "asset_id": "0050",
        "asset_name": "0050 ETF",
        "security": "0050 TT Equity",
    },
]

FACTOR_CONFIG = [
    {
        "file": "市場因子.xlsx",
        "columns": [("市場風險溢酬", "MKT_RF"), ("無風險利率", "RF_ANN")],
    },
    {
        "file": "規模因子.xlsx",
        "columns": [("規模溢酬 (5因子)", "SMB")],
    },
    {
        "file": "淨值市價比因子.xlsx",
        "columns": [("淨值市價比溢酬", "HML_BM")],
    },
    {
        "file": "益本比因子.xlsx",
        "columns": [("益本比溢酬", "EP")],
    },
    {
        "file": "股利殖利率因子.xlsx",
        "columns": [("股利殖利率溢酬", "DY")],
    },
    {
        "file": "動能因子.xlsx",
        "columns": [("動能因子", "MOM")],
    },
]

FACTOR_FIELDNAMES = [
    "month_id",
    "factor_code",
    "factor_name",
    "RF_ANN",
    "RF",
    "MKT_RF",
    "SMB",
    "HML_BM",
    "EP",
    "DY",
    "MOM",
]


def get_shared_strings(workbook: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in workbook.namelist():
        return []

    root = ET.fromstring(workbook.read("xl/sharedStrings.xml"))
    strings: list[str] = []
    for shared_item in root.findall("a:si", MAIN_NS):
        text_parts = [node.text or "" for node in shared_item.iterfind(".//a:t", MAIN_NS)]
        strings.append("".join(text_parts))
    return strings


def get_first_sheet_path(workbook: zipfile.ZipFile) -> str:
    workbook_root = ET.fromstring(workbook.read("xl/workbook.xml"))
    first_sheet = workbook_root.find("a:sheets/a:sheet", MAIN_NS)
    if first_sheet is None:
        raise ValueError("Workbook does not contain any sheets.")

    relation_id = first_sheet.attrib.get(f"{{{DOC_REL_NS}}}id")
    if relation_id is None:
        raise ValueError("Could not resolve the first sheet relation id.")

    rels_root = ET.fromstring(workbook.read("xl/_rels/workbook.xml.rels"))
    for relationship in rels_root.findall("r:Relationship", REL_NS):
        if relationship.attrib.get("Id") == relation_id:
            target = relationship.attrib["Target"].lstrip("/")
            if target.startswith("xl/"):
                return target
            return f"xl/{target}"

    raise ValueError("Could not resolve the first sheet path.")


def col_ref_to_index(cell_ref: str) -> int:
    match = re.match(r"([A-Z]+)", cell_ref)
    if not match:
        raise ValueError(f"Invalid cell reference: {cell_ref}")

    column_label = match.group(1)
    column_index = 0
    for char in column_label:
        column_index = column_index * 26 + (ord(char) - 64)
    return column_index - 1


def parse_cell_value(cell: ET.Element, shared_strings: list[str]) -> str:
    cell_type = cell.attrib.get("t")

    if cell_type == "inlineStr":
        text_parts = [node.text or "" for node in cell.iterfind(".//a:t", MAIN_NS)]
        return "".join(text_parts)

    value_node = cell.find("a:v", MAIN_NS)
    if value_node is None:
        return ""

    raw_value = value_node.text or ""
    if cell_type == "s":
        return shared_strings[int(raw_value)]
    return raw_value


def read_first_sheet_rows(path: Path) -> list[list[str]]:
    with zipfile.ZipFile(path) as workbook:
        shared_strings = get_shared_strings(workbook)
        sheet_path = get_first_sheet_path(workbook)
        sheet_root = ET.fromstring(workbook.read(sheet_path))

    rows: list[list[str]] = []
    for row_node in sheet_root.findall(".//a:sheetData/a:row", MAIN_NS):
        row_values: list[str] = []
        for cell in row_node.findall("a:c", MAIN_NS):
            cell_ref = cell.attrib["r"]
            cell_index = col_ref_to_index(cell_ref)
            while len(row_values) <= cell_index:
                row_values.append("")
            row_values[cell_index] = parse_cell_value(cell, shared_strings)
        rows.append(row_values)
    return rows


def get_row_value(row: list[str], index: int) -> str:
    if index >= len(row):
        return ""
    return row[index]


def build_header_index(header_row: list[str], required_columns: list[str], source_name: str) -> dict[str, int]:
    header_index = {value: idx for idx, value in enumerate(header_row) if value}
    missing = [column for column in required_columns if column not in header_index]
    if missing:
        raise ValueError(f"{source_name} 缺少必要欄位: {missing}")
    return header_index


def excel_serial_to_date(serial_text: str) -> datetime.date:
    return (EXCEL_EPOCH + timedelta(days=float(serial_text))).date()


def to_float(raw_value: str) -> float | None:
    text = str(raw_value).strip()
    if not text or text in {"#N/A", "#N/A N/A"}:
        return None
    return float(text.replace(",", ""))


def month_id_from_date(obs_date: datetime.date) -> str:
    return obs_date.strftime("%Y-%m")


def month_id_from_factor(raw_month: str) -> str:
    return raw_month.replace("/", "-")


def format_value(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        text = f"{value:.10f}".rstrip("0").rstrip(".")
        return "0" if text == "-0" else text
    return str(value)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: format_value(row.get(key)) for key in fieldnames})


def process_asset(config: dict[str, str]) -> tuple[list[dict[str, object]], dict[str, object]]:
    raw_rows = read_first_sheet_rows(BASE_DIR / config["file"])
    if len(raw_rows) < 8:
        raise ValueError(f"{config['file']} 的列數不足。")

    metadata_security = get_row_value(raw_rows[0], 1)
    if metadata_security != config["security"]:
        raise ValueError(f"{config['file']} 的 Security 與預期不符: {metadata_security}")

    header_index = build_header_index(
        raw_rows[6],
        ["Date", "PX_LAST"],
        config["file"],
    )

    raw_records: list[dict[str, object]] = []
    for row in raw_rows[7:]:
        raw_date = get_row_value(row, header_index["Date"])
        raw_price = get_row_value(row, header_index["PX_LAST"])
        if not raw_date:
            continue

        price = to_float(raw_price)
        if price is None:
            continue

        obs_date = excel_serial_to_date(raw_date)
        raw_records.append(
            {
                "month_id": month_id_from_date(obs_date),
                "date": obs_date.isoformat(),
                "asset_id": config["asset_id"],
                "asset_name": config["asset_name"],
                "security": config["security"],
                "px_last": price,
            }
        )

    raw_records.sort(key=lambda row: row["date"])

    month_map: OrderedDict[str, dict[str, object]] = OrderedDict()
    for record in raw_records:
        month_map[record["month_id"]] = record

    cleaned_records = list(month_map.values())

    previous_price: float | None = None
    for record in cleaned_records:
        current_price = record["px_last"]
        if previous_price is None:
            record["ret"] = None
        else:
            record["ret"] = (current_price / previous_price - 1.0) * 100.0
        previous_price = current_price

    output_path = PROCESSED_DIR / f"asset_clean_{config['asset_id']}.csv"
    write_csv(
        output_path,
        ["month_id", "date", "asset_id", "asset_name", "security", "px_last", "ret"],
        cleaned_records,
    )

    summary = {
        "file": config["file"],
        "output": output_path.name,
        "asset_id": config["asset_id"],
        "rows": len(cleaned_records),
        "return_rows": sum(1 for row in cleaned_records if row["ret"] is not None),
        "start_month": cleaned_records[0]["month_id"],
        "end_month": cleaned_records[-1]["month_id"],
    }
    return cleaned_records, summary


def process_factors() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    factor_master: OrderedDict[str, dict[str, object]] = OrderedDict()
    expected_months: list[str] | None = None
    summaries: list[dict[str, object]] = []

    for config in FACTOR_CONFIG:
        raw_rows = read_first_sheet_rows(BASE_DIR / config["file"])
        required_columns = ["代號", "名稱", "年月"] + [source for source, _ in config["columns"]]
        header_index = build_header_index(raw_rows[0], required_columns, config["file"])

        selected_rows: list[dict[str, object]] = []
        for row in raw_rows[1:]:
            code = get_row_value(row, header_index["代號"])
            name = get_row_value(row, header_index["名稱"])
            if code != FACTOR_CODE or name != FACTOR_NAME:
                continue

            month_id = month_id_from_factor(get_row_value(row, header_index["年月"]))
            factor_row: dict[str, object] = {"month_id": month_id}

            for source_column, target_column in config["columns"]:
                factor_value = to_float(get_row_value(row, header_index[source_column]))
                if factor_value is None:
                    raise ValueError(f"{config['file']} 在 {month_id} 的 {source_column} 為空值。")
                factor_row[target_column] = factor_value

            selected_rows.append(factor_row)

        selected_rows.sort(key=lambda row: row["month_id"])

        deduped_rows: OrderedDict[str, dict[str, object]] = OrderedDict()
        for row in selected_rows:
            month_id = row["month_id"]
            if month_id in deduped_rows:
                raise ValueError(f"{config['file']} 的 {month_id} 出現重複資料。")
            deduped_rows[month_id] = row

        month_list = list(deduped_rows.keys())
        if len(month_list) != 60:
            raise ValueError(f"{config['file']} 篩選後應為 60 期，實際為 {len(month_list)} 期。")

        if expected_months is None:
            expected_months = month_list
            for month_id in month_list:
                factor_master[month_id] = {
                    "month_id": month_id,
                    "factor_code": FACTOR_CODE,
                    "factor_name": FACTOR_NAME,
                }
        elif month_list != expected_months:
            raise ValueError(f"{config['file']} 的月份序列與其他因子檔不一致。")

        for month_id, factor_row in deduped_rows.items():
            for _, target_column in config["columns"]:
                factor_master[month_id][target_column] = factor_row[target_column]

        summaries.append(
            {
                "file": config["file"],
                "rows": len(deduped_rows),
                "start_month": month_list[0],
                "end_month": month_list[-1],
                "columns": ", ".join(target for _, target in config["columns"]),
            }
        )

    if expected_months is None:
        raise ValueError("沒有讀到任何因子資料。")

    factor_rows = [factor_master[month_id] for month_id in expected_months]
    for factor_row in factor_rows:
        factor_row["RF"] = factor_row["RF_ANN"] / 12.0
    write_csv(PROCESSED_DIR / "factor_clean.csv", FACTOR_FIELDNAMES, factor_rows)
    return factor_rows, summaries


def build_regression_master(
    factor_rows: list[dict[str, object]],
    asset_rows_map: dict[str, list[dict[str, object]]],
) -> list[dict[str, object]]:
    merged_rows: OrderedDict[str, dict[str, object]] = OrderedDict()

    for factor_row in factor_rows:
        merged_rows[factor_row["month_id"]] = {
            "month_id": factor_row["month_id"],
            "factor_code": factor_row["factor_code"],
            "factor_name": factor_row["factor_name"],
            "RF_ANN": factor_row["RF_ANN"],
            "RF": factor_row["RF"],
            "MKT_RF": factor_row["MKT_RF"],
            "SMB": factor_row["SMB"],
            "HML_BM": factor_row["HML_BM"],
            "EP": factor_row["EP"],
            "DY": factor_row["DY"],
            "MOM": factor_row["MOM"],
        }

    asset_order = ["allianz", "jko", "0050"]
    for asset_id in asset_order:
        return_column = f"ret_{asset_id}"
        excess_column = f"excess_{asset_id}"
        for row in merged_rows.values():
            row[return_column] = None
            row[excess_column] = None

        for asset_row in asset_rows_map[asset_id]:
            month_id = asset_row["month_id"]
            if month_id not in merged_rows:
                continue

            merged_rows[month_id][return_column] = asset_row["ret"]
            rf_value = merged_rows[month_id]["RF"]
            if asset_row["ret"] is not None and rf_value is not None:
                merged_rows[month_id][excess_column] = asset_row["ret"] - rf_value

    regression_rows: list[dict[str, object]] = []
    required_columns = [
        "RF",
        "MKT_RF",
        "SMB",
        "HML_BM",
        "EP",
        "DY",
        "MOM",
        "ret_allianz",
        "ret_jko",
        "ret_0050",
        "excess_allianz",
        "excess_jko",
        "excess_0050",
    ]

    for row in merged_rows.values():
        if all(row[column] is not None for column in required_columns):
            regression_rows.append(row)

    fieldnames = [
        "month_id",
        "factor_code",
        "factor_name",
        "RF_ANN",
        "RF",
        "MKT_RF",
        "SMB",
        "HML_BM",
        "EP",
        "DY",
        "MOM",
        "ret_allianz",
        "ret_jko",
        "ret_0050",
        "excess_allianz",
        "excess_jko",
        "excess_0050",
    ]
    write_csv(PROCESSED_DIR / "regression_master.csv", fieldnames, regression_rows)
    return regression_rows


def write_processing_summary(
    asset_summaries: list[dict[str, object]],
    factor_summaries: list[dict[str, object]],
    regression_rows: list[dict[str, object]],
) -> None:
    summary_lines = [
        "# Processing Summary",
        "",
        f"- Factor version: `{FACTOR_CODE} / {FACTOR_NAME}`",
        "- RF treatment: `RF = RF_ANN / 12`",
        f"- Regression sample rows: `{len(regression_rows)}`",
        (
            f"- Regression sample range: `{regression_rows[0]['month_id']}` to "
            f"`{regression_rows[-1]['month_id']}`"
            if regression_rows
            else "- Regression sample range: `N/A`"
        ),
        "",
        "## Asset Outputs",
        "",
    ]

    for summary in asset_summaries:
        summary_lines.append(
            (
                f"- `{summary['output']}`: {summary['rows']} rows, "
                f"{summary['start_month']} to {summary['end_month']}, "
                f"valid returns {summary['return_rows']} rows"
            )
        )

    summary_lines.extend(["", "## Factor Outputs", ""])

    for summary in factor_summaries:
        summary_lines.append(
            (
                f"- `{summary['file']}` -> {summary['columns']}: {summary['rows']} rows, "
                f"{summary['start_month']} to {summary['end_month']}"
            )
        )

    summary_lines.extend(
        [
            "",
            "## Final Files",
            "",
            "- `factor_clean.csv`",
            "- `regression_master.csv`",
        ]
    )

    summary_path = PROCESSED_DIR / "processing_summary.md"
    summary_path.write_text("\n".join(summary_lines), encoding="utf-8")


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    asset_rows_map: dict[str, list[dict[str, object]]] = {}
    asset_summaries: list[dict[str, object]] = []
    for config in ASSET_CONFIG:
        cleaned_rows, summary = process_asset(config)
        asset_rows_map[config["asset_id"]] = cleaned_rows
        asset_summaries.append(summary)

    factor_rows, factor_summaries = process_factors()
    regression_rows = build_regression_master(factor_rows, asset_rows_map)
    write_processing_summary(asset_summaries, factor_summaries, regression_rows)

    print("Processed files written to:", PROCESSED_DIR)
    print("Factor version:", f"{FACTOR_CODE} / {FACTOR_NAME}")
    print("Regression rows:", len(regression_rows))
    if regression_rows:
        print("Regression range:", regression_rows[0]["month_id"], "to", regression_rows[-1]["month_id"])


if __name__ == "__main__":
    main()
