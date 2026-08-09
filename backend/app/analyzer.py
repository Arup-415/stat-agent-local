import numpy as np

from app.profiler import (
    dataset_summary,
    numerical_summary,
    missing_value_percentage,
    categorical_summary,
    correlation_matrix,
    detect_outliers_iqr,
)

from app.llm import ask_llm


def make_json_serializable(obj):
    if isinstance(obj, dict):
        return {
            str(key): make_json_serializable(value)
            for key, value in obj.items()
        }

    if isinstance(obj, list):
        return [
            make_json_serializable(value)
            for value in obj
        ]

    if isinstance(obj, tuple):
        return [
            make_json_serializable(value)
            for value in obj
        ]

    if isinstance(obj, np.integer):
        return int(obj)

    if isinstance(obj, np.floating):
        return float(obj)

    if isinstance(obj, np.ndarray):
        return obj.tolist()

    if isinstance(obj, np.bool_):
        return bool(obj)

    if obj is None:
        return None

    return obj


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

Correlation Matrix:
{correlation}

Outliers:
{outliers}

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

    result = {
        "Dataset Summary": summary,
        "Numerical Summary": numerical,
        "Missing Values": missing,
        "Categorical Summary": categorical,
        "Correlation Matrix": correlation,
        "Outliers": outliers,
        "AI Report": ai_report,
    }

    # Convert EVERYTHING before returning to FastAPI
    return make_json_serializable(result)