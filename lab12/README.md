# ЛР №12 — воспроизводимый benchmark (вариант 01: каталог курсов)

Сравнение чтения `courses.find({departmentId: 10, semester: 5}).limit(100)` без индекса и с составным
индексом `{departmentId: 1, semester: 1}` при 1 / 4 / 8 параллельных клиентах.

## Запуск
```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# локальная MongoDB на localhost:27017 (только учебный стенд!)
python benchmark.py                # auto: MongoDB, если недоступна — локальное Python-хранилище
python make_report.py              # собирает report.pdf из результатов
```
Принудительно: `BACKEND=mongo python benchmark.py` или `BACKEND=local python benchmark.py`.

## Файлы
| Файл | Назначение |
|---|---|
| `seed.py` | генерация 5000 синтетических документов, `seed = 42` |
| `store.py` | подключение к MongoDB / локальное хранилище (запасной вариант) |
| `benchmark.py` | closed-loop benchmark, warm-up, 3 повтора, explain, графики |
| `results.csv` | метрики каждого из 18 прогонов |
| `raw_latencies.csv` | сырые латентности (для процентилей по объединённым данным) |
| `summary.csv`, `explain.json`, `meta.json` | сводка, планы запроса, окружение |
| `charts/` | `p95.png`, `throughput.png` |
| `make_report.py`, `report.pdf` | отчёт |

## Важно
- Результаты в `results.csv` получены на **локальном Python-хранилище** (`meta.json: backend = local`), т.к.
  в среде выполнения не было MongoDB. Для сдачи на настоящей MongoDB перезапустите `python benchmark.py`
  и `python make_report.py` — отчёт перестроится по новым данным.
- Коллекция `nosql_lab12.courses` пересоздаётся при каждом запуске (`drop`) — только учебная БД.
- Нагрузка — только на собственный локальный стенд.
