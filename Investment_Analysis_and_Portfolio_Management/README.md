# Investment Analysis and Portfolio Management

This folder contains homework projects and course-related analysis work.

## Contents

- `hw2/`: asset pricing analysis, factor regressions, and report outputs
- `midterm_report/`: mutual fund midterm report data, cleaned factors, analysis scripts, and current findings

## Midterm Report Status

Last updated: `2026-04-07`

### Current Data Basis

- Common monthly return sample: `2020-08` to `2026-03`
- Initial common TRI anchor month: `2020-07`
- Carhart regression sample: `2021-04` to `2026-03`, `60` monthly observations per fund
- Official factor file now in use: `midterm_report/data/TEJ_carhart_factor_monthly_2020-01_to_2026-03_utf8.csv`
- Main script: `midterm_report/scripts/analyze_midterm.py`

Source:

- Fund monthly TRI source files:
  - `midterm_report/data/國泰ESG/國泰台灣ESG永續高股息ETF基金2020-7-20~2026-3-31每月總報酬指數.xlsx`
  - `midterm_report/data/統一奔騰基金/統一奔騰基金2020-3-31到2026-3-31每月總報酬指數.xlsx`
  - `midterm_report/data/野村成長基金/野村成長基金-2020-03-31到2026-04-07每月總報酬指數.xlsx`
- Carhart factor source:
  - original raw export: `midterm_report/data/20260407111212.csv`
  - cleaned analysis file: `midterm_report/data/TEJ_carhart_factor_monthly_2020-01_to_2026-03_utf8.csv`
- Processing / analysis script:
  - `midterm_report/scripts/analyze_midterm.py`

### Common-Sample Performance

| Fund | Sample | Cumulative Return | Annualized Return | Annualized Vol | Sharpe | Max Drawdown |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 統一奔騰基金 | 2020-08 to 2026-03 | 539.49% | 38.74% | 25.59% | 1.37 | -27.56% |
| 野村成長基金 | 2020-08 to 2026-03 | 455.88% | 35.35% | 27.06% | 1.22 | -36.35% |
| 國泰台灣 ESG 永續高股息 ETF (00878) | 2020-08 to 2026-03 | 111.30% | 14.11% | 13.70% | 0.94 | -16.05% |

Source:

- Calculated from the three monthly TRI workbooks listed in `Current Data Basis`
- Output table: `midterm_report/analysis_outputs/tables/performance_summary.csv`
- Detailed derivation: `midterm_report/analysis_outputs/midterm_analysis_report.md`

### 5Y Carhart 4-Factor Snapshot

Regression window: `2021-04` to `2026-03`

| Fund | Alpha Ann. | Alpha p-value | MKT-RF | SMB | HML | MOM | Adj. R² |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 國泰台灣 ESG 永續高股息 ETF (00878) | -2.57% | 0.52 | 0.62 | 0.07 | 0.19 | 0.17 | 0.63 |
| 統一奔騰基金 | 10.23% | 0.22 | 1.14 | 0.50 | 0.06 | 0.37 | 0.60 |
| 野村成長基金 | 8.77% | 0.26 | 1.30 | 0.46 | -0.28 | 0.18 | 0.71 |

Source:

- Fund returns: monthly TRI workbooks under `midterm_report/data/`
- Factor inputs: `midterm_report/data/TEJ_carhart_factor_monthly_2020-01_to_2026-03_utf8.csv`
- Regression output: `midterm_report/analysis_outputs/tables/carhart_summary.csv`
- Full OLS summaries:
  - `midterm_report/analysis_outputs/tables/carhart_ols_summary_cathay_esg.txt`
  - `midterm_report/analysis_outputs/tables/carhart_ols_summary_uni_penta.txt`
  - `midterm_report/analysis_outputs/tables/carhart_ols_summary_nomura_growth.txt`

### Holdings Snapshot

Note: current holdings files are partial portfolios, so these figures are useful for structure reading, not precise full-portfolio attribution.

| Fund | Listed Weight | Top 10 Concentration | Max Single Weight | Notes |
| --- | ---: | ---: | ---: | --- |
| 國泰台灣 ESG 永續高股息 ETF (00878) | 46.62% | 37.93% | 7.26% | Most diversified of the three based on available holdings |
| 統一奔騰基金 | 89.29% | 72.66% | 8.98% | Highest concentration and strongest high-conviction profile |
| 野村成長基金 | 89.41% | 57.07% | 8.11% | Still concentrated, but more diversified than 統一奔騰基金 |

