from app.profiler import (
    dataset_summary,
    numerical_summary,
    missing_value_percentage,
    categorical_summary,
    correlation_matrix,
    detect_outliers_iqr,
)

from app.llm import ask_llm


def analyze_dataset(df):
    """
    Perform a complete statistical analysis of the dataset.
    """

    summary = dataset_summary(df)

    numerical = numerical_summary(df)

    missing = missing_value_percentage(df).to_dict()

    categorical = categorical_summary(df)

    correlation = correlation_matrix(df).round(3).to_dict()

    outliers = detect_outliers_iqr(df)

    prompt = f"""
You are an expert statistician.

Analyze the following dataset summary.

Dataset Summary:
{summary}

Numerical Summary:
{numerical}

Missing Values:
{missing}

Categorical Summary:
{categorical}

Based on this information, provide:

1. Dataset Overview
2. Data Quality Issues
3. Possible Outlier Concerns
4. Correlation Insights
5. Statistical Recommendations
6. Final Conclusion

Keep the explanation easy to understand.
"""

    ai_report = ask_llm(prompt)

    return {
        "Dataset Summary": summary,
        "Numerical Summary": numerical,
        "Missing Values": missing,
        "Categorical Summary": categorical,
        "Correlation Matrix": correlation,
        "Outliers": outliers,
        "AI Report": ai_report,
    }