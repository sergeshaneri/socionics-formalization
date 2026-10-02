---
id: "A0042"
title: "Code and tests for the equivariant algebra of traits on 8T9"
kind: "computational_package"
source_paths:
  - "formalization/equivariant-8T9"
representations: []
documented_date: "not established"
origin: "The folder is in the formalization project; according to the author’s note, the materials are associated with long-term work with GPT Astra and Sol. The exact contributions of the author and generative system to the code have not been established."
model: "not established"
prompt: "not established"
topics:
  - "formalization"
  - "model-a-subgroups"
related_artifacts:
  - id: "A0041"
    relation: "contains_report_copy"
    basis: "FORMALIZATION.md in the folder is byte-for-byte identical to the A0041 reports."
---

# Code and tests for the equivariant algebra of traits on 8T9

## Description

The unpacked folder contains an implementation of the ⋆ law, a test module, the source table, a formal report, and auxiliary source files.

## Claimed results

- According to the report, the unit tests compare the ⋆ law with all 256 permutation compositions and check finite matrix and conjugation constructions. **Basis:** FORMALIZATION.md, “Verification and provenance” section; test_equivariant.py.

## Source materials and reading

- `project_sources/09-markdown-1-.md` — the source table inside the package directory.

**Open first:**
- [FORMALIZATION.md](<../../../../formalization/equivariant-8T9/FORMALIZATION.md>)
- [equivariant.py](<../../../../formalization/equivariant-8T9/equivariant.py>)

**Reading level:** `package_tree_and_test_overview`.

## Provenance

The folder is in the formalization project; according to the author’s note, the materials are associated with long-term work with GPT Astra and Sol. The exact contributions of the author and generative system to the code have not been established.

## Status and checks

- Artifact status: `found_readable`.
- Computational check status: `not_run`.
- The tree contents were listed, including code, tests, and the source table. `__pycache__` and `.pyc` were excluded as technical cache. Tests were not run.

## Limitations and uncertainties

- The presence of tests does not establish that they currently pass; cataloging did not repeat the mathematical checks.

## Relationships

- contains_report_copy: [A0041](<../A0041/card.md>). FORMALIZATION.md in the folder is byte-for-byte identical to the A0041 reports.

---

[File manifest](manifest.json) · [Verification log](verification.md)