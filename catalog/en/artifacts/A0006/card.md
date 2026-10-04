---
id: "A0006"
title: "Corrected Tencer–Minaev audit package"
kind: "computational_package"
source_paths:
  - "agent-researches/2026-09-07-tencer-minaev-audit-FIXED.zip"
  - "agent-researches/tencer-minaev-audit"
representations: []
documented_date: "2026-09-07"
origin: "According to the author, the collection was produced through extended work with GPT Astra and Sol. The model, prompt, and creation date of this specific package have not been established."
model: "not established"
prompt: "not established"
topics:
  - "tencer-minaev"
  - "tetrad-classification"
related_artifacts:
  - id: "A0004"
    relation: "supports"
    basis: "The internal README identifies the Markdown as the main report; its bytes match the external copy."
  - id: "A0005"
    relation: "possibly_related"
    basis: "An association is suggested by the names FIXED and the original ZIP; provenance from the damaged archive cannot be established."
---

# Corrected Tencer–Minaev audit package

## Description

The ZIP and the available extracted folder are byte-identical for 20 files. The internal manifests are nevertheless incomplete: the package manifest confirms 19 of 24 expected paths; some source contents are missing, and one file appears only under a different name.

## Claimed results

- The internal README describes recalculation and an independent interpretation of formulas, including 4640 truth values; these computations were not repeated during cataloging. **Basis:** internal README.md, “Reproduction” and “Files” sections.

## Source materials and reading

- Input tables and their provenance are listed in the internal inputs.json and source-manifest.json.

**Read first:**
- [README.md](<../../../../agent-researches/tencer-minaev-audit/README.md>)
- [2026-09-07-tencer-minaev-invariants.md](<../../../../agent-researches/tencer-minaev-audit/2026-09-07-tencer-minaev-invariants.md>)

**Reading level:** `package_readme_and_manifest_overview`.

## Provenance

According to the author, the collection was produced through extended work with GPT Astra and Sol. The model, prompt, and creation date of this specific package have not been established.

## Status and checks

- Artifact state: `incomplete`.
- Computational verification state: `integrity_only`.
- The ZIP opened; CRC passed; no unsafe paths were found. Its 20 files match the extracted tree by path and SHA-256, but this does not confirm package completeness. Package manifest: exact matches 19/24, one content item found under a different name, four declared contents missing, and no SHA-256 mismatches. Source manifest: exact matches 6/9, one content item found under a different name, and two contents missing. The code was not run.

## Limitations and uncertainties

- The manifest lists statistics.json, verify_report.py, and two source materials as missing; one more source path is absent, but its bytes match another archive entry.
- The package's reproducibility and mathematical claims were not checked in a new run.
- The saved report-verification.json is a historical result, not a fresh check.

## Expected attachments

- `M0007` — `incomplete_by_internal_manifest`; details in the [expected-artifact register](../../expected-artifacts.md).

## Relationships

- supports: [A0004](<../A0004/card.md>). The internal README identifies the Markdown as the main report; its bytes match the external copy.
- possibly_related: [A0005](<../A0005/card.md>). An association is suggested by the names FIXED and the original ZIP; provenance from the damaged archive cannot be established.

---

[File manifest](manifest.json) · [Verification log](verification.md)
