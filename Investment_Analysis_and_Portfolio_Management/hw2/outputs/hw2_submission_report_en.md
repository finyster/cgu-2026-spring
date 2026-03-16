# HW2 Regression Report: Alpha, Betas, and Factor Selection Rationale

## Objective
This report evaluates whether two actively managed U.S. equity mutual funds, `FCNTX` and `AGTHX`, delivered abnormal performance relative to a passive market benchmark, `SPY`, over January 2021 to December 2025. I also construct an equal-weight active portfolio, `ACTIVE_EW`, to test whether combining two active managers improves the overall risk-return tradeoff. The objective is not only to estimate `alpha` and `betas`, but also to explain why these factors were chosen and what the coefficients reveal about the underlying investment style of the funds.

## Why These Assets Were Chosen
I chose one passive ETF and two active mutual funds because this creates a clear benchmark-versus-manager comparison.

- `SPY` tracks the S&P 500 and serves as the natural passive benchmark for broad U.S. equity exposure.
- `FCNTX` is a large-cap growth-oriented active fund with concentrated stock selection.
- `AGTHX` is also an active growth fund, but with a different manager process and portfolio construction.

This combination makes the assignment meaningful because it allows a direct test of whether active outperformance reflects manager skill or simply exposure to standard equity risk factors.

## Why These Factors Were Chosen
The factor choice is based on the style of the selected funds, not on trial-and-error searching for a positive alpha.

- `Mkt-RF` is essential because all three assets are U.S. equity vehicles and should have strong market exposure.
- `SMB` is relevant because the funds may tilt toward large-cap or small-cap stocks.
- `HML` is especially important because `FCNTX` and `AGTHX` are growth-oriented funds, so a growth-versus-value tilt is a central style question.
- `RMW` and `CMA` are useful because active managers often favor firms with particular profitability and investment characteristics.
- `MOM` is included because growth funds can overlap with winner-chasing or trend-following behavior.

I also add one non-core factor, `LT_Rev` (long-term reversal), as a style-based extension. I chose `LT_Rev` because growth managers often hold firms with strong multi-year prior performance, so an apparent “alpha” may actually reflect exposure to long-horizon winner/loser cycles not fully captured by the standard models. This is a cleaner extension than `ST_Rev`, which is more suited to short-horizon trading strategies, and more appropriate than industry portfolios or accounting-sorted anomalies for this assignment, which is mainly about parsimonious factor attribution. I also did not use `BAB` as the main extension because these funds are not low-beta products, and I did not use `QMJ` as the main extension because part of the quality story already overlaps with `RMW` and `CMA` in the Fama-French framework.

## Data and Regression Setup
Monthly adjusted price data for `SPY`, `FCNTX`, and `AGTHX` were obtained from Alpha Vantage. Factor data were obtained from the Kenneth French Data Library, including the Fama-French five factors, momentum, and the long-term reversal factor. Monthly simple returns were computed from adjusted prices, and the dependent variable in all regressions is monthly excess return:

`R_i - R_f`

where `R_i` is the asset return and `R_f` is the risk-free rate. The final regression sample contains 59 monthly observations.

I estimated four models:

1. `CAPM`
2. `Carhart 4-factor`
3. `Fama-French 5-factor`
4. `FF5 + LT_Rev`

The first three models are the standard sequence. The fourth model is the main extension used to test whether the active growth funds also load on long-horizon reversal behavior.

## Regression Results

### Table 1. CAPM Results
| Asset | Alpha | p-value | Market Beta | R-squared |
| --- | ---: | ---: | ---: | ---: |
| SPY | 0.0013 | 0.0557 | 0.9750 | 0.9872 |
| FCNTX | 0.0018 | 0.4099 | 1.0161 | 0.8826 |
| AGTHX | -0.0016 | 0.3822 | 1.0990 | 0.9325 |
| ACTIVE_EW | 0.0001 | 0.9370 | 1.0576 | 0.9263 |

