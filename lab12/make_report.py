"""Сборка report.pdf из results.csv / summary.csv / explain.json / meta.json."""
import json

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, PageBreak, Paragraph, Preformatted,
                                SimpleDocTemplate, Spacer, Table, TableStyle)

F = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("DV", F + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DVB", F + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DVM", F + "DejaVuSansMono.ttf"))
pdfmetrics.registerFontFamily("DV", normal="DV", bold="DVB", italic="DV", boldItalic="DVB")

meta = json.load(open("meta.json", encoding="utf-8"))
expl = json.load(open("explain.json", encoding="utf-8"))
res = pd.read_csv("results.csv")
sm = pd.read_csv("summary.csv")
local = meta["backend"] == "local"

B = ParagraphStyle("b", fontName="DV", fontSize=9.5, leading=13.5, spaceAfter=5)
H1 = ParagraphStyle("h1", parent=B, fontName="DVB", fontSize=13, leading=16, spaceBefore=8, spaceAfter=6)
T = ParagraphStyle("t", parent=B, fontName="DVB", fontSize=17, leading=22, alignment=1, spaceAfter=10)
C = ParagraphStyle("c", parent=B, alignment=1)
SM = ParagraphStyle("sm", parent=B, fontSize=8, leading=10)
CODE = ParagraphStyle("code", fontName="DVM", fontSize=6.8, leading=8.4)


def P(t, s=B):
    return Paragraph(t, s)


