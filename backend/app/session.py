"""
Session-level dataset storage.

Keeps the currently uploaded dataframe available to
all FastAPI routes inside the running application.
"""

_dataframe = None
_filename = None


def set_dataframe(df, filename=None):
    global _dataframe, _filename

    _dataframe = df
    _filename = filename


def get_dataframe():
    return _dataframe


def get_filename():
    return _filename


def clear_dataframe():
    global _dataframe, _filename

    _dataframe = None
    _filename = None