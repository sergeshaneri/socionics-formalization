---
id: "A0043"
title: "Audit of conformity between authorial definitions and dichotomy formulas"
kind: "audit_bundle"
source_paths:
  - "audits/dichotomy-definitions-and-corrections.md"
  - "audits/dichotomy-source-audit.json"
  - "audits/aspect-pattern-checks.json"
representations: []
documented_date: "not established"
origin: "The report gives the source commit `cb8d88f` and the research harness commit `6d36916`; authorship of the specific formulas and model has not been established."
model: "not established"
prompt: "not established"
topics:
  - "source-audits"
  - "formalization"
  - "model-a-subgroups"
related_artifacts:
  - id: "A0036"
    relation: "uses"
    basis: "The rerun command in the report explicitly specifies archive A0036 as --archive."
---

# Audit of conformity between authorial definitions and dichotomy formulas

## Description

The audit describes five corrected formula rows, checks of 82 explicit entries across 16 models, and separate aspect-pattern checks; it distinguishes entry errors, authorial definitions, and limitations of the finite table.

## Claimed results

- The JSON baseline records 82 formulas: 45 mapped to the positive pole, 32 to the negative pole, and 5 marked MISMATCH; the report states that after correction all 82 entries isolate one pole. **Basis:** dichotomy-source-audit.json: baseline; report, “Corrections made” section.
- The second JSON reports all_checks_passed=true and 112 direction checks, 64 rational-switch checks, and 128 negation-parity checks. **Basis:** aspect-pattern-checks.json, counter and scope fields.

## Source materials and reading

- The report refers to a source document in a separate repository and to dichotomy-formalization archive A0036.

**Open first:**
- [dichotomy-definitions-and-corrections.md](<../../../../audits/dichotomy-definitions-and-corrections.md>)
- [dichotomy-source-audit.json](<../../../../audits/dichotomy-source-audit.json>)

**Reading level:** `full_audit_report_and_json_headers`.

## Provenance

The report gives the source commit `cb8d88f` and the research harness commit `6d36916`; authorship of the specific formulas and model has not been established.

## Status and checks

- Artifact status: `found_readable`.
- Computational check status: `not_run`.
- The full report was read; the JSON files were reviewed by keys, summary fields, and selected rows. The external source document and checking script are absent from the selected roots; the run was not repeated.

## Limitations and uncertainties

- dichotomy-source-audit.json contains the baseline version before correction; the 82 post-correction rows are not provided in a separate machine-readable JSON. aspect-pattern-checks.json applies to the fixed table and does not check prose or images.

## Expected attachments

- `M0005` — `inputs_absent_from_scope`; details in the [expected attachments register](../../expected-artifacts.md).

## Relationships

- uses: [A0036](<../A0036/card.md>). The rerun command in the report explicitly specifies archive A0036 as --archive.

---

[File manifest](manifest.json) · [Verification log](verification.md)