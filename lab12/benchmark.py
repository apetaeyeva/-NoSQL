"""Closed-loop benchmark ЛР №12 (вариант 01): find({departmentId, semester}).limit(100).

Запуск:  python benchmark.py            (auto: MongoDB, иначе локальное хранилище)
         BACKEND=local python benchmark.py
Результаты: results.csv, raw_latencies.csv, summary.csv, explain.json, meta.json, charts/*.png
"""
import csv
import json
import math
import os
import platform
import statistics
import sys
from concurrent.futures import ThreadPoolExecutor
from time import perf_counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from seed import N_DOCS, SEED, seed_collection
from store import INDEX_KEYS, INDEX_NAME, connect

QUERY = {"departmentId": 10, "semester": 5}
WORKERS = [1, 4, 8]
REPEATS = 3
N_QUERIES = 2000      # запросов в одном прогоне
WARMUP = 40           # прогрев — отдельно, не входит в измерения
LIMIT = 100


def percentile(v, p):
    v = sorted(v)
    if not v:
        return float("nan")
    idx = (len(v) - 1) * p / 100
    lo, hi = math.floor(idx), math.ceil(idx)
    return v[lo] + (v[hi] - v[lo]) * (idx - lo)


def make_one(coll):
    def one():
        start = perf_counter()
        try:
            list(coll.find(QUERY).limit(LIMIT))
            return ((perf_counter() - start) * 1000, True)
        except Exception:  # noqa: BLE001 — ошибки учитываются в метриках
            return ((perf_counter() - start) * 1000, False)
    return one


def run(coll, workers, n=N_QUERIES):
    one = make_one(coll)
    for _ in range(WARMUP):
        one()
    t0 = perf_counter()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(lambda _: one(), range(n)))
    seconds = perf_counter() - t0
    lat = [ms for ms, ok in results if ok]
    success = len(lat)
    return {"workers": workers, "success": success, "errors": n - success,
            "attempts": n, "duration_s": seconds, "rps": success / seconds,
            "p50": percentile(lat, 50), "p95": percentile(lat, 95),
            "p99": percentile(lat, 99)}, lat


def get_explain(coll, backend):
    if backend == "local":
        return coll.explain(QUERY, LIMIT)
    ex = coll.find(QUERY).limit(LIMIT).explain()
    es = ex.get("executionStats", {})

    def stage(p):  # имя нижнего стейджа плана
        while "inputStage" in p:
            p = p["inputStage"]
        return p.get("stage")
    wp = ex["queryPlanner"]["winningPlan"]
    return {"stage": stage(wp), "winningPlan": wp,
            "totalKeysExamined": es.get("totalKeysExamined"),
            "totalDocsExamined": es.get("totalDocsExamined"),
            "nReturned": es.get("nReturned"),
            "executionTimeMillis": es.get("executionTimeMillis")}


def write_cost(coll, backend, with_index, reps=7):
    """Время bulk-вставки 5000 документов без индекса / с индексом (медиана, мс)."""
    from seed import make_rows
    rows = make_rows()
    times = []
    for _ in range(reps):
        coll.drop()
        if with_index:
            coll.create_index(INDEX_KEYS, name=INDEX_NAME) if backend == "mongo" else coll.create_index(None)
        data = [dict(r) for r in rows]  # копии: pymongo добавляет _id
        t = perf_counter()
        coll.insert_many(data)
        times.append((perf_counter() - t) * 1000)
    return statistics.median(times)


def index_size(coll, backend):
    if backend == "mongo":
        st = coll.database.command("collStats", coll.name)
        return st.get("indexSizes", {}).get(INDEX_NAME)
    return coll.index_size_estimate()


def set_index(coll, backend, on):
    if backend == "mongo":
        names = [i["name"] for i in coll.list_indexes()]
        if on and INDEX_NAME not in names:
            coll.create_index(INDEX_KEYS, name=INDEX_NAME)
        if not on and INDEX_NAME in names:
            coll.drop_index(INDEX_NAME)  # только созданный для этой работы индекс
    else:
        coll.create_index(None) if on else coll.drop_index(None)


