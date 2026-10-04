# Research artifact catalog

[Русская версия](../README.md)

This is the English reader copy of the catalog, current as of 2 October 2026. It translates catalog records and navigation; the original research reports and source documents remain unchanged and are mostly in Russian. Source files are not duplicated here; their links resolve when this copy is opened inside a repository checkout.

## Scope

- `agent-researches/`
- `audits/`
- `formalization/equivariant-8T9/`
- `sources/`
- `provenance/import-manifest.json` was read as an administrative provenance record and excluded from research-artifact counts.
- Primary sources are recorded separately and are not treated as AI-generated artifacts without provenance evidence.
- Local handoff files, `.git`, neighboring repositories, and active formalization areas outside the listed roots were not scanned.

## Contents

- [Topic index and artifact cards](topics.md)
- [Open questions](questions.md)
- [Expected but missing or incomplete artifacts](expected-artifacts.md)
- [Catalog schema](schema.md)
- [File-level inventory and hashes](../inventory.json)

## Coverage

The inventory contains 337 physical files: 306 files linked to artifact cards, 27 separately recorded sources, 3 technical exclusions, and 1 administrative file. All 52 identified artifacts have cards; no file remains unclassified.

The inventory JSON is shared with the Russian catalog. Paths, IDs, hashes, and status codes are unchanged; some explanatory strings in that machine-readable file remain in Russian. This page and the English expected-artifact register provide the translated reader-facing descriptions.

The archive pass examined 14 ZIP files. Thirteen open and pass CRC checks; one is unreadable. No unsafe archive paths were found in the 13 readable archives. Three internal-manifest checks across two packages remain incomplete. Archive integrity checks do not constitute a mathematical audit or a fresh computational rerun.

## Status distinctions

Each card separates the artifact's state from the work actually performed. A saved `PASS` file or a report's claim of verification is historical evidence; it is not a rerun performed for this catalog. Results on a finite table are not presented as a proof over a broader domain.

No archive code was executed while preparing this catalog. Mathematical auditing and full topic clustering remain future work.

## Next actions

1. Resolve [Q0001 and Q0002](questions.md), concerning the relationship between report editions and the origin of a repaired archive.
2. Review records M0001–M0005 in [the missing-artifact register](expected-artifacts.md); do not equate packages from filename similarity alone.
3. Locate or clarify the missing members listed in M0006 and M0007 without modifying the historical archives.
4. Plan mathematical auditing and topic clustering as separate stages.

The English topic index and manifest copies can be refreshed with `python catalog/en/build_indexes.py` from the repository root. This does not translate or rebuild card prose. The Russian catalog is rebuilt with `python catalog/build_catalog.py`.
