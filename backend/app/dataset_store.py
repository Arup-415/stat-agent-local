from threading import RLock
from time import monotonic


class DatasetStore:
    """
    Stores uploaded datasets by browser session.
    """

    SESSION_TTL_SECONDS = 24 * 60 * 60
    MAX_SESSIONS = 128

    def __init__(self):
        self._datasets = {}
        self._lock = RLock()

    def _prune(self, now):
        expired = [
            session_id
            for session_id, entry in self._datasets.items()
            if now - entry["last_access"] > self.SESSION_TTL_SECONDS
        ]
        for session_id in expired:
            self._datasets.pop(session_id, None)

        while len(self._datasets) > self.MAX_SESSIONS:
            oldest = min(self._datasets, key=lambda key: self._datasets[key]["last_access"])
            self._datasets.pop(oldest, None)

    def set_dataset(self, df, filename=None, session_id="default"):
        now = monotonic()
        with self._lock:
            self._prune(now)
            self._datasets[session_id] = {
                "dataframe": df,
                "filename": filename,
                "last_access": now,
            }

    def get_dataset(self, session_id="default"):
        now = monotonic()
        with self._lock:
            self._prune(now)
            entry = self._datasets.get(session_id)
            if entry is None:
                return None
            entry["last_access"] = now
            return entry["dataframe"]

    def get_filename(self, session_id="default"):
        now = monotonic()
        with self._lock:
            self._prune(now)
            entry = self._datasets.get(session_id)
            if entry is None:
                return None
            entry["last_access"] = now
            return entry["filename"]

    def clear(self, session_id=None):
        with self._lock:
            if session_id is None:
                self._datasets.clear()
            else:
                self._datasets.pop(session_id, None)


dataset_store = DatasetStore()