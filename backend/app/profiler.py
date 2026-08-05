import pandas as pd
import numpy as np

def load_data(file_path):
    """
    Load a CSV file into a Pandas DataFrame.
    """

    df = pd.read_csv(file_path)
    return df


def dataset_summary(df):
    """
    Returns basic information about the dataset.
    """

    summary = {
        "Rows": df.shape[0],
        "Columns": df.shape[1],
        "Column Names": list(df.columns),
        "Data Types": df.dtypes.astype(str).to_dict(),
        "Missing Values": df.isnull().sum().to_dict()
    }

    return summary


def numerical_summary(df):
    """
    Returns summary statistics for all numerical columns.
    """

    numerical_df = df.select_dtypes(include=np.number)

    summary = {
        "Mean": numerical_df.mean().to_dict(),
        "Median": numerical_df.median().to_dict(),
        "Standard Deviation": numerical_df.std().to_dict(),
        "Minimum": numerical_df.min().to_dict(),
        "Maximum": numerical_df.max().to_dict(),
        "Skewness": numerical_df.skew().to_dict(),
        "Kurtosis": numerical_df.kurtosis().to_dict()
    }

    return summary



def missing_value_percentage(df):
    """
    Returns missing value count and percentage for each column.
    """

    missing = df.isnull().sum()

    percentage = (missing / len(df)) * 100

    result = pd.DataFrame({
        "Missing Count": missing,
        "Missing Percentage": percentage
    })

    return result


def categorical_summary(df):
    """
    Returns summary for categorical columns.
    """

    categorical_df = df.select_dtypes(include=["object", "category"])

    summary = {}

    for col in categorical_df.columns:
        summary[col] = {
            "Unique Values": categorical_df[col].nunique(),
            "Most Frequent": categorical_df[col].mode()[0] if not categorical_df[col].mode().empty else None,
            "Frequency": categorical_df[col].value_counts().iloc[0] if not categorical_df[col].empty else 0
        }

    return summary


def correlation_matrix(df):
    """
    Returns the correlation matrix for numerical columns.
    """

    numerical_df = df.select_dtypes(include=np.number)

    return numerical_df.corr()



def detect_outliers_iqr(df):
    """
    Detect outliers in numerical columns using the IQR method.
    """

    numerical_df = df.select_dtypes(include=np.number)

    outliers = {}

    for column in numerical_df.columns:
        Q1 = numerical_df[column].quantile(0.25)
        Q3 = numerical_df[column].quantile(0.75)
        IQR = Q3 - Q1

        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR

        outliers[column] = numerical_df[
            (numerical_df[column] < lower) |
            (numerical_df[column] > upper)
        ].index.tolist()

    return outliers