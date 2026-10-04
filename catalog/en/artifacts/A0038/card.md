---
id: "A0038"
title: "Verifiable package for H16 and 8T9"
kind: "computational_package"
source_paths:
  - "agent-researches/2026-09-29-fraktal-H16-8T9-vychisleniya.zip"
representations: []
documented_date: "2026-09-29"
origin: "According to the author, the collection was produced during extended work with GPT Astra and Sol. The model, prompt, and creation date of this specific package have not been established."
model: "not established"
prompt: "not established"
topics:
  - "group-cocycles"
  - "model-a-subgroups"
  - "formalization"
related_artifacts:
  - id: "A0037"
    relation: "contains_report_copy"
    basis: "The internal Markdown file is byte-for-byte identical to the external report."
---

# Verifiable package for H16 and 8T9

## Description

The six-file archive contains a report, PDF, snapshot of the source table, verification program, and the full text of the saved results.

## Reported results

- The README specifies verification with an independent script requiring no third-party libraries and lists SHA-256 hashes for the main package members. **Basis:** internal README.md.

## Source materials and reading

- The unchanged Model A table is stored in project_sources/; the full member list is in manifest.json.

**Start with:**
- [2026-09-29-fraktal-H16-8T9-vychisleniya.zip](<../../../../agent-researches/2026-09-29-fraktal-H16-8T9-vychisleniya.zip>)

**Reading level:** `README_and_manifest_overview`.

## Provenance

According to the author, the collection was produced during extended work with GPT Astra and Sol. The model, prompt, and creation date of this specific package have not been established.

## Status and checks

- Artifact status: `found_readable`.
- Computational check status: `not_run`.
- The ZIP opens; all 6 files pass CRC, and no unsafe paths were found. The README and checksums were read; the script was not run.

## Limitations and uncertainties

- The internal results are a saved log, not a fresh verification.

## Relationships

- contains_report_copy: [A0037](<../A0037/card.md>). The internal Markdown file is byte-for-byte identical to the external report.

---

[File manifest](manifest.json) · [Verification log](verification.md)
