#!/usr/bin/env python3
"""Generate the human-facing catalogue and file ledger from registry.json.

Reads original files only; never extracts archives or runs package code.
"""
from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
from pathlib import Path, PurePosixPath
from urllib.parse import quote, unquote, urlsplit
import json
import re
import stat
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "catalog"
REGISTRY_PATH = CATALOG / "registry.json"


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def digest_stream(stream) -> str:
    h = sha256()
    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
        h.update(chunk)
    return h.hexdigest()


def file_digest(path: Path) -> str:
    with path.open("rb") as f:
        return digest_stream(f)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def validate_repo_path(value: str) -> Path:
    p = PurePosixPath(value)
    if p.is_absolute() or ".." in p.parts or (p.parts and ":" in p.parts[0]):
        raise ValueError(f"Unsafe repository-relative path in registry: {value!r}")
    result = ROOT.joinpath(*p.parts)
    if not result.exists():
        raise FileNotFoundError(f"Registry path does not exist: {value}")
    return result


def norm_member(value: str) -> str:
    s = value.replace("\\", "/")
    while s.startswith("./"):
        s = s[2:]
    return PurePosixPath(s).as_posix()


def content_role(path: str) -> str:
    """Assign a descriptive package-member role from its location and suffix."""
    p = PurePosixPath(path.replace("\\", "/"))
    name = p.name.lower()
    parts = {part.lower() for part in p.parts[:-1]}
    suffix = p.suffix.lower()
    if suffix == ".pyc" or "__pycache__" in parts:
        return "technical_cache"
    if name in {"readme.md", "readme.txt"}:
        return "package_readme"
    if "manifest" in name or "checksum" in name or "sha256" in name:
        return "integrity_or_provenance_manifest"
    if name in {"report_template.md", "template.md"} or "report_template" in name:
        return "report_template"
    if parts & {"results", "baseline-results"}:
        return "saved_result"
    if parts & {"code", "src", "scripts"} or suffix in {".py", ".mjs", ".ps1", ".lua"}:
        return "program_source"
    if parts & {"inputs", "input", "project_sources", "originals", "sources", "upload"}:
        return "bundled_source_or_input"
    if suffix == ".pdf":
        return "pdf_document_or_presentation"
    if suffix in {".md", ".tex"}:
        return "research_text_or_documentation"
    if suffix in {".json", ".csv", ".jsonl", ".grp"}:
        return "packaged_data_or_result"
    return "package_member"


def extract_manifest_rows(value):
    """Return (path, sha256, optional_bytes) rows from common manifest shapes."""
    rows = []
    if isinstance(value, list):
        for item in value:
            if not isinstance(item, dict):
                continue
            path = item.get("path") or item.get("archive_path") or item.get("file")
            digest = item.get("sha256") or item.get("SHA256")
            size = item.get("bytes") if item.get("bytes") is not None else item.get("size")
            if path and digest:
                rows.append((str(path), str(digest).lower(), int(size) if size is not None else None))
    elif isinstance(value, dict):
        if isinstance(value.get("files"), dict):
            rows.extend(extract_manifest_rows(value["files"]))
        for key, item in value.items():
            if key == "files":
                continue
            if isinstance(item, str) and re.fullmatch(r"[0-9a-fA-F]{64}", item):
                rows.append((str(key), item.lower(), None))
            elif isinstance(item, dict):
                digest = item.get("sha256") or item.get("SHA256")
                size = item.get("bytes") if item.get("bytes") is not None else item.get("size")
                if digest and re.fullmatch(r"[0-9a-fA-F]{64}", str(digest)):
                    rows.append((str(key), str(digest).lower(), int(size) if size is not None else None))
    # Stable de-duplication for shapes that repeat `files` at multiple levels.
    out = []
    seen = set()
    for row in rows:
        if row not in seen:
            seen.add(row)
            out.append(row)
    return out


def checksum_text_rows(text: str):
    rows = []
    for line in text.splitlines():
        m = re.match(r"\s*([0-9a-fA-F]{64})\s+\*?(.*?)\s*$", line)
        if m and m.group(2):
            rows.append((m.group(2), m.group(1).lower(), None))
    return rows


