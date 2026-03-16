# HW2 Assignment Requirements

## Assignment Goal
This assignment asks you to use the instructor's regression template to run factor regressions on asset return data, report `alpha` and factor `betas`, and then write a short `1-2 page` interpretation of the results.

The core idea is not just to show whether a fund or ETF performed well. The real purpose is to decompose performance and answer:

- Can the asset's return be explained by known risk factors?
- If yes, which factors explain it?
- After controlling for those factors, is there any abnormal return left (`alpha`)?

## Main Tasks

### 1. Run the Regression Model
Use the provided regression template and estimate a factor model for the excess return of your chosen asset or portfolio:

```text
R_i - R_f = alpha + beta_1 F_1 + beta_2 F_2 + ... + epsilon
```

This means you are explaining the asset's excess return with one or more common risk factors.

### 2. Report Alpha and Betas
At a minimum, your regression output should include:

- `alpha`
- each factor's `beta`

It is better to also report:

- `p-value`
- `R^2`
- `Adjusted R^2`

These statistics help you evaluate:

- whether `alpha` is statistically significant
- which factors actually have explanatory power
- how well the model fits the return data overall

### 3. Write a 1-2 Page Interpretation
This is the most important part of the assignment. Do not only paste regression tables. You need to explain what the coefficients mean economically.

Your discussion should answer questions such as:

- Which factors mainly explain the fund or ETF return?
- What do the estimated `betas` imply about investment style?
- Is `alpha` positive or negative?
- Is `alpha` statistically significant?
- If `alpha` is not significant, what does that imply?
- If `alpha` is significantly positive, what does that imply?
- Do the conclusions change across different factor models?

## What The Assignment Is Really Testing
This homework is a performance attribution exercise, not just a return comparison.

The instructor wants you to examine:

- whether the fund's performance can be explained by standard risk factors
- which factor exposures drive the return pattern
- whether any abnormal performance remains after controlling for those factors

So the goal is not to force `alpha` to become positive. The goal is to show whether apparent outperformance is really manager skill, or simply exposure to common styles such as market, size, value, profitability, investment, or momentum.

In other words, a fund can look strong in raw returns but still have little true abnormal performance once factor exposures are taken into account.

## Suggested Interpretation Logic
When writing the report, a clean structure is:

1. State which regression model you ran.
2. Report the main coefficients and significance levels.
3. Explain what the factor loadings mean in economic terms.
4. Discuss whether `alpha` remains after controlling for risk factors.
5. Compare conclusions across models if more than one model is used.

## Factors You Can Consider
The standard factors commonly used in this course or in the Kenneth French framework include:

- `Mkt-RF` or market excess return
- `SMB` (size)
- `HML` (value)
- `RMW` (profitability)
- `CMA` (investment)
- `MOM` (momentum)

If the instructor allows model extensions, you may also consider:

- short-term reversal
- long-term reversal

These extended factors can be used to test whether a return pattern that looks like `alpha` is actually related to another known anomaly or style exposure.

## Final Deliverable Checklist
- Run the regression template correctly
- Report `alpha` and all relevant `betas`
- Include `p-value`, `R^2`, and `Adjusted R^2` if available
- Write a `1-2 page` interpretation in complete sentences
- Explain what the results imply about factor exposure and abnormal return
