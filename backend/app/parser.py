import re


# -----------------------------------------------------
# COLUMN EXTRACTION
# -----------------------------------------------------

def extract_columns(question, dataframe):
    """
    Find dataframe column names mentioned in the user's question.
    """

    question_lower = question.lower()

    matched = []

    for col in dataframe.columns:
        if col.lower() in question_lower:
            matched.append(col)

    return matched


# -----------------------------------------------------
# NUMBER EXTRACTION
# -----------------------------------------------------

def extract_numbers(question):
    """
    Extract numeric values from the question.
    """

    numbers = re.findall(r"\d+\.?\d*", question)

    return [float(x) for x in numbers]


# -----------------------------------------------------
# TEST IDENTIFICATION
# -----------------------------------------------------

def choose_test(question):
    """
    Identify which statistical test the user is asking for.
    """

    q = question.lower()

    test_keywords = {

        "shapiro": [
            "shapiro",
            "normal",
            "normality",
            "normally distributed",
            "gaussian",
            "bell curve"
        ],

        "ttest": [
            "independent t",
            "t test",
            "ttest",
            "compare means",
            "difference in means"
        ],

        "paired_ttest": [
            "paired t",
            "paired test",
            "before after",
            "pre post"
        ],

        "mann_whitney": [
            "mann whitney",
            "mann-whitney",
            "nonparametric two groups"
        ],

        "wilcoxon": [
            "wilcoxon",
            "signed rank"
        ],

        "chi_square": [
            "chi square",
            "chi-square",
            "chisquare",
            "independence test"
        ],

        "pearson": [
            "pearson",
            "linear correlation"
        ],

        "spearman": [
            "spearman",
            "rank correlation"
        ],

        "anova": [
            "anova",
            "one way anova",
            "compare multiple groups"
        ],

        "kruskal": [
            "kruskal",
            "kruskal wallis",
            "nonparametric anova"
        ],

        "adf": [
            "adf",
            "augmented dickey fuller",
            "stationary",
            "stationarity",
            "unit root"
        ],

        "kpss": [
            "kpss"
        ],

        "summary": [
            "summary",
            "dataset summary",
            "overview",
            "describe dataset"
        ],

        "descriptive": [
            "descriptive statistics",
            "describe",
            "statistics"
        ],

        "missing": [
            "missing",
            "null",
            "nan",
            "missing values"
        ],

        "correlation": [
            "correlation matrix",
            "heatmap"
        ],

        "outliers": [
            "outlier",
            "outliers",
            "iqr"
        ]

    }

    for test_name, keywords in test_keywords.items():

        for keyword in keywords:

            if keyword in q:
                return test_name

    return None