def archive_audit(path: Path, external_hashes: dict[str, list[str]]) -> dict:
    result = {
        "path": rel(path), "status": "unreadable", "opens": False,
        "crc_test": "not_run", "unsafe_members": [], "member_count": 0,
        "uncompressed_bytes": 0, "members": [], "internal_manifests": [], "error": None,
    }
    try:
        with zipfile.ZipFile(path, "r") as zf:
            result["opens"] = True
            infos = zf.infolist()
            member_hashes = {}
            for info in infos:
                raw_name = info.filename
                q = PurePosixPath(raw_name.replace("\\", "/"))
                mode = (info.external_attr >> 16) & 0o170000
                unsafe = q.is_absolute() or ".." in q.parts or (q.parts and ":" in q.parts[0])
                symlink = info.create_system == 3 and mode == stat.S_IFLNK
                if unsafe or symlink:
                    result["unsafe_members"].append({"name": raw_name, "absolute_or_traversal": bool(unsafe), "symlink": bool(symlink)})
                if info.is_dir():
                    continue
                with zf.open(info, "r") as f:
                    digest = digest_stream(f)
                member_hashes[raw_name] = digest
                result["members"].append({
                    "path": raw_name,
                    "role": content_role(raw_name),
                    "size_bytes": info.file_size,
                    "compressed_bytes": info.compress_size,
                    "sha256": digest,
                    "same_bytes_as": external_hashes.get(digest, []),
                    "safe_path": not (unsafe or symlink),
                })
                result["uncompressed_bytes"] += info.file_size
            result["member_count"] = len(infos)
            bad = zf.testzip()
            result["crc_test"] = "passed" if bad is None else f"failed:{bad}"
            result["status"] = "readable" if not result["unsafe_members"] and bad is None else "integrity_issue"
            result["internal_manifests"] = verify_internal_manifests(zf, infos, member_hashes)
    except Exception as exc:  # exact failure is retained, not replaced with an assumption
        result["error"] = f"{type(exc).__name__}: {exc}"
    return result


def verify_internal_manifests(zf, infos, member_hashes):
    names = {info.filename for info in infos if not info.is_dir()}
    rows_by_name = {info.filename: info for info in infos if not info.is_dir()}
    candidates = []
    for name in sorted(names):
        base = PurePosixPath(name).name.lower()
        if base in {"sha256sums.json", "checksums.json", "sha256sums.txt", "checksums.txt", "package-manifest.json", "manifest.json", "source-manifest.json", "input_sha256.json"}:
            candidates.append(name)
    reports = []
    for manifest_name in candidates:
        report = {
            "path": manifest_name, "declared": 0, "matched": 0,
            "alternate_path_match_count": 0, "alternate_path_matches": [],
            "missing": 0, "missing_paths": [], "path_missing_paths": [],
            "mismatched": 0, "mismatched_paths": [], "status": "unparsed",
        }
        try:
            raw = zf.read(manifest_name)
            if manifest_name.lower().endswith(".txt"):
                rows = checksum_text_rows(raw.decode("utf-8-sig", "replace"))
            else:
                parsed = json.loads(raw.decode("utf-8-sig"))
                rows = extract_manifest_rows(parsed)
            report["declared"] = len(rows)
            if not rows:
                report["status"] = "no_file_hash_rows"
                reports.append(report)
                continue
            parent = PurePosixPath(manifest_name).parent
            for raw_path, expected_hash, expected_size in rows:
                name = norm_member(raw_path)
                candidates_for_row = [name]
                ancestors = list(parent.parents)
                ancestors.reverse()
                ancestors.append(parent)
                for ancestor in ancestors:
                    if ancestor != PurePosixPath("."):
                        candidates_for_row.append(norm_member((ancestor / raw_path).as_posix()))
                resolved = next((candidate for candidate in candidates_for_row if candidate in rows_by_name), None)
                if resolved is None:
                    report["path_missing_paths"].append(raw_path)
                    alternate = [
                        name for name, digest in member_hashes.items()
                        if digest == expected_hash
                        and (expected_size is None or rows_by_name[name].file_size == expected_size)
                    ]
                    if alternate:
                        report["alternate_path_match_count"] += 1
                        report["alternate_path_matches"].append({"declared_path": raw_path, "archive_paths": alternate})
                    else:
                        report["missing"] += 1
                        report["missing_paths"].append(raw_path)
                    continue
                info = rows_by_name[resolved]
                if member_hashes[resolved] != expected_hash or (expected_size is not None and info.file_size != expected_size):
                    report["mismatched"] += 1
                    report["mismatched_paths"].append(raw_path)
                else:
                    report["matched"] += 1
            if report["matched"] == report["declared"]:
                report["status"] = "all_match"
            elif report["matched"] + report["alternate_path_match_count"] == report["declared"] and not report["missing"] and not report["mismatched"]:
                report["status"] = "content_matches_but_paths_differ"
            else:
                report["status"] = "incomplete_or_mismatch"
        except Exception as exc:
            report["status"] = f"unreadable:{type(exc).__name__}"
        reports.append(report)
    return reports


