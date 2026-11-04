#!/usr/bin/env python3
"""Build a local roadmap/technology library split and traceable name inventory.

This is a source inventory, not a technology classification or tutorial generator.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "references/raw/roadmap-ai"
AUTHORED = ROOT / "local_data/roadmap_authored_v0.5"
DEFAULT_OUTPUT = ROOT / "local_data/knowledge_libraries_v0.6"

ARTICLE_SPLIT = [
    {
        "source": "content/backend/01_后端职责与学习主线.md",
        "destination": "roadmaps/content/backend/01_后端职责与学习主线.md",
        "library": "roadmaps",
        "route": "backend",
        "node_ids": [],
        "source_question_ids": ["68b5d09854c30c6777941f40", "68b5d09854c30c6777941f41"],
        "mapping_note": "该文为作者整理的路线参考，所据roadmap原始问题记录以question id对应，不伪装成图节点。",
    },
    {
        "source": "content/backend/02_HTTP与接口通信.md",
        "destination": "technical/content/http/02_HTTP与接口通信.md",
        "library": "technical",
        "route": "backend",
        "node_ids": ["R12sArWVpbIs_PHxBqVaR"],
        "source_question_ids": [],
        "mapping_note": "HTTP主题与raw节点ID直接匹配，且该ID在content/backend.json存在对应title/desc。",
    },
    {
        "source": "content/backend/03_版本控制与最小协作.md",
        "destination": "technical/content/git/03_版本控制与最小协作.md",
        "library": "technical",
        "route": "backend",
        "node_ids": ["_I1E__wCIVrhjMk6IMieE"],
        "source_question_ids": [],
        "mapping_note": "Git主题与raw节点ID直接匹配，且该ID在content/backend.json存在对应title/desc。",
    },
]
PREVIOUS_REVIEW_SPLIT = [
    ("review/backend_batch1_sources.json", "review/backend_batch1_sources_previous.json"),
    ("review/backend_batch1_checks.json", "review/backend_batch1_checks_previous.json"),
]
# Explicit, batch-reviewed Python technical tutorial extension; not part of the v0.6 baseline snapshot.
BATCH_REVIEWED_EXTENSION = {
    "technical/content/python/01_数据与函数基础.md",
    "technical/content/python/02_文件JSON与异常处理.md",
    "technical/content/python/03_环境依赖与测试入门.md",
    "review/batches/python_sources.json",
    "review/batches/python_checks.json",
}
KNOWN_SOURCE_CONFLICTS = [
    {
        "name": "Box",
        "status": "source_conflict_for_manual_review; raw sources unchanged; no tutorial written",
        "candidates": [
            {"route": "android", "node_id": "Dp2DOX10u2xJUjB8Okhzh", "raw_node_label": "Box", "direct_content_title": "Box Layout", "raw_description_summary": "Describes a one-direction vertical or horizontal arrangement."},
            {"route": "cyber-security", "node_id": "4Man3Bd-ySLFlAdxbLOHw", "raw_node_label": "Box", "direct_content_title": "Box", "raw_description_summary": "Describes Box cloud storage service."},
        ],
        "comparison_source": {"title": "Android Developers: Compose layout basics", "url": "https://developer.android.com/develop/ui/compose/layouts/basics?hl=zh-cn", "summary": "The parent agent reports reading this official page: Box stacks children; Row arranges horizontally; Column arranges vertically."},
        "review_provenance": "Parent-agent source review; this inventory script does not fetch or modify this external page.",
        "action": "Keep the same-name candidates separate; do not rewrite raw roadmap data or merge them as one technology.",
    }
]

FIELD_PATHS = (
    ("data.label", lambda n: (n.get("data") or {}).get("label")),
    ("data.title", lambda n: (n.get("data") or {}).get("title")),
    ("data.text", lambda n: (n.get("data") or {}).get("text")),
    ("label", lambda n: n.get("label")),
    ("title", lambda n: n.get("title")),
    ("text", lambda n: n.get("text")),
)

NODE_KINDS = {
    "topic": "topic_candidate",
    "subtopic": "subtopic_candidate",
    "title": "route_heading",
    "paragraph": "paragraph_text",
    "label": "diagram_label",
    "button": "button_or_navigation",
    "resourceButton": "resource_button",
    "linksgroup": "resource_group",
    "todo": "todo_text",
    "checklist": "checklist_text",
    "legend": "legend_text",
    "section": "section_or_group_label",
    "vertical": "pure_layout_marker",
    "horizontal": "pure_layout_marker",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def json_bytes(obj: Any) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=False) + "\n").encode("utf-8")


def normalize_name(name: str) -> str:
    # Preserve punctuation (e.g. C++, C#, .NET); normalize only edge/duplicate whitespace and case.
    return re.sub(r"\s+", " ", name.strip()).casefold()


def route_url(route: str) -> str:
    return f"https://roadmap.sh/{route}"


def route_json_url(route: str) -> str:
    return f"https://roadmap.sh/{route}.json"


def load_source() -> dict[str, Any]:
    index_path = RAW / "index.json"
    index = read_json(index_path)
    if not isinstance(index, dict) or not isinstance(index.get("roadmaps"), list):
        raise ValueError("index.json schema mismatch: expected object with roadmaps list")
    routes = index["roadmaps"]
    slugs = [r.get("slug") for r in routes]
    if len(routes) != 101 or len(set(slugs)) != len(slugs) or any(not x for x in slugs):
        raise ValueError(f"unexpected route index: count={len(routes)}, unique={len(set(slugs))}")

    route_rows = []
    input_paths = [index_path]
    node_id_occurrences: dict[str, list[tuple[str, int]]] = defaultdict(list)
    raw_node_count = 0
    raw_edge_count = 0
    per_route: dict[str, Any] = {}
    for entry in routes:
        slug = entry["slug"]
        json_path = RAW / "json" / f"{slug}.json"
        content_path = RAW / "content" / f"{slug}.json"
        if not json_path.is_file():
            raise ValueError(f"indexed route JSON missing: {json_path}")
        raw = read_json(json_path)
        if not isinstance(raw, dict) or not isinstance(raw.get("nodes"), list) or not isinstance(raw.get("edges"), list):
            raise ValueError(f"route JSON schema mismatch for {slug}")
        contents = read_json(content_path) if content_path.is_file() else {}
        if not isinstance(contents, dict):
            raise ValueError(f"content schema mismatch for {slug}")
        input_paths.append(json_path)
        if content_path.is_file():
            input_paths.append(content_path)

        route_node_ids = set()
        for i, node in enumerate(raw["nodes"]):
            if not isinstance(node, dict) or not isinstance(node.get("id"), str) or not node["id"]:
                raise ValueError(f"missing/invalid node id: {slug} node index {i}")
            nid = node["id"]
            if nid in route_node_ids:
                raise ValueError(f"duplicate node id in route: {slug}/{nid}")
            route_node_ids.add(nid)
            node_id_occurrences[nid].append((slug, i))
        raw_node_count += len(raw["nodes"])
        raw_edge_count += len(raw["edges"])
        direct_ids = route_node_ids & set(contents)
        orphan_ids = sorted(set(contents) - route_node_ids)
        missing_ids = sorted(route_node_ids - set(contents))
        per_route[slug] = {
            "route_title": entry.get("title", raw.get("title", slug)),
            "route_url": entry.get("url") or route_url(slug),
            "route_json_url": route_json_url(slug),
            "index_type": entry.get("type"),
            "raw_node_count": len(raw["nodes"]),
            "raw_edge_count": len(raw["edges"]),
            "content_entry_count": len(contents),
            "direct_content_id_count": len(direct_ids),
            "orphan_content_id_count": len(orphan_ids),
            "node_ids_without_content_count": len(missing_ids),
            "nodes": raw["nodes"],
            "contents": contents,
            "orphan_content_ids": orphan_ids,
            "node_ids_without_content": missing_ids,
            "raw": raw,
        }
        route_rows.append({"slug": slug, "title": per_route[slug]["route_title"], "type": entry.get("type"), "url": per_route[slug]["route_url"]})

    # Include the fetch report as provenance/hash input, but exclude it from the 101 route inventory.
    report = RAW / "json" / "_fetch_report.json"
    if report.is_file():
        input_paths.append(report)
    return {
        "index": index,
        "routes": route_rows,
        "per_route": per_route,
        "node_id_occurrences": node_id_occurrences,
        "raw_node_count": raw_node_count,
        "raw_edge_count": raw_edge_count,
        "input_paths": input_paths,
    }


def node_source_fields(slug: str, route_data: dict[str, Any], node: dict[str, Any], index: int) -> list[dict[str, Any]]:
    out = []
    nid = node["id"]
    node_type = node.get("type", "unknown")
    attached = route_data["contents"].get(nid)
    data = node.get("data") if isinstance(node.get("data"), dict) else {}
    for field, getter in FIELD_PATHS:
        value = getter(node)
        if isinstance(value, str) and value.strip():
            out.append({
                "candidate_id": f"{slug}::{nid}::{field}",
                "route": slug,
                "route_title": route_data["route_title"],
                "node_id": nid,
                "node_type": node_type,
                "candidate_kind": NODE_KINDS.get(node_type, "other_node_text"),
                "field": field,
                "original_name": value,
                "normalized_name": normalize_name(value),
                "route_url": route_data["route_url"],
                "raw_json_url": route_data["route_json_url"],
                "node_href": data.get("href") if isinstance(data.get("href"), str) else node.get("href"),
                "content_direct_by_node_id": attached is not None,
                "content_id": nid if attached is not None else None,
                "content_title": attached.get("title") if isinstance(attached, dict) else None,
                "has_attached_description": bool(attached.get("desc", "").strip()) if isinstance(attached, dict) and isinstance(attached.get("desc", ""), str) else False,
                "has_node_description": bool(data.get("desc", "").strip()) if isinstance(data.get("desc", ""), str) else False,
                "classification_status": "not_checked",
            })
    if isinstance(attached, dict) and isinstance(attached.get("title"), str) and attached["title"].strip():
        value = attached["title"]
        out.append({
            "candidate_id": f"{slug}::{nid}::content.title",
            "route": slug,
            "route_title": route_data["route_title"],
            "node_id": nid,
            "node_type": node_type,
            "candidate_kind": "attached_content_title",
            "field": "content.title (direct node-id join)",
            "original_name": value,
            "normalized_name": normalize_name(value),
            "route_url": route_data["route_url"],
            "raw_json_url": route_data["route_json_url"],
            "node_href": data.get("href") if isinstance(data.get("href"), str) else node.get("href"),
            "content_direct_by_node_id": True,
            "content_id": nid,
            "content_title": value,
            "has_attached_description": bool(attached.get("desc", "").strip()) if isinstance(attached.get("desc", ""), str) else False,
            "has_node_description": bool(data.get("desc", "").strip()) if isinstance(data.get("desc", ""), str) else False,
            "classification_status": "not_checked",
        })
    return out


def make_inventory(src: dict[str, Any]) -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []
    type_node_counts = Counter()
    kind_counts = Counter()
    route_type_counts: dict[str, Counter] = defaultdict(Counter)
    route_kind_counts: dict[str, Counter] = defaultdict(Counter)
    unnamed_described = []
    all_content_id_count = 0
    direct_content_id_count = 0
    orphan_content_ids: list[dict[str, Any]] = []
    per_route_summaries = {}
    article_id_validation = []

    for route in src["routes"]:
        slug = route["slug"]
        rd = src["per_route"][slug]
        all_content_id_count += rd["content_entry_count"]
        direct_content_id_count += rd["direct_content_id_count"]
        for nid in rd["orphan_content_ids"]:
            orphan_content_ids.append({"route": slug, "content_id": nid, "reason": "content id does not directly match a raw route node; no title fallback used"})
        nodes = rd["nodes"]
        type_node_counts.update(str(n.get("type", "unknown")) for n in nodes)
        route_type_counts[slug].update(str(n.get("type", "unknown")) for n in nodes)
        for i, node in enumerate(nodes):
            rows = node_source_fields(slug, rd, node, i)
            candidates.extend(rows)
            if rows:
                kind_counts.update(r["candidate_kind"] for r in rows)
                route_kind_counts[slug].update(r["candidate_kind"] for r in rows)
            else:
                nid = node["id"]
                content = rd["contents"].get(nid)
                data = node.get("data") if isinstance(node.get("data"), dict) else {}
                has_desc = (isinstance(content, dict) and isinstance(content.get("desc"), str) and bool(content["desc"].strip())) or (isinstance(data.get("desc"), str) and bool(data["desc"].strip()))
                if has_desc:
                    unnamed_described.append({"route": slug, "route_title": rd["route_title"], "node_id": nid, "node_type": node.get("type"), "route_url": rd["route_url"], "content_direct_by_node_id": content is not None, "reason": "non-empty description but no non-empty label/title/text candidate field"})
        per_route_summaries[slug] = {
            "route_title": rd["route_title"],
            "route_url": rd["route_url"],
            "raw_node_count": rd["raw_node_count"],
            "raw_edge_count": rd["raw_edge_count"],
            "node_type_counts": dict(sorted(route_type_counts[slug].items())),
            "candidate_kind_counts": dict(sorted(route_kind_counts[slug].items())),
            "content_entry_count": rd["content_entry_count"],
            "direct_content_id_count": rd["direct_content_id_count"],
            "orphan_content_id_count": rd["orphan_content_id_count"],
            "node_ids_without_content_count": rd["node_ids_without_content_count"],
        }

    candidates.sort(key=lambda c: (c["route"], c["node_id"], c["field"], c["candidate_id"]))
    by_name: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in candidates:
        by_name[row["normalized_name"]].append(row)

    groups = []
    ambiguities = []
    for norm in sorted(by_name):
        rows = by_name[norm]
        routes = sorted({r["route"] for r in rows})
        node_keys = sorted({(r["route"], r["node_id"]) for r in rows})
        content_titles = sorted({r["content_title"] for r in rows if isinstance(r.get("content_title"), str) and r["content_title"].strip()})
        label_names = {normalize_name(r["original_name"]) for r in rows if r["field"] != "content.title (direct node-id join)"}
        title_names = {normalize_name(r["content_title"]) for r in rows if isinstance(r.get("content_title"), str) and r["content_title"].strip()}
        group = {
            "normalized_name": norm,
            "display_names": sorted({r["original_name"] for r in rows}, key=lambda s: (s.casefold(), s)),
            "candidate_count": len(rows),
            "distinct_route_count": len(routes),
            "routes": routes,
            "distinct_node_count": len(node_keys),
            "content_title_variants": content_titles,
            "candidate_ids": [r["candidate_id"] for r in rows],
            "classification_status": "not_checked; names are not merged into canonical entities",
        }
        groups.append(group)
        reasons = []
        if len(node_keys) > 1:
            reasons.append("same_normalized_name_on_multiple_nodes; context review needed")
        if len(routes) > 1:
            reasons.append("same_normalized_name_across_routes; context review needed")
        if label_names and title_names and label_names != title_names:
            reasons.append("raw_node_name_and_direct_content_title_differ")
        if len(content_titles) > 1:
            reasons.append("different_direct_content_titles_in_same_name_group")
        if reasons:
            ambiguities.append({**group, "review_reasons": reasons, "status": "manual_review_needed; do not auto-merge"})

    # Validate article mappings strictly by route node ID and its directly joined content title/description.
    for spec in ARTICLE_SPLIT:
        rd = src["per_route"][spec["route"]]
        for nid in spec["node_ids"]:
            node = next((n for n in rd["nodes"] if n.get("id") == nid), None)
            direct = rd["contents"].get(nid)
            if node is None or not isinstance(direct, dict):
                raise ValueError(f"article mapping does not have direct raw node/content id join: {spec['destination']} -> {nid}")
            node_label = ((node.get("data") or {}).get("label")) if isinstance(node.get("data"), dict) else None
            article_id_validation.append({"destination": spec["destination"], "route": spec["route"], "node_id": nid, "node_type": node.get("type"), "raw_node_label": node_label, "direct_content_title": direct.get("title"), "has_direct_description": bool(direct.get("desc")), "verified_by": "raw node id and content map key equality"})

    return {
        "candidates": candidates,
        "groups": groups,
        "ambiguities": ambiguities,
        "unnamed_described_nodes": unnamed_described,
        "orphan_content_ids": orphan_content_ids,
        "type_node_counts": dict(sorted(type_node_counts.items())),
        "kind_counts": dict(sorted(kind_counts.items())),
        "per_route_summaries": per_route_summaries,
        "content_entry_count": all_content_id_count,
        "direct_content_id_count": direct_content_id_count,
        "article_id_validation": article_id_validation,
    }


def jsonl_bytes(rows: list[dict[str, Any]]) -> bytes:
    return b"".join((json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8") for row in rows)


def make_catalog(src: dict[str, Any], inv: dict[str, Any]) -> str:
    lines = [
        "# roadmap 技术与主题候选清单",
        "",
        "本清单只提取原始 roadmap 图节点的 label/title/text 字段，以及按同路线 node ID 直接关联的 content.title。它是名称出处索引，不是教程，也未将候选审核为技术、产品、概念、动作或职业方向。不得将相同名称行自动合并为同一技术实体。描述正文和问答中提到的术语尚未逐文抽取，因此不代表全部技术提及已穷尽。",
        "",
        "候选分类是按原始节点类型区分来源形态，不是技术分类：topic/subtopic、导航、资源按钮/组、段落、布局等分开显示。名称按首尾去空白、合并内部空白、casefold形成检索组；标点保留，所以 C++、C#、.NET 等不会因符号被抹掉而自动归并。",
        "",
        f"路线数：{len(src['routes'])}；raw节点数：{src['raw_node_count']}；raw边数：{src['raw_edge_count']}；名称候选条目：{len(inv['candidates'])}；规范化名称组：{len(inv['groups'])}；待人工审阅歧义组：{len(inv['ambiguities'])}。",
        "",
        "## 候选名称（按来源形态）",
        "",
    ]
    by_kind: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in inv["candidates"]:
        by_kind[row["candidate_kind"]].append(row)
    for kind in sorted(by_kind):
        lines.extend([f"### {kind}（{len(by_kind[kind])}）", ""])
        for row in by_kind[kind]:
            name = row["original_name"].replace("\n", " ").replace("\r", " ")
            content = row.get("content_title")
            attachment = f"；直连content.title={content}" if content else "；无同ID content.title"
            lines.append(f"- {name}｜route={row['route']}｜node_id={row['node_id']}｜type={row['node_type']}｜field={row['field']}{attachment}｜{row['route_url']}")
        lines.append("")
    lines.extend([
        "## 需要人工审阅",
        "",
        f"完整同名候选与审阅原因见 `review/ambiguous_names.json`（{len(inv['ambiguities'])} 组）。同名只表示名称归一后相同，保留所有 route/node 上下文；不表示是同一个技术。简称和别名未自动推断。无名称但有描述的节点清单见 `review/ambiguous_names.json` 的 `unnamed_described_nodes`。",
        "",
        "完整逐字段候选见 `review/raw_candidates.jsonl`，每个归一名称的完整出处组见 `review/name_groups.jsonl`。路线覆盖、节点类型计数、直接ID关联与明确缺口见 `review/coverage.json`。",
        "",
    ])
    return "\n".join(lines)


def build_expected() -> tuple[dict[str, bytes], dict[str, Any]]:
    src = load_source()
    inv = make_inventory(src)
    out: dict[str, bytes] = {}

    # Copy the three existing authored articles byte-for-byte; don't overwrite or move the originals.
    for spec in ARTICLE_SPLIT:
        source = AUTHORED / spec["source"]
        if not source.is_file():
            raise ValueError(f"previously reviewed article missing: {source}")
        out[spec["destination"]] = source.read_bytes()
    for old_rel, new_rel in PREVIOUS_REVIEW_SPLIT:
        source = AUTHORED / old_rel
        if not source.is_file():
            raise ValueError(f"previous review artifact missing: {source}")
        # Copy unchanged and name it explicitly as historical, not a new inventory review.
        out[new_rel] = source.read_bytes()

    out["review/raw_candidates.jsonl"] = jsonl_bytes(inv["candidates"])
    out["review/name_groups.jsonl"] = jsonl_bytes(inv["groups"])
    ambiguous_obj = {
        "status": "candidate name groups require manual review; no canonical merging performed",
        "group_count": len(inv["ambiguities"]),
        "groups": inv["ambiguities"],
        "unnamed_described_nodes": inv["unnamed_described_nodes"],
        "abbreviation_detection": "not performed; possible abbreviations/aliases need human review and are not inferred from names",
    }
    out["review/ambiguous_names.json"] = json_bytes(ambiguous_obj)

    article_mappings = []
    for spec in ARTICLE_SPLIT:
        article_mappings.append({
            "source_article": spec["source"],
            "destination": spec["destination"],
            "library": spec["library"],
            "route": spec["route"],
            "raw_node_ids": spec["node_ids"],
            "source_question_ids": spec["source_question_ids"],
            "note": spec["mapping_note"],
        })
    coverage = {
        "snapshot_generated_at": src["index"].get("generated_at"),
        "index_route_count": len(src["routes"]),
        "raw_route_count": len(src["per_route"]),
        "raw_node_count": src["raw_node_count"],
        "raw_edge_count": src["raw_edge_count"],
        "cross_route_reused_node_id_count": sum(1 for v in src["node_id_occurrences"].values() if len({r for r, _ in v}) > 1),
        "cross_route_reused_node_ids": {nid: [{"route": route, "node_index": i} for route, i in occurrences] for nid, occurrences in sorted(src["node_id_occurrences"].items()) if len({r for r, _ in occurrences}) > 1},
        "content_entry_count": inv["content_entry_count"],
        "direct_content_id_count": inv["direct_content_id_count"],
        "orphan_content_id_count": len(inv["orphan_content_ids"]),
        "orphan_content_ids": inv["orphan_content_ids"],
        "node_ids_without_content_count": sum(v["node_ids_without_content_count"] for v in inv["per_route_summaries"].values()),
        "unnamed_but_described_node_count": len(inv["unnamed_described_nodes"]),
        "candidate_field_policy": ["node.data.label", "node.data.title", "node.data.text", "node.label", "node.title", "node.text", "content.title only when content key equals raw node id"],
        "description_and_question_term_extraction": "not_checked; no regex or guessed extraction; roadmap descriptions, questions, FAQ and other prose may contain additional technical names",
        "classification_status": "not_checked; candidate kind denotes source-node form only, not a reviewed technology/product/concept/action/direction classification",
        "node_type_counts": inv["type_node_counts"],
        "topic_subtopic_raw_node_count": inv["type_node_counts"].get("topic", 0) + inv["type_node_counts"].get("subtopic", 0),
        "topic_subtopic_candidate_row_count": inv["kind_counts"].get("topic_candidate", 0) + inv["kind_counts"].get("subtopic_candidate", 0),
        "navigation_resource_prose_layout_and_other_candidate_counts": {k: v for k, v in sorted(inv["kind_counts"].items()) if k not in {"topic_candidate", "subtopic_candidate", "attached_content_title"}},
        "candidate_kind_counts": inv["kind_counts"],
        "routes": inv["per_route_summaries"],
        "authored_article_mapping": article_mappings,
        "verified_direct_article_node_mappings": inv["article_id_validation"],
        "known_source_conflicts_for_manual_review": KNOWN_SOURCE_CONFLICTS,
        "library_split": {"snapshot_scope": "initial_split", "roadmaps": {"article_count": 1, "articles": [ARTICLE_SPLIT[0]["destination"]]}, "technical": {"article_count": 2, "articles": [ARTICLE_SPLIT[1]["destination"], ARTICLE_SPLIT[2]["destination"]]}},
        "scope_notes": ["This is a local separation only; it does not represent two cloud knowledge bases.", "The inventory preserves same-name candidates and context. It does not canonicalize or merge them.", "Raw graph field extraction is not a complete extraction of terms mentioned in prose descriptions or FAQ answers."],
    }
    out["review/coverage.json"] = json_bytes(coverage)
    out["review/source_conflicts.json"] = json_bytes({
        "status": "manual source conflict; raw inputs unchanged; no new tutorial authored",
        "conflicts": KNOWN_SOURCE_CONFLICTS,
    })

    readme = """# 本地知识库分离与候选清单 v0.6

