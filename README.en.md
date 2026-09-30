# Formalization of Socionics

**Language:** [Русский](README.md) · English

An open research corpus containing primary definitions and tables, historical reports with computational packages, working chapters of the formalization, and reproducible checks. Publication makes a study available; it does not validate every claim in it.

## Navigation

- [`HANDOFF.md`](HANDOFF.md) — research context, mathematical setup, verified results, and open tasks for a subsequent agent. This document is currently in Russian.
- `sources/primary/` — unchanged copies of 26 primary Markdown documents, in Russian. Draft articles are sources for formulas, not automatically accepted theorems.
- `sources/context/gpt-output.md` — a supplied analytical text; its claims require independent verification.
- `agent-researches/` — historical reports, archives, and computational data imported from `research-harness`. Some later results qualify or correct earlier ones. Most reports are in Russian.
- `formalization/aspect-patterns.md` — working chapter on aspect patterns and actions on paired partitions.
- `formalization/equivariant-8T9/` — separate prototype of an algebra of functions on 8T9, including its source table and tests.
- `audits/`, `tools/`, `tests/` — discrepancy records, verification programs, and regression tests.
- `provenance/import-manifest.json` — SHA-256 and source collection for each imported file.

## Reproducing checks

From the repository root:

```bash
python -m unittest discover -s tests -v
python tools/verify_aspect_patterns.py
python -m unittest discover -s formalization/equivariant-8T9 -v
```

Some audit checks require a local path to the author's original source. See `audits/dichotomy-definitions-and-corrections.md` for an example. Consult each report for the scope of its checks. Primary texts and archives are not edited to make tests pass.

## Epistemic status

Claims are classified as definitions, mathematical consequences of stated axioms, finite-table checks, reconstructions of authorial intent, or hypotheses. Agreement of a formula with the 16 specified models establishes recognition within that family; unique reconstruction of the models among all bijections requires a separate investigation.

The historical archive `agent-researches/2026-09-07-tencer-minaev-audit.zip` is damaged and cannot be opened as a ZIP. A `-FIXED.zip` version is present alongside it; examine their contents and provenance rather than treating the original as repaired.

The monograph from the adjacent older project was not imported as a standalone text. Some historical computational packages may include copies of drafts used as inputs; those copies are retained as recorded package inputs. A reuse license has not yet been selected; public access alone does not grant a license.