def artifact_file_specs(record):
    specs = []
    for item in record.get("source_files", []):
        specs.append((item["path"], item.get("role", "source_file")))
    for item in record.get("representations", []):
        specs.append((item["path"], "representation"))
    for tree in record.get("trees", []):
        base = validate_repo_path(tree["path"])
        if not base.is_dir():
            raise ValueError(f"Expected a directory for tree path: {tree['path']}")
        for item in sorted(p for p in base.rglob("*") if p.is_file() and p.suffix.lower() != ".pyc" and "__pycache__" not in p.parts):
            member_role = content_role(item.relative_to(base).as_posix())
            specs.append((rel(item), f"{tree.get('role', 'package_member')}:{member_role}"))
    # Merge repeated physical paths but keep all roles explicit.
    merged = {}
    for path, role in specs:
        merged.setdefault(path, [])
        if role not in merged[path]:
            merged[path].append(role)
    return merged


def markdown_link(label: str, repo_path: str, from_dir: Path) -> str:
    target = validate_repo_path(repo_path)
    relpath = Path(__import__("os").path.relpath(target, from_dir)).as_posix()
    return f"[{label}](<{quote(relpath, safe='/.-_')}>)"


def validate_catalog_links():
    """Fail if a generated relative Markdown link has no target in the worktree."""
    pattern = re.compile(r"\]\((?:<([^>]+)>|([^\s)]+)(?:\s+[^)]*)?)\)")
    failures = []
    for document in sorted(CATALOG.rglob("*.md")):
        text = document.read_text(encoding="utf-8")
        for match in pattern.finditer(text):
            target = unquote(match.group(1) or match.group(2))
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            resolved = (document.parent / parsed.path).resolve()
            if not resolved.exists():
                failures.append(f"{rel(document)} -> {target}")
    if failures:
        raise SystemExit("Broken catalogue links:\n" + "\n".join(failures))


