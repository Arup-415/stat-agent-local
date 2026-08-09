current_dataframe = None


def set_dataframe(df):
    global current_dataframe
    current_dataframe = df


def get_dataframe():
    return current_dataframe


def clear_dataframe():
    global current_dataframe
    current_dataframe = None