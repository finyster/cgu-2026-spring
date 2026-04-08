# Midterm Report

Last updated: `2026-04-08`

## Current Data Basis

- Common monthly return sample: `2020-08` to `2026-03`
- Initial common TRI anchor month: `2020-07`
- Carhart regression sample: `2021-04` to `2026-03`, `60` monthly observations per fund
- Official factor file now in use: `data/tej_carhart_4factor_monthly_2020-01_to_2026-03.csv`
- Main analysis script: `scripts/analyze_midterm.py`

Source:

- Fund monthly TRI source files:
  - `data/cathay_esg_00878/monthly_total_return_index_2020-07_to_2026-03.xlsx`
  - `data/uni_penta/monthly_total_return_index_2020-03_to_2026-03.xlsx`
  - `data/nomura_growth/monthly_total_return_index_2020-03_to_2026-03.xlsx`
- Carhart factor source:
  - current corrected raw export: `data/tej_carhart_4factor_raw_2026-04-08.csv`
  - cleaned analysis file: `data/tej_carhart_4factor_monthly_2020-01_to_2026-03.csv`
- Processing / analysis scripts:
  - `scripts/analyze_midterm.py`
  - `scripts/fetch_peer_rankings.py`

## Common-Sample Performance

| Fund | Sample | Cumulative Return | Annualized Return | Annualized Vol | Sharpe | Max Drawdown |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 統一奔騰基金 | 2020-08 to 2026-03 | 539.49% | 38.74% | 25.59% | 1.37 | -27.56% |
| 野村成長基金 | 2020-08 to 2026-03 | 455.88% | 35.35% | 27.06% | 1.22 | -36.35% |
| 國泰台灣 ESG 永續高股息 ETF (00878) | 2020-08 to 2026-03 | 111.30% | 14.11% | 13.70% | 0.94 | -16.05% |

Source:

- Calculated from the three monthly TRI workbooks listed in `Current Data Basis`
- Output table: `analysis_outputs/tables/performance_summary.csv`
- Detailed derivation: `analysis_outputs/midterm_analysis_report.md`

## 5Y Carhart 4-Factor Snapshot

Regression window: `2021-04` to `2026-03`

| Fund | Alpha Ann. | Alpha p-value | MKT-RF | SMB | HML | MOM | Adj. R² |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 國泰台灣 ESG 永續高股息 ETF (00878) | -2.33% | 0.57 | 0.62 | 0.04 | 0.17 | 0.10 | 0.62 |
| 統一奔騰基金 | 7.96% | 0.33 | 1.12 | 0.49 | 0.01 | 0.44 | 0.61 |
| 野村成長基金 | 8.04% | 0.31 | 1.26 | 0.43 | -0.35 | 0.23 | 0.70 |

Source:

- Fund returns: monthly TRI workbooks under `data/`
- Factor inputs: `data/tej_carhart_4factor_monthly_2020-01_to_2026-03.csv`
- Regression output: `analysis_outputs/tables/carhart_summary.csv`
- Full OLS summaries:
  - `analysis_outputs/tables/carhart_ols_summary_cathay_esg.txt`
  - `analysis_outputs/tables/carhart_ols_summary_uni_penta.txt`
  - `analysis_outputs/tables/carhart_ols_summary_nomura_growth.txt`

## Holdings Snapshot

Note: current holdings files are partial portfolios, so these figures are useful for structure reading, not precise full-portfolio attribution.

| Fund | Listed Weight | Top 10 Concentration | Max Single Weight | Notes |
| --- | ---: | ---: | ---: | --- |
| 國泰台灣 ESG 永續高股息 ETF (00878) | 46.62% | 37.93% | 7.26% | Most diversified of the three based on available holdings |
| 統一奔騰基金 | 89.29% | 72.66% | 8.98% | Highest concentration and strongest high-conviction profile |
| 野村成長基金 | 89.41% | 57.07% | 8.11% | Still concentrated, but more diversified than 統一奔騰基金 |

Source:

- Holdings files:
  - `data/cathay_esg_00878/holdings_breakdown.xlsx`
  - `data/uni_penta/holdings_breakdown.xlsx`
  - `data/nomura_growth/holdings_breakdown.xlsx`
- Summary tables:
  - `analysis_outputs/tables/holdings_summary.csv`
  - `analysis_outputs/tables/holdings_overlap.csv`

## Fee Snapshot

| Fund | Expense Ratio | Management Fee | Subscription Fee | Redemption Fee |
| --- | ---: | ---: | ---: | ---: |
| 國泰台灣 ESG 永續高股息 ETF (00878) | 0.35% | 0.30% | 2.00% | 0.40% |
| 統一奔騰基金 | 1.75% | 1.60% | 2.00% | 0.00% |
| 野村成長基金 | 1.74% | 1.60% | 2.00% | 1.00% |