def render_card(record: dict, manifest: dict, expected_records=()) -> str:
    artifact_dir = CATALOG / "artifacts" / record["id"]
    paths = [item["path"] for item in record.get("source_files", [])]
    paths.extend(item["path"] for item in record.get("trees", []))
    related = record.get("relations", [])
    lines = [
        "---",
        f"id: {json.dumps(record['id'], ensure_ascii=False)}",
        f"title: {json.dumps(record['title'], ensure_ascii=False)}",
        f"kind: {json.dumps(record['kind'], ensure_ascii=False)}",
        "source_paths:",
    ]
    for path in paths:
        lines.append(f"  - {json.dumps(path, ensure_ascii=False)}")
    representations = record.get("representations", [])
    if representations:
        lines.append("representations:")
        for item in representations:
            lines.append(f"  - path: {json.dumps(item['path'], ensure_ascii=False)}")
            lines.append(f"    basis: {json.dumps(item.get('basis', 'not documented'), ensure_ascii=False)}")
    else:
        lines.append("representations: []")
    lines.extend([
        f"documented_date: {json.dumps(record.get('documented_date', 'не установлено'), ensure_ascii=False)}",
        f"origin: {json.dumps(record.get('origin_note', 'не установлено'), ensure_ascii=False)}",
        'model: "не установлено"',
        'prompt: "не установлено"',
        "topics:",
    ])
    for topic in record.get("topics", []):
        lines.append(f"  - {json.dumps(topic, ensure_ascii=False)}")
    if related:
        lines.append("related_artifacts:")
        for rel_item in related:
            lines.append(f"  - id: {json.dumps(rel_item['id'], ensure_ascii=False)}")
            lines.append(f"    relation: {json.dumps(rel_item['type'], ensure_ascii=False)}")
            lines.append(f"    basis: {json.dumps(rel_item.get('basis', ''), ensure_ascii=False)}")
    else:
        lines.append("related_artifacts: []")
    lines.extend(["---", "", f"# {record['title']}", "", "## Описание", "", record["summary"], "", "## Заявленные результаты", ""])
    for item in record.get("reported_results", []):
        lines.append(f"- {item['text']} **Основание:** {item['basis']}.")
    if not record.get("reported_results"):
        lines.append("В текущем проходе самостоятельный результат не извлечён.")
    lines.extend(["", "## Исходные материалы и чтение", ""])
    inputs = record.get("inputs", [])
    lines.extend(f"- {x}" for x in inputs) if inputs else lines.append("- В карточке не установлены отдельные исходные файлы.")
    lines.extend(["", "**Открыть сначала:**"])
    read_first = record.get("read_first", [])
    for path in read_first:
        label = Path(path).name
        lines.append(f"- {markdown_link(label, path, artifact_dir)}")
    if not read_first:
        lines.append("- Путь к первичному тексту приведён в манифесте.")
    lines.extend(["", f"**Уровень чтения:** `{record.get('reading_level', 'overview')}`.", "", "## Происхождение", "", record.get("origin_note", "Происхождение конкретного артефакта не установлено."), "", "## Статус и проверки", "", f"- Состояние артефакта: `{record.get('artifact_state', 'found_readable')}`.", f"- Состояние вычислительной проверки: `{record.get('verification_state', 'not_run')}`."])
    lines.extend(f"- {note}" for note in record.get("verification_notes", []))
    lines.extend(["", "## Ограничения и неопределённости", ""])
    lines.extend(f"- {item}" for item in record.get("limitations", []))
    if expected_records:
        lines.extend(["", "## Ожидаемые приложения", ""])
        for item in expected_records:
            lines.append(f"- `{item['id']}` — `{item['status']}`; подробности в [реестре ожидаемых приложений](../../expected-artifacts.md).")
    if related:
        lines.extend(["", "## Связи", ""])
        for item in related:
            target = CATALOG / "artifacts" / item["id"] / "card.md"
            relpath = Path(__import__("os").path.relpath(target, artifact_dir)).as_posix()
            lines.append(f"- {item['type']}: [{item['id']}](<{quote(relpath, safe='/.-_')}>). {item.get('basis', '')}")
    lines.extend(["", "---", "", f"[Манифест файлов](manifest.json) · [Журнал проверок](verification.md)"])
    lines.append("")
    return "\n".join(lines)


