"""Слой доступа к данным. Ничего не знает про HTTP и FastAPI.

Содержит:
  * доменные исключения (контракт ошибок репозитория);
  * Protocol CourseRepository (интерфейс);
  * MongoCourseRepository (реальная реализация, pymongo);
  * InMemoryCourseRepository (fake для тестов без СУБД).
"""
import logging
from typing import Optional, Protocol

from pymongo import ASCENDING, MongoClient, ReturnDocument
from pymongo.errors import (
    ConnectionFailure,
    DuplicateKeyError,
    PyMongoError,
    ServerSelectionTimeoutError,
)

log = logging.getLogger("repository")


# ---------- доменные ошибки ----------
class RepositoryError(Exception):
    """Базовая ошибка хранилища."""


class DuplicateCourseError(RepositoryError):
    """Курс с таким code уже существует."""


class StorageUnavailableError(RepositoryError):
    """Хранилище недоступно (нет соединения / timeout)."""


class StorageError(RepositoryError):
    """Прочая ошибка хранилища."""


# ---------- интерфейс ----------
class CourseRepository(Protocol):
    def create(self, data: dict) -> dict: ...
    def get_by_code(self, code: str) -> Optional[dict]: ...
    def list_all(self) -> list[dict]: ...
    def list_by_teacher(self, teacher: str) -> list[dict]: ...
    def update_room(self, code: str, room: str) -> Optional[dict]: ...
    def delete(self, code: str) -> bool: ...
    def ping(self) -> None: ...


# ---------- реализация MongoDB ----------
class MongoCourseRepository:
    def __init__(self, uri: str, db_name: str, timeout_ms: int = 3000):
        # MongoClient подключается лениво: приложение стартует и без СУБД.
        self.client = MongoClient(
            uri,
            serverSelectionTimeoutMS=timeout_ms,
            connectTimeoutMS=timeout_ms,
            socketTimeoutMS=timeout_ms * 2,
        )
        self.col = self.client[db_name]["courses"]
        self._index_ready = False

    # --- внутренние помощники ---
    def _ensure_index(self) -> None:
        if not self._index_ready:
            self.col.create_index([("code", ASCENDING)], unique=True)
            self._index_ready = True

    @staticmethod
    def _map(exc: PyMongoError) -> RepositoryError:
        # Текст исключения драйвера (может содержать URI) уходит только в лог.
        log.error("Storage error: %s", exc.__class__.__name__, exc_info=exc)
        if isinstance(exc, (ServerSelectionTimeoutError, ConnectionFailure)):
            return StorageUnavailableError("storage unavailable")
        return StorageError("storage error")

    # --- операции ---
    def create(self, data: dict) -> dict:
        try:
            self._ensure_index()
            self.col.insert_one(dict(data))
            return self.get_by_code(data["code"])
        except DuplicateKeyError:
            raise DuplicateCourseError(data["code"])
        except PyMongoError as e:
            raise self._map(e)

    def get_by_code(self, code: str) -> Optional[dict]:
        try:
            return self.col.find_one({"code": code}, {"_id": 0})
        except PyMongoError as e:
            raise self._map(e)

    def list_all(self) -> list[dict]:
        try:
            return list(self.col.find({}, {"_id": 0}).sort("code", ASCENDING))
        except PyMongoError as e:
            raise self._map(e)

    def list_by_teacher(self, teacher: str) -> list[dict]:
        """Предметный запрос: курсы преподавателя."""
        try:
            return list(
                self.col.find({"teacher": teacher}, {"_id": 0}).sort("code", ASCENDING)
            )
        except PyMongoError as e:
            raise self._map(e)

    def update_room(self, code: str, room: str) -> Optional[dict]:
        try:
            return self.col.find_one_and_update(
                {"code": code},
                {"$set": {"room": room}},
                projection={"_id": 0},
                return_document=ReturnDocument.AFTER,
            )
        except PyMongoError as e:
            raise self._map(e)

    def delete(self, code: str) -> bool:
        try:
            return self.col.delete_one({"code": code}).deleted_count == 1
        except PyMongoError as e:
            raise self._map(e)

    def ping(self) -> None:
        try:
            self.client.admin.command("ping")
        except PyMongoError as e:
            raise self._map(e)


# ---------- fake для тестов ----------
class InMemoryCourseRepository:
    def __init__(self, available: bool = True):
        self._data: dict[str, dict] = {}
        self.available = available  # False -> имитация остановленной СУБД

    def _check(self) -> None:
        if not self.available:
            raise StorageUnavailableError("storage unavailable")

    def create(self, data: dict) -> dict:
        self._check()
        if data["code"] in self._data:
            raise DuplicateCourseError(data["code"])
        self._data[data["code"]] = dict(data)
        return dict(data)

    def get_by_code(self, code: str) -> Optional[dict]:
        self._check()
        item = self._data.get(code)
        return dict(item) if item else None

    def list_all(self) -> list[dict]:
        self._check()
        return [dict(v) for _, v in sorted(self._data.items())]

    def list_by_teacher(self, teacher: str) -> list[dict]:
        self._check()
        return [dict(v) for _, v in sorted(self._data.items()) if v["teacher"] == teacher]

    def update_room(self, code: str, room: str) -> Optional[dict]:
        self._check()
        if code not in self._data:
            return None
        self._data[code]["room"] = room
        return dict(self._data[code])

    def delete(self, code: str) -> bool:
        self._check()
        return self._data.pop(code, None) is not None

    def ping(self) -> None:
        self._check()
