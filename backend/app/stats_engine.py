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