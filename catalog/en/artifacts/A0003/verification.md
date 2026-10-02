# Checks for A0003

Reading level: `overview`.

- The ZIP was opened; it contains 63 entries, CRC passed, and no unsafe paths were found. The top-level CHECKSUMS.json matches 62/62 listed files. In the internal data/manifest.json, exact path matches are 0/4; hashes for two entries were found under different names; two expected contents were not found. The code was not run.

## Archive `agent-researches/2026-09-28-tetrad-classification.zip`

- Open: `True`; CRC: `passed`.
- File entries: 63; uncompressed size: 8346716 bytes.
- Unsafe paths/links: 0.
- Internal manifest `2026-09-28-tetrad-classification/CHECKSUMS.json`: `all_match`; exact matches 62/62, contents under another path 0, missing files 0, mismatches 0.
- Internal manifest `2026-09-28-tetrad-classification/data/manifest.json`: `incomplete_or_mismatch`; exact matches 0/4, contents under another path 2, missing files 2, mismatches 0.
  The contents for `data/classification.md` were found as `2026-09-28-tetrad-classification/data/классификация разбиений и подгрупп.md` and `2026-09-28-tetrad-classification/originals/классификация разбиений и подгрупп.md`.
  The contents for `data/tables.md` were found as `2026-09-28-tetrad-classification/data/09-markdown-1-.md` and `2026-09-28-tetrad-classification/originals/09-markdown-1-.md`.
  Missing entries: `data/catalog.json`, `data/tetrachotomies-source-text.md`.

No independent mathematical audit or rerun of the computational code was performed as part of cataloging.
