from app.router import choose_test
from app.llm import ask_llm
from app.prompts import *

from app.parser import extract_columns

from app.stats_engine import (
    shapiro_test,
    adf_test,
    kpss_test,
    pearson_corr,
    spearman_corr,
    one_way_anova,
    descriptive_statistics,
    confidence_interval,
    independent_ttest,
)

from app.recommender import recommend_test
from app.memory import memory
from app.analyzer import analyze_dataset


def ask_agent(question, df=None, **kwargs):
    """
    Main AI Statistics Agent.

    The agent:
    1. Detects the statistical test.
    2. Detects columns from the user's question.
    3. Uses previous conversation context when available.
    4. Runs the appropriate statistical analysis.
    5. Generates explanations using the LLM.
    6. Stores the interaction in memory.
    """

    # --------------------------------------------------
    # GET PREVIOUS MEMORY
    # --------------------------------------------------

    previous_question = kwargs.get(
        "previous_question",
        memory.get_last_question()
    )

    previous_result = kwargs.get(
        "previous_result",
        memory.get_last_result()
    )

    # --------------------------------------------------
    # TEST DETECTION
    # --------------------------------------------------

    test = choose_test(question)

    # --------------------------------------------------
    # COLUMN DETECTION
    # --------------------------------------------------

    columns = []

    if df is not None:
        columns = extract_columns(question, df)

    # ==================================================
    # SHAPIRO-WILK TEST
    # ==================================================

    if test == "shapiro":

        if df is None:
            return {
                "Error": "No dataset loaded. Please upload a CSV first."
            }

        column = columns[0] if columns else kwargs.get("column")

        if column is None:
            return {
                "Error": "No column found in the question."
            }

        result = shapiro_test(df, column)

        explanation = ask_llm(
            SHAPIRO_PROMPT.format(
                stat=result["Statistic"],
                pvalue=result["P-Value"],
            )
        )

        response = {
            "Test": "Shapiro-Wilk Test",
            "Column": column,
            "Result": result,
            "Explanation": explanation,
        }

        memory.update(
            question=question,
            result=response,
            dataframe=df
        )

        return response

    # ==================================================
    # ADF TEST
    # ==================================================

    elif test == "adf":

        if df is None:
            return {
                "Error": "No dataset loaded. Please upload a CSV first."
            }

        column = columns[0] if columns else kwargs.get("column")

        if column is None:
            return {
                "Error": "No column found in the question."
            }

        result = adf_test(df[column])

        explanation = ask_llm(
            ADF_PROMPT.format(
                stat=result["ADF Statistic"],
                pvalue=result["P-Value"],
            )
        )

        response = {
            "Test": "ADF Test",
            "Column": column,
            "Result": result,
            "Explanation": explanation,
        }

        memory.update(
            question=question,
            result=response,
            dataframe=df
        )

        return response

    # ==================================================
    # KPSS TEST
    # ==================================================

    elif test == "kpss":

        if df is None:
            return {
                "Error": "No dataset loaded. Please upload a CSV first."
            }

        column = columns[0] if columns else kwargs.get("column")

        if column is None:
            return {
                "Error": "No column found in the question."
            }

        result = kpss_test(df[column])

        explanation = ask_llm(
            f"""
Explain these KPSS test results in simple language.

KPSS Statistic: {result["KPSS Statistic"]}
P-Value: {result["P-Value"]}

Tell the user whether the data is stationary.

If p-value is greater than 0.05:
the data is considered stationary.

If p-value is less than or equal to 0.05:
the data is considered non-stationary.
"""
        )

        response = {
            "Test": "KPSS Test",
            "Column": column,
            "Result": result,
            "Explanation": explanation,
        }

        memory.update(
            question=question,
            result=response,
            dataframe=df
        )

        return response

    # ==================================================
    # PEARSON CORRELATION
    # ==================================================

    elif test == "pearson":

        if df is None:
            return {
                "Error": "No dataset loaded. Please upload a CSV first."
            }

        if len(columns) >= 2:
            x, y = columns[:2]
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
                pvalue=result["P-Value"],
            )
        )

        response = {
            "Test": "Pearson Correlation",
            "Columns": [x, y],
            "Result": result,
            "Explanation": explanation,
        }

        memory.update(
            question=question,
            result=response,
            dataframe=df
        )

        return response

    # ==================================================
    # SPEARMAN CORRELATION
    # ==================================================

    elif test == "spearman":

        if df is None:
            return {
                "Error": "No dataset loaded. Please upload a CSV first."
            }

        if len(columns) >= 2:
            x, y = columns[:2]
        else:
            x = kwargs.get("x")
            y = kwargs.get("y")

        if x is None or y is None:
            return {
                "Error": "Please specify two numeric columns."
            }

        result = spearman_corr(df[x], df[y])

        explanation = ask_llm(
            f"""
Explain these Spearman correlation results in simple language.

Correlation: {result["Correlation"]}
P-Value: {result["P-Value"]}

State:

1. Direction of the relationship.
2. Strength of the relationship.
3. Whether the relationship is statistically significant.

Use a 0.05 significance level.
"""
        )

        response = {
            "Test": "Spearman Correlation",
            "Columns": [x, y],
            "Result": result,
            "Explanation": explanation,
        }

        memory.update(
            question=question,
            result=response,
            dataframe=df
        )

        return response

    # ==================================================
    # INDEPENDENT T TEST
    # ==================================================

    elif test == "ttest":

        group1 = kwargs.get("group1")
        group2 = kwargs.get("group2")

        if group1 is None or group2 is None:
            return {
                "Error": "Please provide group1 and group2."
            }

        result = independent_ttest(
            group1,
            group2
        )

        explanation = ask_llm(
            TTEST_PROMPT.format(
                stat=result["Statistic"],
                pvalue=result["P-Value"],
            )
        )

        response = {
            "Test": "Independent T-Test",
            "Result": result,
            "Explanation": explanation,
        }

        memory.update(
            question=question,
            result=response,
            dataframe=df
        )

        return response

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
                pvalue=result["P-Value"],
            )
        )

        response = {
            "Test": "One Way ANOVA",
            "Result": result,
            "Explanation": explanation,
        }

        memory.update(
            question=question,
            result=response,
            dataframe=df
        )

        return response

    # ==================================================
    # TEST RECOMMENDATION
    # ==================================================

    elif (
        "recommend" in question.lower()
        or "which test" in question.lower()
        or "what test" in question.lower()
        or "which statistical test" in question.lower()
    ):

        recommendation = recommend_test(question)

        response = {
            "Test": "Statistical Test Recommendation",
            "Recommendation": recommendation,
        }

        memory.update(
            question=question,
            result=response,
            dataframe=df
        )

        return response

    # ==================================================
    # COMPLETE DATASET ANALYSIS
    # ==================================================

    elif (
        "analyze my dataset" in question.lower()
        or "analyse my dataset" in question.lower()
        or "analyze dataset" in question.lower()
        or "analyse dataset" in question.lower()
        or "full analysis" in question.lower()
        or "complete analysis" in question.lower()
    ):

        if df is None:
            return {
                "Error": "Please upload a dataset first."
            }

        response = analyze_dataset(df)

        memory.update(
            question=question,
            result=response,
            dataframe=df
        )

        return response

    # ==================================================
    # DESCRIPTIVE STATISTICS
    # ==================================================

    elif (
        test == "descriptive"
        or "describe" in question.lower()
        or "descriptive statistics" in question.lower()
    ):

        if df is None:
            return {
                "Error": "No dataset loaded."
            }

        result = descriptive_statistics(df)

        response = {
            "Test": "Descriptive Statistics",
            "Result": result.to_dict(),
        }

        memory.update(
            question=question,
            result=response,
            dataframe=df
        )

        return response

    # ==================================================
    # CONFIDENCE INTERVAL
    # ==================================================

    elif "confidence" in question.lower():

        data = kwargs.get("data")

        if data is None and df is not None and columns:
            data = df[columns[0]]

        if data is None:
            return {
                "Error": "Please provide data or specify a column."
            }

        confidence = kwargs.get(
            "confidence",
            0.95
        )

        result = confidence_interval(
            data,
            confidence
        )

        response = {
            "Test": "Confidence Interval",
            "Result": result,
        }

        memory.update(
            question=question,
            result=response,
            dataframe=df
        )

        return response

    # ==================================================
    # DEFAULT LLM RESPONSE WITH MEMORY
    # ==================================================

    else:

        context = ""

        if previous_question is not None:
            context += (
                f"\nPrevious question: {previous_question}\n"
            )

        if previous_result is not None:
            context += (
                f"\nPrevious result: {previous_result}\n"
            )

        prompt = f"""
You are a Statistics AI Assistant.

The user is working with a statistical dataset.

Use the previous conversation context when it is relevant.

{context}

Current question:
{question}

Answer clearly and concisely.
If the question refers to a previous result, use that result.
Do not invent statistical results that are not available.
"""

        response = {
            "Response": ask_llm(prompt)
        }

        memory.update(
            question=question,
            result=response,
            dataframe=df
        )

        return response