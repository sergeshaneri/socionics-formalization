---
id: "A0014"
title: "Computational package for products of 16 trait systems"
kind: "computational_package"
source_paths:
  - "agent-researches/2026-09-08_waffle-systems_computations.zip"
representations: []
documented_date: "2026-09-08"
origin: "According to the author, the collection was produced through extended work with GPT Astra and Sol. The model, prompt, and creation date of this specific package are not established."
model: "not established"
prompt: "not established"
topics:
  - "trait-systems"
related_artifacts:
  - id: "A0015"
    relation: "contains_report_copy"
    basis: "The internal REPORT.md is byte-identical to the external Markdown report; the package also contains ALL_WAFFLE_PARTITIONS.md."
---

# Computational package for products of 16 trait systems

## Description

The package contains calculations of all pairwise products of 16 trait systems, tables of 15 additional eight-element sets, the full list of partitions, scripts, and a report with an appendix.

## Claimed results

- The README describes how to reproduce all results using two Python standard-library scripts and how to generate a Markdown report and appendix. **Basis:** README.md, “Reproduce,” “Inputs and provenance,” and “Files.”

## Source materials and reading

- The published systems and Model A tables are listed in the archived `inputs/` directory.

**Start with:**
- [2026-09-08_waffle-systems_computations.zip](../../../../agent-researches/2026-09-08_waffle-systems_computations.zip)

**Reading level:** `README_and_manifest_overview`.

## Provenance

According to the author, the collection was produced through extended work with GPT Astra and Sol. The model, prompt, and creation date of this specific package are not established.

## Status and checks

- Artifact status: `found_readable`.
- Computational check status: `not_run`.
- The ZIP opens; all 28 files pass CRC, and no unsafe paths were found. The README and package contents were inspected; the code was not run.

## Limitations and uncertainties

- The successful computations described in the README were not rerun.

## Relationships

- contains_report_copy: [A0015](../A0015/card.md). The package contains a byte-identical copy of the report, the complete list of pairings, and computation files.

---

[File manifest](manifest.json) · [Verification log](verification.md)
