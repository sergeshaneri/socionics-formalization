# Research artifact catalog

[Project overview](../../README.en.md)

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
- Per-artifact file manifests are linked from their respective cards.

## Coverage

The full catalog covers 337 physical files: 306 files linked to artifact cards, 27 separately recorded sources, 3 technical exclusions, and 1 administrative file. All 52 identified artifacts have cards; no file remains unclassified. This hosted English branch includes the 52 reader cards and per-artifact manifests, not the shared registry or file-level inventory.

In the full catalog, the inventory JSON preserves paths, IDs, hashes, and status codes; some explanatory strings remain in Russian. This English-only branch omits that JSON and provides translated reader-facing descriptions here and in the expected-artifact register.

The archive pass examined 14 ZIP files. Thirteen open and pass CRC checks; one is unreadable. No unsafe archive paths were found in the 13 readable archives. Three internal-manifest checks across two packages remain incomplete. Archive integrity checks do not constitute a mathematical audit or a fresh computational rerun.

## Status distinctions

Each card separates the artifact's state from the work actually performed. A saved `PASS` file or a report's claim of verification is historical evidence; it is not a rerun performed for this catalog. Results on a finite table are not presented as a proof over a broader domain.

No archive code was executed while preparing this catalog. Mathematical auditing and full topic clustering remain future work.

## Next actions

1. Resolve [Q0001 and Q0002](questions.md), concerning the relationship between report editions and the origin of a repaired archive.
2. Review records M0001–M0005 in [the missing-artifact register](expected-artifacts.md); do not equate packages from filename similarity alone.
3. Locate or clarify the missing members listed in M0006 and M0007 without modifying the historical archives.
4. Plan mathematical auditing and topic clustering as separate stages.

This branch is a static reading copy. The index-generation script and registry are maintained with the full catalog and are not included here. Source links point to files in this repository's existing source directories; this catalog does not imply fresh mathematical verification.
