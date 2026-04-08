#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import math

import numpy as np
import pandas as pd
import statsmodels.api as sm


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "analysis_outputs"
TABLE_DIR = OUTPUT_DIR / "tables"
REPORT_PATH = OUTPUT_DIR / "midterm_analysis_report.md"


@dataclass(frozen=True)
class FundConfig:
    fund_id: str
    fund_name: str
    fund_type: str
    monthly_path: Path
    holdings_path: Path


FUNDS = [
    FundConfig(
        fund_id="cathay_esg",
        fund_name="國泰台灣 ESG 永續高股息 ETF (00878)",
        fund_type="Passive ETF",
        monthly_path=DATA_DIR / "cathay_esg_00878" / "monthly_total_return_index_2020-07_to_2026-03.xlsx",
        holdings_path=DATA_DIR / "cathay_esg_00878" / "holdings_breakdown.xlsx",
    ),
    FundConfig(
        fund_id="uni_penta",
        fund_name="統一奔騰基金",
        fund_type="Active Fund",
        monthly_path=DATA_DIR / "uni_penta" / "monthly_total_return_index_2020-03_to_2026-03.xlsx",
        holdings_path=DATA_DIR / "uni_penta" / "holdings_breakdown.xlsx",
    ),
    FundConfig(
        fund_id="nomura_growth",
        fund_name="野村成長基金",
        fund_type="Active Fund",
        monthly_path=DATA_DIR / "nomura_growth" / "monthly_total_return_index_2020-03_to_2026-03.xlsx",
        holdings_path=DATA_DIR / "nomura_growth" / "holdings_breakdown.xlsx",
    ),
]

FACTOR_PATH = DATA_DIR / "tej_carhart_4factor_monthly_2020-01_to_2026-03.csv"

COMMON_START_MONTH = "2020-08"
COMMON_END_MONTH = "2026-03"
REG_START_MONTH = "2021-04"
REG_END_MONTH = "2026-03"


def ensure_dirs() -> None:
    TABLE_DIR.mkdir(parents=True, exist_ok=True)


def format_month(month_value: pd.Timestamp) -> str:
    return month_value.strftime("%Y-%m")


def load_monthly_fund(config: FundConfig) -> pd.DataFrame:
    raw = pd.read_excel(config.monthly_path, skiprows=6)
    df = raw.rename(
        columns={
            "Date": "date",
            "TOT_RETURN_INDEX_GROSS_DVDS": "tri",
            "PX_LAST": "px_last",
        }
    ).copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    df["month"] = df["date"].dt.to_period("M").dt.to_timestamp("M")
    df["month_id"] = df["month"].dt.strftime("%Y-%m")
    df["monthly_return"] = df["tri"].pct_change()
    df["monthly_return_pct"] = df["monthly_return"] * 100.0
    df["fund_id"] = config.fund_id
    df["fund_name"] = config.fund_name
    df["fund_type"] = config.fund_type
    return df[
        [
            "fund_id",
            "fund_name",
            "fund_type",
            "date",
            "month",
            "month_id",
            "tri",
            "px_last",
            "monthly_return",
            "monthly_return_pct",
        ]
    ]


def load_factors() -> pd.DataFrame:
    df = pd.read_csv(FACTOR_PATH, encoding="utf-8")
    df = df.rename(
        columns={
            "年月": "yyyymm",
            "市場風險溢酬": "mkt_rf",
            "規模溢酬 (3因子)": "smb",
            "淨值市價比溢酬": "hml",
            "動能因子": "mom",
            "無風險利率": "rf_ann",
        }
    ).copy()
    numeric_cols = ["mkt_rf", "smb", "hml", "mom", "rf_ann"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="raise")
    df["month"] = pd.PeriodIndex(df["yyyymm"].astype(str), freq="M").to_timestamp("M")
    df["month_id"] = df["month"].dt.strftime("%Y-%m")
    df["rf_month_pct"] = df["rf_ann"] / 12.0
    return df[["month", "month_id", "mkt_rf", "smb", "hml", "mom", "rf_ann", "rf_month_pct"]].sort_values("month")


