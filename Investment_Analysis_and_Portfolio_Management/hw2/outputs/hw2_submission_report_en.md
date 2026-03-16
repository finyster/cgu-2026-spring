# HW2 Regression Report: Alpha, Betas, and Market Interpretation

## Objective
This report evaluates whether two actively managed U.S. equity mutual funds, `FCNTX` and `AGTHX`, delivered abnormal performance relative to a passive market benchmark, `SPY`, from January 2021 to December 2025. I also construct an equal-weight active portfolio, `ACTIVE_EW`, to test whether combining two active managers improves the overall risk-return tradeoff. The goal is to estimate alpha and beta coefficients and interpret what they imply about market exposure, style tilts, and active management.

## Why These Funds Were Chosen
I intentionally chose one passive ETF and two active mutual funds because this setup creates a clean benchmark-versus-manager comparison.

- `SPY` is a broad U.S. equity ETF tracking the S&P 500, so it serves as a natural market benchmark and a low-cost passive alternative.
- `FCNTX` is an actively managed growth-oriented fund with a reputation for concentrated stock selection among large U.S. companies.
- `AGTHX` is another actively managed growth fund, but with a somewhat different portfolio construction process and manager style.

Using `FCNTX` and `AGTHX` together is useful because they represent active management decisions rather than mechanical index replication. Comparing them with `SPY` helps answer a standard finance question: are returns driven by manager skill, or mostly by systematic market and style risk? The equal-weight portfolio `ACTIVE_EW` reduces single-manager noise and tests whether a diversified active-fund mix can outperform passive indexing after controlling for common factors.

## Data and Regression Setup
Price data were obtained from Alpha Vantage using monthly adjusted prices for `SPY`, `FCNTX`, and `AGTHX`. Factor data were taken from the Kenneth French Data Library, including the Fama-French five factors (`Mkt-RF`, `SMB`, `HML`, `RMW`, `CMA`) and the momentum factor (`MOM`). Monthly simple returns were computed from adjusted prices and matched by month to the factor data. The dependent variable in every regression is monthly excess return:

`R_i - R_f`

where `R_i` is the asset return and `R_f` is the risk-free rate. After return construction, the regression sample contains 59 monthly observations.

I ran three OLS regression specifications:

1. `CAPM`: `R_i - R_f = alpha_i + beta_mkt (Mkt-RF) + e_i`
2. `Carhart 4-factor`: adds `SMB`, `HML`, and `MOM`
3. `Fama-French 5-factor`: adds `SMB`, `HML`, `RMW`, and `CMA`

The CAPM shows basic market exposure, while the multi-factor models test whether apparent outperformance is actually explained by growth, size, profitability, investment, or momentum tilts. My main interpretation emphasizes the FF5 model because it is the richest non-momentum specification, while the Carhart regression serves as a momentum check.

## Regression Results

### Table 1. CAPM Results
| Asset | Alpha | p-value | Market Beta | R-squared |
| --- | ---: | ---: | ---: | ---: |
| SPY | 0.0013 | 0.0557 | 0.9750 | 0.9872 |
| FCNTX | 0.0018 | 0.4099 | 1.0161 | 0.8826 |
| AGTHX | -0.0016 | 0.3822 | 1.0990 | 0.9325 |
| ACTIVE_EW | 0.0001 | 0.9370 | 1.0576 | 0.9263 |

### Table 2. FF5 Results
| Asset | Alpha | p-value | Mkt-RF | SMB | HML | RMW | CMA | R-squared |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| SPY | 0.0000 | 0.9181 | 0.9987 | -0.0866 | 0.0139 | 0.0912 | 0.0301 | 0.9969 |
| FCNTX | 0.0015 | 0.3719 | 1.0150 | -0.2433 | -0.1554 | 0.0153 | -0.0667 | 0.9464 |
| AGTHX | 0.0004 | 0.7289 | 1.0605 | -0.0465 | -0.1241 | -0.1968 | -0.0914 | 0.9721 |
| ACTIVE_EW | 0.0010 | 0.4540 | 1.0378 | -0.1449 | -0.1397 | -0.0908 | -0.0790 | 0.9690 |

