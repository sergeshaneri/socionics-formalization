---
id: "A0021"
title: "Вычислительный пакет анализа полноты инвариантов новых систем"
kind: "computational_package"
source_paths:
  - "agent-researches/2026-09-09_new-systems_invariant-completeness_computations.zip"
representations: []
documented_date: "2026-09-09"
origin: "По сообщению автора, коллекция получена в длительной работе с GPT Astra и Sol. Модель, запрос и дата создания конкретного пакета не установлены."
model: "не установлено"
prompt: "не установлено"
topics:
  - "trait-systems"
  - "model-a-subgroups"
  - "formalization"
related_artifacts:
  - id: "A0020"
    relation: "contains_report_copy"
    basis: "Внутренний invariant-completeness/report.md побайтно совпадает с внешним отчётом."
---

# Вычислительный пакет анализа полноты инвариантов новых систем

## Описание

Пакет содержит независимый вычислительный анализ инвариантов, таблицы проектных данных, полный массив результатов и собранный отчёт.

## Заявленные результаты

- README указывает на воспроизведение union-профилей, замыканий, групп, орбит и тестов разделения; код использует стандартную библиотеку Python. **Основание:** внутренний README.md, «Reproduce» и описание независимой archive verification.

## Исходные материалы и чтение

- Входные таблицы и результаты лежат в подпапках inputs/ и results/.

**Открыть сначала:**
- [2026-09-09_new-systems_invariant-completeness_computations.zip](<../../../agent-researches/2026-09-09_new-systems_invariant-completeness_computations.zip>)

**Уровень чтения:** `README_and_manifest_overview`.

## Происхождение

По сообщению автора, коллекция получена в длительной работе с GPT Astra и Sol. Модель, запрос и дата создания конкретного пакета не установлены.

## Статус и проверки

- Состояние артефакта: `found_readable`.
- Состояние вычислительной проверки: `not_run`.
- ZIP открывается; 26 файлов проходят CRC, небезопасных путей не обнаружено. README просмотрен; воспроизведение не запускалось.

## Ограничения и неопределённости

- Сохранённые результаты не являются новым вычислением.

## Связи

- contains_report_copy: [A0020](<../A0020/card.md>). Внутренний invariant-completeness/report.md побайтно совпадает с внешним отчётом.

---

[Манифест файлов](manifest.json) · [Журнал проверок](verification.md)
