# Midterm Analysis Snapshot

## Data Basis

- Common performance sample: `2020-08` to `2026-03` monthly returns (initial TRI available from `2020-07`).
- Carhart regression sample: `2021-04` to `2026-03`, total `60` monthly observations for each fund.
- Factor file used: `data/tej_carhart_4factor_monthly_2020-01_to_2026-03.csv`.

## Common-Sample Performance

| fund_name | start_month | end_month | cumulative_return_pct | annualized_return_pct | annualized_volatility_pct | sharpe_ratio | max_drawdown_pct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 統一奔騰基金 | 2020-08 | 2026-03 | 539.49 | 38.74 | 25.59 | 1.37 | -27.56 |
| 野村成長基金 | 2020-08 | 2026-03 | 455.88 | 35.35 | 27.06 | 1.22 | -36.35 |
| 國泰台灣 ESG 永續高股息 ETF (00878) | 2020-08 | 2026-03 | 111.30 | 14.11 | 13.70 | 0.94 | -16.05 |

## 1Y Performance

| fund_name | annualized_return_pct | annualized_volatility_pct | sharpe_ratio | max_drawdown_pct |
| --- | --- | --- | --- | --- |
| 國泰台灣 ESG 永續高股息 ETF (00878) | 11.81 | 14.57 | 0.72 | -8.15 |
| 統一奔騰基金 | 130.34 | 22.35 | 3.89 | 0.00 |
| 野村成長基金 | 164.70 | 22.68 | 4.49 | -1.64 |

## 5Y Performance

| fund_name | annualized_return_pct | annualized_volatility_pct | sharpe_ratio | max_drawdown_pct |
| --- | --- | --- | --- | --- |
| 國泰台灣 ESG 永續高股息 ETF (00878) | 11.31 | 13.68 | 0.75 | -16.05 |
| 統一奔騰基金 | 34.66 | 25.62 | 1.24 | -27.56 |
| 野村成長基金 | 30.71 | 28.06 | 1.05 | -36.35 |

## Carhart 4-Factor Regression (2021-04 to 2026-03)

| fund_name | n_obs | alpha_annualized_pct | alpha_p_value | mkt_beta | smb_beta | hml_beta | mom_beta | adj_r_squared |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 國泰台灣 ESG 永續高股息 ETF (00878) | 60 | -2.33 | 0.57 | 0.62 | 0.04 | 0.17 | 0.10 | 0.62 |
| 統一奔騰基金 | 60 | 7.96 | 0.33 | 1.12 | 0.49 | 0.01 | 0.44 | 0.61 |
| 野村成長基金 | 60 | 8.04 | 0.31 | 1.26 | 0.43 | -0.35 | 0.23 | 0.70 |

## Holdings Structure

| fund_name | holding_count | listed_weight_pct | top5_weight_pct | top10_weight_pct | max_weight_pct | top_holdings |
| --- | --- | --- | --- | --- | --- | --- |
| 國泰台灣 ESG 永續高股息 ETF (00878) | 15 | 46.62 | 25.17 | 37.93 | 7.26 | 聯華電子股份有限公司 / 聯發科技股份有限公司 / 日月光投資控股股份有限公司 / 華碩電腦股份有限公司 / 京元電子股份有限公司 |
| 統一奔騰基金 | 21 | 89.29 | 41.72 | 72.66 | 8.98 | 奇鋐科技股份有限公司 / 台灣積體電路製造股份有限公司 / 金像電子（股）公司 / 智邦科技股份有限公司 / 貿聯控股（BizLink Holding Inc） |
| 野村成長基金 | 30 | 89.41 | 32.97 | 57.07 | 8.11 | 台灣積體電路製造股份有限公司 / 健策精密工業股份有限公司 / 奇鋐科技股份有限公司 / 貿聯控股（BizLink Holding Inc） / 金像電子（股）公司 |

## Holdings Overlap

| fund_left | fund_right | shared_holdings_count | shared_holdings_sample |
| --- | --- | --- | --- |
| 國泰台灣 ESG 永續高股息 ETF (00878) | 統一奔騰基金 | 3 | 聯發科技股份有限公司 / 京元電子股份有限公司 / 緯創資通股份有限公司 |
| 國泰台灣 ESG 永續高股息 ETF (00878) | 野村成長基金 | 3 | 聯發科技股份有限公司 / 京元電子股份有限公司 / 緯創資通股份有限公司 |
| 野村成長基金 | 統一奔騰基金 | 17 | 台灣積體電路製造股份有限公司 / 健策精密工業股份有限公司 / 奇鋐科技股份有限公司 / 貿聯控股（BizLink Holding Inc） / 金像電子（股）公司 / 富世達股份有限公司 / 台達電子工業股份有限公司 / 智邦科技股份有限公司 / 旺矽科技股份有限公司 / 群聯電子股份有限公司 |

## Quick Takeaways

- Best common-sample risk-adjusted performer so far: `統一奔騰基金` with Sharpe `1.37`.
- Highest common-sample annualized return: `統一奔騰基金` at `38.74%`.
- Largest common-sample drawdown: `野村成長基金` at `-36.35%`.
- The two active funds have much higher return than the passive ETF, but they also carry clearly higher volatility and deeper drawdowns.
- Holdings data still represent partial portfolios, so attribution and active share conclusions should be presented as simplified observations rather than precise portfolio decomposition.