Carhart results are broadly consistent with the FF5 estimates. In particular, the active funds and `ACTIVE_EW` all show momentum coefficients near zero and statistically insignificant, so momentum does not appear to be the main driver of their returns in this sample.

## Interpretation
The first important result is that alpha is not statistically significant for any of the active strategies. Under CAPM, `FCNTX` has a positive monthly alpha of `0.18%`, `AGTHX` has a negative alpha of `-0.16%`, and `ACTIVE_EW` is essentially zero, but none of these estimates is statistically different from zero. After moving to the richer Carhart and FF5 regressions, the same conclusion remains: once common risk factors are controlled for, there is no strong evidence of persistent abnormal performance. In practical terms, the sample does not support a claim of reliable manager skill.

The second result is that all assets have market beta close to one, with the active funds slightly above one. `SPY` has a market beta of about `1.00`, exactly what we would expect from a broad market ETF. `FCNTX` is also near one, while `AGTHX` and `ACTIVE_EW` are somewhat more aggressive, with market betas around `1.04` to `1.10` depending on the model. This means the active funds participated strongly in market rallies but also carried somewhat more downside risk. That pattern is consistent with the performance summary: `FCNTX` produced the highest annualized return, but `SPY` had the best Sharpe ratio and the smallest maximum drawdown.

The third result is the consistent negative `HML` loading for the active funds and the active portfolio. In both Carhart and FF5 regressions, `FCNTX`, `AGTHX`, and `ACTIVE_EW` all have negative and mostly significant `HML` coefficients. This indicates a growth tilt rather than a value tilt. That finding fits the sample period, which included post-pandemic recovery, aggressive monetary tightening, and then a large-cap growth and AI-led rally. Their performance was therefore not style-neutral; it was strongly linked to growth exposure.

The `SMB` coefficients provide a similar message. `FCNTX` and `ACTIVE_EW` have negative and significant `SMB` loadings in the FF5 model, which means they tilt toward larger-cap stocks rather than small-cap stocks. `AGTHX` has a slightly negative but insignificant `SMB` coefficient, implying a weaker size tilt. Combined with the negative `HML` coefficients, the active funds look more like large-cap growth vehicles than broad active stock pickers across the full market spectrum.

The profitability and investment factors add one more layer of interpretation. `AGTHX` has a significantly negative `RMW` coefficient, suggesting weaker exposure to highly profitable firms. `ACTIVE_EW` also has a negative `RMW`, although the estimate is only marginally significant. `CMA` is negative for the active funds as well, but generally not significant. These results suggest that the active strategies were not rewarded primarily for holding conservative, high-profitability firms. The dominant story remains market exposure plus a large-cap growth orientation.

Taken together, the regression results show that market conditions, not alpha, explain most of the observed performance. The high `R-squared` values support that conclusion: `SPY` reaches `0.9969` in FF5, while the active funds and `ACTIVE_EW` are also very high, between `0.9464` and `0.9721`. When a factor model explains that much variation, realized returns are largely systematic rather than idiosyncratic. For this sample, the market rewarded investors mainly for bearing broad equity risk and growth-related style exposure. The active funds did not produce returns that were clearly outside that factor structure.

## Conclusion
This regression exercise suggests that `SPY`, `FCNTX`, `AGTHX`, and the equal-weight active portfolio were all heavily driven by common market forces during 2021-2025. The passive benchmark behaved as expected, with beta near one and alpha near zero. The active funds did not generate statistically significant alpha, so their performance should not be interpreted as clear evidence of manager skill. Instead, their returns were mostly explained by exposure to the market and to growth-oriented, mostly large-cap equity styles. The main lesson is that what looks like active outperformance in raw returns can disappear once returns are decomposed into systematic factor betas.