def tbl(data, widths=None, fs=8):
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "DV"), ("FONTNAME", (0, 0), (-1, 0), "DVB"),
        ("FONTSIZE", (0, 0), (-1, -1), fs), ("GRID", (0, 0), (-1, -1), .4, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dde6f0")),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    return t


def g(mode, w, col):
    return float(sm[(sm["mode"] == mode) & (sm["workers"] == w)][col].iloc[0])


NO, YES = "Без индекса", "С индексом"
story = []

# ---- титул
story += [Spacer(1, 3.5 * cm),
          P("МИНИСТЕРСТВО ОБРАЗОВАНИЯ И НАУКИ", C),
          Spacer(1, 1.2 * cm),
          P("ЛАБОРАТОРНАЯ РАБОТА №12", T),
          P("Разработка и запуск воспроизводимого benchmark-сценария", T),
          Spacer(1, .6 * cm),
          P("Дисциплина: «Проектирование и применение NoSQL-технологий»", C),
          P("Вариант 01. Каталог курсов (фильтр: departmentId + semester)", C),
          Spacer(1, 3 * cm),
          P("Выполнил: ______________________ (ФИО), группа ________", C),
          P("Проверил: ______________________", C),
          Spacer(1, 3 * cm),
          P("2026", C), PageBreak()]

# ---- 1-2 цель, окружение
story += [P("1. Цель работы", H1),
          P("Разработать воспроизводимый эксперимент производительности подсистемы чтения, измерить latency "
            "(P50/P95/P99), throughput и ошибки, сравнить базовую конфигурацию (без индекса) и оптимизированную "
            "(составной индекс {departmentId: 1, semester: 1}) и обосновать выводы."),
          P("2. Окружение и версии", H1)]
env = [["Параметр", "Значение"],
       ["Хранилище (backend)", "MongoDB" if not local else "Локальное Python-хранилище (MongoDB недоступна)"],
       ["Версия", meta["version"]], ["Python", meta["python"]], ["ОС", meta["platform"]],
       ["Число CPU", str(meta["cpu_count"])], ["Seed генератора", str(meta["seed"])],
       ["Документов в коллекции", str(meta["n_docs"])],
       ["Запросов в прогоне / прогрев", f'{meta["queries_per_run"]} / {meta["warmup"]}'],
       ["Клиенты / повторы", f'{meta["workers"]} / {meta["repeats"]}']]
story += [tbl(env, [5.5 * cm, 11 * cm], 8.5), Spacer(1, 6)]
if local:
    story += [P("<b>Ограничение эксперимента.</b> В среде выполнения не было MongoDB и не было доступа к её "
                "дистрибутиву, поэтому, как разрешено в п. 2 задания, использовано локальное Python-хранилище "
                "(<font name='DVM'>store.py</font>): без индекса запрос выполняет полный просмотр списка документов "
                "(аналог COLLSCAN), с индексом — поиск по словарю (аналог IXSCAN). Измерения отражают "
                "поведение этой модели (CPython, GIL, in-memory), а не сервера MongoDB: нет сети, диска, "
                "кэша WiredTiger, планировщика запросов. Код автоматически переключается на MongoDB, если "
                "она доступна (<font name='DVM'>python benchmark.py</font>).")]

# ---- 3 схема, 4 гипотеза
story += [P("3. Схема данных и access patterns", H1),
          P("Коллекция <font name='DVM'>nosql_lab12.courses</font>, 5000 синтетических документов:"),
          Preformatted('{ departmentId: int 1..20, semester: int 1..8, title: "Course i",\n'
                       '  credits: int 2..6, teacherId: int 1..150 }', CODE), Spacer(1, 4),
          P("AP-01 (главный): поиск курсов подразделения и семестра; AP-02: поиск курса по идентификатору; "
            "AP-03: подсчёт курсов подразделения. Тестируется AP-01: "
            "<font name='DVM'>find({departmentId: 10, semester: 5}).limit(100)</font>."),
          P("4. Гипотеза и SLO", H1),
          P("Гипотеза: составной индекс {departmentId: 1, semester: 1} уменьшит число просмотренных документов "
            "с ~5000 до числа совпавших (в среднем 5000/160 ≈ 31) и снизит P95 чтения. "
            "SLO (учебный): ошибок 0 %; P95 при 8 клиентах не более 1 мс для модели локального хранилища "
            "(для реальной MongoDB порог следует задать по замерам стенда)."),
          P("Одинаковы в обеих конфигурациях: seed, набор данных, запрос, число запросов, прогрев. "
            "Меняется только индекс."),
          P("5. Данные и воспроизводимость", H1),
          P("Данные генерирует <font name='DVM'>seed.py</font> отдельным генератором "
            "<font name='DVM'>random.Random(42)</font>, что даёт одинаковый набор при любом запуске. "
            "Коллекция пересоздаётся (drop) перед экспериментом; удаляется только индекс, созданный для этой работы. "
            "Исходные результаты сохранены в results.csv и raw_latencies.csv; зависимости — requirements.txt."),
          PageBreak()]

# ---- 6 код
story += [P("6. Код benchmark (ключевые части)", H1),
          P("Closed-loop сценарий: каждый из N запросов ставится в ThreadPoolExecutor; ошибки учитываются. "
            "Прогрев (40 запросов) выполняется отдельно перед каждым прогоном. Полный код — benchmark.py.", B)]
code = '''def one():
    start = perf_counter()
    try:
        list(coll.find(QUERY).limit(100))
        return ((perf_counter()-start)*1000, True)
    except Exception:
        return ((perf_counter()-start)*1000, False)

def percentile(v, p):                      # линейная интерполяция
    v = sorted(v)
    idx = (len(v)-1)*p/100
    lo, hi = math.floor(idx), math.ceil(idx)
    return v[lo] + (v[hi]-v[lo])*(idx-lo)

def run(coll, workers, n=2000):
    one = make_one(coll)
    for _ in range(40): one()              # warm-up отдельно
    t0 = perf_counter()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(lambda _: one(), range(n)))
    seconds = perf_counter() - t0
    lat = [ms for ms, ok in results if ok]
    return {"rps": len(lat)/seconds, "errors": n-len(lat),
            "p50": percentile(lat,50), "p95": percentile(lat,95),
            "p99": percentile(lat,99), ...}

# порядок: [без индекса] -> explain -> 1/4/8 клиентов x 3 повтора
#          -> create_index -> explain -> те же 9 прогонов'''
story += [Preformatted(code, CODE), Spacer(1, 6),
          P("Отличия от шаблона из задания: число запросов в прогоне увеличено с 400 до 2000, чтобы прогон с "
            "индексом не длился доли миллисекунды; остальная логика (warm-up, ошибки, перцентили) сохранена.")]

# ---- 7 explain
e0, e1 = expl[NO], expl[YES]
story += [P("7. Анализ плана запроса (explain)", H1)]
ex = [["Показатель", NO, YES],
      ["Стадия / winningPlan", e0["stage"], e1["stage"]],
      ["totalKeysExamined", str(e0["totalKeysExamined"]), str(e1["totalKeysExamined"])],
      ["totalDocsExamined", str(e0["totalDocsExamined"]), str(e1["totalDocsExamined"])],
      ["nReturned", str(e0["nReturned"]), str(e1["nReturned"])],
      ["executionTimeMillis", str(e0.get("executionTimeMillis", "н/д (локальная модель)")),
       str(e1.get("executionTimeMillis", "н/д (локальная модель)"))]]
story += [tbl(ex, [5 * cm, 5.5 * cm, 5.5 * cm], 8.5), Spacer(1, 6),
          P(f"Без индекса просматривается {e0['totalDocsExamined']} документов, чтобы вернуть {e0['nReturned']}; "
            f"с индексом — {e1['totalDocsExamined']} (ключей: {e1['totalKeysExamined']}). Сокращение просмотра "
            f"в {e0['totalDocsExamined'] / max(e1['totalDocsExamined'], 1):.0f} раз. По требованию задания вывод "
            "об ускорении подтверждается не только планом, но и независимыми замерами latency (разд. 8–9)."),
          PageBreak()]

# ---- 8 таблица результатов
story += [P("8. Результаты: все прогоны", H1),
          P("Реальные измерения (results.csv). Время — мс; RPS — успешные запросы в секунду.", SM)]
rows = [["Режим", "Клиенты", "Повтор", "RPS", "P50", "P95", "P99", "Ошибки"]]
for _, r in res.iterrows():
    rows.append([r["mode"], int(r["workers"]), int(r["repeat"]), f'{r["rps"]:.0f}', f'{r["p50"]:.4f}',
                 f'{r["p95"]:.4f}', f'{r["p99"]:.4f}', int(r["errors"])])
story += [tbl(rows, [3 * cm, 1.8 * cm, 1.6 * cm, 2 * cm, 2 * cm, 2 * cm, 2 * cm, 1.8 * cm], 7.5),
          Spacer(1, 8), P("Сводка: медиана трёх прогонов и процентили по объединённым сырым данным", H1)]
srows = [["Режим", "Клиенты", "RPS (мед.)", "P50 (мед.)", "P95 (мед.)", "P95 объед.", "P99 объед.", "Ошиб., %"]]
for _, r in sm.iterrows():
    srows.append([r["mode"], int(r["workers"]), f'{r["rps_median"]:.0f}', f'{r["p50_median"]:.4f}',
                  f'{r["p95_median"]:.4f}', f'{r["p95_pooled"]:.4f}', f'{r["p99_pooled"]:.4f}',
                  f'{r["error_rate_pct"]:.2f}'])
story += [tbl(srows, [2.8 * cm, 1.6 * cm, 2 * cm, 2 * cm, 2 * cm, 2.2 * cm, 2.2 * cm, 1.8 * cm], 7.5),
          Spacer(1, 4),
          P("Колонки «объед.» — процентили по всем 6000 сырым значениям режима/нагрузки (3 прогона × 2000), "
            "а не среднее P95 отдельных прогонов.", SM), PageBreak()]

# ---- 9 графики и расчёты
story += [P("9. Графики", H1),
          Image("charts/p95.png", width=13 * cm, height=13 * cm * 4.2 / 7),
          Image("charts/throughput.png", width=13 * cm, height=13 * cm * 4.2 / 7),
          P("10. Расчёты", H1)]
imp = [["Клиенты", "P95 до, мс", "P95 после, мс", "Улучшение P95, %"]]
for w in (1, 4, 8):
    a, b = g(NO, w, "p95_median"), g(YES, w, "p95_median")
    imp.append([w, f"{a:.4f}", f"{b:.4f}", f"{(a - b) / a * 100:.1f}"])
story += [P("Улучшение P95 = (P95_до − P95_после) / P95_до × 100 % (медианы трёх прогонов):"),
          tbl(imp, [3 * cm, 4 * cm, 4 * cm, 4.5 * cm], 8.5), Spacer(1, 6),
          P("Доля ошибок = ошибки / все попытки × 100 %. Во всех 18 прогонах: "
            f"{int(res['errors'].sum())} ошибок из {int(res['attempts'].sum())} попыток = "
            f"{res['errors'].sum() / res['attempts'].sum() * 100:.2f} %."),
          PageBreak()]

# ---- 11 запись и размер индекса
ratio = meta["insert_ms_with_index"] / meta["insert_ms_no_index"]
story += [P("11. Стоимость записи и размер индекса", H1),
          tbl([["Показатель", "Без индекса", "С индексом"],
               ["Bulk-вставка 5000 документов, мс (медиана 7)", f'{meta["insert_ms_no_index"]:.3f}',
                f'{meta["insert_ms_with_index"]:.3f}'],
               ["Размер индекса, байт", "0", f'{meta["index_size_bytes_with"]}']],
              [8 * cm, 4 * cm, 4 * cm], 8.5), Spacer(1, 4),
          P(f"Стоимость записи с индексом выше примерно в {ratio:.1f} раза (индекс нужно поддерживать при каждой "
            "вставке). " + (f"Размер индекса — {meta['index_size_note']}; число нельзя переносить на MongoDB. "
                            "Абсолютные миллисекунды вставки относятся к in-memory модели без диска и журнала, "
                            "значим только факт роста стоимости записи." if local else
                            "Размер индекса получен из collStats.")),
          P("12. Интерпретация", H1)]
r1n, r8n = g(NO, 1, "rps_median"), g(NO, 8, "rps_median")
p1, p8 = g(NO, 1, "p95_median"), g(NO, 8, "p95_median")
p99_8 = g(NO, 8, "p99_pooled") if "p99_pooled" in sm else 0
story += [P(f"<b>Эффект индекса.</b> Просмотр документов снизился с {e0['totalDocsExamined']} до "
            f"{e1['totalDocsExamined']}, а P95 при 1 клиенте — с {g(NO, 1, 'p95_median'):.3f} до "
            f"{g(YES, 1, 'p95_median'):.4f} мс. Гипотеза подтверждается в рамках модели: и план, и независимые "
            "замеры указывают в одну сторону."),
          P(f"<b>Масштабирование по клиентам.</b> Без индекса RPS почти не растёт с числом клиентов "
            f"({r1n:.0f} → {r8n:.0f} запросов/с при 1 → 8 клиентах), а P95 растёт ({p1:.3f} → {p8:.3f} мс), хвост P99 "
            f"при 8 клиентах достигает {g(NO, 8, 'p99_pooled'):.1f} мс. "
            "Общая причина плато throughput: ресурс-ограничитель уже занят одним клиентом, а новые клиенты лишь "
            "встают в очередь — число клиентов не равно throughput. В нашей модели узким местом является "
            "CPU-bound код при GIL: потоки не ускоряют выполнение, а добавляют переключения и ожидание, "
            "поэтому растут хвостовые перцентили; на реальной MongoDB плато определялось бы "
            "CPU/диском сервера, блокировками и сетью. Объяснение через GIL — предположение по "
            "устройству CPython, отдельно им не проверялось."),
          P("<b>Нестабильность RPS с индексом.</b> Прогон с индексом (2000 запросов по ~1–2 мкс) длится "
            "десятки миллисекунд, и RPS в большей степени отражает накладные расходы ThreadPoolExecutor и "
            "планировщика ОС, чем хранилище: значения при 4 клиентах (32–107 тыс. RPS между повторами) "
            "шумят в несколько раз. Поэтому по RPS с индексом надёжно только утверждение «на порядок выше, чем без "
            "индекса»; для точных цифр нужен более длинный прогон или несколько тысяч запросов с разными "
            "параметрами."),
          P("12.1 Ограничения", H1),
          P("1) Используется локальная модель, а не MongoDB (см. разд. 2). 2) Closed-loop тест: клиенты шлют "
            "следующий запрос только после ответа, поэтому он не воспроизводит фиксированный open-loop RPS и "
            "подвержен coordinated omission — хвосты latency занижаются при перегрузке. 3) Один и тот же запрос "
            "{10, 5} повторяется всегда: на реальном сервере это означает горячий кэш; результат не "
            "обобщается на произвольные значения фильтра. 4) Клиент и «сервер» в одном процессе Python. "
            "5) Только три повтора; медиана из трёх — грубая оценка разброса. 6) Измерено только чтение; "
            "влияние индекса на смешанную нагрузку не проверялось."),
          P("13. Вывод", H1),
          P("Реализован воспроизводимый closed-loop benchmark с фиксированным seed, прогревом, тремя повторами, "
            "учётом ошибок, анализом плана и сохранением сырых данных. В рамках локальной модели составной индекс "
            "{departmentId: 1, semester: 1} сократил просмотр документов в "
            f"{e0['totalDocsExamined'] / max(e1['totalDocsExamined'], 1):.0f} раз и снизил P95 на порядки при всех "
            "уровнях нагрузки без ошибок, за счёт более дорогой записи и дополнительной памяти под индекс. "
            "Для итоговых выводов о MongoDB эксперимент необходимо повторить на реальном сервере тем же кодом."),
          PageBreak()]

# ---- контрольные вопросы
story += [P("14. Ответы на контрольные вопросы", H1)]
qa = [("Чем throughput отличается от числа клиентов?",
       "Число клиентов — параметр нагрузки (сколько запросов в полёте), throughput — результат: число "
       "успешных операций в секунду. После насыщения ресурса рост клиентов не увеличивает throughput."),
      ("Почему P95 важнее одного среднего?",
       "Среднее скрывает хвосты: 5 % запросов могут быть в десятки раз медленнее. Пользователи и SLO "
       "чувствительны к хвосту (см. P99 при 8 клиентах без индекса)."),
      ("Какие показатели возвращает explain(\"executionStats\")?",
       "winningPlan (стадии COLLSCAN/IXSCAN/FETCH), nReturned, totalKeysExamined, totalDocsExamined, "
       "executionTimeMillis и статистику по стадиям."),
      ("Зачем выполнять warm-up?", "Чтобы исключить холодный кэш, ленивую инициализацию соединений и JIT/"
       "кэширование плана: первые запросы нетипично медленные и искажают процентили."),
      ("Почему нельзя менять индекс и объём данных одновременно?",
       "Нельзя будет приписать изменение latency конкретному фактору: нарушается принцип изменения одной "
       "переменной."),
      ("Что означает выход throughput на плато?",
       "Система насыщена: узкое место (CPU, диск, блокировки, GIL клиента) занято, дополнительные клиенты "
       "увеличивают только очередь и latency."),
      ("Ограничения closed-loop benchmark?",
       "Нагрузка зависит от скорости ответа, нет заданного RPS, возможен coordinated omission, "
       "хвосты при перегрузке занижены; клиентский генератор сам может быть узким местом."),
      ("Как доказать воспроизводимость?",
       "Фиксированный seed, версии ПО в отчёте, одинаковые данные и запросы, скрипты в репозитории, "
       "сырые результаты в CSV, три повтора и инструкция запуска в README.")]
for q, a in qa:
    story += [P(f"<b>{q}</b>"), P(a)]
story += [P("15. Источники", H1),
          P("MongoDB Explain Results: https://www.mongodb.com/docs/manual/reference/explain-results/<br/>"
            "MongoDB Database Profiler: https://www.mongodb.com/docs/manual/tutorial/manage-the-database-profiler/<br/>"
            "Kleppmann M. Designing Data-Intensive Applications. O’Reilly, 2017.<br/>"
            "Силлабус дисциплины, лекция №12 и лабораторная №12.")]


def footer(c, d):
    c.setFont("DV", 8)
    c.drawCentredString(A4[0] / 2, 1.2 * cm, f"ЛР №12 · вариант 01 · стр. {d.page}")


SimpleDocTemplate("report.pdf", pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                  topMargin=2 * cm, bottomMargin=2 * cm,
                  title="ЛР №12 — benchmark").build(story, onFirstPage=footer, onLaterPages=footer)
print("report.pdf готов")
