#!/usr/bin/env python3
"""HW2: Investment analysis and portfolio management workflow.

這份腳本把參考的 Colab 程式整理成一個可以在本地端直接執行的研究流程。
核心目標不是只把結果算出來，而是把每一步的資料處理邏輯寫清楚，方便學習：

1. 從 Alpha Vantage 下載基金 / ETF 的月資料。
2. 從 Kenneth French 資料庫下載 Fama-French 5 因子、Momentum 因子與 LT reversal 因子。
3. 整理月報酬、建立等權重主動基金投資組合。
4. 計算績效指標與風險指標。
5. 估計 CAPM、Carhart 4-factor、Fama-French 5-factor，以及 FF5 + LT reversal 模型。
6. 輸出圖表、CSV 與 Markdown 報告。
"""

from __future__ import annotations

import io
import math
import os
import re
import textwrap
import time
import zipfile
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import statsmodels.api as sm


# =========================
# 0) Project configuration
# =========================
# 專案根目錄使用腳本所在位置，避免 Colab 那種 /content 寫死路徑的問題。
PROJECT_DIR = Path(__file__).resolve().parent
DATA_RAW_DIR = PROJECT_DIR / "data" / "raw"
DATA_PROCESSED_DIR = PROJECT_DIR / "data" / "processed"
OUTPUT_DIR = PROJECT_DIR / "outputs"
FIGURE_DIR = OUTPUT_DIR / "figures"

# 樣本期間沿用參考檔設定，方便直接與原始版本比對。
START_DATE = pd.Timestamp("2021-01-01")
END_DATE = pd.Timestamp("2025-12-31")

# 參考檔使用的資產組合：兩檔共同基金 + 一檔市場 ETF。
ASSETS: dict[str, str] = {
    "FCNTX": "Fidelity Contrafund",
    "AGTHX": "Growth Fund of America",
    "SPY": "SPDR S&P 500 ETF Trust",
}

# 這裡額外建立一個等權重主動基金投資組合，讓作業更符合「投資組合管理」。
ACTIVE_PORTFOLIO_NAME = "ACTIVE_EW"
ACTIVE_PORTFOLIO_MEMBERS = ["FCNTX", "AGTHX"]
BENCHMARK_SYMBOL = "SPY"

# 參考檔已經提供一組 Alpha Vantage key。正式情況建議改成自己的 key，
# 但為了讓這份作業能直接重現，我先保留成 fallback。
REFERENCE_ALPHA_VANTAGE_API_KEY = "Z8I0C6L7P6AOGB07"
ALPHA_VANTAGE_API_KEY = os.getenv(
    "ALPHA_VANTAGE_API_KEY",
    REFERENCE_ALPHA_VANTAGE_API_KEY,
)

ALPHA_VANTAGE_URL = "https://www.alphavantage.co/query"
KEN_FRENCH_BASE_URL = (
    "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp"
)
FF5_URL = f"{KEN_FRENCH_BASE_URL}/F-F_Research_Data_5_Factors_2x3_CSV.zip"
MOM_URL = f"{KEN_FRENCH_BASE_URL}/F-F_Momentum_Factor_CSV.zip"
LT_REV_URL = f"{KEN_FRENCH_BASE_URL}/F-F_LT_Reversal_Factor_CSV.zip"

REQUEST_TIMEOUT = 60
ALPHA_VANTAGE_SLEEP_SECONDS = 12
ALPHA_VANTAGE_RETRY_LIMIT = 5

# 研究流程通常會先看簡單模型，再看較完整模型，因此把 CAPM 放進來。
MODEL_SPECS: dict[str, list[str]] = {
    "CAPM": ["Mkt_RF"],
    "Carhart4": ["Mkt_RF", "SMB", "HML", "MOM"],
    "FF5": ["Mkt_RF", "SMB", "HML", "RMW", "CMA"],
    "FF5_LTRev": ["Mkt_RF", "SMB", "HML", "RMW", "CMA", "LT_Rev"],
}


def ensure_directories() -> None:
    """建立專案所需的資料夾。"""
    for folder in [DATA_RAW_DIR, DATA_PROCESSED_DIR, OUTPUT_DIR, FIGURE_DIR]:
        folder.mkdir(parents=True, exist_ok=True)


def save_dataframe(df: pd.DataFrame, path: Path) -> None:
    """統一用 utf-8-sig 存檔，Excel 開啟中文欄位比較不會亂碼。"""
    safe_df = df.copy()
    for column in safe_df.columns:
        if isinstance(safe_df[column].dtype, pd.PeriodDtype):
            safe_df[column] = safe_df[column].astype(str)
    safe_df.to_csv(path, index=False, encoding="utf-8-sig")


