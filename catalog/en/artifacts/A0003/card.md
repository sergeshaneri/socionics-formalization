---
id: "A0003"
title: "Computational package for the classification of tetrachotomies and tetrads (2026-09-28)"
kind: "computational_package"
source_paths:
  - "agent-researches/2026-09-28-tetrad-classification.zip"
representations: []
documented_date: "2026-09-28"
origin: "According to the author, the collection was produced through extended work with GPT Astra and Sol. The model, prompt, and creation date of this specific package have not been established."
model: "not established"
prompt: "not established"
topics:
  - "tetrad-classification"
  - "model-a-subgroups"
related_artifacts:
  - id: "A0002"
    relation: "possibly_related"
    basis: "The ZIP contains a Markdown file with the same title. Its size and SHA-256 hash differ from those of the external report; identity between the editions is not assumed."
---

# Computational package for the classification of tetrachotomies and tetrads (2026-09-28)

## Description

The ZIP contains a README, source tables, code, results, a correction log, and its own edition of the report. The top-level CHECKSUMS.json passes verification; the internal data/manifest.json identifies two missing data files and two files whose contents have different names inside the package. The code was not run.

## Claimed results

- The README claims calculations for 35 partitions and 140 tetrads, and verification of 704 formulas in a derived copy of the source. **Basis:** the internal README.md and results sections; the claimed checks were not repeated.

## Source materials and reading

- Snapshots of the input tables and texts are listed in the package file catalog and internal manifests.

**Read first:**
- [2026-09-28-tetrad-classification.zip](<../../../../agent-researches/2026-09-28-tetrad-classification.zip>)

**Reading level:** `overview`.

## Provenance

According to the author, the collection was produced through extended work with GPT Astra and Sol. The model, prompt, and creation date of this specific package have not been established.

## Status and checks

- Artifact state: `incomplete`.
- Computational verification state: `integrity_only`.
- The ZIP was opened; it contains 63 entries, CRC passed, and no unsafe paths were found. The top-level CHECKSUMS.json matches 62/62 listed files. In the internal data/manifest.json, exact path matches are 0/4; hashes for two entries were found under different names; two expected contents were not found. The code was not run.

## Limitations and uncertainties

- The package is readable, but its data do not fully match the internal manifest: catalog.json and tetrachotomies-source-text.md were not found either at their expected paths or by SHA-256; two other files are present under different names.
- Stored PASS/check files inside the package are historical files; they do not confirm a new run.
- The archive was not extracted; the source archive was not modified.

## Expected attachments

- `M0006` — `incomplete_by_internal_manifest`; details in the [expected-artifact register](../../expected-artifacts.md).

## Relationships

- possibly_related: [A0002](<../A0002/card.md>). The ZIP contains a Markdown file with the same title. Its size and SHA-256 hash differ from those of the external report; identity between the editions is not assumed.

---

[File manifest](manifest.json) · [Verification log](verification.md)
