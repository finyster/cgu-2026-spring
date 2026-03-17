#!/usr/bin/env python3
from __future__ import annotations

import math
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm


BASE_DIR = Path(__file__).resolve().parents[1]
INPUT_PATH = BASE_DIR / "processed" / "regression_master.csv"
OUTPUT_DIR = BASE_DIR / "analysis_outputs"
TABLE_DIR = OUTPUT_DIR / "tables"
FIGURE_DIR = OUTPUT_DIR / "figures"
REPORT_PATH = OUTPUT_DIR / "hw2_report.md"

ASSET_ORDER = ["allianz", "jko", "0050"]
ASSET_NAMES = {
    "allianz": "Allianz Taiwan Smart",
    "jko": "JKO Taiwan 5Y",
    "0050": "0050 ETF",
}
ASSET_NAMES_ZH = {
    "allianz": "安聯台灣智慧",
    "jko": "街口台灣5年",
    "0050": "0050 ETF",
}
ASSET_COLORS = {
    "allianz": "#1f4e79",
    "jko": "#2e7d32",
    "0050": "#8e2a2a",
}

FACTOR_COLS = ["MKT_RF", "SMB", "HML_BM", "EP", "DY", "MOM"]
FACTOR_LABELS = {
    "MKT_RF": "MKT-RF",
    "SMB": "SMB",
    "HML_BM": "HML(BM)",
    "EP": "EP",
    "DY": "DY",
    "MOM": "MOM",
}


def setup_plot_style() -> None:
    plt.rcParams.update(
        {
            "figure.figsize": (9.2, 5.2),
            "figure.dpi": 160,
            "savefig.dpi": 320,
            "font.family": "serif",
            "font.serif": ["DejaVu Serif", "Times New Roman", "Times"],
            "axes.titlesize": 13,
            "axes.labelsize": 11,
            "axes.titleweight": "semibold",
            "axes.edgecolor": "#2b2b2b",
            "axes.linewidth": 0.8,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "grid.color": "#bbbbbb",
            "grid.linestyle": "--",
            "grid.linewidth": 0.6,
            "grid.alpha": 0.55,
            "legend.frameon": False,
        }
    )


def ensure_dirs() -> None:
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)


def significance_star(p_value: float) -> str:
    if p_value < 0.01:
        return "***"
    if p_value < 0.05:
        return "**"
    if p_value < 0.10:
        return "*"
    return ""


def load_regression_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="utf-8-sig")
    required = (
        ["month_id", "RF"]
        + FACTOR_COLS
        + [f"ret_{asset}" for asset in ASSET_ORDER]
        + [f"excess_{asset}" for asset in ASSET_ORDER]
    )
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    for col in required:
        if col == "month_id":
            continue
        df[col] = pd.to_numeric(df[col], errors="coerce")

    if df[required[1:]].isna().any().any():
        bad_cols = df[required[1:]].columns[df[required[1:]].isna().any()].tolist()
        raise ValueError(f"Numeric parsing failed for columns: {bad_cols}")

    df["month"] = pd.PeriodIndex(df["month_id"], freq="M").to_timestamp("M")
    df = df.sort_values("month").reset_index(drop=True)
    return df