def merge_with_factors(fund_frames: list[pd.DataFrame], factor_df: pd.DataFrame) -> pd.DataFrame:
    merged = pd.concat(fund_frames, ignore_index=True)
    merged = merged.merge(factor_df, on=["month", "month_id"], how="left", validate="many_to_one")
    if merged[["mkt_rf", "smb", "hml", "mom", "rf_month_pct"]].isna().any().any():
        missing = merged.loc[merged["mkt_rf"].isna(), ["fund_name", "month_id"]]
        raise ValueError(f"Missing factor rows for merged data:\n{missing}")
    merged["excess_return_pct"] = merged["monthly_return_pct"] - merged["rf_month_pct"]
    merged["excess_return"] = merged["excess_return_pct"] / 100.0
    return merged


def compute_window_metrics(window_df: pd.DataFrame, label: str) -> dict[str, object]:
    returns = window_df["monthly_return"].dropna()
    excess = window_df.loc[returns.index, "excess_return"]
    wealth = (1.0 + returns).cumprod()
    drawdown = wealth / wealth.cummax() - 1.0
    n_months = len(returns)
    cumulative_return = wealth.iloc[-1] - 1.0
    annualized_return = (1.0 + cumulative_return) ** (12.0 / n_months) - 1.0
    annualized_vol = returns.std(ddof=1) * math.sqrt(12.0)
    sharpe = np.nan if annualized_vol == 0 else (excess.mean() * 12.0) / annualized_vol
    return {
        "window": label,
        "start_month": format_month(window_df["month"].iloc[0]),
        "end_month": format_month(window_df["month"].iloc[-1]),
        "return_obs": n_months,
        "cumulative_return_pct": cumulative_return * 100.0,
        "annualized_return_pct": annualized_return * 100.0,
        "annualized_volatility_pct": annualized_vol * 100.0,
        "sharpe_ratio": sharpe,
        "max_drawdown_pct": drawdown.min() * 100.0,
    }