def render_verification(record: dict, manifest: dict) -> str:
    lines = [f"# Проверки {record['id']}", "", f"Уровень чтения: `{record.get('reading_level', 'overview')}`.", ""]
    lines.extend(f"- {note}" for note in record.get("verification_notes", []))
    for archive in manifest.get("archives", []):
        lines.extend(["", f"## Архив `{archive['path']}`", ""])
        lines.append(f"- Открытие: `{archive['opens']}`; CRC: `{archive['crc_test']}`.")
        lines.append(f"- Файловых записей: {sum(1 for m in archive['members'] if m['safe_path'])}; распакованный объём: {archive['uncompressed_bytes']} байт.")
        lines.append(f"- Небезопасных путей/ссылок: {len(archive['unsafe_members'])}.")
        if archive.get("internal_manifests"):
            for check in archive["internal_manifests"]:
                lines.append(f"- Внутренний манифест `{check['path']}`: `{check['status']}`; точных совпадений {check['matched']}/{check['declared']}, содержимое по другому пути {check.get('alternate_path_match_count', 0)}, отсутствующих файлов {check['missing']}, несовпадений {check['mismatched']}.")
                for alternate in check.get("alternate_path_matches", []):
                    lines.append(f"  Путь `{alternate['declared_path']}`: содержимое найдено как " + ", ".join(f"`{x}`" for x in alternate["archive_paths"]) + ".")
                if check.get("missing_paths"):
                    lines.append("  Отсутствующие записи: " + ", ".join(f"`{x}`" for x in check["missing_paths"]) + ".")
                if check.get("mismatched_paths"):
                    lines.append("  Несовпавшие записи: " + ", ".join(f"`{x}`" for x in check["mismatched_paths"]) + ".")
        else:
            lines.append("- Проверяемый внутренний манифест с контрольными суммами не обнаружен.")
        if archive.get("error"):
            lines.append(f"- Ошибка чтения: `{archive['error']}`.")
    lines.extend(["", "Независимый математический аудит и повторный запуск вычислительного кода в рамках каталогизации не выполнялись.", ""])
    return "\n".join(lines)


