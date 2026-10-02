# Проверки A0006

Уровень чтения: `package_readme_and_manifest_overview`.

- ZIP открыт; перечислено 20 файлов, проверены безопасные пути и CRC. SHA-256 всех файлов в архиве совпали с соответствующей распакованной папкой. Внутренний package-manifest будет независимо сверён сборщиком каталога. Код не запускался.

## Архив `agent-researches/2026-09-07-tencer-minaev-audit-FIXED.zip`

- Открытие: `True`; CRC: `passed`.
- Файловых записей: 20; распакованный объём: 13048789 байт.
- Небезопасных путей/ссылок: 0.
- Внутренний манифест `tencer-minaev-audit/package-manifest.json`: `incomplete_or_mismatch`; записей 19/24, отсутствует 5, несовпадений 0.
  Отсутствующие записи: `sources/.codex-upload-6a83d91047714bdba4669fd6bda48e71`, `sources/.codex-upload-6e1a86afa65a4cfabfbb397c01c0efd1`, `sources/.codex-upload-6f77ab2b01c24b2dbf05a07e99139d62`, `statistics.json`, `verify_report.py`.
- Внутренний манифест `tencer-minaev-audit/source-manifest.json`: `incomplete_or_mismatch`; записей 6/9, отсутствует 3, несовпадений 0.
  Отсутствующие записи: `sources/.codex-upload-6a83d91047714bdba4669fd6bda48e71`, `sources/.codex-upload-6e1a86afa65a4cfabfbb397c01c0efd1`, `sources/.codex-upload-6f77ab2b01c24b2dbf05a07e99139d62`.

Независимый математический аудит и повторный запуск вычислительного кода в рамках каталогизации не выполнялись.
