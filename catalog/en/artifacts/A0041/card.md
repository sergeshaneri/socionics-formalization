---
id: "A0041"
title: "First formal layer: equivariant algebra of traits on 8T9"
kind: "formalization_report"
source_paths:
  - "agent-researches/FORMALIZATION.md"
  - "agent-researches/FORMALIZATION research"
  - "formalization/equivariant-8T9/FORMALIZATION.md"
representations: []
documented_date: "not established"
origin: "According to the author’s HANDOFF note, the materials were produced through long-term work with GPT Astra and Sol. The exact model, session, and authorship of individual formulas in this text have not been established."
model: "not established"
prompt: "not established"
topics:
  - "formalization"
  - "model-a-subgroups"
related_artifacts:
  - id: "A0042"
    relation: "accompanies"
    basis: "The file is located in a package with code and tests; the same report content is included in the package directory."
  - id: "A0038"
    relation: "uses"
    basis: "The text ties the finite checks to the table from the H16/8T9 package."
---

# First formal layer: equivariant algebra of traits on 8T9

## Description

The text builds a first formal layer on V=F₂⁴: it distinguishes coordinate-wise addition of traits from composition of relation permutations, defines a transportable ⋆ law, and considers invariants under conjugation.

## Claimed results

- The report’s author states that the formulas in the selected coordinates were checked against the finite table; the 2→4 formulas and order-dependent formulas are not yet included as proven generators of the algebra. **Basis:** Status; §§1–4.

## Source materials and reading

- The main Model A table is included in computational package A0042 and archive A0038.

**Open first:**
- [FORMALIZATION.md](<../../../../agent-researches/FORMALIZATION.md>)

**Reading level:** `overview_opening_headings_conclusion_and_provenance`.

## Provenance

According to the author’s HANDOFF note, the materials were produced through long-term work with GPT Astra and Sol. The exact model, session, and authorship of individual formulas in this text have not been established.

## Status and checks

- Artifact status: `found_readable`.
- Computational check status: `not_run`.
- The three report files are byte-for-byte identical. The construction statements, limits of the claimed proof, and verification section were reviewed; package tests were not run separately.

## Limitations and uncertainties

- The document itself marks several ARP formulas and a complete algebraic classification as future work.

## Relationships

- accompanies: [A0042](<../A0042/card.md>). The file is located in a package with code and tests; the same report content is included in the package directory.
- uses: [A0038](<../A0038/card.md>). The text ties the finite checks to the table from the H16/8T9 package.

---

[File manifest](manifest.json) · [Verification log](verification.md)