def read_cached_dataframe(path: Path, parse_dates: list[str] | None = None) -> pd.DataFrame:
    """讀取快取 CSV，並把 month 欄位還原成 pandas Period。"""
    df = pd.read_csv(path, parse_dates=parse_dates)
    if "month" in df.columns:
        df["month"] = pd.PeriodIndex(df["month"], freq="M")
    return df


def fetch_alpha_vantage_monthly_adjusted(
    symbol: str,
    api_key: str,
    refresh: bool = False,
) -> pd.DataFrame:
    """下載單一資產的月調整收盤資料，並計算月簡單報酬率。

    這裡保留本地快取，原因有兩個：
    1. Alpha Vantage 免費版有頻率限制。
    2. 作業若需要反覆修改分析段落，沒有必要每次都重抓。
    """
    cache_path = DATA_RAW_DIR / f"{symbol}_monthly_adjusted.csv"
    if cache_path.exists() and not refresh:
        return read_cached_dataframe(cache_path, parse_dates=["Date"])

    endpoint_specs = [
        (
            "TIME_SERIES_MONTHLY_ADJUSTED",
            "Monthly Adjusted Time Series",
            {
                "1. open": "open",
                "2. high": "high",
                "3. low": "low",
                "4. close": "close",
                "5. adjusted close": "adjusted_close",
                "6. volume": "volume",
                "7. dividend amount": "dividend_amount",
            },
        ),
        (
            "TIME_SERIES_MONTHLY",
            "Monthly Time Series",
            {
                "1. open": "open",
                "2. high": "high",
                "3. low": "low",
                "4. close": "close",
                "5. volume": "volume",
            },
        ),
    ]

    last_response_keys: list[str] = []
    last_message = ""
    for function_name, series_key, rename_map in endpoint_specs:
        for attempt in range(1, ALPHA_VANTAGE_RETRY_LIMIT + 1):
            params = {
                "function": function_name,
                "symbol": symbol,
                "apikey": api_key,
                "datatype": "json",
            }
            response = requests.get(ALPHA_VANTAGE_URL, params=params, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            payload = response.json()

            if "Error Message" in payload:
                last_response_keys = list(payload.keys())
                last_message = payload["Error Message"]
                break

            warning_message = payload.get("Note") or payload.get("Information")
            if warning_message and series_key not in payload:
                last_response_keys = list(payload.keys())
                last_message = warning_message
                if attempt < ALPHA_VANTAGE_RETRY_LIMIT:
                    time.sleep(ALPHA_VANTAGE_SLEEP_SECONDS)
                    continue
                break

            series = payload.get(series_key)
            if not series:
                last_response_keys = list(payload.keys())
                last_message = (
                    f"Expected key '{series_key}' not found for function {function_name}."
                )
                break

            df = (
                pd.DataFrame.from_dict(series, orient="index")
                .sort_index()
                .reset_index()
                .rename(columns={"index": "Date"})
            )
            df["Date"] = pd.to_datetime(df["Date"])
            df = df.rename(columns=rename_map)

            if "adjusted_close" not in df.columns:
                # 一般 monthly time series 沒有 adjusted close，就先用 close 代替。
                df["adjusted_close"] = df["close"]
            if "dividend_amount" not in df.columns:
                df["dividend_amount"] = 0.0

            numeric_columns = [
                "open",
                "high",
                "low",
                "close",
                "adjusted_close",
                "volume",
                "dividend_amount",
            ]
            for column in numeric_columns:
                df[column] = pd.to_numeric(df[column], errors="coerce")

            # 先排序再計算 pct_change，避免報酬率方向顛倒。
            df = df.sort_values("Date").reset_index(drop=True)
            df = df[(df["Date"] >= START_DATE) & (df["Date"] <= END_DATE)].copy()
            df["ret"] = df["adjusted_close"].pct_change()

            # 之後所有資產與因子都以「月份」為對齊單位，而不是精確日期。
            # 這樣可以避免基金和 ETF 在月底交易日不同時合併失敗。
            df["month"] = df["Date"].dt.to_period("M")

            save_dataframe(df, cache_path)
            return df

    raise ValueError(
        f"{symbol}: usable Alpha Vantage data not found. "
        f"Last response keys: {last_response_keys}. Last message: {last_message}"
    )


MONTHLY_ROW_PATTERN = re.compile(r"^\d{6}$")


def parse_ken_french_monthly_zip(
    zip_bytes: bytes,
    value_columns: list[str],
) -> pd.DataFrame:
    """從 Kenneth French ZIP 檔中擷取月資料區段。

    Kenneth French 資料檔通常包含：
    - 前言文字
    - 月資料
    - 空白列
    - 年資料

    所以這裡不能直接用 read_csv 全讀，必須自己找出 YYYYMM 開頭的月資料列。
    """
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        inner_name = zf.namelist()[0]
        raw_text = zf.read(inner_name).decode("latin1")

    rows: list[list[str]] = []
    for line in raw_text.splitlines():
        parts = [part.strip() for part in line.split(",")]
        if not parts or not parts[0]:
            if rows:
                break
            continue

        if MONTHLY_ROW_PATTERN.fullmatch(parts[0]):
            rows.append(parts[: len(value_columns) + 1])
            continue

        if rows:
            break

    if not rows:
        raise ValueError("Unable to parse monthly section from Kenneth French file.")

    df = pd.DataFrame(rows, columns=["date_key"] + value_columns)
    df["Date"] = pd.to_datetime(df["date_key"], format="%Y%m") + pd.offsets.MonthEnd(0)
    for column in value_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce") / 100.0

    df = df.drop(columns=["date_key"])
    df["month"] = df["Date"].dt.to_period("M")
    df = df[(df["Date"] >= START_DATE) & (df["Date"] <= END_DATE)].copy()
    df = df.sort_values("Date").reset_index(drop=True)
    return df


def fetch_ff5_factors(refresh: bool = False) -> pd.DataFrame:
    """下載並快取 Fama-French 5 factors 月資料。"""
    cache_path = DATA_RAW_DIR / "ff5_monthly.csv"
    if cache_path.exists() and not refresh:
        return read_cached_dataframe(cache_path, parse_dates=["Date"])

    response = requests.get(FF5_URL, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    df = parse_ken_french_monthly_zip(
        response.content,
        ["Mkt_RF", "SMB", "HML", "RMW", "CMA", "RF"],
    )
    save_dataframe(df, cache_path)
    return df


def fetch_momentum_factor(refresh: bool = False) -> pd.DataFrame:
    """下載並快取 Carhart 模型常用的 Momentum 月因子。"""
    cache_path = DATA_RAW_DIR / "momentum_monthly.csv"
    if cache_path.exists() and not refresh:
        return read_cached_dataframe(cache_path, parse_dates=["Date"])

    response = requests.get(MOM_URL, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    df = parse_ken_french_monthly_zip(response.content, ["MOM"])
    save_dataframe(df, cache_path)
    return df


def fetch_lt_reversal_factor(refresh: bool = False) -> pd.DataFrame:
    """下載並快取 Kenneth French long-term reversal 月因子。"""
    cache_path = DATA_RAW_DIR / "lt_reversal_monthly.csv"
    if cache_path.exists() and not refresh:
        return read_cached_dataframe(cache_path, parse_dates=["Date"])

    response = requests.get(LT_REV_URL, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    df = parse_ken_french_monthly_zip(response.content, ["LT_Rev"])
    save_dataframe(df, cache_path)
    return df


def fetch_factor_data(refresh: bool = False) -> pd.DataFrame:
    """合併 FF5、Momentum 與 long-term reversal 因子。"""
    ff5 = fetch_ff5_factors(refresh=refresh)
    mom = fetch_momentum_factor(refresh=refresh)
    lt_rev = fetch_lt_reversal_factor(refresh=refresh)

    factors = ff5.merge(
        mom[["month", "MOM"]],
        on="month",
        how="inner",
    )
    factors = factors.merge(
        lt_rev[["month", "LT_Rev"]],
        on="month",
        how="inner",
    )
    factors["Date"] = factors["month"].dt.to_timestamp("M")
    factors = factors.sort_values("month").reset_index(drop=True)
    save_dataframe(factors, DATA_PROCESSED_DIR / "factors_monthly.csv")
    return factors


def combine_asset_returns(asset_frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """把每一檔資產的月報酬合併成同一張寬表。"""
    merged: pd.DataFrame | None = None
    for symbol, df in asset_frames.items():
        temp = df[["month", "ret"]].copy().rename(columns={"ret": f"{symbol}_ret"})
        if merged is None:
            merged = temp
        else:
            merged = merged.merge(temp, on="month", how="outer")

    if merged is None:
        raise ValueError("No asset data available.")

    merged["Date"] = merged["month"].dt.to_timestamp("M")
    merged = merged.sort_values("month").reset_index(drop=True)
    save_dataframe(merged, DATA_PROCESSED_DIR / "asset_returns_monthly.csv")
    return merged


def add_equal_weight_portfolio(
    returns_df: pd.DataFrame,
    members: list[str],
    portfolio_name: str,
) -> pd.DataFrame:
    """用等權重方式建立投資組合。

    這裡採用「成分都要有資料才計算」的保守寫法，
    避免只有部分基金有值時，投組權重被動態改變。
    """
    member_columns = [f"{symbol}_ret" for symbol in members]
    portfolio_returns = returns_df[member_columns].mean(axis=1)
    missing_member_mask = returns_df[member_columns].isna().any(axis=1)
    portfolio_returns[missing_member_mask] = np.nan

    result = returns_df.copy()
    result[f"{portfolio_name}_ret"] = portfolio_returns
    return result


def build_analysis_dataset(returns_df: pd.DataFrame, factors_df: pd.DataFrame) -> pd.DataFrame:
    """整合資產報酬、投資組合報酬與因子資料。"""
    analysis_df = returns_df.merge(
        factors_df.drop(columns=["Date"], errors="ignore"),
        on="month",
        how="inner",
    )
    analysis_df["Date"] = analysis_df["month"].dt.to_timestamp("M")

    return_columns = [column for column in analysis_df.columns if column.endswith("_ret")]
    for column in return_columns:
        asset_name = column.replace("_ret", "")
        analysis_df[f"{asset_name}_excess"] = analysis_df[column] - analysis_df["RF"]

    analysis_df = analysis_df.sort_values("month").reset_index(drop=True)
    save_dataframe(analysis_df, DATA_PROCESSED_DIR / "analysis_dataset.csv")
    return analysis_df


def calculate_max_drawdown(returns: pd.Series) -> float:
    """由報酬率序列計算最大回撤。"""
    clean_returns = returns.dropna()
    if clean_returns.empty:
        return np.nan

    wealth_index = (1 + clean_returns).cumprod()
    running_peak = wealth_index.cummax()
    drawdown = wealth_index / running_peak - 1
    return float(drawdown.min())


def compute_performance_summary(
    analysis_df: pd.DataFrame,
    benchmark_name: str,
) -> pd.DataFrame:
    """計算作業常見的投資績效與風險指標。"""
    rf_series = analysis_df["RF"]
    benchmark_col = f"{benchmark_name}_ret"
    return_columns = [column for column in analysis_df.columns if column.endswith("_ret")]

    summary_rows: list[dict[str, float | int | str]] = []
    for column in return_columns:
        asset = column.replace("_ret", "")
        selected_columns = list(dict.fromkeys([column, "RF", benchmark_col]))
        temp = analysis_df[selected_columns].dropna().copy()
        monthly_returns = temp[column]
        monthly_rf = temp["RF"]
        active_returns = monthly_returns - temp[benchmark_col]

        if monthly_returns.empty:
            continue

        n_months = len(monthly_returns)
        cumulative_return = (1 + monthly_returns).prod() - 1
        annualized_return = (1 + cumulative_return) ** (12 / n_months) - 1
        annualized_vol = monthly_returns.std(ddof=1) * math.sqrt(12)
        annualized_excess_mean = (monthly_returns - monthly_rf).mean() * 12
        sharpe_ratio = (
            annualized_excess_mean / annualized_vol
            if annualized_vol and not np.isclose(annualized_vol, 0.0)
            else np.nan
        )

        tracking_error = active_returns.std(ddof=1) * math.sqrt(12)
        information_ratio = (
            active_returns.mean() * 12 / tracking_error
            if tracking_error and not np.isclose(tracking_error, 0.0)
            else np.nan
        )

        summary_rows.append(
            {
                "asset": asset,
                "n_months": n_months,
                "cumulative_return": cumulative_return,
                "annualized_return": annualized_return,
                "annualized_volatility": annualized_vol,
                "annualized_sharpe": sharpe_ratio,
                "tracking_error_vs_spy": tracking_error,
                "information_ratio_vs_spy": information_ratio,
                "max_drawdown": calculate_max_drawdown(monthly_returns),
                "monthly_mean": monthly_returns.mean(),
                "monthly_std": monthly_returns.std(ddof=1),
                "best_month": monthly_returns.max(),
                "worst_month": monthly_returns.min(),
                "skewness": monthly_returns.skew(),
                "kurtosis": monthly_returns.kurt(),
            }
        )

    summary_df = pd.DataFrame(summary_rows).sort_values(
        ["annualized_sharpe", "annualized_return"],
        ascending=[False, False],
    )
    save_dataframe(summary_df, OUTPUT_DIR / "performance_summary.csv")
    return summary_df


def run_ols(df: pd.DataFrame, y_column: str, x_columns: list[str]):
    """估計 OLS 因子模型。"""
    temp = df[[y_column] + x_columns].dropna().copy()
    y = temp[y_column]
    X = sm.add_constant(temp[x_columns], has_constant="add")
    return sm.OLS(y, X).fit()


def tidy_regression_output(model, asset_name: str, model_name: str) -> pd.DataFrame:
    """把 statsmodels 輸出整理成 tidy 格式。"""
    result = pd.DataFrame(
        {
            "variable": model.params.index,
            "coef": model.params.values,
            "std_err": model.bse.values,
            "t_value": model.tvalues.values,
            "p_value": model.pvalues.values,
        }
    )
    result["asset"] = asset_name
    result["model"] = model_name
    result["r_squared"] = model.rsquared
    result["adj_r_squared"] = model.rsquared_adj
    result["n_obs"] = int(model.nobs)
    return result


def build_regression_summary(results_df: pd.DataFrame) -> pd.DataFrame:
    """把各模型的主要係數彙整到單列表格。"""
    variables = ["const", "Mkt_RF", "SMB", "HML", "MOM", "RMW", "CMA", "LT_Rev"]
    summary_rows: list[dict[str, float | str | int]] = []

    for (asset, model_name), subset in results_df.groupby(["asset", "model"]):
        row: dict[str, float | str | int] = {"asset": asset, "model": model_name}
        for variable in variables:
            hit = subset[subset["variable"] == variable]
            if hit.empty:
                continue
            row[f"{variable}_coef"] = hit["coef"].iloc[0]
            row[f"{variable}_p_value"] = hit["p_value"].iloc[0]

        row["r_squared"] = subset["r_squared"].iloc[0]
        row["adj_r_squared"] = subset["adj_r_squared"].iloc[0]
        row["n_obs"] = subset["n_obs"].iloc[0]
        summary_rows.append(row)

    summary_df = pd.DataFrame(summary_rows).sort_values(["asset", "model"])
    save_dataframe(summary_df, OUTPUT_DIR / "regression_summary.csv")
    return summary_df


def estimate_factor_models(
    analysis_df: pd.DataFrame,
    targets: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    """對每個資產 / 投組估計所有指定因子模型。"""
    tidy_frames: list[pd.DataFrame] = []
    regression_text_blocks: list[str] = []

    for target in targets:
        y_column = f"{target}_excess"
        for model_name, x_columns in MODEL_SPECS.items():
            model = run_ols(analysis_df, y_column, x_columns)
            tidy_frames.append(tidy_regression_output(model, target, model_name))
            regression_text_blocks.append(
                f"{'=' * 90}\n"
                f"{target} - {model_name}\n"
                f"{'=' * 90}\n"
                f"{model.summary().as_text()}"
            )

    results_df = pd.concat(tidy_frames, ignore_index=True)
    save_dataframe(results_df, OUTPUT_DIR / "regression_tidy.csv")
    summary_df = build_regression_summary(results_df)

    (OUTPUT_DIR / "regression_summaries.txt").write_text(
        "\n\n".join(regression_text_blocks),
        encoding="utf-8",
    )
    return results_df, summary_df, regression_text_blocks


def plot_cumulative_wealth(analysis_df: pd.DataFrame, targets: list[str], path: Path) -> None:
    """繪製 1 元累積財富圖。"""
    plt.figure(figsize=(12, 6))
    for target in targets:
        series = analysis_df[f"{target}_ret"].dropna()
        wealth = (1 + series).cumprod()
        plt.plot(analysis_df.loc[series.index, "Date"], wealth, label=target, linewidth=2)

    plt.title("Cumulative Wealth of $1")
    plt.xlabel("Date")
    plt.ylabel("Portfolio Value")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()


def plot_drawdown(analysis_df: pd.DataFrame, targets: list[str], path: Path) -> None:
    """繪製最大回撤路徑。"""
    plt.figure(figsize=(12, 6))
    for target in targets:
        returns = analysis_df[f"{target}_ret"].dropna()
        wealth = (1 + returns).cumprod()
        running_peak = wealth.cummax()
        drawdown = wealth / running_peak - 1
        plt.plot(analysis_df.loc[returns.index, "Date"], drawdown, label=target, linewidth=2)

    plt.title("Drawdown")
    plt.xlabel("Date")
    plt.ylabel("Drawdown")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()


def plot_return_distribution(analysis_df: pd.DataFrame, targets: list[str], path: Path) -> None:
    """繪製報酬分配，用來輔助觀察波動與偏態。"""
    plt.figure(figsize=(12, 6))
    for target in targets:
        plt.hist(
            analysis_df[f"{target}_ret"].dropna(),
            bins=14,
            alpha=0.4,
            label=target,
        )

    plt.title("Distribution of Monthly Returns")
    plt.xlabel("Monthly Return")
    plt.ylabel("Frequency")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()


def plot_correlation_heatmap(analysis_df: pd.DataFrame, targets: list[str], path: Path) -> None:
    """以熱圖呈現資產與因子之間的線性相關性。"""
    columns = [f"{target}_ret" for target in targets] + ["Mkt_RF", "SMB", "HML", "MOM", "RMW", "CMA"]
    correlation = analysis_df[columns].corr()

    fig, ax = plt.subplots(figsize=(10, 8))
    image = ax.imshow(correlation, cmap="coolwarm", vmin=-1, vmax=1)
    ax.set_xticks(range(len(columns)))
    ax.set_yticks(range(len(columns)))
    ax.set_xticklabels(columns, rotation=45, ha="right")
    ax.set_yticklabels(columns)
    ax.set_title("Correlation Heatmap")

    # 把數字直接寫到圖上，讓作業報告不用來回對照表格。
    for i in range(len(columns)):
        for j in range(len(columns)):
            ax.text(
                j,
                i,
                f"{correlation.iloc[i, j]:.2f}",
                ha="center",
                va="center",
                color="black",
                fontsize=8,
            )

    fig.colorbar(image, ax=ax, shrink=0.8)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def plot_factor_betas(summary_df: pd.DataFrame, target: str, path: Path) -> None:
    """把等權重投組在各模型下的因子暴露畫成柱狀圖。"""
    focus = summary_df[summary_df["asset"] == target].copy()
    if focus.empty:
        return

    factor_columns = [
        "Mkt_RF_coef",
        "SMB_coef",
        "HML_coef",
        "MOM_coef",
        "RMW_coef",
        "CMA_coef",
        "LT_Rev_coef",
    ]
    plot_frame = focus[["model"] + factor_columns].fillna(0.0).set_index("model")

    ax = plot_frame.plot(kind="bar", figsize=(11, 6))
    ax.set_title(f"Factor Exposures of {target}")
    ax.set_xlabel("Model")
    ax.set_ylabel("Estimated Coefficient")
    ax.grid(axis="y", alpha=0.3)
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()


def build_markdown_table(df: pd.DataFrame, decimals: int = 4) -> str:
    """不用額外安裝 tabulate，也能把 DataFrame 轉成 Markdown table。"""
    display_df = df.copy()
    for column in display_df.columns:
        if pd.api.types.is_numeric_dtype(display_df[column]):
            display_df[column] = display_df[column].map(
                lambda value: "" if pd.isna(value) else f"{value:.{decimals}f}"
            )
        else:
            display_df[column] = display_df[column].fillna("").astype(str)

    header = "| " + " | ".join(display_df.columns) + " |"
    separator = "| " + " | ".join(["---"] * len(display_df.columns)) + " |"
    rows = [
        "| " + " | ".join(row.astype(str).tolist()) + " |"
        for _, row in display_df.iterrows()
    ]
    return "\n".join([header, separator] + rows)


def interpret_alpha(alpha: float, p_value: float) -> str:
    """把 alpha 係數轉成較自然語言的解釋。"""
    if pd.isna(alpha):
        return "無法判讀 alpha。"
    if pd.isna(p_value):
        return f"alpha = {alpha:.4f}，但沒有 p-value 可判讀。"
    if p_value < 0.05:
        if alpha > 0:
            return f"alpha = {alpha:.4f}，且在 5% 顯著水準下為正，代表存在正向異常報酬。"
        return f"alpha = {alpha:.4f}，且在 5% 顯著水準下為負，代表風險調整後表現偏弱。"
    return f"alpha = {alpha:.4f}，但未達統計顯著，不能主張存在穩定異常報酬。"


def build_observations(
    performance_df: pd.DataFrame,
    regression_summary_df: pd.DataFrame,
) -> list[str]:
    """根據實際輸出整理出可直接放進報告的觀察結論。"""
    observations: list[str] = []

    best_return = performance_df.sort_values("annualized_return", ascending=False).iloc[0]
    best_sharpe = performance_df.sort_values("annualized_sharpe", ascending=False).iloc[0]
    smallest_drawdown = performance_df.sort_values("max_drawdown", ascending=False).iloc[0]

    observations.append(
        f"年化報酬最高的是 {best_return['asset']}，年化報酬約為 "
        f"{best_return['annualized_return']:.2%}。"
    )
    observations.append(
        f"風險調整後表現最佳的是 {best_sharpe['asset']}，年化 Sharpe ratio 約為 "
        f"{best_sharpe['annualized_sharpe']:.2f}。"
    )
    observations.append(
        f"最大回撤最小的是 {smallest_drawdown['asset']}，最大回撤約為 "
        f"{smallest_drawdown['max_drawdown']:.2%}。"
    )

    active_ff5 = regression_summary_df[
        (regression_summary_df["asset"] == ACTIVE_PORTFOLIO_NAME)
        & (regression_summary_df["model"] == "FF5")
    ]
    if not active_ff5.empty:
        row = active_ff5.iloc[0]
        observations.append(
            f"{ACTIVE_PORTFOLIO_NAME} 的 FF5 模型解釋力 R-squared 約為 "
            f"{row['r_squared']:.3f}，"
            f"{interpret_alpha(row.get('const_coef', np.nan), row.get('const_p_value', np.nan))}"
        )

    active_carhart = regression_summary_df[
        (regression_summary_df["asset"] == ACTIVE_PORTFOLIO_NAME)
        & (regression_summary_df["model"] == "Carhart4")
    ]
    if not active_carhart.empty:
        row = active_carhart.iloc[0]
        mom_beta = row.get("MOM_coef", np.nan)
        if pd.notna(mom_beta):
            if abs(mom_beta) < 0.05:
                observations.append(
                    f"{ACTIVE_PORTFOLIO_NAME} 在 Carhart 模型下的 MOM 係數為 {mom_beta:.3f}，"
                    "接近 0，顯示投組幾乎沒有明顯的 momentum 暴露。"
                )
            else:
                direction = "正向" if mom_beta > 0 else "負向"
                observations.append(
                    f"{ACTIVE_PORTFOLIO_NAME} 在 Carhart 模型下的 MOM 係數為 {mom_beta:.3f}，"
                    f"顯示投組具有{direction} momentum 暴露。"
                )

    lt_rev_hits = regression_summary_df[
        (regression_summary_df["model"] == "FF5_LTRev")
        & (regression_summary_df["LT_Rev_p_value"] < 0.05)
    ]
    for _, row in lt_rev_hits.iterrows():
        beta = row.get("LT_Rev_coef", np.nan)
        if pd.isna(beta):
            continue
        if beta > 0:
            observations.append(
                f"{row['asset']} 在 FF5 + LT reversal 模型下的 LT_Rev 係數為 {beta:.3f}，"
                "且達統計顯著，表示其報酬與 long-term reversal 因子呈正向關聯。"
            )
        else:
            observations.append(
                f"{row['asset']} 在 FF5 + LT reversal 模型下的 LT_Rev 係數為 {beta:.3f}，"
                "且達統計顯著，表示其表現更像是長期贏家風格，而非長期落後股反轉。"
            )

    return observations


def write_report(
    performance_df: pd.DataFrame,
    regression_summary_df: pd.DataFrame,
    observations: list[str],
) -> Path:
    """輸出一份可直接交作業或繼續修改的 Markdown 報告。"""
    key_performance_columns = [
        "asset",
        "annualized_return",
        "annualized_volatility",
        "annualized_sharpe",
        "information_ratio_vs_spy",
        "max_drawdown",
    ]
    key_regression_columns = [
        "asset",
        "model",
        "const_coef",
        "const_p_value",
        "Mkt_RF_coef",
        "SMB_coef",
        "HML_coef",
        "MOM_coef",
        "RMW_coef",
        "CMA_coef",
        "LT_Rev_coef",
        "r_squared",
        "adj_r_squared",
    ]

    report_text = f"""# HW2: Investment Analysis and Portfolio Management

## 1. Research Question
本作業的核心問題是：在 2021-01 到 2025-12 的樣本期間內，`FCNTX`、`AGTHX` 與 `SPY`
的績效與風險特性有何差異？若將兩檔主動型基金組成等權重投資組合 `{ACTIVE_PORTFOLIO_NAME}`，
其表現是否優於單純持有市場指數 ETF `SPY`？

## 2. Data Sources
- Asset prices: Alpha Vantage monthly adjusted data
- Risk factors: Kenneth French Data Library
  - Fama-French 5 Factors (monthly)
  - Momentum factor (monthly)
  - Long-term reversal factor (monthly)

## 3. Workflow
1. 下載並快取資產月資料與因子月資料。
2. 使用 adjusted close 計算月簡單報酬率。
3. 以月份對齊所有資料，避免不同資產月底交易日不一致造成合併偏誤。
4. 建立 `{ACTIVE_PORTFOLIO_NAME}` 等權重投資組合。
5. 計算績效指標：年化報酬、年化波動、Sharpe ratio、Information ratio、最大回撤。
6. 估計 CAPM、Carhart 4-factor、Fama-French 5-factor 與 FF5 + LT reversal 模型。
7. 根據統計結果進行風險暴露與 alpha 判讀。

## 4. Performance Summary
{build_markdown_table(performance_df[key_performance_columns])}

## 5. Factor Model Summary
{build_markdown_table(regression_summary_df[key_regression_columns])}

## 6. Key Findings
"""

    for observation in observations:
        report_text += f"- {observation}\n"

    report_text += textwrap.dedent(
        f"""

## 7. Interpretation
- 如果某資產的 `Mkt_RF` 係數接近 1，代表它和整體市場風險暴露相近。
- `SMB` 為正表示偏向小型股風格；`HML` 為正表示偏向價值股風格。
- `MOM` 為正表示較偏向動能；`RMW` 為正表示偏向高獲利公司；`CMA` 為正表示偏向保守投資公司。
- `LT_Rev` 為正表示和 long-term reversal 因子同向，通常較受長期落後股反轉影響；若為負，則較像長期贏家風格。
- `const` 即 alpha。若 alpha 為正且顯著，表示在控制常見系統性風險後仍有超額報酬。
- 若 alpha 不顯著，較合理的結論是：資產表現大致可以由既有因子暴露解釋，而非穩定選股能力。

## 8. Limitations
- 樣本期間集中在 2021-2025，包含疫情後復甦、升息與 AI 題材行情，未必能代表長期平均情況。
- 共同基金月資料的揭露與交易時點可能和 ETF 不完全一致，因此應避免過度解讀單月差異。
- 本作業沒有加入交易成本、申購贖回費用與稅負，因此實際投資人報酬可能低於回測結果。

## 9. Output Files
- `data/raw/`: 原始下載資料快取
- `data/processed/`: 合併後可直接分析的資料表
- `outputs/performance_summary.csv`: 主要績效指標
- `outputs/regression_tidy.csv`: 回歸結果 tidy 表
- `outputs/regression_summary.csv`: 回歸摘要表
- `outputs/figures/`: 圖表

## 10. Suggested Next Step
如果老師希望更強調投資組合管理，可以在下一版加入：
- mean-variance optimization
- rolling beta / rolling Sharpe
- benchmark-relative attribution
"""
    ).strip()

    report_path = OUTPUT_DIR / "hw2_report.md"
    report_path.write_text(report_text + "\n", encoding="utf-8")
    return report_path


def main(refresh_data: bool = False) -> None:
    """執行完整作業流程。"""
    ensure_directories()

    print("Step 1/7: Downloading monthly asset data...")
    asset_data: dict[str, pd.DataFrame] = {}
    metadata_rows: list[dict[str, str | int]] = []
    for idx, (symbol, description) in enumerate(ASSETS.items()):
        cache_exists = (DATA_RAW_DIR / f"{symbol}_monthly_adjusted.csv").exists()
        asset_df = fetch_alpha_vantage_monthly_adjusted(
            symbol=symbol,
            api_key=ALPHA_VANTAGE_API_KEY,
            refresh=refresh_data,
        )
        asset_data[symbol] = asset_df
        metadata_rows.append(
            {
                "symbol": symbol,
                "description": description,
                "n_obs_after_filter": len(asset_df),
            }
        )

        # 只有真的發送 API request 才需要休眠，避免免費版超過速率限制。
        if (refresh_data or not cache_exists) and idx < len(ASSETS) - 1:
            time.sleep(ALPHA_VANTAGE_SLEEP_SECONDS)

    metadata_df = pd.DataFrame(metadata_rows)
    save_dataframe(metadata_df, OUTPUT_DIR / "asset_metadata.csv")

    print("Step 2/7: Combining asset returns and building portfolio...")
    returns_df = combine_asset_returns(asset_data)
    returns_df = add_equal_weight_portfolio(
        returns_df,
        members=ACTIVE_PORTFOLIO_MEMBERS,
        portfolio_name=ACTIVE_PORTFOLIO_NAME,
    )
    save_dataframe(returns_df, DATA_PROCESSED_DIR / "asset_returns_with_portfolio.csv")

    print("Step 3/7: Downloading factor data...")
    factors_df = fetch_factor_data(refresh=refresh_data)

    print("Step 4/7: Merging returns and factors...")
    analysis_df = build_analysis_dataset(returns_df, factors_df)

    print("Step 5/7: Computing performance statistics...")
    analysis_targets = list(ASSETS.keys()) + [ACTIVE_PORTFOLIO_NAME]
    performance_df = compute_performance_summary(
        analysis_df,
        benchmark_name=BENCHMARK_SYMBOL,
    )

    print("Step 6/7: Estimating factor models...")
    _, regression_summary_df, _ = estimate_factor_models(
        analysis_df,
        targets=analysis_targets,
    )

    print("Step 7/7: Creating figures and report...")
    plot_cumulative_wealth(
        analysis_df,
        analysis_targets,
        FIGURE_DIR / "01_cumulative_wealth.png",
    )
    plot_drawdown(
        analysis_df,
        analysis_targets,
        FIGURE_DIR / "02_drawdown.png",
    )
    plot_return_distribution(
        analysis_df,
        analysis_targets,
        FIGURE_DIR / "03_return_distribution.png",
    )
    plot_correlation_heatmap(
        analysis_df,
        analysis_targets,
        FIGURE_DIR / "04_correlation_heatmap.png",
    )
    plot_factor_betas(
        regression_summary_df,
        ACTIVE_PORTFOLIO_NAME,
        FIGURE_DIR / "05_active_portfolio_factor_betas.png",
    )

    observations = build_observations(performance_df, regression_summary_df)
    report_path = write_report(
        performance_df=performance_df,
        regression_summary_df=regression_summary_df,
        observations=observations,
    )

    print("\nAnalysis completed.")
    print(f"Processed dataset: {DATA_PROCESSED_DIR / 'analysis_dataset.csv'}")
    print(f"Performance summary: {OUTPUT_DIR / 'performance_summary.csv'}")
    print(f"Regression summary: {OUTPUT_DIR / 'regression_summary.csv'}")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    # 若你想強制重新下載資料，可改成 main(refresh_data=True)。
    main(refresh_data=False)
