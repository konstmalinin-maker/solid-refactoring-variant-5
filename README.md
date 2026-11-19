# SOLID: управление документами — вариант №5

![CI](https://github.com/konstmalinin-maker/solid-refactoring-variant-5/actions/workflows/ci.yml/badge.svg?branch=main)

Практическая работа №9: характеризующие тесты → отдельные шаги S/O/L/I/D → метрики,
mutation testing, альтернативный дизайн и benchmark. Выполнены все допзадания A–G.

PDF содержит описание DocumentManager, но не исходник преподавателя. Учебный
legacy подготовлен по описанию и не выдаётся за упомянутые там 2000 строк.
Его поведение зафиксировано до рефакторинга, далее файл и исходные тесты не менялись.

## Запуск

Python 3.10+ (проверено на 3.12), Git:

```bash
git clone https://github.com/konstmalinin-maker/solid-refactoring-variant-5.git
cd solid-refactoring-variant-5
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python main.py --directory demo-data
```

В Windows активация: `.venv\Scripts\activate`. Пакет solid установлен из src/solid
в editable-режиме; внешний путь src.compat сохранён тонким импортом для старых тестов.

## Проверки

```bash
ruff check .
pytest tests_before --backend=legacy -q --cov=legacy --cov-fail-under=80
pytest tests_before tests_after -q --cov=solid --cov-fail-under=85
pytest tests_before --backend=alternative -q
python scripts/check_frozen.py
python scripts/metrics.py --path src/solid --output docs/metrics-final.json --gate
mutmut run --max-children 2
python scripts/mutation_summary.py --output docs/mutation-full.json --gate
python -m scripts.compare_designs
python -m scripts.benchmark
```

`check_frozen.py` требует Git-историю; скачанный полный комплект содержит bundle.
Не запускайте одновременные mutmut и benchmark для итоговых измерений.

## Структура

- legacy/ — сохранённый плохой код.
- src/solid/domain — модели, валидация, возможности и порты.
- src/solid/application — команды, запросы, версии, экспорт и read-only клиент.
- src/solid/infrastructure — JSON/memory, audit, контейнер, заказный репозиторий.
- src/solid/extensions — точные заказные примеры A–C: политики, Factory Method, Order Builder и OrderService.
- alternative/ — функциональные use cases и dispatch table для того же DocumentManager.
- tests_before/ — неизменные 23 характеризующих теста; tests_after/ — новый дизайн и точные контракты ошибок.
- quality_demo/ — намеренно слабые проверки для сравнения покрытия и качества.
- benchmarks/ — отдельный монолитный эталон для буквального задания про 1000 заказов.
- scripts/ — метрики, мутации, аудит неизменности и измерения.
- docs/ — план, данные, обоснования и отчёт со скриншотами.

## Результаты

75 тестов проходят; покрытие строк реализации 100%.
Core: CC 1,6364 → 1,373; weighted MI 43,8101 → 67,3672;
максимум метода 15 → 11 LOC; методов основного обработчика 13 → 4.
Количество типов и SLOC возросло, это явно показано в таблице.
Mutmut: 469 killed / 496, 27 survived (5,44%), без пропусков и timeout.
Слабый smoke-тест также имеет 100% line coverage, но 33,33% выживших на том же модуле.

## Допзадания

A — расширяемый Factory Method политик скидок, регистрация декоратором.
B — неизменяемый Order и Builder с проверкой обязательных параметров.
C — register/resolve/override контейнер; main.py собирает OrderService, тесты подменяют реализации.
D — CI с Ruff, pytest >=85%, CC <=10, weighted MI >=60 и реальным рангом A для каждого файла.
E — весь src/solid проверен mutmut; сырые данные и разбор survivors сохранены.
F — самостоятельный функциональный вариант, те же исходные тесты и сравнение метрик.
G — реальные timeit для 1000 документов и 1000 заказов; ухудшение CPU-примера объяснено.

Основной workflow должен быть зелёным. Отдельный `Expected failure - legacy quality gate`
на ветке demo/quality-gate-baseline специально красный: он доказывает отказ CI на плохих метриках.

[План](docs/refactoring-plan.md) · [Метрики](docs/metrics.md) · [Мутации](docs/mutation-review.md) ·
[Сравнение дизайнов](docs/alternative.md) · [Бенчмарк](docs/benchmark.md) · [Самопроверка](docs/self-review.md)

Внешний одногруппник не участвовал; независимое одобрение PR не имитировалось.

## Отчёт и скриншоты

[Основной отчёт, Markdown (8 страниц при экспорте)](PR9_Отчёт_Малинин.md) ·
[Word](docs/reports/PR9_Отчёт_Малинин.docx) · [PDF](docs/reports/PR9_Отчёт_Малинин.pdf)

[Подробное приложение, 25 страниц / 23 скриншота](PR9_Приложение_Скриншоты_Малинин.md) ·
[Word приложения](docs/reports/PR9_Приложение_Скриншоты_Малинин.docx) ·
[PDF приложения](docs/reports/PR9_Приложение_Скриншоты_Малинин.pdf)

Оригинальные PNG: [docs/pr9-images](docs/pr9-images). Контрольные суммы и описание
происхождения: [screenshots.json](docs/evidence/screenshots.json). Снимки терминала
показывают реальное выполнение команд либо сохранённые исходные журналы,
измеренные JSON и ответы GitHub API. Изображения не перерисовывались; в печатной
вёрстке скрыта только пустая нижняя область некоторых снимков.
