import pandas as pd

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
    paired_ttest,
    mann_whitney_test,
    wilcoxon_test,
    chi_square_test,
    kruskal_test,
)

from app.recommender import recommend_test
from app.memory import memory as default_memory
from app.analyzer import analyze_dataset
from app.profiler import (
    dataset_summary,
    missing_value_percentage,
    detect_outliers_iqr,
    correlation_matrix,
)


def _groups_from_columns(df, columns):
    if df is None or len(columns) < 2:
        return None, []

    numeric_column = next(
        (name for name in columns if pd.api.types.is_numeric_dtype(df[name])),
        None,
    )
    group_column = next((name for name in columns if name != numeric_column), None)
    if numeric_column is None or group_column is None:
        return None, []

    values = pd.to_numeric(df[numeric_column], errors="coerce")
    usable = pd.DataFrame({"value": values, "group": df[group_column]}).dropna()
    groups = [part["value"].to_numpy() for _, part in usable.groupby("group", observed=True, sort=False)]
    return groups, [numeric_column, group_column]


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

    memory = kwargs.get("conversation_memory", default_memory)

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
    # COMPLETE DATASET ANALYSIS
    # ==================================================

    if any (phrase in question.lower() for phrase in [
         "analyze my dataset",
         "analyse my dataset",
         "analyze dataset",
         "analyse dataset",
         "full analysis",
         "complete analysis",
         "analyze the dataset",
         "analyse the dataset",
    ]):

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
    # PAIRED AND NON-PARAMETRIC TESTS
    # ==================================================

    elif test in {"paired_ttest", "wilcoxon"}:
        if df is None:
            return {"Error": "No dataset loaded. Please upload a CSV first."}
        if len(columns) < 2:
            return {"Error": "Please specify two paired numeric columns."}

        paired = df[columns[:2]].apply(pd.to_numeric, errors="coerce").dropna()
        if len(paired) < 2:
            return {"Error": "At least two complete pairs are required."}
        result = paired_ttest(paired.iloc[:, 0], paired.iloc[:, 1]) if test == "paired_ttest" else wilcoxon_test(paired.iloc[:, 0], paired.iloc[:, 1])
        response = {"Test": "Paired t-test" if test == "paired_ttest" else "Wilcoxon signed-rank test", "Columns": columns[:2], "Result": result}
        memory.update(question=question, result=response, dataframe=df)
        return response

    elif test in {"mann_whitney", "kruskal"}:
        groups = kwargs.get("groups")
        group_columns = columns[:2]
        if groups is None:
            groups, group_columns = _groups_from_columns(df, columns)
        if groups is None or len(groups) < 2 or any(len(group) < 2 for group in groups):
            return {"Error": "Select a numeric outcome and a group column with at least two observations per group."}
        if test == "mann_whitney" and len(groups) != 2:
            return {"Error": "The Mann-Whitney U test requires exactly two groups."}
        result = mann_whitney_test(*groups) if test == "mann_whitney" else kruskal_test(*groups)
        response = {"Test": "Mann-Whitney U test" if test == "mann_whitney" else "Kruskal-Wallis test", "Columns": group_columns, "Result": result}
        memory.update(question=question, result=response, dataframe=df)
        return response

    elif test == "chi_square":
        if df is None:
            return {"Error": "No dataset loaded. Please upload a CSV first."}
        if len(columns) < 2:
            return {"Error": "Please specify two categorical columns."}
        table = pd.crosstab(df[columns[0]], df[columns[1]])
        if table.shape[0] < 2 or table.shape[1] < 2:
            return {"Error": "Each categorical column must contain at least two observed categories."}
        result = chi_square_test(table.to_numpy())
        response = {"Test": "Chi-square test of independence", "Columns": columns[:2], "Result": result}
        memory.update(question=question, result=response, dataframe=df)
        return response

    # ==================================================
    # INDEPENDENT T TEST
    # ==================================================

    elif test == "ttest":
        groups = kwargs.get("groups")
        group_columns = columns[:2]
        if groups is None:
            groups, group_columns = _groups_from_columns(df, columns)
        if groups is None or len(groups) != 2 or any(len(group) < 2 for group in groups):
            return {"Error": "Select a numeric outcome and a grouping column containing exactly two groups with at least two observations each."}

        result = independent_ttest(*groups)

        explanation = ask_llm(
            TTEST_PROMPT.format(
                stat=result["Statistic"],
                pvalue=result["P-Value"],
            )
        )

        response = {
            "Test": "Independent T-Test",
            "Columns": group_columns,
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
        group_columns = columns[:2]
        if groups is None:
            groups, group_columns = _groups_from_columns(df, columns)
        if groups is None or len(groups) < 2 or any(len(group) < 2 for group in groups):
            return {"Error": "Select a numeric outcome and a grouping column with at least two observations in each group."}

        result = one_way_anova(*groups)

        explanation = ask_llm(
            ANOVA_PROMPT.format(
                stat=result["F Statistic"],
                pvalue=result["P-Value"],
            )
        )

        response = {
            "Test": "One Way ANOVA",
            "Columns": group_columns,
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
            "Result": result,
        }

        memory.update(
            question=question,
            result=response,
            dataframe=df
        )

        return response

    elif test == "summary":
        if df is None:
            return {"Error": "No dataset loaded."}
        response = {"Test": "Dataset overview", "Result": dataset_summary(df)}
        memory.update(question=question, result=response, dataframe=df)
        return response

    elif test == "missing":
        if df is None:
            return {"Error": "No dataset loaded."}
        response = {"Test": "Missing value analysis", "Result": missing_value_percentage(df).to_dict()}
        memory.update(question=question, result=response, dataframe=df)
        return response

    elif test == "outliers":
        if df is None:
            return {"Error": "No dataset loaded."}
        response = {"Test": "IQR outlier analysis", "Result": detect_outliers_iqr(df)}
        memory.update(question=question, result=response, dataframe=df)
        return response

    elif test == "correlation_matrix":
        if df is None:
            return {"Error": "No dataset loaded."}
        response = {"Test": "Pearson correlation matrix", "Result": correlation_matrix(df).to_dict()}
        memory.update(question=question, result=response, dataframe=df)
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