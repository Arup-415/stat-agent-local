def choose_test(question: str):
    """
    Determine which statistical test should be executed.
    """

    q = question.lower()

    if any(word in q for word in ["normal", "normality", "normally distributed"]):
        return "shapiro"

    if any(word in q for word in ["stationary", "stationarity", "time series"]):
        return "adfuller"

    if any(word in q for word in ["correlation", "relationship"]):
        return "pearson"

    if any(word in q for word in ["t test", "t-test", "compare two groups"]):
        return "ttest"

    if "anova" in q:
        return "anova"

    return "unknown"


