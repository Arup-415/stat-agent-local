def choose_test(question: str):
    """
    Determine which statistical test should be executed.
    """

    q = question.lower()

    if any(word in q for word in ["normal", "normality", "normally distributed", "shapiro"]):
        return "shapiro"

    if "kpss" in q:
        return "kpss"

    if any(word in q for word in ["adf", "augmented dickey", "stationary", "stationarity", "time series"]):
        return "adf"

    if any(word in q for word in ["spearman", "rank correlation"]):
        return "spearman"

    if any(word in q for word in ["correlation", "relationship"]):
        return "pearson"

    if any(word in q for word in ["paired", "before after", "pre post"]):
        return "paired_ttest"

    if any(word in q for word in ["mann-whitney", "mann whitney"]):
        return "mann_whitney"

    if "wilcoxon" in q:
        return "wilcoxon"

    if any(word in q for word in ["kruskal", "nonparametric anova"]):
        return "kruskal"

    if any(word in q for word in ["chi square", "chi-square", "chi-square test"]):
        return "chi_square"

    if any(word in q for word in ["correlation matrix", "heatmap"]):
        return "correlation_matrix"

    if any(word in q for word in ["missing", "null values", "missingness"]):
        return "missing"

    if "outlier" in q:
        return "outliers"

    if any(word in q for word in ["dataset summary", "dataset overview", "describe dataset"]):
        return "summary"

    if any(word in q for word in ["descriptive", "describe", "summary statistics"]):
        return "descriptive"

    if "confidence interval" in q:
        return "confidence_interval"

    if any(word in q for word in ["t test", "t-test", "compare two groups"]):
        return "ttest"

    if "anova" in q:
        return "anova"

    return "unknown"


