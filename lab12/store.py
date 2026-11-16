"""Backend abstraction: настоящая MongoDB (pymongo) или локальное Python-хранилище.

Локальное хранилище — запасной вариант из п. 2 задания ЛР №12. Оно НЕ заменяет MongoDB:
моделирует только то, что нужно эксперименту (find по равенству + limit, составной индекс,
explain-подобная статистика).
"""
import os
import sys
import sys as _sys

DB_NAME = "nosql_lab12"
COLL_NAME = "courses"
INDEX_KEYS = [("departmentId", 1), ("semester", 1)]
INDEX_NAME = "departmentId_1_semester_1"


class LocalCursor:
    def __init__(self, docs, stats):
        self._docs, self._stats = docs, stats

    def limit(self, n):
        self._docs = self._docs[:n]
        return self

    def __iter__(self):
        return iter(self._docs)


class LocalCollection:
    """Модель коллекции: без индекса — COLLSCAN, с индексом — IXSCAN по (departmentId, semester)."""

    def __init__(self):
        self.docs = []
        self.index = None  # dict[(dept, sem)] -> list[doc]

    def drop(self):
        self.docs, self.index = [], None

    def insert_many(self, rows):
        for r in rows:
            self.docs.append(r)
            if self.index is not None:  # стоимость записи: поддержка индекса
                self.index.setdefault((r["departmentId"], r["semester"]), []).append(r)

    def count_documents(self, _flt):
        return len(self.docs)

    def create_index(self, keys, name=None):
        idx = {}
        for d in self.docs:
            idx.setdefault((d["departmentId"], d["semester"]), []).append(d)
        self.index = idx

    def drop_index(self, name):
        self.index = None

    def has_index(self):
        return self.index is not None

    def find(self, flt):
        dept, sem = flt["departmentId"], flt["semester"]
        if self.index is not None:
            return LocalCursor(list(self.index.get((dept, sem), [])), None)
        return LocalCursor([d for d in self.docs
                            if d["departmentId"] == dept and d["semester"] == sem], None)

    def explain(self, flt, limit=100):
        dept, sem = flt["departmentId"], flt["semester"]
        if self.index is not None:
            hits = self.index.get((dept, sem), [])
            n = min(len(hits), limit)
            return {"stage": "FETCH+IXSCAN", "totalKeysExamined": n,
                    "totalDocsExamined": n, "nReturned": n}
        out, examined = 0, 0
        for d in self.docs:
            examined += 1
            if d["departmentId"] == dept and d["semester"] == sem:
                out += 1
                if out >= limit:
                    break
        return {"stage": "COLLSCAN", "totalKeysExamined": 0,
                "totalDocsExamined": examined, "nReturned": out}

    def index_size_estimate(self):
        """Грубая оценка: размер dict + списков ссылок (не равна размеру индекса MongoDB)."""
        if self.index is None:
            return 0
        return _sys.getsizeof(self.index) + sum(
            _sys.getsizeof(k) + _sys.getsizeof(v) for k, v in self.index.items())


def connect():
    """Возвращает (collection, backend_name, info_dict)."""
    uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
    forced = os.environ.get("BACKEND", "auto")  # auto | mongo | local
    if forced != "local":
        try:
            from pymongo import MongoClient
            client = MongoClient(uri, serverSelectionTimeoutMS=3000)
            ver = client.server_info()["version"]
            return client[DB_NAME][COLL_NAME], "mongo", {"version": ver}
        except Exception as e:  # noqa: BLE001
            if forced == "mongo":
                raise
            print(f"[!] MongoDB недоступна ({type(e).__name__}); "
                  f"используется ЛОКАЛЬНОЕ Python-хранилище", file=sys.stderr)
    return LocalCollection(), "local", {"version": f"python {sys.version.split()[0]} (local store)"}