def compute_performance(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    wealth = pd.DataFrame({"month": df["month"]})
    drawdown = pd.DataFrame({"month": df["month"]})
    records: list[dict[str, float | str]] = []

    n_obs = len(df)
    for asset in ASSET_ORDER:
        ret_pct = df[f"ret_{asset}"].astype(float)
        ret_dec = ret_pct / 100.0
        excess_dec = df[f"excess_{asset}"].astype(float) / 100.0

        wealth_series = (1.0 + ret_dec).cumprod()
        dd_series = wealth_series / wealth_series.cummax() - 1.0

        wealth[asset] = wealth_series
        drawdown[asset] = dd_series

        ann_return = wealth_series.iloc[-1] ** (12.0 / n_obs) - 1.0
        ann_vol = ret_dec.std(ddof=1) * math.sqrt(12.0)
        sharpe = np.nan if ann_vol == 0 else (excess_dec.mean() * 12.0) / ann_vol

        records.append(
            {
                "asset_id": asset,
                "asset_name": ASSET_NAMES[asset],
                "asset_name_zh": ASSET_NAMES_ZH[asset],
                "sample_months": n_obs,
                "annualized_return_pct": ann_return * 100.0,
                "annualized_volatility_pct": ann_vol * 100.0,
                "sharpe_ratio": sharpe,
                "max_drawdown_pct": dd_series.min() * 100.0,
                "cumulative_return_pct": (wealth_series.iloc[-1] - 1.0) * 100.0,
            }
        )

    perf_df = pd.DataFrame(records)
    return perf_df, wealth, drawdown


def compute_factor_stats(df: pd.DataFrame) -> pd.DataFrame:
    stats = (
        df[FACTOR_COLS]
        .agg(["mean", "std", "var", "min", "max", "skew", "kurt"])
        .T.reset_index()
        .rename(columns={"index": "factor"})
    )
    stats["factor_label"] = stats["factor"].map(FACTOR_LABELS)
    stats["annualized_mean_pct"] = stats["mean"] * 12.0
    stats["annualized_volatility_pct"] = stats["std"] * math.sqrt(12.0)
    ordered_cols = [
        "factor",
        "factor_label",
        "mean",
        "std",
        "var",
        "min",
        "max",
        "skew",
        "kurt",
        "annualized_mean_pct",
        "annualized_volatility_pct",
    ]
    return stats[ordered_cols]


def run_regressions(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, sm.regression.linear_model.RegressionResultsWrapper]]:
    x = sm.add_constant(df[FACTOR_COLS], has_constant="add")
    coef_rows: list[dict[str, float | str]] = []
    model_rows: list[dict[str, float | str]] = []
    models: dict[str, sm.regression.linear_model.RegressionResultsWrapper] = {}

    for asset in ASSET_ORDER:
        y = df[f"excess_{asset}"].astype(float)
        model = sm.OLS(y, x).fit()
        models[asset] = model

        ci = model.conf_int(alpha=0.05)
        for term in ["const"] + FACTOR_COLS:
            coef_rows.append(
                {
                    "asset_id": asset,
                    "asset_name": ASSET_NAMES[asset],
                    "asset_name_zh": ASSET_NAMES_ZH[asset],
                    "term": term,
                    "term_label": "Alpha" if term == "const" else FACTOR_LABELS[term],
                    "coefficient": model.params[term],
                    "std_error": model.bse[term],
                    "t_stat": model.tvalues[term],
                    "p_value": model.pvalues[term],
                    "significance": significance_star(model.pvalues[term]),
                    "ci_lower_95": ci.loc[term, 0],
                    "ci_upper_95": ci.loc[term, 1],
                }
            )

        alpha_monthly = model.params["const"]
        alpha_annual = ((1.0 + alpha_monthly / 100.0) ** 12.0 - 1.0) * 100.0
        model_rows.append(
            {
                "asset_id": asset,
                "asset_name": ASSET_NAMES[asset],
                "asset_name_zh": ASSET_NAMES_ZH[asset],
                "n_obs": int(model.nobs),
                "r_squared": model.rsquared,
                "adj_r_squared": model.rsquared_adj,
                "alpha_monthly_pct": alpha_monthly,
                "alpha_annualized_pct": alpha_annual,
                "alpha_p_value": model.pvalues["const"],
                "f_stat": model.fvalue,
                "f_p_value": model.f_pvalue,
                "dw_stat": sm.stats.stattools.durbin_watson(model.resid),
            }
        )

    coef_df = pd.DataFrame(coef_rows)
    model_df = pd.DataFrame(model_rows)
    return coef_df, model_df, models


def plot_cumulative_returns(wealth: pd.DataFrame) -> None:
    fig, ax = plt.subplots()
    for asset in ASSET_ORDER:
        ax.plot(
            wealth["month"],
            wealth[asset],
            label=ASSET_NAMES[asset],
            color=ASSET_COLORS[asset],
            linewidth=2.0,
        )
    ax.set_title("Cumulative Wealth Index (Start = 1)")
    ax.set_xlabel("Month")
    ax.set_ylabel("Wealth Index")
    ax.grid(True)
    ax.legend(ncol=3, loc="upper left")
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "01_cumulative_return.png")
    plt.close(fig)


