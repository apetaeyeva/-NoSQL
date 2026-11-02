# Лабораторная работа № 9 — Подключение NoSQL-хранилища к прикладному сервису
**Вариант 1.** Университет · MongoDB · `CourseRepository` · FastAPI · PyMongo

## 1. Схема слоёв
```
HTTP -> main.py (API: валидация, коды) -> service.py -> repository.py -> pymongo -> MongoDB
HTTP <- маппинг ошибок <- доменный результат / доменные исключения <-
```
| Слой | Файл | Ответственность |
|---|---|---|
| API | main.py, models.py | HTTP, валидация (Pydantic), статусы, маппинг ошибок |
| Service | service.py | прикладная логика, `CourseNotFoundError` |
| Repository | repository.py | операции хранения, доменные ошибки, ничего не знает про HTTP |
| Driver | pymongo | протокол и соединение |
| Config | config.py, .env | URI, имя БД, timeout |

## 2. Драйвер
Официальный `pymongo`: `MongoClient` с `serverSelectionTimeoutMS`, `connectTimeoutMS`, `socketTimeoutMS`. Подключение ленивое, поэтому сервис стартует и при остановленной СУБД и отвечает 503.

## 3. Запуск
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # заполнить локально, .env не коммитить
docker run -d --name mongo-lab9 -p 127.0.0.1:27017:27017 mongo:7
python seed.py              # 15 синтетических курсов
uvicorn main:app --reload   # Swagger: http://127.0.0.1:8000/docs
pytest -q                   # тесты без СУБД (fake repository)
```
`.env` пример: `MONGODB_URI=mongodb://localhost:27017`, `DB_NAME=lab9`.
Порт Mongo привязан к 127.0.0.1, во внешнюю сеть не открыт.

## 4. Repository-интерфейс (`Protocol CourseRepository`)
`create`, `get_by_code`, `list_all`, `list_by_teacher` (предметный запрос), `update_room`, `delete`, `ping`.
Реализации: `MongoCourseRepository` (реальная) и `InMemoryCourseRepository` (fake, флаг `available=False` имитирует отказ СУБД).
Что скрывает repository: коллекцию и `_id`, проекцию `{_id: 0}`, уникальный индекс по `code`, синтаксис фильтров и `$set`, исключения pymongo (преобразуются в `DuplicateCourseError`, `StorageUnavailableError`, `StorageError`).

## 5. Контракт API
| Операция | Метод и путь | Успех | Ошибки |
|---|---|---|---|
| Создать | POST /courses | 201 | 409 дубликат, 422 валидация, 503 |
| Получить | GET /courses/{code} | 200 | 404, 422, 503 |
| Список / по преподавателю | GET /courses?teacher=... | 200 | 422, 503 |
| Обновить аудиторию | PATCH /courses/{code}/room | 200 | 404, 422, 503 |
| Удалить | DELETE /courses/{code} | 204 | 404, 503 |
| Здоровье | GET /health | 200 | 503 |

Валидация: `code` по шаблону `^[A-Z]{2,10}[0-9]{2,4}$`, `title` 3–120 символов, `teacher` 2–80, `room` 1–20, `credits` 1–10.

## 6. Проверка (curl) — сделайте скриншоты для отчёта
```bash
curl -i -X POST localhost:8000/courses -H "Content-Type: application/json" \
  -d '{"code":"NOSQL301","title":"NoSQL design","teacher":"Ivanov A.","room":"A-204","credits":4}'   # 201 / 409
curl -i localhost:8000/courses/NOSQL301                      # 200
curl -i localhost:8000/courses/NOSQL999                      # 404
curl -i localhost:8000/courses/bad-code                      # 422
curl -i "localhost:8000/courses?teacher=Ivanov%20A."         # 200
curl -i -X PATCH localhost:8000/courses/NOSQL301/room -H "Content-Type: application/json" -d '{"room":"B-101"}'
curl -i -X DELETE localhost:8000/courses/NOSQL301            # 204
docker stop mongo-lab9
curl -i localhost:8000/courses/NOSQL301                      # 503 {"detail":"Storage temporarily unavailable"}
```

## 7. Обработка ошибок
| Ситуация | Код | Где формируется |
|---|---|---|
| Нет объекта | 404 | service -> `CourseNotFoundError` -> handler |
| Неверные данные | 422 | Pydantic в API-слое |
| Дубликат | 409 | `DuplicateKeyError` -> `DuplicateCourseError` |
| СУБД недоступна | 503 | `ServerSelectionTimeoutError` -> `StorageUnavailableError` |
| Прочее | 500 | общий handler, детали только в логе |

Клиент никогда не получает URI, пароль, stack trace или текст исключения драйвера; всё это пишется только в серверный лог.

## 8. Конфигурация без секретов
Переменные: `MONGODB_URI`, `DB_NAME`, `SERVER_SELECTION_TIMEOUT_MS`, `LOG_LEVEL`. В Git лежит только `.env.example` без значений, `.env` в `.gitignore`.

## 9. Ответы на контрольные вопросы (кратко)
- Драйвер: библиотека для соединения и выполнения операций СУБД.
- Repository: инкапсулирует хранение, упрощает тесты и замену БД.
- URI не в Git: содержит учётные данные, утечка секретов.
- Валидация HTTP: в API-слое (Pydantic).
- 404 vs 503: ресурса нет (ошибка клиента) vs сервис не может обратиться к хранилищу (временная ошибка сервера).
- Repository не возвращает HTTP-объекты: иначе смешиваются слои и его нельзя переиспользовать.
- Timeout: `serverSelectionTimeoutMS` -> `ServerSelectionTimeoutError` -> 503.
- Замена хранилища: новая реализация `CourseRepository`, API и service не меняются.
- Логировать, но не показывать: исключения драйвера, URI, stack trace, 500-ошибки.

## 10. Вывод
HTTP-слой отделён от хранения через Protocol и DI (`Depends` + `dependency_overrides`), что позволило протестировать API без СУБД на fake-репозитории. Ошибки хранилища преобразуются в доменные, а затем в согласованные HTTP-коды без раскрытия внутренних данных.