def main() -> int:
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    records = registry["artifacts"]
    ids = [r["id"] for r in records]
    if len(ids) != len(set(ids)):
        raise SystemExit("Duplicate artifact IDs")
    id_set = set(ids)
    allowed_relations = {
        "accompanies", "contains_report_copy", "is_representation_of",
        "byte_identical_copy_of", "corrects", "supersedes", "uses",
        "supports", "contradicts", "possibly_related", "possibly_repaired_by",
    }
    for record in records:
        for rel_item in record.get("relations", []):
            if rel_item["id"] not in id_set:
                raise SystemExit(f"Unknown relation target {rel_item['id']} in {record['id']}")
            if rel_item["type"] not in allowed_relations:
                raise SystemExit(f"Unknown relation type {rel_item['type']!r} in {record['id']}")

    expected_records = registry.get("expected_artifacts", [])
    expected_ids = [item["id"] for item in expected_records]
    if len(expected_ids) != len(set(expected_ids)):
        raise SystemExit("Duplicate expected-artifact IDs")
    allowed_expected_statuses = {
        "absent_in_scope", "partial_candidate", "partial_unverified",
        "candidate_not_verified", "inputs_absent_from_scope",
        "incomplete_by_internal_manifest",
    }
    expected_by_owner = defaultdict(list)
    for item in expected_records:
        if item["owner_artifact_id"] not in id_set:
            raise SystemExit(f"Unknown expected-artifact owner {item['owner_artifact_id']} in {item['id']}")
        if item["status"] not in allowed_expected_statuses:
            raise SystemExit(f"Unknown expected-artifact status {item['status']!r} in {item['id']}")
        for candidate_id in item.get("candidate_artifact_ids", []):
            if candidate_id not in id_set:
                raise SystemExit(f"Unknown candidate artifact {candidate_id} in {item['id']}")
        expected_by_owner[item["owner_artifact_id"]].append(item)

    all_paths = []
    for root_name in registry["scope_roots"]:
        base = validate_repo_path(root_name)
        if not base.is_dir():
            raise SystemExit(f"Scope root is not a directory: {root_name}")
        all_paths.extend(rel(p) for p in base.rglob("*") if p.is_file())
    for value in registry.get("administrative_paths", []):
        if validate_repo_path(value).is_file():
            all_paths.append(value)
    all_paths = sorted(set(all_paths))

    # Hash every physical source file once. Duplicates are detected by bytes, not names.
    physical = {path: validate_repo_path(path) for path in all_paths}
    hashes = {path: file_digest(p) for path, p in physical.items()}
    by_hash = defaultdict(list)
    for path, digest in hashes.items():
        by_hash[digest].append(path)
    external_hashes = defaultdict(list)
    for path, digest in hashes.items():
        external_hashes[digest].append(path)

    manifests = {}
    assigned = defaultdict(list)
    for record in records:
        specs = artifact_file_specs(record)
        file_entries = []
        archive_entries = []
        for path, roles in sorted(specs.items()):
            src = validate_repo_path(path)
            if src.is_file():
                file_entries.append({"path": path, "roles": roles, "size_bytes": src.stat().st_size, "sha256": hashes.get(path) or file_digest(src)})
                assigned[path].append(record["id"])
                if src.suffix.lower() == ".zip":
                    archive_entries.append(archive_audit(src, external_hashes))
        manifest = {
            "artifact_id": record["id"],
            "artifact_title": record["title"],
            "generated_by": "catalog/build_catalog.py",
            "files": file_entries,
            "archives": archive_entries,
        }
        manifests[record["id"]] = manifest
        artifact_dir = CATALOG / "artifacts" / record["id"]
        write_text(artifact_dir / "card.md", render_card(record, manifest, expected_by_owner.get(record["id"], [])))
        write_text(artifact_dir / "manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
        write_text(artifact_dir / "verification.md", render_verification(record, manifest))

    source_paths = sorted(p for p in all_paths if p.startswith("sources/"))
    source_ids = {path: f"SRC{i:04d}" for i, path in enumerate(source_paths, 1)}
    inventory = []
    for path in all_paths:
        source = physical[path]
        row = {
            "path": path,
            "size_bytes": source.stat().st_size,
            "sha256": hashes[path],
            "artifact_ids": sorted(assigned.get(path, [])),
            "identical_copy_paths": sorted(x for x in by_hash[hashes[path]] if x != path),
        }
        if path.startswith("sources/"):
            row.update({"record_type": "source", "source_id": source_ids[path], "catalog_status": "source_recorded_separately"})
            if path.startswith("sources/primary/"):
                row["role"] = "author_primary_source; not classified as AI artifact without provenance"
            elif path.startswith("sources/context/"):
                row["role"] = "context_source; item-level provenance not established"
            else:
                row["role"] = "source_file"
        elif path in registry.get("administrative_paths", []):
            row.update({"record_type": "administrative", "catalog_status": "excluded_from_artifacts", "exclusion_reason": "project import-provenance manifest; administrative record, not an AI research artifact"})
        elif source.suffix.lower() == ".pyc":
            row.update({"record_type": "excluded", "catalog_status": "excluded", "exclusion_reason": "compiled Python cache; technical cache, not source or research artifact"})
        elif path == "agent-researches/repair_zip.py":
            row.update({"record_type": "excluded", "catalog_status": "excluded", "exclusion_reason": "small archive-repair utility; operational tool rather than independent research artifact"})
        elif row["artifact_ids"]:
            row.update({"record_type": "artifact_file", "catalog_status": "cataloged"})
        else:
            row.update({"record_type": "unassigned", "catalog_status": "pending_review"})
        inventory.append(row)

    totals = {
        "physical_files": len(inventory),
        "cataloged_source_files": sum(x["catalog_status"] == "cataloged" for x in inventory),
        "source_records": sum(x["record_type"] == "source" for x in inventory),
        "excluded_files": sum(x["record_type"] == "excluded" for x in inventory),
        "administrative_files": sum(x["record_type"] == "administrative" for x in inventory),
        "pending_files": sum(x["catalog_status"] == "pending_review" for x in inventory),
        "artifacts_with_cards": len(records),
        "expected_artifact_records": len(expected_records),
        "promised_packages_absent": sum(item["status"] == "absent_in_scope" for item in expected_records),
        "promised_packages_partial_or_unverified": sum(item["status"] in {"partial_candidate", "partial_unverified", "candidate_not_verified"} for item in expected_records),
        "external_reproduction_input_gaps": sum(item["status"] == "inputs_absent_from_scope" for item in expected_records),
        "incomplete_packages_by_manifest": sum(item["status"] == "incomplete_by_internal_manifest" for item in expected_records),
    }
    ledger = {
        "catalogued_on": "2026-10-02",
        "stage": registry.get("stage", "in_progress"),
        "scope_roots": registry["scope_roots"],
        "administrative_paths": registry.get("administrative_paths", []),
        "scope_note": "Repository-relative inventory; primary author sources are recorded separately. .git, local handoff files, and unrelated active working areas are outside scope.",
        "totals": totals,
        "expected_artifacts": expected_records,
        "files": inventory,
    }
    write_text(CATALOG / "inventory.json", json.dumps(ledger, ensure_ascii=False, indent=2) + "\n")

    # Topic navigation is intentionally preliminary and permits multiple topics per artifact.
    topic_map = {item["id"]: item for item in registry.get("topics", [])}
    cards_by_topic = defaultdict(list)
    for record in records:
        for topic in record.get("topics", []):
            if topic not in topic_map:
                raise SystemExit(f"Unknown topic {topic!r} in {record['id']}")
            cards_by_topic[topic].append(record)
    topic_lines = ["# Тематическая навигация", "", "Классификация предварительная; один артефакт может относиться к нескольким темам.", ""]
    for topic_id, topic in topic_map.items():
        topic_lines.extend([f"## {topic['label']}", "", topic["description"], "", "| ID | Артефакт | Кратко |", "|---|---|---|"])
        for record in cards_by_topic.get(topic_id, []):
            link = f"[карточка](artifacts/{record['id']}/card.md)"
            topic_lines.append(f"| {record['id']} | {link} — {record['title']} | {record['summary']} |")
        topic_lines.append("")
    write_text(CATALOG / "topics.md", "\n".join(topic_lines))

    question_lines = ["# Неоднозначности и вопросы автору", ""]
    questions = registry.get("questions", [])
    if not questions:
        question_lines.append("В текущем этапе открытых вопросов не зарегистрировано.")
    for item in questions:
        refs = ", ".join(f"[{aid}](artifacts/{aid}/card.md)" for aid in item.get("basis", []))
        question_lines.extend([f"## {item['id']}", "", item["text"], "", f"Основание: {refs}.", ""])
    write_text(CATALOG / "questions.md", "\n".join(question_lines))

    record_by_id = {record["id"]: record for record in records}
    expected_kind_labels = {
        "promised_computational_package": "Заявленный вычислительный пакет",
        "external_reproduction_inputs": "Внешние входы для воспроизведения",
        "internal_manifest_members": "Неполный состав по внутреннему манифесту",
    }
    expected_status_labels = {
        "absent_in_scope": "пакет в выбранном охвате не найден",
        "partial_candidate": "кандидат содержит часть заявленных файлов; связь не установлена",
        "partial_unverified": "возможное совпадение; принадлежность не подтверждена",
        "candidate_not_verified": "содержательно близкий пакет не подтверждён как тот же выпуск",
        "inputs_absent_from_scope": "исходные входы или скрипт находятся вне охвата",
        "incomplete_by_internal_manifest": "внутренний манифест указывает на отсутствующие файлы",
    }
    expected_lines = ["# Ожидаемые приложения и пробелы охвата", "", "Записи отделяют обещанные, но отсутствующие файлы от вероятных совпадений и внешних входов. Одинаковое имя не считается доказательством принадлежности пакету.", ""]
    if not expected_records:
        expected_lines.append("В текущем охвате нет зарегистрированных ожиданий отсутствующих приложений.")
    for item in expected_records:
        owner = record_by_id[item["owner_artifact_id"]]
        expected_lines.extend([
            f"## {item['id']} — {expected_kind_labels.get(item['kind'], item['kind'])}", "",
            f"- Связанный артефакт: [{owner['id']} — {owner['title']}](artifacts/{owner['id']}/card.md)",
            f"- Статус: `{item['status']}` — {expected_status_labels.get(item['status'], item['status'])}.",
            f"- Основание: {item['basis']}", "",
            item["notes"], "",
        ])
        for label, key in [("Ожидалось", "expected_members"), ("Наблюдаемые совпадения/кандидаты", "observed_members"), ("Не найдено в подтверждённом составе", "missing_members")]:
            values = item.get(key, [])
            expected_lines.extend([f"### {label}", ""])
            expected_lines.extend(f"- `{value}`" for value in values) if values else expected_lines.append("- Нет зарегистрированных записей.")
            expected_lines.append("")
        candidates = item.get("candidate_artifact_ids", [])
        if candidates:
            refs = ", ".join(f"[{candidate}](artifacts/{candidate}/card.md)" for candidate in candidates)
            expected_lines.extend([f"Кандидаты для ручной сверки: {refs}.", ""])
    write_text(CATALOG / "expected-artifacts.md", "\n".join(expected_lines))

    readme = [
        "# Каталог исследовательских артефактов", "",
        f"Состояние: **{registry.get('stage', 'in_progress')}**. Это рабочий слой для навигации по самостоятельным отчётам, планам, программным пакетам и результатам исследований.", "",
        "## Охват", "",
        *[f"- `{x}/`" for x in registry["scope_roots"]],
        "- `provenance/import-manifest.json` прочитан как административный источник provenance и исключён из числа исследовательских артефактов.",
        "- `sources/primary/` учтён отдельно как авторский источник; он не считается ИИ-артефактом без сведений о происхождении.",
        "- Локальный handoff, `.git`, соседние репозитории и активные разделы формализации вне перечисленных корней не сканировались.", "",
        "## Использование", "",
        "1. Начните с [тематической навигации](topics.md) или [полного реестра](inventory.json).",
        "2. Карточка описывает, что утверждает документ, где читать исходник и что проверял каталогизатор.",
        "3. Для ZIP откройте манифест файлов на карточке пакета: перечислены члены и контрольные суммы; извлечение и запуск кода в первом проходе не выполняются.",
        "4. Сверяйте ограничения в карточке и [открытые вопросы](questions.md). Статус архивной проверки не является математическим аудитом.",
        "5. [Ожидаемые приложения](expected-artifacts.md) показывают отсутствующие пакеты, частичные совпадения и недостающие внешние входы.", "",
        "## Счётчики текущего этапа", "",
        f"- Физических файлов в реестре: {totals['physical_files']}",
        f"- Файлов, связанных с карточками: {totals['cataloged_source_files']}",
        f"- Источников, учитываемых отдельно: {totals['source_records']}",
        f"- Исключено с причиной: {totals['excluded_files'] + totals['administrative_files']}",
        f"- Ожидает классификации: {totals['pending_files']}",
        f"- Карточек артефактов: {totals['artifacts_with_cards']}", "",
        f"- Заявленных отсутствующих/неполных приложений: {totals['expected_artifact_records']}",
        f"- Пакетов не найдено: {totals['promised_packages_absent']}",
        f"- Частичных или неустановленных совпадений пакета: {totals['promised_packages_partial_or_unverified']}",
        f"- Пакетов с пробелами по внутреннему манифесту: {totals['incomplete_packages_by_manifest']}",
        f"- Внешних входов для повторной проверки не хватает: {totals['external_reproduction_input_gaps']}", "",
        "## Следующая очередь", "",
        "1. Получить решения по [Q0001 и Q0002](questions.md): редакции отчёта A0002/A0003 и происхождение исправленного пакета A0005/A0006.",
        "2. Сверить ожидаемые выпуски и кандидатов M0001–M0005 по [реестру приложений](expected-artifacts.md); не приписывать совпадающие имена другому отчёту.",
        "3. Запросить или найти отсутствующие члены по M0006/M0007; исторические ZIP и исходные файлы не изменять.",
        "4. После разрешения пробелов отдельно планировать математический аудит и тематическую кластеризацию; в этот этап они не входили.", "",
        "По сообщению автора, коллекция создавалась в длительной работе с GPT Astra и Sol. Модель, запрос и дата конкретного артефакта указываются только при документированном основании; иначе отмечаются как не установленные.", "",
        "Пересборка реестра и карточек: `python catalog/build_catalog.py`. Скрипт читает исходники и ZIP, но не распаковывает архивы и не запускает содержащийся в них код.", "",
    ]
    write_text(CATALOG / "README.md", "\n".join(readme))
    validate_catalog_links()

    pending = [x["path"] for x in inventory if x["catalog_status"] == "pending_review"]
    print(json.dumps({"stage": ledger["stage"], "totals": totals, "pending_sample": pending[:10]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"catalog build failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise
