# HW2: Investment Analysis and Portfolio Management

## 1. Research Question
本作業的核心問題是：在 2021-01 到 2025-12 的樣本期間內，`FCNTX`、`AGTHX` 與 `SPY`
的績效與風險特性有何差異？若將兩檔主動型基金組成等權重投資組合 `ACTIVE_EW`，
其表現是否優於單純持有市場指數 ETF `SPY`？

## 2. Data Sources
- Asset prices: Alpha Vantage monthly adjusted data
- Risk factors: Kenneth French Data Library
  - Fama-French 5 Factors (monthly)
  - Momentum factor (monthly)

## 3. Workflow
1. 下載並快取資產月資料與因子月資料。
2. 使用 adjusted close 計算月簡單報酬率。
3. 以月份對齊所有資料，避免不同資產月底交易日不一致造成合併偏誤。
4. 建立 `ACTIVE_EW` 等權重投資組合。
5. 計算績效指標：年化報酬、年化波動、Sharpe ratio、Information ratio、最大回撤。
6. 估計 CAPM、Carhart 4-factor 與 Fama-French 5-factor 模型。
7. 根據統計結果進行風險暴露與 alpha 判讀。

## 4. Performance Summary
| asset | annualized_return | annualized_volatility | annualized_sharpe | information_ratio_vs_spy | max_drawdown |
| --- | --- | --- | --- | --- | --- |
| SPY | 0.1484 | 0.1523 | 0.7813 |  | -0.2393 |
| FCNTX | 0.1578 | 0.1686 | 0.7707 | 0.1876 | -0.3095 |
| ACTIVE_EW | 0.1392 | 0.1712 | 0.6653 | -0.0955 | -0.3184 |
| AGTHX | 0.1202 | 0.1773 | 0.5525 | -0.3576 | -0.3357 |

## 5. Factor Model Summary
| asset | model | const_coef | const_p_value | Mkt_RF_coef | SMB_coef | HML_coef | MOM_coef | RMW_coef | CMA_coef | r_squared |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ACTIVE_EW | CAPM | 0.0001 | 0.9370 | 1.0576 |  |  |  |  |  | 0.9263 |
| ACTIVE_EW | Carhart4 | 0.0011 | 0.4053 | 1.0381 | -0.0900 | -0.2018 | 0.0003 |  |  | 0.9657 |
| ACTIVE_EW | FF5 | 0.0010 | 0.4540 | 1.0378 | -0.1449 | -0.1397 |  | -0.0908 | -0.0790 | 0.9690 |
| AGTHX | CAPM | -0.0016 | 0.3822 | 1.0990 |  |  |  |  |  | 0.9325 |
| AGTHX | Carhart4 | 0.0004 | 0.7729 | 1.0580 | 0.0535 | -0.2154 | 0.0004 |  |  | 0.9616 |
| AGTHX | FF5 | 0.0004 | 0.7289 | 1.0605 | -0.0465 | -0.1241 |  | -0.1968 | -0.0914 | 0.9721 |
| FCNTX | CAPM | 0.0018 | 0.4099 | 1.0161 |  |  |  |  |  | 0.8826 |
| FCNTX | Carhart4 | 0.0018 | 0.2778 | 1.0183 | -0.2335 | -0.1883 | 0.0002 |  |  | 0.9456 |
| FCNTX | FF5 | 0.0015 | 0.3719 | 1.0150 | -0.2433 | -0.1554 |  | 0.0153 | -0.0667 | 0.9464 |
| SPY | CAPM | 0.0013 | 0.0557 | 0.9750 |  |  |  |  |  | 0.9872 |
| SPY | Carhart4 | 0.0001 | 0.8169 | 0.9948 | -0.1456 | 0.0483 | -0.0353 |  |  | 0.9948 |
| SPY | FF5 | 0.0000 | 0.9181 | 0.9987 | -0.0866 | 0.0139 |  | 0.0912 | 0.0301 | 0.9969 |

## 6. Key Findings
- 年化報酬最高的是 FCNTX，年化報酬約為 15.78%。
- 風險調整後表現最佳的是 SPY，年化 Sharpe ratio 約為 0.78。
- 最大回撤最小的是 SPY，最大回撤約為 -23.93%。
- ACTIVE_EW 的 FF5 模型解釋力 R-squared 約為 0.969，alpha = 0.0010，但未達統計顯著，不能主張存在穩定異常報酬。
- ACTIVE_EW 在 Carhart 模型下的 MOM 係數為 0.000，接近 0，顯示投組幾乎沒有明顯的 momentum 暴露。
## 7. Interpretation
- 如果某資產的 `Mkt_RF` 係數接近 1，代表它和整體市場風險暴露相近。
- `SMB` 為正表示偏向小型股風格；`HML` 為正表示偏向價值股風格。
- `MOM` 為正表示較偏向動能；`RMW` 為正表示偏向高獲利公司；`CMA` 為正表示偏向保守投資公司。
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
