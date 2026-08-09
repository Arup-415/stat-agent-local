from app.llm import ask_llm


def recommend_test(question: str):

    q = question.lower()

    # -------------------------------------------------
    # Two Independent Groups
    # -------------------------------------------------

    if (
        "two groups" in q
        or "independent groups" in q
        or "compare two groups" in q
    ):

        return {
            "Recommended Test": "Independent T-Test",
            "Reason":
                "Compare the means of two independent groups when data is approximately normal."
        }

    # -------------------------------------------------
    # Paired Samples
    # -------------------------------------------------

    elif (
        "paired" in q
        or "before after" in q
        or "pre post" in q
    ):

        return {
            "Recommended Test": "Paired T-Test",
            "Reason":
                "Compare two measurements from the same subjects."
        }

    # -------------------------------------------------
    # Nonparametric Two Groups
    # -------------------------------------------------

    elif (
        "non normal" in q
        or "non-normal" in q
        or "not normal" in q
    ):

        return {
            "Recommended Test": "Mann-Whitney U Test",
            "Reason":
                "Non-parametric alternative to the independent t-test."
        }

    # -------------------------------------------------
    # Three or More Groups
    # -------------------------------------------------

    elif (
        "three groups" in q
        or "more than two groups" in q
        or "multiple groups" in q
    ):

        return {
            "Recommended Test": "One-Way ANOVA",
            "Reason":
                "Compare means across three or more independent groups."
        }

    # -------------------------------------------------
    # Correlation
    # -------------------------------------------------

    elif "correlation" in q:

        return {
            "Recommended Test": "Pearson or Spearman Correlation",
            "Reason":
                "Use Pearson for normally distributed continuous variables; otherwise use Spearman."
        }

    # -------------------------------------------------
    # Categorical Variables
    # -------------------------------------------------

    elif (
        "categorical" in q
        or "association" in q
        or "contingency" in q
    ):

        return {
            "Recommended Test": "Chi-Square Test",
            "Reason":
                "Tests the association between categorical variables."
        }

    # -------------------------------------------------
    # Time Series
    # -------------------------------------------------

    elif (
        "time series" in q
        or "stationary" in q
        or "stationarity" in q
    ):

        return {
            "Recommended Test": "ADF and KPSS Tests",
            "Reason":
                "Check stationarity before fitting forecasting models."
        }

    # -------------------------------------------------
    # Fallback to LLM
    # -------------------------------------------------

    answer = ask_llm(
        f"""
You are an expert statistician.

Recommend the most appropriate statistical test.

Question:

{question}

Respond in the following format:

Recommended Test:
Reason:
"""
    )

    return {
        "Recommendation": answer
    }