from app.router import choose_test
from app.llm import ask_llm
from app.prompts import *

from app.parser import extract_columns

from app.stats_engine import (
    shapiro_test,
    adf_test,
    pearson_corr,
    one_way_anova,
    descriptive_statistics,
    confidence_interval,
    independent_ttest
)


def ask_agent(question, df=None, **kwargs):
    """
    AI Statistics Agent
    """

    test = choose_test(question)

    # Automatically detect columns from question
    columns = []

    if df is not None:
        columns = extract_columns(question, df)

    # ==================================================
    # SHAPIRO TEST
    # ==================================================

    if test == "shapiro":

        if columns:
            column = columns[0]
        else:
            column = kwargs.get("column")

        if column is None:
            return {
                "Error": "No column found in the question."
            }

        result = shapiro_test(df, column)

        explanation = ask_llm(
            SHAPIRO_PROMPT.format(
                stat=result["Statistic"],
                pvalue=result["P-Value"]
            )
        )

        return {
            "Test": "Shapiro-Wilk Test",
            "Column": column,
            "Result": result,
            "Explanation": explanation
        }

    # ==================================================
    # ADF TEST
    # ==================================================

    elif test == "adfuller":

        if columns:
            column = columns[0]
        else:
            column = kwargs.get("column")

        if column is None:
            return {
                "Error": "No column found in the question."
            }

        result = adf_test(df[column])

        explanation = ask_llm(
            ADF_PROMPT.format(
                stat=result["ADF Statistic"],
                pvalue=result["P-Value"]
            )
        )

        return {
            "Test": "ADF Test",
            "Column": column,
            "Result": result,
            "Explanation": explanation
        }

    # ==================================================
    # PEARSON CORRELATION
    # ==================================================

    elif test == "pearson":

        if len(columns) >= 2:
            x = columns[0]
            y = columns[1]
        else:
            x = kwargs.get("x")
            y = kwargs.get("y")

        if x is None or y is None:
            return {
                "Error": "Please specify two numeric columns."
            }

        result = pearson_corr(df[x], df[y])

        explanation = ask_llm(
            PEARSON_PROMPT.format(
                stat=result["Correlation"],
                pvalue=result["P-Value"]
            )
        )

        return {
            "Test": "Pearson Correlation",
            "Columns": [x, y],
            "Result": result,
            "Explanation": explanation
        }

    # ==================================================
    # T TEST
    # ==================================================

    elif test == "ttest":

        group1 = kwargs.get("group1")
        group2 = kwargs.get("group2")

        if group1 is None or group2 is None:
            return {
                "Error": "Please provide group1 and group2."
            }

        result = independent_ttest(group1, group2)

        explanation = ask_llm(
            TTEST_PROMPT.format(
                stat=result["Statistic"],
                pvalue=result["P-Value"]
            )
        )

        return {
            "Test": "Independent T-Test",
            "Result": result,
            "Explanation": explanation
        }

    # ==================================================
    # ANOVA
    # ==================================================

    elif test == "anova":

        groups = kwargs.get("groups")

        if groups is None:
            return {
                "Error": "Please provide groups."
            }

        result = one_way_anova(*groups)

        explanation = ask_llm(
            ANOVA_PROMPT.format(
                stat=result["F Statistic"],
                pvalue=result["P-Value"]
            )
        )

        return {
            "Test": "One Way ANOVA",
            "Result": result,
            "Explanation": explanation
        }

    # ==================================================
    # DESCRIPTIVE STATISTICS
    # ==================================================

    elif "describe" in question.lower():

        result = descriptive_statistics(df)

        return {
            "Test": "Descriptive Statistics",
            "Result": result.to_dict()
        }

    # ==================================================
    # CONFIDENCE INTERVAL
    # ==================================================

    elif "confidence" in question.lower():

        data = kwargs.get("data")

        if data is None:
            return {
                "Error": "Please provide data."
            }

        confidence = kwargs.get("confidence", 0.95)

        result = confidence_interval(data, confidence)

        return {
            "Test": "Confidence Interval",
            "Result": result
        }

    # ==================================================
    # DEFAULT
    # ==================================================

    else:

        return {
            "Response": ask_llm(question)
        }