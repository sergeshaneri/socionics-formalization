# Ожидаемые приложения и пробелы охвата

Записи отделяют обещанные, но отсутствующие файлы от вероятных совпадений и внешних входов. Одинаковое имя не считается доказательством принадлежности пакету.

## M0001 — Заявленный вычислительный пакет

- Связанный артефакт: [A0010 — Множество систем признаков модели А: интерпретация, инварианты и алгебраическая программа](artifacts/A0010/card.md)
- Статус: `partial_candidate` — кандидат содержит часть заявленных файлов; связь не установлена.
- Основание: В A0010, §18, перечислены ожидаемые файлы пакета; A0011 — единственный тематически близкий ZIP, проверенный по точным относительным путям членов.

A0011 содержит 7 из 21 заявленного пути. Внутренний REPORT.md побайтно совпадает с A0012, а не с A0010; связь выпусков не установлена.

### Ожидалось

- `inputs/project_tables.md`
- `inputs/models.txt`
- `inputs/systems.json`
- `code/reproduce.py`
- `results/all_30_affine_structures.json`
- `results/compatible_4_structures.json`
- `results/affine_coefficients.csv`
- `results/coefficient_groups.csv`
- `results/balanced_coefficient_subspaces.json`
- `results/minimal_model_a_invariants.json`
- `results/system_invariant_profiles.json`
- `results/partition_stabilizers.json`
- `AFFINE_TRAITS_AND_NEW_SYSTEMS.md`
- `results/checks.json`
- `results/run.log`
- `code/build_report.py`
- `code/report_template.md`
- `code/probe_affine.py`
- `results/affine_probe.json`
- `README.md`
- `SHA256SUMS.txt`

### Наблюдаемые совпадения/кандидаты

- `inputs/models.txt`
- `inputs/systems.json`
- `code/reproduce.py`
- `results/checks.json`
- `results/run.log`
- `README.md`
- `SHA256SUMS.txt`

### Не найдено в подтверждённом составе

- `inputs/project_tables.md`
- `results/all_30_affine_structures.json`
- `results/compatible_4_structures.json`
- `results/affine_coefficients.csv`
- `results/coefficient_groups.csv`
- `results/balanced_coefficient_subspaces.json`
- `results/minimal_model_a_invariants.json`
- `results/system_invariant_profiles.json`
- `results/partition_stabilizers.json`
- `AFFINE_TRAITS_AND_NEW_SYSTEMS.md`
- `code/build_report.py`
- `code/report_template.md`
- `code/probe_affine.py`
- `results/affine_probe.json`

Кандидаты для ручной сверки: [A0011](artifacts/A0011/card.md).

## M0002 — Заявленный вычислительный пакет

- Связанный артефакт: [A0047 — Инварианты дихотомий и тетрахотомий: формальное описание и полнота](artifacts/A0047/card.md)
- Статус: `partial_unverified` — возможное совпадение; принадлежность не подтверждена.
- Основание: A0047, §13, перечисляет состав пакета; A0044 — отдельный читаемый каталог с теми же заявленными числами классов.

Совпадающий архив или распакованный выпуск не найден. A0044 — возможный сопровождающий результат, но принадлежность пакету и побайтное совпадение не установлены.

### Ожидалось

- `catalogue.md`
- `catalogue.json`
- `inputs.json`
- `audit.py`
- `statistics.json`
- `README.md`
- `копия формального отчёта внутри пакета`

### Наблюдаемые совпадения/кандидаты

- `agent-researches/catalogue.md`

### Не найдено в подтверждённом составе

- `catalogue.json`
- `inputs.json`
- `audit.py`
- `statistics.json`
- `README.md`
- `копия отчёта внутри пакета (отдельно не проверена)`

Кандидаты для ручной сверки: [A0044](artifacts/A0044/card.md).

## M0003 — Заявленный вычислительный пакет

- Связанный артефакт: [A0050 — Октохотомии социона: классификация и инварианты моделей А](artifacts/A0050/card.md)
- Статус: `absent_in_scope` — пакет в выбранном охвате не найден.
- Основание: A0050, §9.1, перечисляет файлы вычислительного приложения.

В выбранном охвате не найден соответствующий архив или распакованный пакет. Одноимённые файлы в других выпусках не отнесены к этому пакету.

### Ожидалось

- `inputs.json`
- `catalogue.json`
- `audit.py`
- `build_report.py`
- `statistics.json`
- `README.md`
- `source-conflict-semantics.png`

### Наблюдаемые совпадения/кандидаты

- Нет зарегистрированных записей.

### Не найдено в подтверждённом составе

- `inputs.json`
- `catalogue.json`
- `audit.py`
- `build_report.py`
- `statistics.json`
- `README.md`
- `source-conflict-semantics.png`

## M0004 — Заявленный вычислительный пакет