### Table 2. FF5 + LT_Rev Results
| Asset | Alpha | p-value | Mkt-RF | SMB | HML | RMW | CMA | LT_Rev | R-squared | Adj. R-squared |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| SPY | 0.0001 | 0.8685 | 0.9974 | -0.0865 | 0.0211 | 0.0855 | 0.0350 | -0.0136 | 0.9969 | 0.9966 |
| FCNTX | 0.0016 | 0.3614 | 1.0121 | -0.2431 | -0.1393 | 0.0024 | -0.0558 | -0.0306 | 0.9465 | 0.9403 |
| AGTHX | 0.0007 | 0.5953 | 1.0483 | -0.0460 | -0.0571 | -0.2500 | -0.0462 | -0.1270 | 0.9742 | 0.9712 |
| ACTIVE_EW | 0.0011 | 0.3937 | 1.0302 | -0.1446 | -0.0982 | -0.1238 | -0.0510 | -0.0788 | 0.9699 | 0.9664 |

Carhart results show that the momentum coefficients for `FCNTX`, `AGTHX`, and `ACTIVE_EW` are all near zero and statistically insignificant, so short-horizon momentum is not the main driver of these funds in this sample.

## Interpretation
The main result is that none of the active strategies generates statistically significant alpha. Under CAPM, `FCNTX` has a positive alpha and `AGTHX` has a negative alpha, but neither is significant. After controlling for broader style factors in Carhart, FF5, and `FF5 + LT_Rev`, the same conclusion remains. This means the data do not support the claim that these managers produced persistent abnormal return after adjusting for common risk exposures.

The market betas are all close to one, with `AGTHX` and `ACTIVE_EW` slightly above one. This shows that the funds are basically full-equity market vehicles, not niche or defensive strategies. That helps explain why `SPY`, `FCNTX`, and `AGTHX` all moved strongly with the broad U.S. market during the sample period.

The negative `SMB` and `HML` coefficients are especially informative. For `FCNTX`, `SMB = -0.2431` and `HML = -0.1393`, which indicates a large-cap growth tilt. `ACTIVE_EW` shows the same pattern. This is exactly what we would expect from active growth funds concentrated in well-known U.S. companies rather than small-cap or deep-value stocks. The factor choice was therefore justified ex ante and confirmed ex post by the regression output.

`AGTHX` provides the most interesting extended result. In the baseline FF5 model, it already shows a negative `RMW` loading, meaning it does not behave like a high-profitability tilt. After adding `LT_Rev`, the long-term reversal beta is `-0.1270` with `p = 0.0489`, which is statistically significant. A negative loading means the fund behaves more like a portfolio of long-horizon winners than a reversal strategy that profits from long-run losers rebounding. This fits the intuition that a growth manager may hold firms with persistent multi-year leadership rather than names that have been weak for several years.

The change in model fit also matters. For `AGTHX`, `R-squared` rises from `0.9721` in FF5 to `0.9742` in `FF5 + LT_Rev`, and the absolute `HML` loading becomes smaller. That suggests some of what initially looked like pure growth exposure may actually be tied to long-horizon winner behavior. In contrast, `FCNTX` and `ACTIVE_EW` also have negative `LT_Rev` betas, but those coefficients are not statistically significant, so the evidence is much weaker there.

This is exactly the concept the assignment is trying to teach. A fund can look attractive in raw returns, but once returns are decomposed into systematic factors, the interpretation changes. In this project, the active funds do not show strong alpha. Instead, they look like funds whose returns are largely explained by exposure to the equity market, large-cap growth characteristics, and in the case of `AGTHX`, some exposure to long-horizon winner behavior. The regression therefore converts “performance” into a more defensible story about style exposure.

## Conclusion
The results imply that `SPY`, `FCNTX`, `AGTHX`, and `ACTIVE_EW` were all driven primarily by common market forces over 2021-2025. The passive benchmark behaves as expected, with beta near one and alpha near zero. The active funds also do not produce statistically significant alpha, so their performance should not be interpreted as clear evidence of manager skill. Their returns are better understood as a combination of market exposure, large-cap growth tilts, and, for `AGTHX`, a significant negative loading on the long-term reversal factor. This makes `LT_Rev` a useful extension because it adds a style-consistent explanation rather than simply increasing model complexity.
