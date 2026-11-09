"""Конфигурация: все параметры подключения читаются из переменных окружения."""
import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()  # подхватывает .env, если файл существует (в Git он не попадает)


@dataclass(frozen=True)
class Settings:
    mongodb_uri: str
    db_name: str
    server_selection_timeout_ms: int
    log_level: str


def get_settings() -> Settings:
    return Settings(
        mongodb_uri=os.getenv("MONGODB_URI", "mongodb://localhost:27017"),
        db_name=os.getenv("DB_NAME", "lab9"),
        server_selection_timeout_ms=int(os.getenv("SERVER_SELECTION_TIMEOUT_MS", "3000")),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )
