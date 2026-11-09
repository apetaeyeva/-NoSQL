"""ЛР №11. Проектирование стратегии шардирования и тест распределения.
Вариант 5: Библиотека. Кандидат: reader_id (readerId); низкокардинальный
альтернативный ключ: genre_id (genreId); основной запрос - выдачи читателя.

Запуск: python simulation.py   (seed = 42, результаты воспроизводимы)
Создаёт: results.json и chart_load.png (при наличии matplotlib).
"""
import random, hashlib, json
from collections import Counter

random.seed(42)
N, Q, SHARDS = 12000, 30000, 3
READERS, GENRES, DAYS = 2500, 5, 30          # >= 1000 уникальных readerId

# ---------- Данные: loan_id - монотонный ключ выдачи ----------
rows = [dict(reader_id=i % READERS,
             genre_id=i % GENRES,
             loan_id=i,
             day=(i * 7) % DAYS) for i in range(N)]


def stable_hash(value):
    """SHA-256 - только для учебной симуляции, не алгоритм MongoDB."""
    digest = hashlib.sha256(str(value).encode()).digest()
    return int.from_bytes(digest[:8], 'big')


# ---------- Стратегии размещения ----------
def low_card(row):                      # (A) genre_id, низкая кардинальность
    return row['genre_id'] % SHARDS


def hashed_reader(row):                 # (B) reader_id + hashed
    return stable_hash(row['reader_id']) % SHARDS


def range_loan(row):                    # (C) ranged по монотонному loan_id
    return min(row['loan_id'] // (N // SHARDS), SHARDS - 1)


def metrics(assign, data, requests):
    docs = Counter(assign(r) for r in data)
    load = Counter(assign(r) for r in requests)
    d = [docs[i] for i in range(SHARDS)]
    q = [load[i] for i in range(SHARDS)]
    res = dict(docs=d, queries=q,
               doc_pct=[round(x / len(data) * 100, 1) for x in d],
               query_pct=[round(x / len(requests) * 100, 1) for x in q],
               doc_max_mean=round(max(d) / (sum(d) / SHARDS), 2),
               query_max_mean=round(max(q) / (sum(q) / SHARDS), 2),
               query_max_min=(round(max(q) / min(q), 2) if min(q) > 0 else None))
    return res


def describe(name, assign, data, requests, out):
    m = metrics(assign, data, requests)
    out[name] = m
    print(name, 'docs=', m['docs'], 'queries=', m['queries'],
          'doc_max_mean=', m['doc_max_mean'],
          'query_max_mean=', m['query_max_mean'],
          'query_max_min=', m['query_max_min'])


results = {}

# ---------- Часть 1: базовый эксперимент (как в методичке) ----------
uniform = random.choices(rows, k=Q)
hot_rows = [r for r in rows if r['genre_id'] == 0]
hot = [random.choice(hot_rows) if random.random() < 0.6
       else random.choice(rows) for _ in range(Q)]

base = [('genre_id', low_card), ('hashed_reader', hashed_reader),
        ('range_loan', range_loan)]
print('=== Часть 1: базовый набор (12000 док., 30000 запросов) ===')
for name, fn in base:
    describe(name + '/uniform', fn, rows, uniform, results)
    describe(name + '/hot', fn, rows, hot, results)

# ---------- Часть 2: шаг 4 - один жанр содержит 80% записей ----------
rng = random.Random(42)
rows80 = []
for i in range(N):
    g = 0 if rng.random() < 0.8 else rng.randint(1, GENRES - 1)
    rows80.append(dict(reader_id=i % READERS, genre_id=g,
                       loan_id=i, day=(i * 7) % DAYS))
print('\n=== Часть 2: 80% записей в жанре 0 ===')
share0 = sum(r['genre_id'] == 0 for r in rows80) / N
print('доля жанра 0 =', round(share0 * 100, 1), '%')
results['genre0_share_pct'] = round(share0 * 100, 1)

# запросы: 80% запросов тоже идут к жанру 0 (популярный жанр)
hot80_rows = [r for r in rows80 if r['genre_id'] == 0]
req80 = [rng.choice(hot80_rows) if rng.random() < 0.8
         else rng.choice(rows80) for _ in range(Q)]


def genre_only(row):
    # в 80%-наборе жанр 0 -> шард 0, остальные жанры раскладываются по модулю
    return row['genre_id'] % SHARDS


def hashed_reader2(row):
    return stable_hash(row['reader_id']) % SHARDS


def compound_genre_reader(row):          # (D) {genre_id, reader_id} hashed
    return stable_hash((row['genre_id'], row['reader_id'])) % SHARDS


def reader_day(row):                     # (E) {reader_id, day_bucket} hashed
    return stable_hash((row['reader_id'], row['day'])) % SHARDS


for name, fn in [('genre_id', genre_only),
                 ('hashed_reader', hashed_reader2),
                 ('hashed{genre,reader}', compound_genre_reader),
                 ('hashed{reader,day}', reader_day)]:
    describe('80%/' + name, fn, rows80, req80, results)

# кардинальность кандидатов
card = dict(
    genre_id=len({r['genre_id'] for r in rows}),
    reader_id=len({r['reader_id'] for r in rows}),
    loan_id=len({r['loan_id'] for r in rows}),
    genre_reader=len({(r['genre_id'], r['reader_id']) for r in rows}),
    reader_day=len({(r['reader_id'], r['day']) for r in rows}))
card['genre_reader_80'] = len({(r['genre_id'], r['reader_id']) for r in rows80})
results['cardinality'] = card
print('\nКардинальность:', card)

# AP-04: загрузка нового потока - последние 1000 выдач (loan_id монотонно растёт)
new_stream = [dict(reader_id=(N + i) % READERS, genre_id=(N + i) % GENRES,
                   loan_id=N + i, day=((N + i) * 7) % DAYS) for i in range(1000)]
print('\n=== AP-04: новый поток из 1000 выдач ===')
for name, fn in base:
    c = Counter(fn(r) for r in new_stream)
    results['AP04/' + name] = [c[i] for i in range(SHARDS)]
    print(name, [c[i] for i in range(SHARDS)])

with open('results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=1)

# ---------- График: доля запросов по шардам (hot-режим) ----------
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    labels = ['genre_id', 'hashed_reader', 'range_loan']
    fig, ax = plt.subplots(figsize=(8, 4.2))
    w = 0.25
    for s in range(SHARDS):
        vals = [results[l + '/hot']['query_pct'][s] for l in labels]
        bars = ax.bar([k + (s - 1) * w for k in range(3)], vals, w,
                      label='Shard ' + 'ABC'[s])
        ax.bar_label(bars, fmt='%.1f', fontsize=8)
    ax.axhline(100 / SHARDS, ls='--', c='gray', lw=1)
    ax.set_xticks(range(3)); ax.set_xticklabels(labels)
    ax.set_ylabel('Доля запросов, %')
    ax.set_title('Нагрузка по шардам, hot-режим (60% к жанру 0)')
    ax.legend(); fig.tight_layout(); fig.savefig('chart_load.png', dpi=160)
except ImportError:
    pass