def main():
    coll, backend, info = connect()
    meta = {"backend": backend, "version": info["version"], "python": platform.python_version(),
            "platform": platform.platform(), "cpu_count": os.cpu_count(), "seed": SEED,
            "n_docs_requested": N_DOCS, "query": QUERY, "limit": LIMIT, "workers": WORKERS,
            "repeats": REPEATS, "queries_per_run": N_QUERIES, "warmup": WARMUP}
    meta["n_docs"] = seed_collection(coll)
    print("backend:", backend, info, "docs:", meta["n_docs"])

    rows, raw, explains = [], [], {}
    for mode, on in (("Без индекса", False), ("С индексом", True)):
        set_index(coll, backend, on)
        explains[mode] = get_explain(coll, backend)
        print(mode, "explain:", explains[mode])
        for w in WORKERS:
            for rep in range(1, REPEATS + 1):
                r, lat = run(coll, w)
                r.update(mode=mode, repeat=rep)
                rows.append(r)
                raw.extend((mode, w, rep, ms) for ms in lat)
                print(f"{mode:12s} w={w} rep={rep} rps={r['rps']:.0f} "
                      f"p50={r['p50']:.3f} p95={r['p95']:.3f} p99={r['p99']:.3f} err={r['errors']}")
        meta[f"index_size_bytes_{'with' if on else 'without'}"] = index_size(coll, backend)

    # стоимость записи и размер индекса
    meta["insert_ms_no_index"] = write_cost(coll, backend, False)
    meta["insert_ms_with_index"] = write_cost(coll, backend, True)
    meta["index_size_bytes_with"] = index_size(coll, backend)
    meta["index_size_note"] = ("точный (collStats)" if backend == "mongo"
                               else "ОЦЕНКА для Python dict, не размер индекса MongoDB")

    df = pd.DataFrame(rows)[["mode", "workers", "repeat", "attempts", "success", "errors",
                             "duration_s", "rps", "p50", "p95", "p99"]]
    df.to_csv("results.csv", index=False, float_format="%.4f")
    with open("raw_latencies.csv", "w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["mode", "workers", "repeat", "latency_ms"])
        wr.writerows((m, w, r, f"{ms:.5f}") for m, w, r, ms in raw)

    # сводка: медиана трёх прогонов + процентили по объединённым сырым данным
    rawdf = pd.DataFrame(raw, columns=["mode", "workers", "repeat", "ms"])
    summ = []
    for (mode, w), g in df.groupby(["mode", "workers"]):
        pooled = rawdf[(rawdf["mode"] == mode) & (rawdf["workers"] == w)]["ms"].tolist()
        summ.append({"mode": mode, "workers": w,
                     "rps_median": g["rps"].median(), "p50_median": g["p50"].median(),
                     "p95_median": g["p95"].median(), "p99_median": g["p99"].median(),
                     "p95_pooled": percentile(pooled, 95), "p99_pooled": percentile(pooled, 99),
                     "errors_total": int(g["errors"].sum()),
                     "error_rate_pct": g["errors"].sum() / g["attempts"].sum() * 100})
    sdf = pd.DataFrame(summ).sort_values(["mode", "workers"], ascending=[False, True])
    sdf.to_csv("summary.csv", index=False, float_format="%.4f")

    with open("explain.json", "w", encoding="utf-8") as f:
        json.dump(explains, f, ensure_ascii=False, indent=2, default=str)
    with open("meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2, default=str)

    make_charts(sdf, backend)
    print(sdf.to_string(index=False))


def make_charts(sdf, backend):
    os.makedirs("charts", exist_ok=True)
    note = "" if backend == "mongo" else " (локальное Python-хранилище)"
    colors = {"Без индекса": "#c0504d", "С индексом": "#2e75b6"}
    for col, title, ylabel, fn in (
            ("p95_median", "P95 latency по числу клиентов" + note, "P95, мс (медиана 3 прогонов)", "p95.png"),
            ("rps_median", "Throughput по числу клиентов" + note, "RPS (медиана 3 прогонов)", "throughput.png")):
        fig, ax = plt.subplots(figsize=(7, 4.2))
        for mode, g in sdf.groupby("mode"):
            ax.plot(g["workers"], g[col], marker="o", lw=2, label=mode, color=colors[mode])
        ax.set_xticks([1, 4, 8])
        ax.set_xlabel("Параллельные клиенты")
        ax.set_ylabel(ylabel)
        ax.set_title(title, fontsize=10)
        ax.grid(alpha=.3)
        ax.legend()
        fig.tight_layout()
        fig.savefig(f"charts/{fn}", dpi=160)
        plt.close(fig)


if __name__ == "__main__":
    sys.exit(main())
