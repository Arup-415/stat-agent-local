class DatasetStore:
    """
    Stores the currently uploaded dataset.
    """

    def __init__(self):
        self.df = None
        self.filename = None

    def set_dataset(self, df, filename=None):
        self.df = df
        self.filename = filename

    def get_dataset(self):
        return self.df

    def get_filename(self):
        return self.filename

    def clear(self):
        self.df = None
        self.filename = None


dataset_store = DatasetStore()