Source:

- `report_digest.md`
- Original fund summaries:
  - `data/cathay_esg_00878/fund_report.pdf`
  - `data/uni_penta/fund_report.pdf`
  - `data/nomura_growth/fund_report.pdf`

## Current Read

- Two active funds clearly outperformed the passive ETF in raw return over the common sample, but they also took materially higher volatility and deeper drawdowns.
- `統一奔騰基金` currently has the strongest common-sample risk-adjusted profile in this dataset.
- `野村成長基金` has the deepest drawdown, so its strong return came with the highest downside pain.
- In the 5-year Carhart regression, both active funds show positive annualized alpha estimates, but neither alpha is statistically significant at conventional levels.
- The active funds both load strongly on market risk and positively on `SMB`, which is still more consistent with aggressive active style exposure than clean standalone alpha.
- `統一奔騰基金` now shows a clearly positive `MOM` loading, and that momentum exposure is statistically more meaningful than before.
- `野村成長基金` still shows a negative `HML` loading, which is consistent with a stronger growth tilt than `統一奔騰基金`.
- `統一奔騰基金` and `野村成長基金` share many technology-heavy holdings, so the active-vs-active comparison is more about concentration and implementation than about completely different style universes.

Source:

- `analysis_outputs/tables/performance_summary.csv`
- `analysis_outputs/tables/carhart_summary.csv`
- `analysis_outputs/tables/holdings_summary.csv`
- `analysis_outputs/tables/holdings_overlap.csv`

## Official Peer Ranking / Percentile

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
  - `analysis_outputs/tables/peer_ranking_summary.csv`
- Extraction script:
  - `scripts/fetch_peer_rankings.py`
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

## Ranking Read

- `野村成長基金` 在官方同類一般股票型裡，`1Y / 3Y / 5Y` 都維持在前 10% 內，這是目前三檔中最穩定的同類相對績效。
- `統一奔騰基金` 的官方同類科技類長期排名很強，`5Y` 排名達 `2 / 33`，但 `1Y` 已回落到前 40% 左右，近期相對表現沒有野村穩定。
- `00878` 在高股息 ETF 同類中，`3Y` 與 `5Y` 排名不錯，但 `1Y` 只在類別中段，較符合「穩定但非最強勢」的被動型特徵。

## Limitations

- Same-category ranking is available from official SITCA pages, but ranking observation month is `2026-02`, whereas local return analysis runs through `2026-03`.
- Current holdings files are incomplete, so `Attribution Analysis` and `Active Share Analysis` can only be done in simplified form for now.
- PDF benchmark / tracking fields are not fully consistent across the three funds, so regression results should rely on the cleaned monthly dataset rather than the PDF summaries.

Source:

- `data_review.md`
- `report_digest.md`

## Requirement Check

Requirement-by-requirement status:

- `requirements_checklist.md`

Current conclusion:

- Requirements `1`, `2`, `3` are already usable for report writing.
- Requirements `4`, `5` can only be written as simplified analysis with current holdings data.
- Requirements `6`, `7` can now be written as preliminary conclusions if you are willing to disclose those data limitations.

## Useful Files

- Detailed analysis report: [analysis_outputs/midterm_analysis_report.md](analysis_outputs/midterm_analysis_report.md)
- Performance table: [analysis_outputs/tables/performance_summary.csv](analysis_outputs/tables/performance_summary.csv)
- Carhart summary: [analysis_outputs/tables/carhart_summary.csv](analysis_outputs/tables/carhart_summary.csv)
- Holdings summary: [analysis_outputs/tables/holdings_summary.csv](analysis_outputs/tables/holdings_summary.csv)
- Holdings overlap: [analysis_outputs/tables/holdings_overlap.csv](analysis_outputs/tables/holdings_overlap.csv)
- Peer ranking summary: [analysis_outputs/tables/peer_ranking_summary.csv](analysis_outputs/tables/peer_ranking_summary.csv)
- Data review notes: [data_review.md](data_review.md)
- Next-step plan: [next_steps.md](next_steps.md)
- Requirement checklist: [requirements_checklist.md](requirements_checklist.md)
- PDF digest notes: [report_digest.md](report_digest.md)
- Source registry: [source_registry.md](source_registry.md)
- Assignment notes: [assignment_notes.md](assignment_notes.md)
- Assignment details: [assignment_details.md](assignment_details.md)

## Re-run

```bash
/home/henry/homeworks/.venv/bin/python scripts/analyze_midterm.py
```

```bash
/home/henry/homeworks/.venv/bin/python scripts/fetch_peer_rankings.py
```
