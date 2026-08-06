import re


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


def extract_numbers(question):
    """
    Extract numeric values from the question.
    """

    numbers = re.findall(r"\d+\.?\d*", question)

    return [float(x) for x in numbers]