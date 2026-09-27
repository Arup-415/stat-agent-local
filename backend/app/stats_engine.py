from scipy import stats
from statsmodels.tsa.stattools import adfuller, kpss
import numpy as np
import pandas as pd


# -----------------------------------------------------
# NORMALITY TEST
# -----------------------------------------------------

def shapiro_test(df, column):
    data = df[column].dropna()

    stat, p = stats.shapiro(data)

    return {
        "Statistic": stat,
        "P-Value": p,
        "Normally Distributed": p > 0.05
    }


# -----------------------------------------------------
# T TEST
# -----------------------------------------------------

def independent_ttest(group1, group2):

    stat, p = stats.ttest_ind(
        group1,
        group2,
        equal_var=False
    )

    return {
        "Statistic": stat,
        "P-Value": p,
        "Significant": p < 0.05
    }


# -----------------------------------------------------
# PAIRED T TEST
# -----------------------------------------------------

def paired_ttest(before, after):

    stat, p = stats.ttest_rel(before, after)

    return {
        "Statistic": stat,
        "P-Value": p,
        "Significant": p < 0.05
    }


# -----------------------------------------------------
# MANN WHITNEY U TEST
# -----------------------------------------------------

def mann_whitney_test(group1, group2):

    stat, p = stats.mannwhitneyu(
        group1,
        group2,
        alternative="two-sided"
    )

    return {
        "Statistic": stat,
        "P-Value": p,
        "Significant": p < 0.05
    }


# -----------------------------------------------------
# WILCOXON SIGNED RANK TEST
# -----------------------------------------------------

def wilcoxon_test(before, after):

    stat, p = stats.wilcoxon(before, after)

    return {
        "Statistic": stat,
        "P-Value": p,
        "Significant": p < 0.05
    }


# -----------------------------------------------------
# CHI SQUARE TEST
# -----------------------------------------------------

def chi_square_test(table):

    chi2, p, dof, expected = stats.chi2_contingency(table)

    return {
        "Chi Square": chi2,
        "P-Value": p,
        "Degrees of Freedom": dof,
        "Expected Frequency": expected.tolist(),
        "Significant": p < 0.05
    }


# -----------------------------------------------------
# PEARSON CORRELATION
# -----------------------------------------------------

def pearson_corr(x, y):

    corr, p = stats.pearsonr(x, y)

    return {
        "Correlation": corr,
        "P-Value": p,
        "Significant": p < 0.05
    }


# -----------------------------------------------------
# SPEARMAN CORRELATION
# -----------------------------------------------------

def spearman_corr(x, y):

    corr, p = stats.spearmanr(x, y)

    return {
        "Correlation": corr,
        "P-Value": p,
        "Significant": p < 0.05
    }


# -----------------------------------------------------
# ONE WAY ANOVA
# -----------------------------------------------------

def one_way_anova(*groups):

    stat, p = stats.f_oneway(*groups)

    return {
        "F Statistic": stat,
        "P-Value": p,
        "Significant": p < 0.05
    }


# -----------------------------------------------------
# KRUSKAL WALLIS TEST
# -----------------------------------------------------

def kruskal_test(*groups):

    stat, p = stats.kruskal(*groups)

    return {
        "Statistic": stat,
        "P-Value": p,
        "Significant": p < 0.05
    }


# -----------------------------------------------------
# ADF TEST
# -----------------------------------------------------

def adf_test(series):

    result = adfuller(series.dropna())

    return {
        "ADF Statistic": result[0],
        "P-Value": result[1],
        "Lags Used": result[2],
        "Observations": result[3],
        "Critical Values": result[4],
        "Stationary": result[1] < 0.05
    }


# -----------------------------------------------------
# KPSS TEST
# -----------------------------------------------------

def kpss_test(series):

    result = kpss(series.dropna(), regression="c")

    return {
        "KPSS Statistic": result[0],
        "P-Value": result[1],
        "Lags Used": result[2],
        "Critical Values": result[3],
        "Stationary": result[1] > 0.05
    }


# -----------------------------------------------------
# DESCRIPTIVE STATISTICS
# -----------------------------------------------------

def descriptive_statistics(df):
    numerical = df.select_dtypes(include=np.number)

    if numerical.empty:
        return {
            "available": False,
            "message": "No numerical variables found in the dataset.",
            "statistics": {}
        }

    return {
        "available": True,
        "message": "Numerical descriptive statistics calculated successfully.",
        "statistics": numerical.describe().T.to_dict(orient="index")
    }
# -----------------------------------------------------
# CONFIDENCE INTERVAL
# -----------------------------------------------------

def confidence_interval(data, confidence=0.95):

    data = np.array(data)

    mean = np.mean(data)

    sem = stats.sem(data)

    interval = stats.t.interval(
        confidence,
        len(data)-1,
        loc=mean,
        scale=sem
    )

    return {
        "Mean": mean,
        "Lower Bound": interval[0],
        "Upper Bound": interval[1]
    }


def test_assumptions(test_name):
    guidance = {
        "shapiro": [
            "Requires 3 to 5,000 usable observations; a non-significant result does not prove normality.",
            "Observations should be independent and representative of the population.",
        ],
        "confidence-interval": [
            "This is a 95% t-based confidence interval for the mean.",
            "Interpretation assumes independent, representative observations; skew and outliers matter for small samples.",
        ],
        "adf": [
            "The row order must be the time order, with equally spaced observations.",
            "This configuration includes an intercept and no trend term; structural breaks can affect the result.",
        ],
        "kpss": [
            "The row order must be the time order, with equally spaced observations.",
            "This configuration tests level stationarity with a constant; structural breaks can affect the result.",
        ],
        "pearson": [
            "Measures linear association; inspect a scatterplot for curvature and influential outliers.",
            "Pairs should be independent; the p-value also relies on distributional assumptions.",
        ],
        "spearman": [
            "Measures monotonic rank association, not necessarily a linear relationship.",
            "Pairs should be independent; many tied ranks can affect the p-value approximation.",
        ],
        "paired-t-test": [
            "Rows must form valid matched pairs, and different pairs should be independent.",
            "The paired differences should be approximately normal, especially for small samples.",
        ],
        "wilcoxon": [
            "Rows must form valid matched pairs, and different pairs should be independent.",
            "A symmetric distribution of paired differences is needed for a location-shift interpretation.",
        ],
        "independent-t-test": [
            "Groups should be independent, with approximately normal outcomes within each group for small samples.",
            "Welch's test does not assume equal group variances; observations within each group must still be independent.",
        ],
        "mann-whitney": [
            "Groups should be independent; this test compares rank distributions, not always medians.",
            "A median-shift interpretation requires similarly shaped group distributions.",
        ],
        "anova": [
            "Groups should be independent; residuals should be approximately normal with similar variances.",
            "A significant omnibus result does not identify which groups differ; post-hoc testing is not included.",
        ],
        "kruskal": [
            "Groups should be independent; similarly shaped distributions are needed for a median comparison.",
            "A significant omnibus result does not identify which groups differ; post-hoc testing is not included.",
        ],
        "chi-square": [
            "Observations should be independent, and each record should contribute to one cell only.",
            "The chi-square approximation may be unreliable when expected cell counts are small; see diagnostics.",
        ],
    }
    return guidance.get(test_name, [])