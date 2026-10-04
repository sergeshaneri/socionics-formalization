# Expected artifacts and coverage gaps

These records distinguish explicitly promised files from possible matches and external inputs. A shared filename alone does not establish that a file belongs to a package.

## M0001 — Promised computational package

Related artifact: [A0010 — Systems of Model A traits: interpretation, invariants, and an algebraic program](artifacts/A0010/card.md). Status: `partial_candidate`.

Section 18 of A0010 lists 21 expected package paths. The only topic-matched ZIP tested, A0011, contains 7 of them. Its internal `REPORT.md` is byte-identical to A0012, not A0010, so the package lineage is unresolved. [Candidate: A0011](artifacts/A0011/card.md).

Missing from the candidate package:

- `inputs/project_tables.md`
- `results/all_30_affine_structures.json`
- `results/compatible_4_structures.json`
- `results/affine_coefficients.csv`
- `results/coefficient_groups.csv`
- `results/balanced_coefficient_subspaces.json`
- `results/minimal_model_a_invariants.json`
- `results/system_invariant_profiles.json`
- `results/partition_stabilizers.json`
- `AFFINE_TRAITS_AND_NEW_SYSTEMS.md`
- `code/build_report.py`
- `code/report_template.md`
- `code/probe_affine.py`
- `results/affine_probe.json`

The seven observed paths are `inputs/models.txt`, `inputs/systems.json`, `code/reproduce.py`, `results/checks.json`, `results/run.log`, `README.md`, and `SHA256SUMS.txt`.

## M0002 — Promised computational package

Related artifact: [A0047 — Dichotomy and tetrachotomy invariants: formal description and completeness](artifacts/A0047/card.md). Status: `partial_unverified`.

Section 13 of A0047 lists `catalogue.md`, `catalogue.json`, `inputs.json`, `audit.py`, `statistics.json`, `README.md`, and a copy of the report. The standalone [`catalogue.md`](../../agent-researches/catalogue.md) has the same stated scope, but no package hash or release link confirms that it was part of the promised bundle. No matching archive or extracted release was found. [Candidate: A0044](artifacts/A0044/card.md).

The other package members and the in-package report copy remain unverified.

## M0003 — Promised computational package

Related artifact: [A0050 — Socionics octochotomies: classification and Model A invariants](artifacts/A0050/card.md). Status: `absent_in_scope`.

Section 9.1 lists the expected appendix:

- `inputs.json`
- `catalogue.json`
- `audit.py`
- `build_report.py`
- `statistics.json`
- `README.md`
- `source-conflict-semantics.png`

No matching archive or extracted package was found in the selected scope. Same-named files from other releases were not treated as this package.

## M0004 — Promised computational package

Related artifact: [A0030 — Actions of socion subgroups on eight functions](artifacts/A0030/card.md). Status: `candidate_not_verified`.

Section 10 describes an archive but gives no archive filename or path. Expected contents include `src/analyze.py`, `src/report.py`, `README.md`, source tables, data for 35 subgroups and their inclusions, results for 140 tetrads, and a report/PDF.

[A0034](artifacts/A0034/card.md) is a 25 September orbit-kernels package with subgroup baseline data and `src/report.py`. It has a different report and `src/analyze_kernels.py`, not `src/analyze.py`; it is not counted as the promised A0030 package.

## M0005 — External reproduction inputs

Related artifact: [A0043 — Audit of author definitions and dichotomy formulas](artifacts/A0043/card.md). Status: `inputs_absent_from_scope`.

The rerun instructions require an original source Markdown file from another repository and `tools/audit_dichotomy_source.py`. The selected roots contain the audit report and two JSON outputs, but not the source document or script. The audit cannot be rerun from this repository alone. [Related archive input: A0036](artifacts/A0036/card.md).

## M0006 — Incomplete internal manifest

Related artifact: [A0003 — Tetrad-classification computational package](artifacts/A0003/card.md). Status: `incomplete_by_internal_manifest`.

The ZIP's `data/manifest.json` declares four SHA-256 values. The content for `data/classification.md` and `data/tables.md` occurs under different filenames inside the archive. These two declared files were not found by path or hash:

- `data/catalog.json`
- `data/tetrachotomies-source-text.md`

The separate `CHECKSUMS.json` matches all 62 files it lists; that does not resolve this internal-manifest gap.

## M0007 — Incomplete internal manifests

Related artifact: [A0006 — Repaired Tencer–Minaev audit package](artifacts/A0006/card.md). Status: `incomplete_by_internal_manifest`.

The package manifest declares 24 entries: 19 exact path/size/hash matches, one content match under a different name, and four missing contents. The source manifest declares 9 entries: 6 exact matches, one alternate-path content match, and two missing contents.

The missing package members are:

- `sources/.codex-upload-6e1a86afa65a4cfabfbb397c01c0efd1` (declared as zero bytes, but the path is absent)
- `sources/.codex-upload-6f77ab2b01c24b2dbf05a07e99139d62`
- `statistics.json`
- `verify_report.py`

The bytes declared for `sources/.codex-upload-6a83d91047714bdba4669fd6bda48e71` match a different archive member, `sources/.codex-upload-01e6b54f44f84d1e9359afde19d38159`.
