"""Генерация синтетических данных (вариант 01: каталог курсов). Seed зафиксирован."""
import random

SEED = 42
N_DOCS = 5000


def make_rows(n=N_DOCS, seed=SEED):
    rng = random.Random(seed)  # отдельный генератор: результат не зависит от остального кода
    return [{"departmentId": rng.randint(1, 20),
             "semester": rng.randint(1, 8),
             "title": f"Course {i}",
             "credits": rng.randint(2, 6),
             "teacherId": rng.randint(1, 150)} for i in range(n)]


def seed_collection(coll):
    coll.drop()  # ТОЛЬКО учебная коллекция nosql_lab12.courses
    coll.insert_many(make_rows())
    return coll.count_documents({})


if __name__ == "__main__":
    from store import connect
    c, backend, info = connect()
    print("backend:", backend, info)
    print("Документов:", seed_collection(c))