Source:

- Holdings files:
  - `midterm_report/data/國泰ESG/營收細項.xlsx`
  - `midterm_report/data/統一奔騰基金/營收細項.xlsx`
  - `midterm_report/data/野村成長基金/營收細項.xlsx`
- Summary tables:
  - `midterm_report/analysis_outputs/tables/holdings_summary.csv`
  - `midterm_report/analysis_outputs/tables/holdings_overlap.csv`

### Current Read

- Two active funds clearly outperformed the passive ETF in raw return over the common sample, but they also took materially higher volatility and deeper drawdowns.
- `統一奔騰基金` currently has the strongest common-sample risk-adjusted profile in this dataset.
- `野村成長基金` has the deepest drawdown, so its strong return came with the highest downside pain.
- In the 5-year Carhart regression, both active funds show positive annualized alpha estimates, but neither alpha is statistically significant at conventional levels.
- The active funds both load strongly on market risk and positively on `SMB`, which is more consistent with aggressive active style exposure than clean standalone alpha.
- `野村成長基金` shows a negative `HML` loading, which is consistent with a stronger growth tilt than `統一奔騰基金`.
- `統一奔騰基金` and `野村成長基金` share many technology-heavy holdings, so the active-vs-active comparison is more about concentration and implementation than about completely different style universes.

Source:

- `midterm_report/analysis_outputs/tables/performance_summary.csv`
- `midterm_report/analysis_outputs/tables/carhart_summary.csv`
- `midterm_report/analysis_outputs/tables/holdings_summary.csv`
- `midterm_report/analysis_outputs/tables/holdings_overlap.csv`

### Official Peer Ranking / Percentile

Observation month: `2026-02`

This uses the latest official SITCA ranking month currently listed on the SITCA detailed-data page, which shows `2026年02月：基金績效評比` with file date `20260309`.

| Fund | Official Category | 1Y Rank | 3Y Rank | 5Y Rank |
| --- | --- | --- | --- | --- |
| 統一奔騰基金 | 股票型/投資國內/科技類 | 13 / 33, 前 39.39% | 6 / 33, 前 18.18% | 2 / 33, 前 6.06% |
| 野村成長基金 | 股票型/投資國內/一般股票型 | 4 / 132, 前 3.03% | 7 / 132, 前 5.30% | 9 / 132, 前 6.82% |
| 國泰台灣 ESG 永續高股息 ETF (00878) | 股票型/投資國內/指數股票型/一般型ETF/高股息ETF | 10 / 22, 前 45.45% | 5 / 22, 前 22.73% | 3 / 22, 前 13.64% |

Source:

- Official SITCA ranking availability page:
  - <https://www.sitca.org.tw/ROC/Industry/IN2401.aspx?Back=IN2400.aspx&PGMID=IN0202&PORDER=4&form=02&kind=F>
- Detailed extracted table:
  - `midterm_report/analysis_outputs/tables/peer_ranking_summary.csv`
- Extraction script:
  - `midterm_report/scripts/fetch_peer_rankings.py`