- Связанный артефакт: [A0030 — Действия подгрупп социона на восьми функциях](artifacts/A0030/card.md)
- Статус: `candidate_not_verified` — содержательно близкий пакет не подтверждён как тот же выпуск.
- Основание: A0030, §10, приводит команды и описывает содержимое архива, но не указывает имя или путь архива.

A0034 — пакет от 25 сентября о ядрах орбит с исходными данными по подгруппам и src/report.py. В нём другой отчёт и src/analyze_kernels.py вместо src/analyze.py; он не считается обещанным пакетом A0030.

### Ожидалось

- `src/analyze.py`
- `src/report.py`
- `README.md`
- `таблицы исходных данных (имена не указаны)`
- `35 подгрупп и данные включений`
- `результаты для 140 тетрад`
- `отчёт и PDF`

### Наблюдаемые совпадения/кандидаты

- Нет зарегистрированных записей.

### Не найдено в подтверждённом составе

- `архив и README соответствующего выпуска`
- `src/analyze.py`
- `манифест пакета и полные результаты`

Кандидаты для ручной сверки: [A0034](artifacts/A0034/card.md).

## M0005 — Внешние входы для воспроизведения

- Связанный артефакт: [A0043 — Аудит соответствия авторских определений и формул дихотомий](artifacts/A0043/card.md)
- Статус: `inputs_absent_from_scope` — исходные входы или скрипт находятся вне охвата.
- Основание: Раздел повторного запуска A0043 указывает внешний исходник, скрипт и архивный вход; исходник и скрипт находятся вне выбранных корней.

Отчёт и два JSON-результата доступны. Повторить аудит исходных формул только по этому репозиторию нельзя.

### Ожидалось

- `исходный Markdown из отдельного репозитория`
- `tools/audit_dichotomy_source.py`

### Наблюдаемые совпадения/кандидаты

- `audits/dichotomy-source-audit.json (снимок исходных значений)`
- `audits/aspect-pattern-checks.json (зафиксированные конечные проверки)`

### Не найдено в подтверждённом составе

- `исходный Markdown-файл`
- `tools/audit_dichotomy_source.py`

Кандидаты для ручной сверки: [A0036](artifacts/A0036/card.md).

## M0006 — Неполный состав по внутреннему манифесту

- Связанный артефакт: [A0003 — Вычислительный пакет классификации тетрахотомий и тетрад (2026-09-28)](artifacts/A0003/card.md)
- Статус: `incomplete_by_internal_manifest` — внутренний манифест указывает на отсутствующие файлы.
- Основание: Внутренний data/manifest.json перечисляет четыре SHA-256; их сопоставили по содержимому со всеми 63 ZIP-членами.

Два ожидаемых содержимых присутствуют под другими именами; два не найдены ни по пути, ни по SHA-256. Отдельный CHECKSUMS.json подтверждает 62/62 фактически перечисленных файла и не отменяет этот пробел.

### Ожидалось

- `data/catalog.json`
- `data/classification.md`
- `data/tables.md`
- `data/tetrachotomies-source-text.md`

### Наблюдаемые совпадения/кандидаты

- `data/classification.md: тот же SHA-256 у data/классификация разбиений и подгрупп.md`
- `data/tables.md: тот же SHA-256 у data/09-markdown-1-.md`

### Не найдено в подтверждённом составе

- `data/catalog.json`
- `data/tetrachotomies-source-text.md`

## M0007 — Неполный состав по внутреннему манифесту

- Связанный артефакт: [A0006 — Исправленный пакет аудита Тенсера—Минаева](artifacts/A0006/card.md)
- Статус: `incomplete_by_internal_manifest` — внутренний манифест указывает на отсутствующие файлы.
- Основание: Сопоставлены package-manifest.json (24 записи) и source-manifest.json (9 записей) с членами ZIP по относительному пути, размеру и SHA-256.

Манифест пакета: 19 точных совпадений, одно совпадение содержимого под другим путём, четыре отсутствующих содержимых. Манифест источников: 6 точных совпадений, одно под другим путём и два отсутствующих содержимых.

### Ожидалось

- `sources/.codex-upload-6a83d91047714bdba4669fd6bda48e71`
- `sources/.codex-upload-6e1a86afa65a4cfabfbb397c01c0efd1`
- `sources/.codex-upload-6f77ab2b01c24b2dbf05a07e99139d62`
- `statistics.json`
- `verify_report.py`

### Наблюдаемые совпадения/кандидаты

- `sources/.codex-upload-6a83d91047714bdba4669fd6bda48e71: такой же SHA-256 имеет sources/.codex-upload-01e6b54f44f84d1e9359afde19d38159`

### Не найдено в подтверждённом составе

- `sources/.codex-upload-6e1a86afa65a4cfabfbb397c01c0efd1 (нулевой размер по манифесту; путь отсутствует)`
- `sources/.codex-upload-6f77ab2b01c24b2dbf05a07e99139d62`
- `statistics.json`
- `verify_report.py`