def plot_drawdown(drawdown: pd.DataFrame) -> None:
    fig, ax = plt.subplots()
    for asset in ASSET_ORDER:
        dd_pct = drawdown[asset] * 100.0
        ax.plot(
            drawdown["month"],
            dd_pct,
            label=ASSET_NAMES[asset],
            color=ASSET_COLORS[asset],
            linewidth=1.8,
        )
    ax.axhline(0.0, color="#4d4d4d", linewidth=0.9)
    ax.set_title("Drawdown Comparison")
    ax.set_xlabel("Month")
    ax.set_ylabel("Drawdown (%)")
    ax.grid(True)
    ax.legend(ncol=3, loc="lower left")
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "02_drawdown.png")
    plt.close(fig)


def plot_risk_return(perf_df: pd.DataFrame) -> None:
    fig, ax = plt.subplots()
    for asset in ASSET_ORDER:
        row = perf_df.loc[perf_df["asset_id"] == asset].iloc[0]
        x_val = row["annualized_volatility_pct"]
        y_val = row["annualized_return_pct"]
        ax.scatter(x_val, y_val, s=90, color=ASSET_COLORS[asset], edgecolors="white", linewidth=0.7)
        ax.annotate(ASSET_NAMES[asset], (x_val, y_val), textcoords="offset points", xytext=(8, 6), fontsize=9.5)
    ax.axhline(0.0, color="#4d4d4d", linewidth=0.9)
    ax.set_title("Annualized Risk-Return Profile")
    ax.set_xlabel("Annualized Volatility (%)")
    ax.set_ylabel("Annualized Return (%)")
    ax.grid(True)
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "03_annualized_risk_return.png")
    plt.close(fig)


def plot_factor_exposure(coef_df: pd.DataFrame) -> None:
    beta_df = (
        coef_df[coef_df["term"].isin(FACTOR_COLS)]
        .pivot(index="term", columns="asset_id", values="coefficient")
        .loc[FACTOR_COLS]
    )

    x = np.arange(len(beta_df.index))
    width = 0.24

    fig, ax = plt.subplots()
    for i, asset in enumerate(ASSET_ORDER):
        ax.bar(
            x + (i - 1) * width,
            beta_df[asset],
            width=width,
            label=ASSET_NAMES[asset],
            color=ASSET_COLORS[asset],
            alpha=0.9,
        )
    ax.axhline(0.0, color="#4d4d4d", linewidth=0.9)
    ax.set_xticks(x)
    ax.set_xticklabels([FACTOR_LABELS[factor] for factor in beta_df.index])
    ax.set_title("Factor Exposure Comparison (Beta)")
    ax.set_xlabel("Factor")
    ax.set_ylabel("Coefficient")
    ax.grid(True, axis="y")
    ax.legend(ncol=3, loc="upper left")
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "04_factor_exposure.png")
    plt.close(fig)


def plot_alpha_ci(coef_df: pd.DataFrame) -> None:
    alpha_df = coef_df[coef_df["term"] == "const"].set_index("asset_id").loc[ASSET_ORDER]
    x = np.arange(len(ASSET_ORDER))
    y = alpha_df["coefficient"].to_numpy()
    ci_low = alpha_df["ci_lower_95"].to_numpy()
    ci_high = alpha_df["ci_upper_95"].to_numpy()
    yerr = np.vstack([y - ci_low, ci_high - y])

    fig, ax = plt.subplots()
    for i, asset in enumerate(ASSET_ORDER):
        ax.errorbar(
            x[i],
            y[i],
            yerr=np.array([[yerr[0, i]], [yerr[1, i]]]),
            fmt="o",
            color=ASSET_COLORS[asset],
            capsize=5,
            markersize=7.5,
            linewidth=1.6,
        )
    ax.axhline(0.0, color="#4d4d4d", linewidth=0.9, linestyle="--")
    ax.set_xticks(x)
    ax.set_xticklabels([ASSET_NAMES[a] for a in ASSET_ORDER], rotation=12, ha="right")
    ax.set_title("Alpha Estimates with 95% Confidence Intervals")
    ax.set_ylabel("Monthly Alpha (%)")
    ax.grid(True, axis="y")
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "05_alpha_ci.png")
    plt.close(fig)