- Official ranking pages used:
  - 統一奔騰基金 1Y:
    <https://www.sitca.org.tw/ROC/Industry/IN240201.aspx?txtFCS_CLASS=1110&txtMONTH=02&txtNFC_MENU1=1&txtNFC_MENU2=1&txtYEAR=2026&txtOrderby=FCS_1Y&txtchkList=>
  - 統一奔騰基金 3Y:
    <https://www.sitca.org.tw/ROC/Industry/IN240201.aspx?txtFCS_CLASS=1110&txtMONTH=02&txtNFC_MENU1=1&txtNFC_MENU2=1&txtYEAR=2026&txtOrderby=FCS_3Y&txtchkList=>
  - 統一奔騰基金 5Y:
    <https://www.sitca.org.tw/ROC/Industry/IN240201.aspx?txtFCS_CLASS=1110&txtMONTH=02&txtNFC_MENU1=1&txtNFC_MENU2=1&txtYEAR=2026&txtOrderby=FCS_5Y&txtchkList=>
  - 野村成長基金 1Y:
    <https://www.sitca.org.tw/ROC/Industry/IN240201.aspx?txtFCS_CLASS=1140&txtMONTH=02&txtNFC_MENU1=1&txtNFC_MENU2=4&txtYEAR=2026&txtOrderby=FCS_1Y&txtchkList=>
  - 野村成長基金 3Y:
    <https://www.sitca.org.tw/ROC/Industry/IN240201.aspx?txtFCS_CLASS=1140&txtMONTH=02&txtNFC_MENU1=1&txtNFC_MENU2=4&txtYEAR=2026&txtOrderby=FCS_3Y&txtchkList=>
  - 野村成長基金 5Y:
    <https://www.sitca.org.tw/ROC/Industry/IN240201.aspx?txtFCS_CLASS=1140&txtMONTH=02&txtNFC_MENU1=1&txtNFC_MENU2=4&txtYEAR=2026&txtOrderby=FCS_5Y&txtchkList=>
  - 00878 1Y:
    <https://www.sitca.org.tw/ROC/Industry/IN240201.aspx?txtFCS_CLASS=1161C&txtMONTH=02&txtNFC_MENU1=1&txtNFC_MENU2=9&txtYEAR=2026&txtOrderby=FCS_1Y&txtchkList=>
  - 00878 3Y:
    <https://www.sitca.org.tw/ROC/Industry/IN240201.aspx?txtFCS_CLASS=1161C&txtMONTH=02&txtNFC_MENU1=1&txtNFC_MENU2=9&txtYEAR=2026&txtOrderby=FCS_3Y&txtchkList=>
  - 00878 5Y:
    <https://www.sitca.org.tw/ROC/Industry/IN240201.aspx?txtFCS_CLASS=1161C&txtMONTH=02&txtNFC_MENU1=1&txtNFC_MENU2=9&txtYEAR=2026&txtOrderby=FCS_5Y&txtchkList=>

### Ranking Read

- `野村成長基金` 在官方同類一般股票型裡，`1Y / 3Y / 5Y` 都維持在前 10% 內，這是目前三檔中最穩定的同類相對績效。
- `統一奔騰基金` 的官方同類科技類長期排名很強，`5Y` 排名達 `2 / 33`，但 `1Y` 已回落到前 40% 左右，近期相對表現沒有野村穩定。
- `00878` 在高股息 ETF 同類中，`3Y` 與 `5Y` 排名不錯，但 `1Y` 只在類別中段，較符合「穩定但非最強勢」的被動型特徵。

### Limitations

- Same-category ranking is now available from official SITCA pages, but ranking observation month is `2026-02`, whereas local return analysis runs through `2026-03`.
- Current holdings files are incomplete, so `Attribution Analysis` and `Active Share Analysis` can only be done in simplified form for now.
- PDF benchmark / tracking fields are not fully consistent across the three funds, so regression results should rely on the cleaned monthly dataset rather than the PDF summaries.

Source:

- Data review memo: `midterm_report/data_review.md`
- PDF digest memo: `midterm_report/report_digest.md`

### Useful Files

- Detailed analysis report: [midterm_report/analysis_outputs/midterm_analysis_report.md](midterm_report/analysis_outputs/midterm_analysis_report.md)
- Performance table: [midterm_report/analysis_outputs/tables/performance_summary.csv](midterm_report/analysis_outputs/tables/performance_summary.csv)
- Carhart summary: [midterm_report/analysis_outputs/tables/carhart_summary.csv](midterm_report/analysis_outputs/tables/carhart_summary.csv)
- Holdings summary: [midterm_report/analysis_outputs/tables/holdings_summary.csv](midterm_report/analysis_outputs/tables/holdings_summary.csv)
- Holdings overlap: [midterm_report/analysis_outputs/tables/holdings_overlap.csv](midterm_report/analysis_outputs/tables/holdings_overlap.csv)
- Peer ranking summary: [midterm_report/analysis_outputs/tables/peer_ranking_summary.csv](midterm_report/analysis_outputs/tables/peer_ranking_summary.csv)
- Data review notes: [midterm_report/data_review.md](midterm_report/data_review.md)
- PDF digest notes: [midterm_report/report_digest.md](midterm_report/report_digest.md)
- Source registry: [midterm_report/source_registry.md](midterm_report/source_registry.md)

### Re-run Analysis

```bash
/home/henry/homeworks/.venv/bin/python midterm_report/scripts/analyze_midterm.py
```

```bash
/home/henry/homeworks/.venv/bin/python midterm_report/scripts/fetch_peer_rankings.py
```
