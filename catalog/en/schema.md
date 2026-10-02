# Catalog schema

The catalog records research artifacts separately from source files, file representations, package copies, and exclusions. Each artifact receives a stable ID (`A0001`, etc.) independent of topic. Source IDs (`SRC0001`, etc.) use a separate sequence.

## Card: `artifacts/Axxxx/card.md`

The YAML front matter records:

- `id`, `title`, and `kind`;
- `source_paths`, repository-relative paths to source files;
- `representations`, files treated as representations of the same artifact, with the basis stated;
- `documented_date`, a research date explicitly stated in the document or README, or `not established`;
- `origin`, `model`, and `prompt`, at the level of the individual artifact. General attribution of the collection to GPT Astra and Sol does not identify the model used for a particular file;
- `topics` and `related_artifacts`, provisional topics and typed relations with their evidence.

Card text separates the purpose and reported results from cataloger checks. Claims cite the relevant report sections. Reading depth is described as overview, full, or a specific account of the portions examined. Cards do not label an entire report as proven.

## File manifest: `manifest.json`

Each physical file is recorded with a repository-relative path, role, byte size, and SHA-256. ZIP records also include member paths, uncompressed size, per-member hashes, CRC results, path-safety checks, and comparisons with available internal manifests. ZIPs are inspected without extraction. A saved `PASS` report is not a fresh rerun.

A declared size of `0` differs from an unspecified size. If a manifest path is absent but the same SHA-256 and size occur under another path, the record marks a content match under an alternate name. This is neither an exact path match nor missing content.

## Verification: `verification.md`

Only completed actions are recorded: reading depth, accessibility and integrity checks, and actual execution results. Mathematical checking and computational reruns that were not performed are stated as such.

## Inventory: `inventory.json`

The inventory has one record for each physical file in scope. Each file links to an artifact card, is recorded as a source, is assigned a package role, or is explicitly excluded. Exact duplicates are identified by SHA-256, not filenames. ZIP members belong to the package manifest and are not counted as separate working-tree files.

`expected_artifacts` records files or packages explicitly implied by a report but absent or unmatched in the selected scope. These are expectations, not physical files. Each record identifies its owner, evidence, expected and observed members, missing members, and candidate artifacts.

Expectation statuses:

- `absent_in_scope`: no matching package was found in the selected scope;
- `partial_candidate`: a candidate contains only part of the declared package;
- `partial_unverified`: a possible companion output exists, but its relation to the release is unconfirmed;
- `candidate_not_verified`: a related package was found but cannot be identified as the same release;
- `inputs_absent_from_scope`: required source material or a program is outside the selected roots;
- `incomplete_by_internal_manifest`: an archive's manifest declares files that are missing or appear under alternate names; hash matches are reported separately.

## Relations

Allowed relation values are `accompanies`, `contains_report_copy`, `is_representation_of`, `byte_identical_copy_of`, `corrects`, `supersedes`, `uses`, `supports`, `contradicts`, `possibly_related`, and `possibly_repaired_by`. Cards give evidence for substantive and uncertain relations. Texts are not merged automatically when their bytes differ.

## Status values

- Artifact: `found_readable`, `damaged`, or `incomplete`.
- Verification: `not_run`, `integrity_only`, `spot_check`, or `rerun`.
- Claim basis: `definition`, `claimed_proof`, `proof_reviewed`, `finite_computation_claimed`, `finite_computation_rerun`, `hypothesis`, or `interpretation`.

Cataloging is not a mathematical audit of the collection.
