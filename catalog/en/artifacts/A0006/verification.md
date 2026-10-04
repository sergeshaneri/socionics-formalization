# Checks for A0006

Reading level: `package_readme_and_manifest_overview`.

- The ZIP opened; CRC passed; no unsafe paths were found. Its 20 files match the extracted tree by path and SHA-256, but this does not confirm package completeness. Package manifest: exact matches 19/24, one content item found under a different name, four declared contents missing, and no SHA-256 mismatches. Source manifest: exact matches 6/9, one content item found under a different name, and two contents missing. The code was not run.

## Archive `agent-researches/2026-09-07-tencer-minaev-audit-FIXED.zip`

- Open: `True`; CRC: `passed`.
- File entries: 20; uncompressed size: 13048789 bytes.
- Unsafe paths/links: 0.
- Internal manifest `tencer-minaev-audit/package-manifest.json`: `incomplete_or_mismatch`; exact matches 19/24, contents under another path 1, missing files 4, mismatches 0.
  The contents for `sources/.codex-upload-6a83d91047714bdba4669fd6bda48e71` were found as `tencer-minaev-audit/sources/.codex-upload-01e6b54f44f84d1e9359afde19d38159`.
  Missing entries: `sources/.codex-upload-6e1a86afa65a4cfabfbb397c01c0efd1`, `sources/.codex-upload-6f77ab2b01c24b2dbf05a07e99139d62`, `statistics.json`, `verify_report.py`.
- Internal manifest `tencer-minaev-audit/source-manifest.json`: `incomplete_or_mismatch`; exact matches 6/9, contents under another path 1, missing files 2, mismatches 0.
  The contents for `sources/.codex-upload-6a83d91047714bdba4669fd6bda48e71` were found as `tencer-minaev-audit/sources/.codex-upload-01e6b54f44f84d1e9359afde19d38159`.
  Missing entries: `sources/.codex-upload-6e1a86afa65a4cfabfbb397c01c0efd1`, `sources/.codex-upload-6f77ab2b01c24b2dbf05a07e99139d62`.

No independent mathematical audit or rerun of the computational code was performed as part of cataloging.