def plot_r_squared(model_df: pd.DataFrame) -> None:
    ordered = model_df.set_index("asset_id").loc[ASSET_ORDER]
    x = np.arange(len(ASSET_ORDER))
    values = ordered["r_squared"].to_numpy()

    fig, ax = plt.subplots()
    bars = ax.bar(x, values, color=[ASSET_COLORS[a] for a in ASSET_ORDER], width=0.58, alpha=0.9)
    ax.set_xticks(x)
    ax.set_xticklabels([ASSET_NAMES[a] for a in ASSET_ORDER], rotation=12, ha="right")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("R-squared")
    ax.set_title("Model Explanatory Power by Asset")
    ax.grid(True, axis="y")
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 0.02, f"{value:.3f}", ha="center", va="bottom", fontsize=9.5)
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "06_r_squared.png")
    plt.close(fig)


def write_model_summaries(models: dict[str, sm.regression.linear_model.RegressionResultsWrapper]) -> None:
    for asset in ASSET_ORDER:
        summary_path = TABLE_DIR / f"ols_summary_{asset}.txt"
        summary_path.write_text(models[asset].summary().as_text(), encoding="utf-8")


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def build_report(
    df: pd.DataFrame,
    perf_df: pd.DataFrame,
    factor_stats: pd.DataFrame,
    coef_df: pd.DataFrame,
    model_df: pd.DataFrame,
) -> None:
    sample_start = df["month_id"].iloc[0]
    sample_end = df["month_id"].iloc[-1]
    sample_n = len(df)

    perf_table_rows: list[list[str]] = []
    ordered_perf = perf_df.set_index("asset_id").loc[ASSET_ORDER].reset_index()
    for _, row in ordered_perf.iterrows():
        perf_table_rows.append(
            [
                row["asset_name_zh"],
                f"{row['annualized_return_pct']:.2f}%",
                f"{row['annualized_volatility_pct']:.2f}%",
                f"{row['sharpe_ratio']:.3f}",
                f"{row['max_drawdown_pct']:.2f}%",
                f"{row['cumulative_return_pct']:.2f}%",
            ]
        )

    factor_table_rows: list[list[str]] = []
    for _, row in factor_stats.iterrows():
        factor_table_rows.append(
            [
                row["factor_label"],
                f"{row['mean']:.3f}",
                f"{row['std']:.3f}",
                f"{row['var']:.3f}",
                f"{row['min']:.3f}",
                f"{row['max']:.3f}",
            ]
        )

    alpha_rows = (
        coef_df[coef_df["term"] == "const"]
        .set_index("asset_id")
        .loc[ASSET_ORDER]
        .reset_index(drop=False)
    )
    r2_rows = model_df.set_index("asset_id").loc[ASSET_ORDER].reset_index(drop=False)

    reg_table_rows: list[list[str]] = []
    for asset in ASSET_ORDER:
        alpha_row = alpha_rows[alpha_rows["asset_id"] == asset].iloc[0]
        model_row = r2_rows[r2_rows["asset_id"] == asset].iloc[0]
        reg_table_rows.append(
            [
                ASSET_NAMES_ZH[asset],
                f"{alpha_row['coefficient']:.3f}",
                f"[{alpha_row['ci_lower_95']:.3f}, {alpha_row['ci_upper_95']:.3f}]",
                f"{alpha_row['p_value']:.4f}{alpha_row['significance']}",
                f"{model_row['r_squared']:.3f}",
            ]
        )

    positive_alpha_5 = [
        ASSET_NAMES_ZH[row["asset_id"]]
        for _, row in alpha_rows.iterrows()
        if row["coefficient"] > 0 and row["p_value"] < 0.05
    ]
    if positive_alpha_5:
        alpha_conclusion = "、".join(positive_alpha_5) + " 具有顯著正 alpha。"
    else:
        alpha_conclusion = "三個標的在 5% 顯著水準下皆未出現顯著正 alpha。"

    top_sharpe_asset = ordered_perf.sort_values("sharpe_ratio", ascending=False).iloc[0]["asset_name_zh"]
    top_r2_asset = r2_rows.sort_values("r_squared", ascending=False).iloc[0]["asset_id"]
    top_r2_name = ASSET_NAMES_ZH[top_r2_asset]

    md_lines = [
        "# 六因子模型實證分析報告（Homework 2）",
        "",
        "## 1. 研究設定",
        f"- 樣本期間：`{sample_start}` 至 `{sample_end}`（共 `{sample_n}` 個月）",
        "- 資料來源：資產價格資料（Bloomberg）與因子資料（TEJ Pro），皆已整理為月頻百分比尺度。",
        "- 模型：`Ri - Rf = alpha + b1*MKT_RF + b2*SMB + b3*HML_BM + b4*EP + b5*DY + b6*MOM + e`",
        "- 比較標的：安聯台灣智慧、街口台灣5年、0050 ETF",
        "",
        "## 2. 績效與風險指標",
        markdown_table(
            ["標的", "年化報酬", "年化波動", "Sharpe", "最大回撤", "累積報酬"],
            perf_table_rows,
        ),
        "",
        "## 3. 因子描述統計（月頻，單位：%）",
        markdown_table(
            ["因子", "平均", "標準差", "變異數", "最小值", "最大值"],
            factor_table_rows,
        ),
        "",
        "## 4. 六因子回歸重點",
        markdown_table(
            ["標的", "Alpha(月%)", "95% CI", "Alpha p-value", "R-squared"],
            reg_table_rows,
        ),
        "",
        f"- Alpha 判斷：{alpha_conclusion}",
        f"- 風險調整後報酬（Sharpe）最佳：`{top_sharpe_asset}`。",
        f"- 六因子模型解釋力最高：`{top_r2_name}`（R-squared 最大）。",
        "",
        "## 5. 圖表（學術風格 PNG）",
        "![Cumulative Return](figures/01_cumulative_return.png)",
        "",
        "![Drawdown](figures/02_drawdown.png)",
        "",
        "![Annualized Risk Return](figures/03_annualized_risk_return.png)",
        "",
        "![Factor Exposure](figures/04_factor_exposure.png)",
        "",
        "![Alpha CI](figures/05_alpha_ci.png)",
        "",
        "![R-squared](figures/06_r_squared.png)",
        "",
        "## 6. 投資與管理意涵",
        "- 若以「是否具備顯著正 alpha」作為主動管理價值判準，樣本中尚未看到強而穩健的統計證據。",
        "- 若重視風格可解釋性，R-squared 較高者代表報酬主要來自因子暴露而非選股 alpha。",
        "- 建議實務上再搭配滾動視窗回歸與子期間穩健性檢定，以確認風格曝險是否隨時間漂移。",
        "",
        "## 7. 主要輸出檔",
        "- `analysis_outputs/tables/asset_performance_summary.csv`",
        "- `analysis_outputs/tables/factor_descriptive_stats.csv`",
        "- `analysis_outputs/tables/regression_coefficients.csv`",
        "- `analysis_outputs/tables/regression_model_stats.csv`",
        "- `analysis_outputs/tables/ols_summary_allianz.txt`",
        "- `analysis_outputs/tables/ols_summary_jko.txt`",
        "- `analysis_outputs/tables/ols_summary_0050.txt`",
    ]
    REPORT_PATH.write_text("\n".join(md_lines), encoding="utf-8")


