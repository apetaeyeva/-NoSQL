"""Загрузка 15 синтетических курсов: python seed.py"""
from config import get_settings
from repository import DuplicateCourseError, MongoCourseRepository

TEACHERS = ["Ivanov A.", "Petrova M.", "Sidorov K.", "Nurlanova A."]
TITLES = [
    ("NOSQL", "Проектирование NoSQL-систем"), ("DB", "Реляционные базы данных"),
    ("ALGO", "Алгоритмы и структуры данных"), ("WEB", "Веб-разработка"),
    ("PY", "Программирование на Python"), ("ML", "Основы машинного обучения"),
    ("NET", "Компьютерные сети"), ("OS", "Операционные системы"),
    ("SEC", "Основы информационной безопасности"), ("CLOUD", "Облачные технологии"),
    ("BIGD", "Технологии больших данных"), ("UX", "Проектирование интерфейсов"),
    ("TEST", "Тестирование ПО"), ("DEVOPS", "DevOps-практики"), ("IS", "Информационные системы"),
]

if __name__ == "__main__":
    s = get_settings()
    repo = MongoCourseRepository(s.mongodb_uri, s.db_name, s.server_selection_timeout_ms)
    for i, (prefix, title) in enumerate(TITLES):
        doc = {
            "code": f"{prefix}{301 + i}", "title": title,
            "teacher": TEACHERS[i % len(TEACHERS)],
            "room": f"A-{200 + i}", "credits": 3 + i % 3,
        }
        try:
            repo.create(doc)
            print("created", doc["code"])
        except DuplicateCourseError:
            print("exists ", doc["code"])
