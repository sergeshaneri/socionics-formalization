---
id: "A0021"
title: "Computational package for analyzing the completeness of invariants for new systems"
kind: "computational_package"
source_paths:
  - "agent-researches/2026-09-09_new-systems_invariant-completeness_computations.zip"
representations: []
documented_date: "2026-09-09"
origin: "According to the author, the collection was produced through extended work with GPT Astra and Sol. The model, prompt, and creation date of this specific package are not established."
model: "not established"
prompt: "not established"
topics:
  - "trait-systems"
  - "model-a-subgroups"
  - "formalization"
related_artifacts:
  - id: "A0020"
    relation: "contains_report_copy"
    basis: "The internal invariant-completeness/report.md is byte-identical to the external report."
---

# Computational package for analyzing the completeness of invariants for new systems

## Description

The package contains an independent computational analysis of invariants, tables of project data, a complete results array, and a compiled report.

## Claimed results

- The README describes how to reproduce union profiles, closures, groups, orbits, and separation tests; the code uses the Python standard library. **Basis:** internal README.md, “Reproduce” and the description of the independent archive verification.

## Source materials and reading

- Input tables and results are in the `inputs/` and `results/` subdirectories.

**Start with:**
- [2026-09-09_new-systems_invariant-completeness_computations.zip](../../../../agent-researches/2026-09-09_new-systems_invariant-completeness_computations.zip)

**Reading level:** `README_and_manifest_overview`.

## Provenance

According to the author, the collection was produced through extended work with GPT Astra and Sol. The model, prompt, and creation date of this specific package are not established.

## Status and checks

- Artifact status: `found_readable`.
- Computational check status: `not_run`.
- The ZIP opens; all 26 files pass CRC, and no unsafe paths were found. The README was reviewed; reproduction was not run.

## Limitations and uncertainties

- Saved results are not a new computation.

## Relationships

- contains_report_copy: [A0020](../A0020/card.md). The internal invariant-completeness/report.md is byte-identical to the external report.

---

[File manifest](manifest.json) · [Verification log](verification.md)
