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