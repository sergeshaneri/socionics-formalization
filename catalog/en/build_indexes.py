from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "catalog"
EN = CATALOG / "en"
REGISTRY = json.loads((CATALOG / "registry.json").read_text(encoding="utf-8"))
TOPICS = {
    "model-a-subgroups": ("Model A permutations and subgroups", "Permutation realizations, actions, stabilizers, and orbits."),
    "tetrad-classification": ("Tetrachotomies and tetrad classification", "Finite partitions of types, tetrads, and their invariants."),
    "research-planning": ("Research plans and problem statements", "Plans, task lists, and methodological proposals that do not claim a completed enumeration."),
    "tencer-minaev": ("Tencer–Minaev traits", "Formulas, finite classifications, and related computational packages."),
    "group-cocycles": ("Groups, 2-cocycles, and Model A permutations", "Algebraic laws, permutation representations, and finite-table constructions."),
    "trait-systems": ("Trait systems and waffle partitions", "Comparisons of 16 trait systems, products, pairs, and invariants."),
    "weaving-theory": ("Weaving theory", "Combinatorial cycles on Model A cells, author hypotheses, and computational refinements."),
    "formalization": ("Formalization of finite models", "Explicit definitions, finite proofs, and machine-checkable representations."),
    "source-audits": ("Audits of source formulas and data", "Comparisons with author records, corrections, and provenance of machine tables."),
    "presentation-planning": ("Talks and teaching materials", "Talk plans, transcripts, and research assignments."),
    "dual-tetrads": ("Duality of tetrachotomies", "Annihilators, orthogonal complements, and tetrachotomy orbits."),
}


def card_title_and_summary(path: Path) -> tuple[str, str]:
    text = path.read_text(encoding="utf-8")
    heading = re.search(r"^# (.+?)\s*$", text, re.MULTILINE)
    if not heading:
        raise ValueError(f"English card has no H1 title: {path}")
    title = heading.group(1).strip()
    body = text[heading.end():]
    description = re.search(r"^## Description\s*\n\s*\n(.*?)(?=\n## |\Z)", body, re.MULTILINE | re.DOTALL)
    summary = " ".join(line.strip() for line in description.group(1).splitlines() if line.strip()) if description else ""
    return title, summary


def main() -> None:
    cards = {record["id"]: record for record in REGISTRY["artifacts"]}
    if len(cards) != 52:
        raise SystemExit(f"Expected 52 artifact records, found {len(cards)}")
    card_data = {}
    for artifact_id, record in cards.items():
        card_path = EN / "artifacts" / artifact_id / "card.md"
        if not card_path.is_file():
            raise SystemExit(f"Missing English card: {card_path.relative_to(ROOT)}")
        title, summary = card_title_and_summary(card_path)
        card_data[artifact_id] = (title, summary)

    topic_records = {topic["id"]: topic for topic in REGISTRY["topics"]}
    if set(topic_records) != set(TOPICS):
        raise SystemExit("English topic labels do not match registry topic IDs")
    groups = {topic_id: [] for topic_id in topic_records}
    for artifact_id, record in cards.items():
        for topic_id in record.get("topics", []):
            if topic_id not in groups:
                raise SystemExit(f"Unknown topic {topic_id} in {artifact_id}")
            groups[topic_id].append(artifact_id)

    lines = [
        "# Topic index",
        "",
        "The topic assignment is provisional; an artifact may appear under more than one topic. The linked cards are in English. Source reports and data retain their original language.",
        "",
    ]
    for topic_id, (label, description) in TOPICS.items():
        lines.extend([f"## {label}", "", description, "", "| ID | Artifact | Summary |", "|---|---|---|"])
        for artifact_id in sorted(groups[topic_id]):
            title, summary = card_data[artifact_id]
            link = f"[card](artifacts/{artifact_id}/card.md)"
            lines.append(f"| {artifact_id} | {link} — {title} | {summary} |")
        lines.append("")
    (EN / "topics.md").write_text("\n".join(lines), encoding="utf-8")

    manifest_count = 0
    for artifact_id, (title, _) in card_data.items():
        source = CATALOG / "artifacts" / artifact_id / "manifest.json"
        target = EN / "artifacts" / artifact_id / "manifest.json"
        manifest = json.loads(source.read_text(encoding="utf-8"))
        manifest["artifact_title"] = title
        manifest["generated_by"] = "catalog/en/build_indexes.py; file data copied from catalog/artifacts"
        target.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        manifest_count += 1

    print(json.dumps({"english_cards": len(card_data), "topic_groups": len(groups), "english_manifests": manifest_count}, indent=2))


if __name__ == "__main__":
    main()