def main() -> None:
    ensure_dirs()
    setup_plot_style()

    legacy_paths = [
        FIGURE_DIR / "cumulative_return.svg",
        TABLE_DIR / "regression_results.csv",
    ]
    for legacy_path in legacy_paths:
        if legacy_path.exists():
            legacy_path.unlink()

    df = load_regression_data(INPUT_PATH)
    perf_df, wealth_df, drawdown_df = compute_performance(df)
    factor_stats = compute_factor_stats(df)
    coef_df, model_df, models = run_regressions(df)

    perf_df.to_csv(TABLE_DIR / "asset_performance_summary.csv", index=False, encoding="utf-8-sig")
    factor_stats.to_csv(TABLE_DIR / "factor_descriptive_stats.csv", index=False, encoding="utf-8-sig")
    coef_df.to_csv(TABLE_DIR / "regression_coefficients.csv", index=False, encoding="utf-8-sig")
    model_df.to_csv(TABLE_DIR / "regression_model_stats.csv", index=False, encoding="utf-8-sig")
    write_model_summaries(models)

    plot_cumulative_returns(wealth_df)
    plot_drawdown(drawdown_df)
    plot_risk_return(perf_df)
    plot_factor_exposure(coef_df)
    plot_alpha_ci(coef_df)
    plot_r_squared(model_df)
    build_report(df, perf_df, factor_stats, coef_df, model_df)

    print("Homework 2 analysis completed.")
    print("Tables:", TABLE_DIR)
    print("Figures:", FIGURE_DIR)
    print("Report :", REPORT_PATH)


if __name__ == "__main__":
    main()
