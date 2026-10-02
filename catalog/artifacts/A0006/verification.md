# Проверки A0006

Уровень чтения: `package_readme_and_manifest_overview`.

- ZIP открыт; CRC пройден; небезопасных путей нет. Его 20 файлов совпадают с распакованным деревом по путям и SHA-256, но это не подтверждает полноту пакета. Package-manifest: точные совпадения 19/24, одно содержимое найдено под другим именем, четыре объявленных содержимых отсутствуют, несовпадений SHA-256 нет. Source-manifest: точные совпадения 6/9, одно содержимое найдено под другим именем, два содержимых отсутствуют. Код не запускался.

## Архив `agent-researches/2026-09-07-tencer-minaev-audit-FIXED.zip`

- Открытие: `True`; CRC: `passed`.
- Файловых записей: 20; распакованный объём: 13048789 байт.
- Небезопасных путей/ссылок: 0.
- Внутренний манифест `tencer-minaev-audit/package-manifest.json`: `incomplete_or_mismatch`; точных совпадений 19/24, содержимое по другому пути 1, отсутствующих файлов 4, несовпадений 0.
  Путь `sources/.codex-upload-6a83d91047714bdba4669fd6bda48e71`: содержимое найдено как `tencer-minaev-audit/sources/.codex-upload-01e6b54f44f84d1e9359afde19d38159`.
  Отсутствующие записи: `sources/.codex-upload-6e1a86afa65a4cfabfbb397c01c0efd1`, `sources/.codex-upload-6f77ab2b01c24b2dbf05a07e99139d62`, `statistics.json`, `verify_report.py`.
- Внутренний манифест `tencer-minaev-audit/source-manifest.json`: `incomplete_or_mismatch`; точных совпадений 6/9, содержимое по другому пути 1, отсутствующих файлов 2, несовпадений 0.
  Путь `sources/.codex-upload-6a83d91047714bdba4669fd6bda48e71`: содержимое найдено как `tencer-minaev-audit/sources/.codex-upload-01e6b54f44f84d1e9359afde19d38159`.
  Отсутствующие записи: `sources/.codex-upload-6e1a86afa65a4cfabfbb397c01c0efd1`, `sources/.codex-upload-6f77ab2b01c24b2dbf05a07e99139d62`.

Независимый математический аудит и повторный запуск вычислительного кода в рамках каталогизации не выполнялись.