初次分离快照中，roadmaps 有 1 篇后端路线参考正文，technical 有 2 篇技术正文（HTTP、Git）。后续教程见 `technical/content/` 下的技术目录及 `review/batches/` 对应审核记录；当前实际篇数以现有目录与批次记录为准。这是本地目录分离，不代表云端两个知识库，也未上传、解析或检索验证。

`TECHNOLOGY_CATALOG.md` 与 `review/` 是原始 roadmap 名称候选索引及审核材料，不是新教程，不上传。候选按节点来源形态区分，不代表已经分类为技术、产品、概念或动作。名称组仅供同名复核，不自动合并。描述和问答正文里的技术提及尚未逐文抽取，因此不声称覆盖全部提及。

已完成正文的来源核验和检查记录以 `review/backend_batch1_sources_previous.json`、`review/backend_batch1_checks_previous.json` 原字节保留；文件名标注 previous，属于原批次审核，不代表本清单已做内容分类审核。HTTP与Git正文映射到backend路线实际节点ID，并以同route、同node ID的content条目直接校验；路线正文按原始question记录ID注明。

完整候选逐条见 `review/raw_candidates.jsonl`；同名候选分组见 `review/name_groups.jsonl`；需要人工判别的重复名称及无名称但有描述节点见 `review/ambiguous_names.json`；来源计数、ID对账、范围缺口和文件映射见 `review/coverage.json`。
"""
    out["README.md"] = readme.encode("utf-8")
    out["TECHNOLOGY_CATALOG.md"] = make_catalog(src, inv).encode("utf-8")

    input_hashes = {}
    for path in sorted(set(src["input_paths"]) | {AUTHORED / spec["source"] for spec in ARTICLE_SPLIT} | {AUTHORED / old for old, _ in PREVIOUS_REVIEW_SPLIT}):
        input_hashes[str(path.relative_to(ROOT))] = sha256_file(path)
    manifest = {
        "package": "knowledge_libraries_v0.6",
        "snapshot_generated_at": src["index"].get("generated_at"),
        "input_hashes": input_hashes,
        "source_counts": {
            "routes": len(src["routes"]),
            "route_json_files": len(src["routes"]),
            "content_route_files": sum(1 for r in src["routes"] if (RAW / "content" / f"{r['slug']}.json").is_file()),
            "raw_nodes": src["raw_node_count"],
            "raw_edges": src["raw_edge_count"],
            "content_entries": inv["content_entry_count"],
            "direct_content_ids": inv["direct_content_id_count"],
            "candidate_rows": len(inv["candidates"]),
            "normalized_name_groups": len(inv["groups"]),
            "manual_review_name_groups": len(inv["ambiguities"]),
        },
        "outputs_sha256_excluding_manifest": {path: sha256_bytes(data) for path, data in sorted(out.items())},
        "manifest_hash_note": "manifest.json is excluded from outputs_sha256_excluding_manifest to avoid self-reference; --verify checks its parsed fields and all listed file hashes.",
    }
    out["review/manifest.json"] = json_bytes(manifest)
    return out, manifest


def write_output(output: Path) -> None:
    expected, _ = build_expected()
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"refusing to overwrite non-empty output directory: {output}")
    output.mkdir(parents=True, exist_ok=True)
    for rel, data in sorted(expected.items()):
        dest = output / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
    print(f"Generated {len(expected)} files under {output}")
    print((output / "review/manifest.json").read_text(encoding="utf-8"))


def verify_output(output: Path) -> None:
    expected, manifest = build_expected()
    if not output.is_dir():
        raise FileNotFoundError(f"output directory missing: {output}")
    expected_rel = set(expected)
    actual_rel = {str(p.relative_to(output)) for p in output.rglob("*") if p.is_file()}
    missing = expected_rel - actual_rel
    extra = actual_rel - expected_rel
    disallowed_extra = extra - BATCH_REVIEWED_EXTENSION
    if missing or disallowed_extra:
        raise ValueError(f"output file set mismatch: missing={sorted(missing)[:10]}, unapproved_extra={sorted(disallowed_extra)[:10]}")
    for rel, data in expected.items():
        actual = (output / rel).read_bytes()
        if sha256_bytes(actual) != sha256_bytes(data):
            raise ValueError(f"output hash/content mismatch: {rel}")
    stored = read_json(output / "review/manifest.json")
    if stored != manifest:
        raise ValueError("manifest/source hash or output hash mismatch")

    # Explicitly report punctuation normalization behavior and directly joined article node IDs.
    names = {r["original_name"]: r["normalized_name"] for line in (output / "review/raw_candidates.jsonl").read_text(encoding="utf-8").splitlines() for r in [json.loads(line)]}
    for raw in ("C++", "C#"):
        assert normalize_name(raw) == raw.casefold()
        if raw in names:
            assert names[raw] == raw.casefold()
    for spec in ARTICLE_SPLIT[1:]:
        route = spec["route"]
        rd = read_json(RAW / "json" / f"{route}.json")
        c = read_json(RAW / "content" / f"{route}.json")
        for nid in spec["node_ids"]:
            assert any(n.get("id") == nid for n in rd["nodes"]), (route, nid)
            assert nid in c, (route, nid)
    print("VERIFY OK")
    print(f"routes={manifest['source_counts']['routes']} raw_nodes={manifest['source_counts']['raw_nodes']} content_entries={manifest['source_counts']['content_entries']} direct_content_ids={manifest['source_counts']['direct_content_ids']}")
    print(f"candidate_rows={manifest['source_counts']['candidate_rows']} name_groups={manifest['source_counts']['normalized_name_groups']} manual_review_groups={manifest['source_counts']['manual_review_name_groups']}")
    print("direct article node/content ID joins=2; C++/C# punctuation remains distinct when present")
    if extra:
        print("AUTHORIZED EXTENSION (outside initial snapshot; reviewed by dedicated batch):")
        for rel in sorted(extra):
            print(f"  {rel}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="output directory (default: local_data/knowledge_libraries_v0.6)")
    parser.add_argument("--verify", action="store_true", help="read-only compare source hashes, expected outputs, IDs and counts")
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else (ROOT / args.output)
    try:
        if args.verify:
            verify_output(output)
        else:
            write_output(output)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
