# Source Registry

This file records the source basis for each current result block in the midterm project.

## 1. Performance Results

Primary source files:

- `data/cathay_esg_00878/monthly_total_return_index_2020-07_to_2026-03.xlsx`
- `data/uni_penta/monthly_total_return_index_2020-03_to_2026-03.xlsx`
- `data/nomura_growth/monthly_total_return_index_2020-03_to_2026-03.xlsx`

Derived output:

- `analysis_outputs/tables/performance_summary.csv`

Processing logic:

- `scripts/analyze_midterm.py`

## 2. Carhart 4-Factor Regression

Primary factor sources:

- Current corrected raw TEJ export: `data/tej_carhart_4factor_raw_2026-04-08.csv`
- Cleaned factor file used in analysis: `data/tej_carhart_4factor_monthly_2020-01_to_2026-03.csv`

Fund return sources:

- Same three monthly TRI workbooks listed in section 1

Derived outputs:

- `analysis_outputs/tables/carhart_summary.csv`
- `analysis_outputs/tables/carhart_coefficients.csv`
- `analysis_outputs/tables/carhart_ols_summary_cathay_esg.txt`
- `analysis_outputs/tables/carhart_ols_summary_uni_penta.txt`
- `analysis_outputs/tables/carhart_ols_summary_nomura_growth.txt`

Processing logic:

- `scripts/analyze_midterm.py`

Important note:

- The TEJ `無風險利率` field is treated as annualized and converted to monthly rate by dividing by `12` before computing excess return.
- The cleaned factor file was rebuilt on `2026-04-08` from `tej_carhart_4factor_raw_2026-04-08.csv`.

## 3. Holdings Structure

Primary source files:

- `data/cathay_esg_00878/holdings_breakdown.xlsx`
- `data/uni_penta/holdings_breakdown.xlsx`
- `data/nomura_growth/holdings_breakdown.xlsx`

Derived outputs:

- `analysis_outputs/tables/holdings_summary.csv`
- `analysis_outputs/tables/holdings_overlap.csv`

Processing logic:

- `scripts/analyze_midterm.py`

Important limitation:

- These holdings files are partial portfolios, not complete fund holdings.

## 4. Basic Fund Description

Primary source files:

- `data/cathay_esg_00878/fund_report.pdf`
- `data/uni_penta/fund_report.pdf`
- `data/nomura_growth/fund_report.pdf`

Supporting digest:

- `report_digest.md`

Important limitation:

- PDF benchmark / tracking fields are not fully consistent across funds.

## 5. Same-Category Ranking / Percentile

Official source status:

- SITCA fund ranking entry page:
  - <https://www.sitca.org.tw/ROC/Industry/IN2002.aspx>
- SITCA detailed-data listing page showing latest available ranking month:
  - <https://www.sitca.org.tw/ROC/Industry/IN2401.aspx?Back=IN2400.aspx&PGMID=IN0202&PORDER=4&form=02&kind=F>

Current observation month used:

- `2026-02`
- Reason: this is the latest official ranking month currently listed on the SITCA detailed-data page.

Official SITCA category basis already identified:

- `統一奔騰基金`: `股票型/投資國內/科技類`
- `野村成長基金`: `股票型/投資國內/一般股票型`
- `國泰台灣 ESG 永續高股息 ETF (00878)`: `股票型/投資國內/指數股票型/一般型ETF/高股息ETF`

Examples of official SITCA ranking pages that match the relevant categories:

- `股票型/投資國內/科技類` example:
  - <https://www.sitca.org.tw/ROC/Industry/IN240201.aspx?txtFCS_CLASS=1110&txtKeyWord=&txtMONTH=10&txtNFC_MENU1=1&txtNFC_MENU2=1&txtOrderby=FCS_5Y&txtYEAR=2025&txtchkList=>
- `股票型/投資國內/一般股票型` example:
  - <https://www.sitca.org.tw/ROC/Industry/IN240201.aspx?txtFCS_CLASS=1140&txtMONTH=07&txtNFC_MENU1=1&txtNFC_MENU2=4&txtYEAR=2025&txtsNFC_CLASSNAME=%E8%82%A1%E7%A5%A8%E5%9E%8B>

Current extracted ranking output:

- `analysis_outputs/tables/peer_ranking_summary.csv`

Processing logic:

- `scripts/fetch_peer_rankings.py`

Official pages used for extraction:

- `統一奔騰基金`
  - 1Y:
    <https://www.sitca.org.tw/ROC/Industry/IN240201.aspx?txtFCS_CLASS=1110&txtMONTH=02&txtNFC_MENU1=1&txtNFC_MENU2=1&txtYEAR=2026&txtOrderby=FCS_1Y&txtchkList=>
  - 3Y:
    <https://www.sitca.org.tw/ROC/Industry/IN240201.aspx?txtFCS_CLASS=1110&txtMONTH=02&txtNFC_MENU1=1&txtNFC_MENU2=1&txtYEAR=2026&txtOrderby=FCS_3Y&txtchkList=>
  - 5Y:
    <https://www.sitca.org.tw/ROC/Industry/IN240201.aspx?txtFCS_CLASS=1110&txtMONTH=02&txtNFC_MENU1=1&txtNFC_MENU2=1&txtYEAR=2026&txtOrderby=FCS_5Y&txtchkList=>

- `野村成長基金`
  - 1Y:
    <https://www.sitca.org.tw/ROC/Industry/IN240201.aspx?txtFCS_CLASS=1140&txtMONTH=02&txtNFC_MENU1=1&txtNFC_MENU2=4&txtYEAR=2026&txtOrderby=FCS_1Y&txtchkList=>
  - 3Y:
    <https://www.sitca.org.tw/ROC/Industry/IN240201.aspx?txtFCS_CLASS=1140&txtMONTH=02&txtNFC_MENU1=1&txtNFC_MENU2=4&txtYEAR=2026&txtOrderby=FCS_3Y&txtchkList=>
  - 5Y:
    <https://www.sitca.org.tw/ROC/Industry/IN240201.aspx?txtFCS_CLASS=1140&txtMONTH=02&txtNFC_MENU1=1&txtNFC_MENU2=4&txtYEAR=2026&txtOrderby=FCS_5Y&txtchkList=>

- `國泰台灣 ESG 永續高股息 ETF (00878)`
  - 1Y:
    <https://www.sitca.org.tw/ROC/Industry/IN240201.aspx?txtFCS_CLASS=1161C&txtMONTH=02&txtNFC_MENU1=1&txtNFC_MENU2=9&txtYEAR=2026&txtOrderby=FCS_1Y&txtchkList=>
  - 3Y:
    <https://www.sitca.org.tw/ROC/Industry/IN240201.aspx?txtFCS_CLASS=1161C&txtMONTH=02&txtNFC_MENU1=1&txtNFC_MENU2=9&txtYEAR=2026&txtOrderby=FCS_3Y&txtchkList=>
  - 5Y:
    <https://www.sitca.org.tw/ROC/Industry/IN240201.aspx?txtFCS_CLASS=1161C&txtMONTH=02&txtNFC_MENU1=1&txtNFC_MENU2=9&txtYEAR=2026&txtOrderby=FCS_5Y&txtchkList=>

Working rule:

- Ranking and percentile will be reported only after matching each fund to the official SITCA peer category and extracting its rank within the full category table for the same observation month and return window.
