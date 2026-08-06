SHAPIRO_PROMPT = """
You are a statistics expert.

Explain the following Shapiro-Wilk test result.

Statistic:
{stat}

P-value:
{pvalue}

Explain:
1. Null hypothesis
2. Interpretation
3. Final conclusion
4. Keep it under 150 words.
"""

ADF_PROMPT = """
You are a time-series expert.

Explain the following Augmented Dickey-Fuller test.

Statistic:
{stat}

P-value:
{pvalue}

Explain:
1. Null hypothesis
2. Interpretation
3. Final conclusion
4. Keep it under 150 words.
"""

PEARSON_PROMPT = """
Explain the following Pearson correlation result.

Correlation:
{stat}

P-value:
{pvalue}

Keep the explanation concise.
"""

TTEST_PROMPT = """
Explain the following Independent T-Test.

Statistic:
{stat}

P-value:
{pvalue}

Keep the explanation concise.
"""

ANOVA_PROMPT = """
Explain the following One-Way ANOVA result.

Statistic:
{stat}

P-value:
{pvalue}

Keep the explanation concise.
"""