def summarize_performance(merged: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for fund_id, group in merged.groupby("fund_id", sort=False):
        group = group.sort_values("month").reset_index(drop=True)
        common = group[(group["month_id"] >= COMMON_START_MONTH) & (group["month_id"] <= COMMON_END_MONTH)].copy()
        common = common.loc[common["monthly_return"].notna()].reset_index(drop=True)

        windows = [
            ("1Y", common.tail(12)),
            ("3Y", common.tail(36)),
            ("5Y", common.tail(60)),
            ("CommonSample", common),
        ]
        for label, window_df in windows:
            metrics = compute_window_metrics(window_df, label)
            metrics["fund_id"] = fund_id
            metrics["fund_name"] = group["fund_name"].iloc[0]
            metrics["fund_type"] = group["fund_type"].iloc[0]
            rows.append(metrics)
    return pd.DataFrame(rows)


def run_carhart_regression(merged: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    coef_rows: list[dict[str, object]] = []
    summary_rows: list[dict[str, object]] = []
    reg_sample = merged[(merged["month_id"] >= REG_START_MONTH) & (merged["month_id"] <= REG_END_MONTH)].copy()
    reg_sample = reg_sample.loc[reg_sample["monthly_return"].notna()].copy()

    for fund_id, group in reg_sample.groupby("fund_id", sort=False):
        y = group["excess_return_pct"].astype(float)
        x = sm.add_constant(group[["mkt_rf", "smb", "hml", "mom"]], has_constant="add")
        model = sm.OLS(y, x).fit()
        ci = model.conf_int(alpha=0.05)

        term_labels = {
            "const": "Alpha",
            "mkt_rf": "MKT-RF",
            "smb": "SMB",
            "hml": "HML",
            "mom": "MOM",
        }

        for term in ["const", "mkt_rf", "smb", "hml", "mom"]:
            coef_rows.append(
                {
                    "fund_id": fund_id,
                    "fund_name": group["fund_name"].iloc[0],
                    "term": term,
                    "term_label": term_labels[term],
                    "coef": model.params[term],
                    "std_err": model.bse[term],
                    "t_stat": model.tvalues[term],
                    "p_value": model.pvalues[term],
                    "ci_lower_95": ci.loc[term, 0],
                    "ci_upper_95": ci.loc[term, 1],
                }
            )

        alpha_monthly = float(model.params["const"])
        alpha_annualized = ((1.0 + alpha_monthly / 100.0) ** 12.0 - 1.0) * 100.0
        summary_rows.append(
            {
                "fund_id": fund_id,
                "fund_name": group["fund_name"].iloc[0],
                "n_obs": int(model.nobs),
                "alpha_monthly_pct": alpha_monthly,
                "alpha_annualized_pct": alpha_annualized,
                "alpha_p_value": model.pvalues["const"],
                "mkt_beta": model.params["mkt_rf"],
                "mkt_p_value": model.pvalues["mkt_rf"],
                "smb_beta": model.params["smb"],
                "smb_p_value": model.pvalues["smb"],
                "hml_beta": model.params["hml"],
                "hml_p_value": model.pvalues["hml"],
                "mom_beta": model.params["mom"],
                "mom_p_value": model.pvalues["mom"],
                "r_squared": model.rsquared,
                "adj_r_squared": model.rsquared_adj,
            }
        )

        summary_path = TABLE_DIR / f"carhart_ols_summary_{fund_id}.txt"
        summary_path.write_text(model.summary().as_text(), encoding="utf-8")

    return pd.DataFrame(coef_rows), pd.DataFrame(summary_rows)


def load_holdings_summary() -> tuple[pd.DataFrame, pd.DataFrame]:
    rows: list[dict[str, object]] = []
    all_holdings: dict[str, pd.DataFrame] = {}
    for config in FUNDS:
        df = pd.read_excel(config.holdings_path).copy()
        df = df.rename(columns={"成員公司": "company", "成員代碼": "code", "權重%": "weight_pct"})
        df["weight_pct"] = pd.to_numeric(df["weight_pct"], errors="raise")
        df = df.sort_values("weight_pct", ascending=False).reset_index(drop=True)
        all_holdings[config.fund_id] = df
        rows.append(
            {
                "fund_id": config.fund_id,
                "fund_name": config.fund_name,
                "holding_count": int(len(df)),
                "listed_weight_pct": df["weight_pct"].sum(),
                "top5_weight_pct": df["weight_pct"].head(5).sum(),
                "top10_weight_pct": df["weight_pct"].head(10).sum(),
                "max_weight_pct": df["weight_pct"].max(),
                "top_holdings": " / ".join(df["company"].head(5).tolist()),
            }
        )

    overlap_rows: list[dict[str, object]] = []
    for left in FUNDS:
        for right in FUNDS:
            if left.fund_id >= right.fund_id:
                continue
            left_df = all_holdings[left.fund_id]
            right_df = all_holdings[right.fund_id]
            shared_codes = sorted(set(left_df["code"]) & set(right_df["code"]))
            shared_names = (
                left_df.loc[left_df["code"].isin(shared_codes), "company"].drop_duplicates().tolist()
            )
            overlap_rows.append(
                {
                    "fund_left": left.fund_name,
                    "fund_right": right.fund_name,
                    "shared_holdings_count": len(shared_codes),
                    "shared_holdings_sample": " / ".join(shared_names[:10]),
                }
            )
    return pd.DataFrame(rows), pd.DataFrame(overlap_rows)


def fmt(value: float, digits: int = 2) -> str:
    if pd.isna(value):
        return ""
    return f"{value:.{digits}f}"


def markdown_table(df: pd.DataFrame) -> str:
    headers = list(df.columns)
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(str(row[col]) for col in headers) + " |")
    return "\n".join(lines)


def build_report(
    perf_df: pd.DataFrame,
    carhart_df: pd.DataFrame,
    holdings_df: pd.DataFrame,
    overlap_df: pd.DataFrame,
) -> None:
    full_sample = perf_df.loc[perf_df["window"] == "CommonSample"].copy()
    full_sample = full_sample.sort_values("annualized_return_pct", ascending=False)
    five_year = perf_df.loc[perf_df["window"] == "5Y"].copy()
    one_year = perf_df.loc[perf_df["window"] == "1Y"].copy()

    perf_report = full_sample[
        [
            "fund_name",
            "start_month",
            "end_month",
            "cumulative_return_pct",
            "annualized_return_pct",
            "annualized_volatility_pct",
            "sharpe_ratio",
            "max_drawdown_pct",
        ]
    ].copy()
    for col in ["cumulative_return_pct", "annualized_return_pct", "annualized_volatility_pct", "sharpe_ratio", "max_drawdown_pct"]:
        perf_report[col] = perf_report[col].map(fmt)

    one_year_report = one_year[["fund_name", "annualized_return_pct", "annualized_volatility_pct", "sharpe_ratio", "max_drawdown_pct"]].copy()
    for col in ["annualized_return_pct", "annualized_volatility_pct", "sharpe_ratio", "max_drawdown_pct"]:
        one_year_report[col] = one_year_report[col].map(fmt)

    five_year_report = five_year[["fund_name", "annualized_return_pct", "annualized_volatility_pct", "sharpe_ratio", "max_drawdown_pct"]].copy()
    for col in ["annualized_return_pct", "annualized_volatility_pct", "sharpe_ratio", "max_drawdown_pct"]:
        five_year_report[col] = five_year_report[col].map(fmt)

    carhart_report = carhart_df[
        [
            "fund_name",
            "n_obs",
            "alpha_annualized_pct",
            "alpha_p_value",
            "mkt_beta",
            "smb_beta",
            "hml_beta",
            "mom_beta",
            "adj_r_squared",
        ]
    ].copy()
    for col in ["alpha_annualized_pct", "alpha_p_value", "mkt_beta", "smb_beta", "hml_beta", "mom_beta", "adj_r_squared"]:
        carhart_report[col] = carhart_report[col].map(fmt)

    holdings_report = holdings_df[
        [
            "fund_name",
            "holding_count",
            "listed_weight_pct",
            "top5_weight_pct",
            "top10_weight_pct",
            "max_weight_pct",
            "top_holdings",
        ]
    ].copy()
    for col in ["listed_weight_pct", "top5_weight_pct", "top10_weight_pct", "max_weight_pct"]:
        holdings_report[col] = holdings_report[col].map(fmt)

    best_sharpe = full_sample.sort_values("sharpe_ratio", ascending=False).iloc[0]
    best_return = full_sample.sort_values("annualized_return_pct", ascending=False).iloc[0]
    worst_drawdown = full_sample.sort_values("max_drawdown_pct").iloc[0]

    lines = [
        "# Midterm Analysis Snapshot",
        "",
        "## Data Basis",
        "",
        "- Common performance sample: `2020-08` to `2026-03` monthly returns (initial TRI available from `2020-07`).",
        "- Carhart regression sample: `2021-04` to `2026-03`, total `60` monthly observations for each fund.",
        "- Factor file used: `data/tej_carhart_4factor_monthly_2020-01_to_2026-03.csv`.",
        "",
        "## Common-Sample Performance",
        "",
        markdown_table(perf_report),
        "",
        "## 1Y Performance",
        "",
        markdown_table(one_year_report),
        "",
        "## 5Y Performance",
        "",
        markdown_table(five_year_report),
        "",
        "## Carhart 4-Factor Regression (2021-04 to 2026-03)",
        "",
        markdown_table(carhart_report),
        "",
        "## Holdings Structure",
        "",
        markdown_table(holdings_report),
        "",
        "## Holdings Overlap",
        "",
        markdown_table(overlap_df),
        "",
        "## Quick Takeaways",
        "",
        f"- Best common-sample risk-adjusted performer so far: `{best_sharpe['fund_name']}` with Sharpe `{best_sharpe['sharpe_ratio']:.2f}`.",
        f"- Highest common-sample annualized return: `{best_return['fund_name']}` at `{best_return['annualized_return_pct']:.2f}%`.",
        f"- Largest common-sample drawdown: `{worst_drawdown['fund_name']}` at `{worst_drawdown['max_drawdown_pct']:.2f}%`.",
        "- The two active funds have much higher return than the passive ETF, but they also carry clearly higher volatility and deeper drawdowns.",
        "- Holdings data still represent partial portfolios, so attribution and active share conclusions should be presented as simplified observations rather than precise portfolio decomposition.",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    fund_frames = [load_monthly_fund(config) for config in FUNDS]
    factor_df = load_factors()
    merged = merge_with_factors(fund_frames, factor_df)

    perf_df = summarize_performance(merged)
    coef_df, carhart_df = run_carhart_regression(merged)
    holdings_df, overlap_df = load_holdings_summary()

    merged.to_csv(TABLE_DIR / "fund_monthly_master.csv", index=False, encoding="utf-8-sig")
    perf_df.to_csv(TABLE_DIR / "performance_summary.csv", index=False, encoding="utf-8-sig")
    coef_df.to_csv(TABLE_DIR / "carhart_coefficients.csv", index=False, encoding="utf-8-sig")
    carhart_df.to_csv(TABLE_DIR / "carhart_summary.csv", index=False, encoding="utf-8-sig")
    holdings_df.to_csv(TABLE_DIR / "holdings_summary.csv", index=False, encoding="utf-8-sig")
    overlap_df.to_csv(TABLE_DIR / "holdings_overlap.csv", index=False, encoding="utf-8-sig")

    build_report(perf_df, carhart_df, holdings_df, overlap_df)


if __name__ == "__main__":
    main()
