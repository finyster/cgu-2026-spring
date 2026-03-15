# HW2 Project Guide

這個 `hw2` 專案是把參考的 Colab 作業整理成可以在本地端直接執行、也比較像正式研究流程的版本。整個設計重點是「學習導向」：

- 保留清楚的資料來源與研究問題
- 讓下載、清理、計算、回歸分析、結果解讀各自有明確步驟
- 透過詳細註解讓你之後回頭看程式時知道每一步在做什麼

## Project Structure

```text
hw2/
├── README.md
├── hw2_asset_pricing_analysis.py
├── requirements.txt
├── data/
│   ├── raw/
│   └── processed/
└── outputs/
    └── figures/
```

## Research Question

在 2021-01-01 到 2025-12-31 的樣本期間內：

1. `FCNTX`、`AGTHX` 與 `SPY` 的績效與風險特性有何差異？
2. 若把 `FCNTX` 與 `AGTHX` 組成等權重主動基金投資組合 `ACTIVE_EW`，其表現是否優於 `SPY`？
3. 這些資產 / 投組的超額報酬能否被 CAPM、Carhart 4-factor 與 Fama-French 5-factor 模型解釋？

## Data Sources

- Asset data: Alpha Vantage monthly adjusted prices
- Factor data: Kenneth French Data Library
  - Fama-French 5 Factors (monthly)
  - Momentum factor (monthly)

## How To Run

1. 建立虛擬環境並安裝套件：

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

2. 如果你想用自己的 Alpha Vantage key，可以先設定環境變數：

```bash
export ALPHA_VANTAGE_API_KEY='your_api_key'
```

3. 執行分析：

```bash
python3 hw2_asset_pricing_analysis.py
```

## Expected Outputs

執行後，這些檔案會自動產生：

- `data/raw/`: 原始資料快取
- `data/processed/analysis_dataset.csv`: 合併後分析資料
- `outputs/performance_summary.csv`: 績效與風險摘要
- `outputs/regression_tidy.csv`: 完整回歸結果
- `outputs/regression_summary.csv`: 回歸摘要表
- `outputs/regression_summaries.txt`: statsmodels 原始摘要
- `outputs/hw2_report.md`: 可直接閱讀或延伸修改的作業報告
- `outputs/figures/*.png`: 圖表

## What Was Improved Compared With The Reference Script

- 移除了 Colab 專用指令，例如 `!pip` 與 `files.download(...)`
- 改用本地專案路徑，不再寫死 `/content/...`
- 補上投資組合建構，而不只分析單一資產
- 加入 CAPM，讓模型難度有遞進
- 以「月份」對齊資料，避免月底交易日不同造成錯誤合併
- 用 Markdown 報告整理結果，交作業時更容易直接修改與引用

## Suggested Submission Strategy

如果你要交作業，建議把這幾個東西一起整理給老師：

- `hw2_report.md`
- `performance_summary.csv`
- `regression_summary.csv`
- `outputs/figures/` 裡最重要的 2 到 4 張圖

這樣既有方法，也有結果與解讀。
