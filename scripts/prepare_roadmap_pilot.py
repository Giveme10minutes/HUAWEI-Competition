#!/usr/bin/env python3
"""准备 roadmap.sh 本地检索资料包（试点：frontend / backend / python）。

输入（只读）：references/raw/roadmap-ai/
  index.json, graph/<slug>.json, json/<slug>.json, content/<slug>.json,
  nodes.jsonl, md/<slug>.md
输出（本地、Git 忽略）：local_data/roadmap_pilot_v0.1/
  nodes.jsonl, relations.jsonl, chunks.jsonl, resources.jsonl,
  review_items.jsonl, manifest.json, qa_report.json, README.md

原则：
  * 不做全站抓取、不补写缺失描述、不调用云端模型或 embedding。
  * 官方边保持原样（端点、样式、来源）；父子关系一律标为结构推导。
  * 描述匹配方式逐节点重新判定（id / title_fallback / ambiguous / missing）。
  * 只有 id 命中且有描述的节点进入 chunks.jsonl。
  * 输出可重复：同样输入产生相同 id、计数与正文（时间字段除外）。

用法：
  python scripts/prepare_roadmap_pilot.py            # 生成资料包
  python scripts/prepare_roadmap_pilot.py --verify    # 生成 + 抽样核对
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "references" / "raw" / "roadmap-ai"
OUT = ROOT / "local_data" / "roadmap_pilot_v0.1"
PACKAGE = "roadmap_pilot_v0.1"
SCRIPT_VERSION = "0.1.0"
SCOPE = ("frontend", "backend", "python")

NODE_TYPES = {"title", "topic", "subtopic", "button", "label", "paragraph", "linksgroup"}
LAYOUT_TYPES = {"vertical", "horizontal", "legend", "section"}

CHROME_PATTERNS = [
    r"find the detailed version",
    r"roadmap\.sh\s*$",
    r"visit .*beginner( friendly)? version",
    r"have a look at the following relevant tracks",
    r"click to visit the roadmap",
    r"roadmap\.sh.*logo",
]
CHROME_RE = re.compile("|".join(CHROME_PATTERNS), re.I)

# 已知错位（来自既有核对结论，不据此重写原始结构，只隔离并标记）
KNOWN_MISPLACEMENTS = [
    ("backend", "Docker",
     "已知错位：Docker 被归到 Message Brokers 下的 Containerization 标题块；官方 JSON 中无对应 topic 节点"),
    ("backend", "Kubernetes",
     "已知错位：Kubernetes 被归到 Message Brokers 下的 Containerization 标题块；官方 JSON 中无对应 topic 节点"),
    ("backend", "System Design",
     "已知错位：System Design 被归入 Architectural Patterns；模块归属未经核实"),
]

MATCH_METHODS = ("id", "title_fallback", "ambiguous", "missing")

# 检索案例：expected/absent 用 (slug, label) 表示，构建时解析成 node_id。
RETRIEVAL_CASES = [
    {
        "case_id": "R01",
        "topic": "前端-具体主题",
        "question": "Vitest 和 Playwright 这两条前端测试工具，路线图里各自是什么定位？",
        "expects": [("frontend", "Vitest"), ("frontend", "Playwright")],
        "absent": [],
        "evidence": "对应节点的官方描述（description）",
        "must_not": "不比较性能或推荐选哪个；不声称二者有先后学习顺序",
        "keywords": ["Vitest", "Playwright"],
    },
    {
        "case_id": "R02",
        "topic": "前端-学习资源查找",
        "question": "前端部署这一块，路线图给了哪些平台资源？",
        "expects": [("frontend", "Deployment"), ("frontend", "Vercel"), ("frontend", "Netlify")],
        "absent": [],
        "evidence": "resources：official/article/video 条目",
        "must_not": "不声称链接已核验可用，不比较平台优劣或免费额度",
        "keywords": ["Vercel", "Netlify", "Deployment"],
    },
    {
        "case_id": "R03",
        "topic": "后端-具体主题",
        "question": "后端路线里的关系型数据库包含哪些具体数据库？",
        "expects": [("backend", "Relational Databases"), ("backend", "MySQL"), ("backend", "PostgreSQL")],
        "absent": [],
        "evidence": "节点描述 + 结构推导（subtopic 归属）",
        "must_not": "不声称这些是必学或存在学习顺序",
        "keywords": ["MySQL", "PostgreSQL", "Relational Databases"],
    },
    {
        "case_id": "R04",
        "topic": "后端-缓存",
        "question": "后端做缓存需要了解哪些内容？",
        "expects": [("backend", "Caching"), ("backend", "Redis"), ("backend", "Memcached")],
        "absent": [],
        "evidence": "Caching 节点描述与子项描述",
        "must_not": "不把 Caching 的子项当成固定先后步骤；不引用推断 path 当事实",
        "keywords": ["Caching", "Redis", "Memcached"],
    },
    {
        "case_id": "R05",
        "topic": "后端-已知错位",
        "question": "Docker 和 Kubernetes 在后端路线里属于哪个部分？",
        "expects": [("backend", "Docker"), ("backend", "Kubernetes")],
        "absent": [],
        "evidence": "节点描述；结构字段被标记为隔离（quarantined）",
        "must_not": "不回答它们属于 Message Brokers 的某个阶段；该层级是错误归组，只能说明“归属待核”",
        "keywords": ["Docker", "Kubernetes"],
    },
    {
        "case_id": "R06",
        "topic": "后端-推断层级误用",
        "question": "System Design 是不是应该先于架构模式学习？",
        "expects": [("backend", "System Design")],
        "absent": [],
        "evidence": "只有节点描述；结构被标记为隔离",
        "must_not": "不给出先后顺序结论；本资料不含 prerequisite 关系",
        "keywords": ["System Design"],
    },
    {
        "case_id": "R07",
        "topic": "Python-具体主题",
        "question": "Python 路线里装饰器和迭代器讲的是什么？",
        "expects": [("python", "Decorators"), ("python", "Iterators")],
        "absent": [],
        "evidence": "两个节点的 description",
        "must_not": "不把二者合并成同一知识点，不补写原文没有的例子",
        "keywords": ["Decorators", "Iterators"],
    },
    {
        "case_id": "R08",
        "topic": "Python-环境与包管理",
        "question": "Python 的虚拟环境和包管理在路线里列了哪些工具？",
        "expects": [("python", "virtualenv"), ("python", "Pipenv"), ("python", "Poetry")],
        "absent": [],
        "evidence": "各工具的 description 与 resources",
        "must_not": "不推荐某一个为默认最佳，不声称已评测",
        "keywords": ["virtualenv", "Pipenv", "Poetry"],
    },
    {
        "case_id": "R09",
        "topic": "跨路线-近似主题",
        "question": "Python 的排序算法和前端性能优化是同一类知识吗？",
        "expects": [("python", "Sorting Algorithms"), ("frontend", "Performance")],
        "absent": [],
        "evidence": "两条路线中不同节点的描述，需分别标注来源路线",
        "must_not": "不把跨路线同名/近似主题合并为一个知识点；不推断二者学习顺序",
        "keywords": ["Sorting Algorithms", "Performance"],
    },
    {
        "case_id": "R10",
        "topic": "缺资料-不支持",
        "question": "AWS 最佳实践路线里 S3 的权限配置该怎么写？",
        "expects": [],
        "absent": [("aws-best-practices", "S3")],
        "evidence": "无：本试点只含 frontend/backend/python，不含该路线与该主题",
        "must_not": "不编造步骤或链接，应说明资料范围不足",
        "keywords": ["S3", "aws-best-practices"],
    },
]


# ------------------------------------------------------------------ helpers
def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def stable_id(*parts: object) -> str:
    raw = "|".join(str(p) for p in parts)
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


def norm(text: str | None) -> str:
    return re.sub(r"[^a-z0-9]+", "", (text or "").lower())


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path: Path, obj: object) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def edge_style(edge: dict) -> str:
    data = edge.get("data") or {}
    if data.get("edgeStyle"):
        return str(data["edgeStyle"])
    dash = str((edge.get("style") or {}).get("strokeDasharray", "0"))
    return "solid" if dash in {"0", "0 0", "none", ""} else "dashed"


# ------------------------------------------------------------------ loading
def load_sources(slug: str) -> dict:
    return {
        "raw": read_json(SRC / "json" / f"{slug}.json"),
        "graph": read_json(SRC / "graph" / f"{slug}.json"),
        "content": read_json(SRC / "content" / f"{slug}.json"),
    }


def ancestor_ids(node_id: str, by_id: dict[str, dict]) -> list[str]:
    chain: list[str] = []
    seen: set[str] = set()
    cur = by_id.get(node_id, {}).get("parent")
    while cur and cur not in seen and cur in by_id:
        seen.add(cur)
        chain.append(cur)
        cur = by_id[cur].get("parent")
    return chain


def path_labels(node_id: str, by_id: dict[str, dict]) -> list[str]:
    out: list[str] = []
    for nid in reversed(ancestor_ids(node_id, by_id)):
        out.append(by_id[nid].get("label") or "")
    out.append(by_id[node_id].get("label") or "")
    return out


def path_rules(node_id: str, by_id: dict[str, dict]) -> list[str]:
    out: list[str] = []
    for nid in reversed(ancestor_ids(node_id, by_id)):
        out.append(by_id[nid].get("parent_rule") or "unknown")
    out.append(by_id[node_id].get("parent_rule") or "unknown")
    return out


# ------------------------------------------------------------------ build
def build_roadmap(slug: str) -> dict:
    src = load_sources(slug)
    raw, graph, content = src["raw"], src["graph"], src["content"]

    nodes = graph["nodes"]
    by_id = {n["id"]: n for n in nodes}
    item_ids = set(by_id)
    raw_by_id = {n.get("id"): n for n in raw.get("nodes", [])}

    # 内容标题索引（用于重新判定匹配方式）
    title_index: dict[str, list[str]] = defaultdict(list)
    for key, entry in content.items():
        t = norm(entry.get("title"))
        if t:
            title_index[t].append(key)
    for key in title_index:
        title_index[key].sort()

    # 内容条目的归属：id 命中优先；标题兜底若撞到已被占用的条目，判定为歧义（不任取）
    id_claims = {nid for nid in by_id if nid in content}
    fallback_candidate: dict[str, str] = {}
    for n in nodes:
        if n["id"] in content:
            continue
        cands = title_index.get(norm(n.get("label")), [])
        if len(cands) == 1:
            fallback_candidate[n["id"]] = cands[0]
    claim_count = Counter(fallback_candidate.values())

    # 已知错位：自节点与全部后代标记隔离
    child_map: dict[str, list[str]] = defaultdict(list)
    for n in nodes:
        if n.get("parent"):
            child_map[n["parent"]].append(n["id"])
    quarantine: dict[str, str] = {}
    for s, label, reason in KNOWN_MISPLACEMENTS:
        if s != slug:
            continue
        for n in nodes:
            if (n.get("label") or "").strip() == label:
                quarantine[n["id"]] = reason
    stack = list(quarantine)
    while stack:
        cur = stack.pop()
        for child in child_map.get(cur, []):
            if child not in quarantine:
                quarantine[child] = quarantine[cur] if cur not in quarantine else quarantine[cur]
                stack.append(child)

    node_rows: list[dict] = []
    review_rows: list[dict] = []
    chunk_rows: list[dict] = []
    resource_rows: list[dict] = []
    match_counts: Counter = Counter()
    desc_counts: Counter = Counter()
    scope_counts: Counter = Counter()

    for n in sorted(nodes, key=lambda x: (x.get("order") if x.get("order") is not None else 0, x["id"])):
        nid = n["id"]
        label = n.get("label") or ""
        entry: dict = {}
        key: str | None = None
        candidates: list[str] = []
        ambiguous_reason: str | None = None
        if nid in content:
            method = "id"
            key = nid
        else:
            cands = title_index.get(norm(label), [])
            if not cands:
                method = "missing"
            elif len(cands) == 1 and cands[0] not in id_claims and claim_count[cands[0]] == 1:
                method = "title_fallback"
                key = cands[0]
            else:
                method = "ambiguous"
                candidates = list(cands)
                ambiguous_reason = ("content_key_owned_by_other_node"
                                    if cands[0] in id_claims or claim_count[cands[0]] > 1
                                    else "multiple_title_candidates")
        if key:
            entry = content.get(key, {})
        desc = (entry.get("desc") or "").strip()
        description_status = ("present" if desc
                              else "unresolved" if method == "ambiguous"
                              else "empty" if key else "unavailable")

        if method == "id" and desc:
            usage = "content_reference"
        elif method == "title_fallback" and desc:
            usage = "pending_review"
        elif method == "ambiguous":
            usage = "excluded"
        else:
            usage = "navigation_only"

        review_status = {
            "id": "unreviewed",
            "title_fallback": "needs_review",
            "ambiguous": "blocked",
            "missing": "not_applicable",
        }[method]

        anc = ancestor_ids(nid, by_id)
        quarantined_self = nid in quarantine
        quarantined_ancestor = any(a in quarantine for a in anc)
        chain_rules = path_rules(nid, by_id)
        chain_has_inferred = any(r in {"block", "caption-group"} for r in chain_rules[:-1])

        node_rows.append({
            "roadmap": slug,
            "roadmap_title": graph.get("title") or slug,
            "roadmap_url": graph.get("url") or f"https://roadmap.sh/{slug}",
            "node_id": nid,
            "label": label,
            "node_type": n.get("type"),
            "legend": n.get("legend"),
            "href": n.get("href"),
            "description": desc,
            "description_status": description_status,
            "content_match_method": method,
            "content_source_ref": f"content/{slug}.json#{key}" if key else None,
            "content_candidates": candidates or None,
            "content_ambiguous_reason": ambiguous_reason,
            "review_status": review_status,
            "usage_scope": usage,
            "inferred_parent_node_id": n.get("parent"),
            "inferred_parent_rule": n.get("parent_rule"),
            "inferred_depth": n.get("depth"),
            "inferred_path": path_labels(nid, by_id),
            "structure_note": "parent/depth/path 由官方画布布局推导，非官方父子事实；仅 official-edge 有官方连线依据",
            "structure_quarantined": quarantined_self,
            "structure_ancestor_quarantined": quarantined_ancestor,
            "structure_quarantine_reason": quarantine.get(nid) if quarantined_self else None,
            "structure_chain_has_inferred_groups": chain_has_inferred,
        })
        match_counts[method] += 1
        desc_counts[description_status] += 1
        scope_counts[usage] += 1

        if method == "ambiguous":
            review_rows.append({
                "review_id": stable_id("review", slug, nid, "ambiguous"),
                "roadmap": slug,
                "node_id": nid,
                "item_type": "content_match_ambiguous",
                "reason": "节点 id 未命中，归一化标题对应多个内容条目，未任取其一",
                "detail": {"label": label, "normalized": norm(label), "candidates": candidates,
                            "reason_code": ambiguous_reason},
                "status": "pending",
            })
        if method == "title_fallback":
            review_rows.append({
                "review_id": stable_id("review", slug, nid, "title_fallback"),
                "roadmap": slug,
                "node_id": nid,
                "item_type": "content_match_title_fallback",
                "reason": "仅按归一化标题唯一匹配，需人工确认后再进入可用检索片段",
                "detail": {"label": label, "content_key": key,
                            "content_title": (content.get(key) or {}).get("title")},
                "status": "pending",
            })
        if quarantined_self:
            review_rows.append({
                "review_id": stable_id("review", slug, nid, "misplacement"),
                "roadmap": slug,
                "node_id": nid,
                "item_type": "known_misplacement",
                "reason": quarantine[nid],
                "detail": {"label": label, "inferred_parent": n.get("parent"),
                            "inferred_parent_rule": n.get("parent_rule"),
                            "inferred_path": path_labels(nid, by_id)},
                "status": "pending",
            })
        elif quarantined_ancestor:
            review_rows.append({
                "review_id": stable_id("review", slug, nid, "ancestor"),
                "roadmap": slug,
                "node_id": nid,
                "item_type": "structure_chain_suspect",
                "reason": "祖先链含已隔离的错位节点，路径不可作为事实使用",
                "detail": {"label": label, "inferred_path": path_labels(nid, by_id)},
                "status": "pending",
            })

        # 资源
        for kind, rtitle, url in (entry.get("links") or []):
            resource_rows.append({
                "resource_id": stable_id("res", slug, nid, kind, rtitle, url),
                "roadmap": slug,
                "node_id": nid,
                "label": label,
                "kind": kind,
                "title": rtitle,
                "url": url,
                "content_match_method": method,
                "review_status": review_status,
                "usage_scope": usage,
                "link_status": "unchecked",
                "authority_note": "来源标为 official 仅表示原内容这样标注，未核验权威性与有效性",
            })

        # 片段：仅 id 命中 + 有描述
        if usage == "content_reference":
            paragraphs = [p.strip() for p in re.split(r"\n\s*\n", desc) if p.strip()]
            for i, para in enumerate(paragraphs):
                chunk_rows.append({
                    "chunk_id": stable_id("chunk", slug, nid, i),
                    "roadmap": slug,
                    "node_id": nid,
                    "label": label,
                    "text": "\n".join([
                        f"路线：{graph.get('title') or slug}（{slug}）",
                        f"知识点：{label}",
                        f"来源：{graph.get('url') or f'https://roadmap.sh/{slug}'}",
                        f"内容来源：content/{slug}.json#{key}",
                        "",
                        para,
                    ]),
                    "source_url": graph.get("url") or f"https://roadmap.sh/{slug}",
                    "content_source_ref": f"content/{slug}.json#{key}",
                    "content_match_method": method,
                    "description_status": description_status,
                    "review_status": review_status,
                    "usage_scope": usage,
                    "structure_status": ("quarantined" if quarantined_self
                                         else "ancestor_quarantined" if quarantined_ancestor
                                         else "ok"),
                    "segment_index": i,
                    "segment_count": len(paragraphs),
                })

    # 关系：原图连线（原样保留）
    relation_rows: list[dict] = []
    pattern: Counter = Counter()
    for e in raw.get("edges", []):
        src_id, tgt_id = e.get("source"), e.get("target")

        def endpoint(nid: str) -> tuple[str, str | None]:
            if nid in item_ids:
                return "resolved", (raw_by_id.get(nid) or {}).get("type")
            rn = raw_by_id.get(nid)
            if rn is None:
                return "missing", None
            t = rn.get("type")
            if t in LAYOUT_TYPES:
                return "layout_node", t
            return "filtered_item", t

        s_status, s_type = endpoint(src_id)
        t_status, t_type = endpoint(tgt_id)
        pattern[(s_status, t_status)] += 1
        relation_rows.append({
            "relation_id": stable_id("diagram", slug, e.get("id") or f"{src_id}->{tgt_id}"),
            "roadmap": slug,
            "relation_type": "diagram_connection",
            "source_node_id": src_id,
            "target_node_id": tgt_id,
            "edge_style": edge_style(e),
            "source_handle": e.get("sourceHandle"),
            "target_handle": e.get("targetHandle"),
            "raw_edge_id": e.get("id"),
            "raw_source_ref": f"json/{slug}.json#edges[{e.get('id') or src_id + '->' + tgt_id}]",
            "source_endpoint_status": s_status,
            "source_endpoint_type": s_type,
            "target_endpoint_status": t_status,
            "target_endpoint_type": t_type,
            "both_endpoints_resolved": s_status == "resolved" and t_status == "resolved",
            "in_pilot_node_set": s_status == "resolved" and t_status == "resolved",
            "semantics": "原始图连线；仅表示画布上相连，不表示先修或必须先后",
            "quarantined": any(x in quarantine for x in (src_id, tgt_id) if x),
        })

    # 关系：结构推导分组
    for n in node_rows:
        nid = n["node_id"]
        parent = n["inferred_parent_node_id"]
        if not parent:
            continue
        confidence = {
            "official-edge": "inferred_from_official_edge",
            "section": "inferred_from_section_box",
            "section-frame": "inferred_from_section_box",
            "caption-group": "inferred_from_caption_group",
            "block": "inferred_from_layout_block",
            "spine": "inferred_root_topic_convention",
        }.get(n["inferred_parent_rule"] or "", "unknown")
        relation_rows.append({
            "relation_id": stable_id("group", slug, parent, nid),
            "roadmap": slug,
            "relation_type": "inferred_grouping",
            "source_node_id": parent,
            "target_node_id": nid,
            "parent_rule": n["inferred_parent_rule"],
            "confidence": confidence,
            "basis": "官方连线" if confidence == "inferred_from_official_edge" else "画布坐标/分组框",
            "semantics": "结构推导的分组关系，不是官方父子事实，也不表示学习顺序",
            "structure_quarantined": bool(n["structure_quarantined"] or n["structure_ancestor_quarantined"]),
            "raw_source_ref": f"graph/{slug}.json#{nid}",
        })

    # 统计
    raw_nodes = raw.get("nodes", [])
    excluded: Counter = Counter()
    excluded_detail: list[dict] = []
    for rn in raw_nodes:
        rid = rn.get("id")
        if rid in item_ids:
            continue
        rtype = rn.get("type")
        label = ((rn.get("data") or {}).get("label") or "").strip()
        if rtype in LAYOUT_TYPES:
            reason = f"layout_type:{rtype}"
        elif CHROME_RE.search(label):
            reason = "chrome_panel"
        elif rtype in NODE_TYPES:
            reason = "content_node_filtered_by_builder"
        else:
            reason = f"unknown_type:{rtype}"
        excluded[reason] += 1
        excluded_detail.append({"node_id": rid, "type": rtype, "reason": reason, "label": label})

    stats = {
        "roadmap": slug,
        "raw_nodes": len(raw_nodes),
        "kept_nodes": len(node_rows),
        "excluded_nodes": len(excluded_detail),
        "excluded_reasons": dict(sorted(excluded.items())),
        "raw_edges": len(raw.get("edges", [])),
        "edge_endpoint_patterns": {f"{a}->{b}": c for (a, b), c in sorted(pattern.items())},
        "match_methods": {m: match_counts.get(m, 0) for m in MATCH_METHODS},
        "ambiguous_reasons": dict(sorted(Counter(
            r["content_ambiguous_reason"] for r in node_rows
            if r["content_ambiguous_reason"]).items())),
        "description_status": dict(sorted(desc_counts.items())),
        "usage_scope": dict(sorted(scope_counts.items())),
        "chunks": len(chunk_rows),
        "resources": len(resource_rows),
        "quarantined_nodes": len([r for r in node_rows if r["structure_quarantined"]]),
        "quarantined_descendants": len([r for r in node_rows if r["structure_ancestor_quarantined"]]),
    }
    return {
        "nodes": node_rows,
        "relations": relation_rows,
        "chunks": chunk_rows,
        "resources": resource_rows,
        "review_items": review_rows,
        "stats": stats,
        "excluded_detail": excluded_detail,
        "graph_meta": {
            "fetched_at": (graph.get("source") or {}).get("fetched_at"),
            "graph_source": (graph.get("source") or {}).get("graph"),
            "content_source": (graph.get("source") or {}).get("content"),
            "title": graph.get("title"),
        },
    }


# ------------------------------------------------------------------ qa
def run_checks(built: dict[str, dict], determinism: dict, docs: dict) -> dict:
    checks: list[dict] = []

    def add(cid: int, name: str, ok: bool, detail: str, warn: bool = False) -> None:
        checks.append({"id": cid, "name": name,
                        "status": "warn" if (warn and ok) else ("pass" if ok else "fail"),
                        "detail": detail})

    slugs = [s for s in SCOPE if s in built]
    add(1, "三条路线均成功处理", len(slugs) == len(SCOPE), f"processed={slugs}")

    keys = Counter((r["roadmap"], r["node_id"]) for s in slugs for r in built[s]["nodes"])
    dup = [k for k, c in keys.items() if c > 1]
    add(2, "唯一键 (roadmap,node_id) 无重复", not dup, f"keys={sum(keys.values())}, dup={dup[:5]}")

    chunks = [c for s in slugs for c in built[s]["chunks"]]
    node_ids = {(r["roadmap"], r["node_id"]) for s in slugs for r in built[s]["nodes"]}
    untraceable = [c for c in chunks
                   if (c["roadmap"], c["node_id"]) not in node_ids or not c["content_source_ref"]]
    add(3, "所有可用片段可回溯节点与内容来源", not untraceable,
        f"chunks={len(chunks)}, untraceable={len(untraceable)}")

    all_nodes = [r for s in slugs for r in built[s]["nodes"]]
    bad_method = [r for r in all_nodes if r["content_match_method"] not in MATCH_METHODS]
    amb = [r for r in all_nodes if r["content_match_method"] == "ambiguous"]
    amb_in_chunks = [r for r in amb if r["usage_scope"] == "content_reference"]
    amb_reviewed = {r["node_id"] for s in slugs for r in built[s]["review_items"]
                    if r["item_type"] == "content_match_ambiguous"}
    add(4, "匹配方式完整、歧义未被静默消除", not bad_method and not amb_in_chunks
        and {r["node_id"] for r in amb} == amb_reviewed,
        f"ambiguous={len(amb)}, review_items={len(amb_reviewed)}, in_chunks={len(amb_in_chunks)}")

    diag = [r for s in slugs for r in built[s]["relations"] if r["relation_type"] == "diagram_connection"]
    raw_edge_total = sum(built[s]["stats"]["raw_edges"] for s in slugs)
    no_status = [r for r in diag if not r["source_endpoint_status"] or not r["target_endpoint_status"]]
    unresolved = [r for r in diag if not r["both_endpoints_resolved"]]
    add(5, "边端点状态明确", len(diag) == raw_edge_total and not no_status,
        f"raw_edges={raw_edge_total}, emitted={len(diag)}, unresolved_but_flagged={len(unresolved)}, missing_status={len(no_status)}")

    fabricated = [r for r in all_nodes
                  if r["content_match_method"] in {"missing", "ambiguous"} and r["description"]]
    add(6, "缺描述未被自动补写", not fabricated, f"fabricated={len(fabricated)}")

    leaks = [c for c in chunks if "inferred_path" in c or " > " in c["text"]]
    quarantined_keys = {(r["roadmap"], r["node_id"]) for r in all_nodes if r["structure_quarantined"]}
    q_in_chunks = [c for c in chunks if (c["roadmap"], c["node_id"]) in quarantined_keys]
    add(7, "已知错位路径未进入检索正文", not leaks,
        f"path_leaks={len(leaks)}, quarantined_nodes_with_chunks={len(q_in_chunks)}"
        "（片段正文不含推断 path；隔离仅作用于结构字段与审核标记）")

    pre = [r for s in slugs for r in built[s]["relations"] if r["relation_type"] == "prerequisite"]
    add(8, "未生成未经证实的先修关系", not pre, f"prerequisite_relations={len(pre)}")

    recon_ok = all(
        built[s]["stats"]["raw_nodes"] == built[s]["stats"]["kept_nodes"] + built[s]["stats"]["excluded_nodes"]
        for s in slugs)
    add(9, "保留/排除节点可对账", recon_ok,
        "; ".join(f"{s}: raw={built[s]['stats']['raw_nodes']} kept={built[s]['stats']['kept_nodes']} "
                  f"excluded={built[s]['stats']['excluded_nodes']}" for s in slugs))

    add(10, "重复运行内容一致", determinism.get("identical", False),
        f"hashes={determinism.get('compare', {})}")

    stats = {
        "roadmaps": {s: built[s]["stats"] for s in slugs},
        "total_nodes": len(all_nodes),
        "total_chunks": len(chunks),
        "total_resources": sum(built[s]["stats"]["resources"] for s in slugs),
        "total_relations": sum(len(built[s]["relations"]) for s in slugs),
        "diagram_connections": len(diag),
        "inferred_groupings": sum(len(built[s]["relations"]) - built[s]["stats"]["raw_edges"] for s in slugs),
        "prerequisite_relations": len(pre),
        "review_items": sum(len(built[s]["review_items"]) for s in slugs),
        "nodes_without_description": len([r for r in all_nodes if r["description_status"] != "present"]),
        "ambiguous_nodes": len(amb),
        "title_fallback_nodes": len([r for r in all_nodes if r["content_match_method"] == "title_fallback"]),
        "quarantined_relations": sum(1 for s in slugs for r in built[s]["relations"]
                                      if r.get("quarantined") or r.get("structure_quarantined")),
    }
    return {
        "generated_at": now_iso(),
        "inputs": docs,
        "checks": checks,
        "stats": stats,
        "failures": [c for c in checks if c["status"] == "fail"],
        "warnings": [c for c in checks if c["status"] == "warn"],
    }


# ------------------------------------------------------------------ verify
def pick_node_samples(rows: list[dict], limit: int = 10) -> tuple[list[dict], dict]:
    picked: list[dict] = []
    seen: set[tuple[str, str]] = set()
    coverage: dict[str, str] = {}

    def take(tag: str, pred) -> None:
        nonlocal picked
        for r in rows:
            key = (r["roadmap"], r["node_id"])
            if key in seen or not pred(r):
                continue
            seen.add(key)
            picked.append(r)
            coverage[tag] = r["node_id"]
            return
        coverage[tag] = "absent"

    for method in MATCH_METHODS:
        take(f"match:{method}", lambda r, m=method: r["content_match_method"] == m)
    for status in ("present", "empty", "unavailable"):
        take(f"description:{status}", lambda r, s=status: r["description_status"] == s)
    for rule in ("spine", "official-edge", "block", "section", "section-frame", "caption-group"):
        take(f"rule:{rule}", lambda r, x=rule: r["inferred_parent_rule"] == x)
    for ntype in ("title", "topic", "subtopic", "button", "label", "paragraph"):
        take(f"type:{ntype}", lambda r, t=ntype: r["node_type"] == t)
    for r in rows:
        if len(picked) >= limit:
            break
        key = (r["roadmap"], r["node_id"])
        if key in seen:
            continue
        seen.add(key)
        picked.append(r)
    return picked[:limit], coverage


def verify(slug: str, built: dict, docs: dict, pkg_dir: Path) -> dict:
    src = load_sources(slug)
    raw_by_id = {n.get("id"): n for n in src["raw"].get("nodes", [])}
    content = src["content"]

    nodes, coverage = pick_node_samples(built["nodes"], 10)
    node_checks = []
    for r in nodes:
        nid = r["node_id"]
        in_raw = nid in raw_by_id
        ok = in_raw
        note = ""
        if r["content_match_method"] == "id":
            entry = content.get(nid) or {}
            ok = ok and bool(entry) and (entry.get("desc") or "").strip() == r["description"]
            note = "id 命中，描述与 content 条目逐字一致"
        elif r["content_match_method"] == "title_fallback":
            key = (r["content_source_ref"] or "").split("#")[-1]
            entry = content.get(key) or {}
            ok = ok and norm(entry.get("title")) == norm(r["label"])
            note = "标题归一化一致，仍需人工审核"
        elif r["content_match_method"] == "ambiguous":
            cands = r["content_candidates"] or []
            ok = ok and bool(cands) and r["description"] == ""
            note = ("内容条目已被其他节点占用，未取描述"
                    if r["content_ambiguous_reason"] == "content_key_owned_by_other_node"
                    else "多候选，未取描述")
        else:
            ok = ok and r["description"] == ""
            note = "无匹配，描述留空"
        node_checks.append({
            "roadmap": slug, "node_id": nid, "label": r["label"], "node_type": r["node_type"],
            "content_match_method": r["content_match_method"],
            "description_status": r["description_status"],
            "inferred_parent_rule": r["inferred_parent_rule"],
            "in_raw_graph": in_raw,
            "check_pass": ok,
            "note": note,
        })

    diag = [x for x in built["relations"] if x["relation_type"] == "diagram_connection"]
    edge_samples: list[dict] = []
    seen: set[str] = set()

    def take_edge(pred) -> None:
        for rel in diag:
            if rel["relation_id"] in seen:
                continue
            if pred(rel):
                seen.add(rel["relation_id"])
                edge_samples.append(rel)
                return

    take_edge(lambda r: r["edge_style"] == "solid")
    take_edge(lambda r: r["edge_style"] == "dashed")
    take_edge(lambda r: not r["both_endpoints_resolved"])
    for rel in diag:
        if len(edge_samples) >= 5:
            break
        if rel["relation_id"] in seen:
            continue
        seen.add(rel["relation_id"])
        edge_samples.append(rel)

    raw_edges = {e.get("id"): e for e in src["raw"].get("edges", []) if e.get("id")}
    edge_checks = []
    for rel in edge_samples[:5]:
        raw_edge = raw_edges.get(rel["raw_edge_id"])
        ok = raw_edge is not None
        if raw_edge:
            ok = ok and raw_edge.get("source") == rel["source_node_id"]
            ok = ok and raw_edge.get("target") == rel["target_node_id"]
            ok = ok and edge_style(raw_edge) == rel["edge_style"]
            ok = ok and raw_edge.get("sourceHandle") == rel["source_handle"]
            ok = ok and raw_edge.get("targetHandle") == rel["target_handle"]
        edge_checks.append({
            "roadmap": slug,
            "relation_id": rel["relation_id"],
            "source_node_id": rel["source_node_id"],
            "target_node_id": rel["target_node_id"],
            "edge_style": rel["edge_style"],
            "source_endpoint_status": rel["source_endpoint_status"],
            "target_endpoint_status": rel["target_endpoint_status"],
            "endpoint_types": [rel["source_endpoint_type"], rel["target_endpoint_type"]],
            "check_pass": ok,
        })
    return {
        "node_samples": node_checks,
        "node_sample_coverage": coverage,
        "edge_samples": edge_checks,
    }


def keyword_baseline(built: dict[str, dict]) -> list[dict]:
    rows = []
    for case in RETRIEVAL_CASES:
        hits: list[dict] = []
        for slug in SCOPE:
            if slug not in built:
                continue
            for n in built[slug]["nodes"]:
                text = f"{n['label']}\n{n['description']}"
                score = sum(1 for kw in case["keywords"] if kw.lower() in text.lower())
                if score:
                    hits.append({"roadmap": slug, "node_id": n["node_id"], "label": n["label"],
                                 "hit_terms": [kw for kw in case["keywords"] if kw.lower() in text.lower()],
                                 "in_chunks": n["usage_scope"] == "content_reference"})
        expected_ids = []
        for slug, label in case["expects"]:
            for n in built.get(slug, {}).get("nodes", []):
                if n["label"] == label:
                    expected_ids.append(n["node_id"])
        retrieved = {h["node_id"] for h in hits}
        rows.append({
            "case_id": case["case_id"],
            "baseline": "label+description 子串匹配（非语义检索）",
            "hit_nodes": hits[:12],
            "expected_node_ids": sorted(set(expected_ids)),
            "expected_hit": all(i in retrieved for i in expected_ids) if expected_ids else None,
        })
    return rows


# ------------------------------------------------------------------ README
def render_readme(built: dict[str, dict], manifest: dict) -> str:
    lines = [
        "# roadmap 检索资料包 v0.1（frontend / backend / python）",
        "",
        "本目录由 `scripts/prepare_roadmap_pilot.py` 从 `references/raw/roadmap-ai/` 生成，"
        "只读原始资料、不修改原始文件。全部内容为本地试点资料，Git 忽略，不对外分发。",
        "",
        f"- 生成时间：{manifest['generated_at']}",
        f"- 处理范围：{', '.join(manifest['scope'])}（其余 98 条路线未处理，也未删除）",
        "- 结构来源：官方画布数据；父子关系为布局推导，不是官方事实",
        "- 内容来源：官方 content markdown，按节点 id 重新判定匹配方式",
        "",
        "## 文件",
        "",
        "| 文件 | 内容 |",
        "|---|---|",
        "| `nodes.jsonl` | 每节点一行：描述、匹配方式、审核状态、结构推导字段与隔离标记 |",
        "| `relations.jsonl` | `diagram_connection`（原图连线，原样保留）与 `inferred_grouping`（结构推导）；不含 prerequisite |",
        "| `chunks.jsonl` | 仅供正文检索的片段：路线名 + 知识点 + 描述 + 来源标识；仅 id 命中且有描述的节点 |",
        "| `resources.jsonl` | 资源条目，全部 `link_status=unchecked` |",
        "| `review_items.jsonl` | 待审核项：标题兜底、匹配歧义、已知错位、祖先链可疑 |",
        "| `manifest.json` | 输入/输出哈希、来源时间、计数 |",
        "| `qa_report.json` | 10 项确定性检查与统计 |",
        "| `qa_samples.json` | `--verify` 生成的 30 节点 / 15 边抽样核对 |",
        "| `retrieval_cases.json` | 10 个中文检索案例（预期节点、证据类型、不应得出的结论） |",
        "",
        "## 字段含义（要点）",
        "",
        "- `content_match_method`：`id` = 节点 id 命中；`title_fallback` = 仅归一化标题唯一匹配，待审核；"
        "`ambiguous` = 多候选，不取描述；`missing` = 无匹配。",
        "- `usage_scope`：`content_reference` 可进入检索片段；`navigation_only` 无描述；"
        "`pending_review` 待审核；`excluded` 因歧义排除。",
        "- `structure_*` / `inferred_*`：父子、深度、路径均为画布布局推导，不表示学习顺序；"
        "`structure_quarantined` 标记已知错位节点，`structure_ancestor_quarantined` 表示祖先链含错位。",
        "- `relations.jsonl` 中 `semantics` 明确指出：图示连线与推导分组都不表示先修关系。",
        "",
        "## 统计",
        "",
        "| 路线 | 原始节点 | 保留 | 排除 | 片段 | 资源 | 有描述 | 歧义 | 待审核 |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for slug in manifest["scope"]:
        st = built[slug]["stats"]
        lines.append(
            f"| {slug} | {st['raw_nodes']} | {st['kept_nodes']} | {st['excluded_nodes']} | "
            f"{st['chunks']} | {st['resources']} | {st['description_status'].get('present', 0)} | "
            f"{st['match_methods'].get('ambiguous', 0)} | "
            f"{st['match_methods'].get('title_fallback', 0)} |")
    lines += [
        "",
        "## 重跑",
        "",
        "```bash",
        "python scripts/prepare_roadmap_pilot.py --verify",
        "```",
        "",
        "输入不变时，`nodes.jsonl` / `relations.jsonl` / `chunks.jsonl` / `resources.jsonl` / "
        "`review_items.jsonl` 的 id、计数和正文保持一致（时间字段除外）。",
        "",
        "## 边界",
        "",
        "- 未做全站抓取、未补写缺失描述、未调用云端模型或 embedding、未引入检索依赖。",
        "- 未核验任何资源链接可用性；未做端到端 RAG 验证，检索案例运行状态见 `qa_report.json`。",
        "- 原始 roadmap 文本版权归 roadmap.sh，本目录只作本地研究资料，不得对外发布。",
        "",
    ]
    return "\n".join(lines)


# ------------------------------------------------------------------ main
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true", help="额外做抽样核对")
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args(argv)
    out_dir = Path(args.out)

    for slug in SCOPE:
        need = [SRC / "graph" / f"{slug}.json", SRC / "json" / f"{slug}.json",
                SRC / "content" / f"{slug}.json"]
        missing = [str(p) for p in need if not p.exists()]
        if missing:
            print(f"missing input: {missing}", file=sys.stderr)
            return 2

    first = {slug: build_roadmap(slug) for slug in SCOPE}
    second = {slug: build_roadmap(slug) for slug in SCOPE}

    compare: dict[str, str] = {}
    det_ok = True
    for slug in SCOPE:
        for kind in ("nodes", "relations", "chunks", "resources", "review_items"):
            digest = sha256_bytes(
                "\n".join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in first[slug][kind])
                .encode("utf-8"))
            digest2 = sha256_bytes(
                "\n".join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in second[slug][kind])
                .encode("utf-8"))
            compare[f"{slug}.{kind}"] = digest[:12]
            det_ok = det_ok and digest == digest2
    determinism = {"identical": det_ok, "compare": compare}

    out_dir.mkdir(parents=True, exist_ok=True)
    kind_files = {
        "nodes": "nodes.jsonl",
        "relations": "relations.jsonl",
        "chunks": "chunks.jsonl",
        "resources": "resources.jsonl",
        "review_items": "review_items.jsonl",
    }
    for kind, name in kind_files.items():
        rows = [r for slug in SCOPE for r in first[slug][kind]]
        write_jsonl(out_dir / name, rows)

    # 检索案例（解析节点 id）
    cases_out = []
    for case in RETRIEVAL_CASES:
        resolved = []
        for slug, label in case["expects"]:
            for n in first[slug]["nodes"]:
                if n["label"] == label:
                    resolved.append({"roadmap": slug, "node_id": n["node_id"], "label": label,
                                     "usage_scope": n["usage_scope"]})
        absent = []
        for slug, label in case["absent"]:
            in_scope = slug in SCOPE
            absent.append({"roadmap": slug, "label": label, "in_pilot_scope": in_scope})
        cases_out.append({
            "case_id": case["case_id"],
            "topic": case["topic"],
            "question": case["question"],
            "expected_nodes": resolved,
            "expected_absent": absent,
            "evidence_type": case["evidence"],
            "must_not_conclude": case["must_not"],
            "run_status": "not_run",
            "run_note": "本轮未引入检索器或向量库；仅提供资料与案例，未评估召回或答案质量",
            "coverage_note": ("预期节点中存在仅有标题、没有官方描述的节点（usage_scope=navigation_only）时，"
                              "本资料只能确认其存在与结构状态，不能提供解释性内容")
            if any(e.get("usage_scope") != "content_reference" for e in resolved) else
            "预期节点均有官方描述，可作为内容证据",
        })
    write_json(out_dir / "retrieval_cases.json", {
        "generated_at": now_iso(),
        "retrieval_run_status": "not_run",
        "reason": "本地没有可复用的检索器；按约定不引入 embedding/向量库/云服务，也不做语义检索声明",
        "keyword_baseline": keyword_baseline(first),
        "baseline_caveat": ("该基线用节点标签与描述做子串匹配，而案例关键词本来就取自这些标签，"
                            "属自证式检验，只能说明字段可用，不能作为检索效果或召回质量证据"),
        "cases": cases_out,
    })

    # 输入哈希与来源时间
    input_files = [SRC / "index.json", SRC / "nodes.jsonl"]
    for slug in SCOPE:
        input_files += [SRC / "graph" / f"{slug}.json", SRC / "json" / f"{slug}.json",
                        SRC / "content" / f"{slug}.json", SRC / "md" / f"{slug}.md"]
    inputs = [{"path": str(p.relative_to(ROOT)), "sha256": sha256_file(p), "bytes": p.stat().st_size}
              for p in input_files]

    script_path = Path(__file__).resolve()
    manifest = {
        "package": PACKAGE,
        "generated_at": now_iso(),
        "generator": {
            "script": str(script_path.relative_to(ROOT)),
            "version": SCRIPT_VERSION,
            "sha256": sha256_file(script_path),
        },
        "scope": list(SCOPE),
        "unprocessed_roadmaps": 101 - len(SCOPE),
        "source_times": {
            "graph_fetched_at": {slug: first[slug]["graph_meta"]["fetched_at"] for slug in SCOPE},
            "content_snapshot": "unknown：本地快照 developer-roadmap-master，无上游提交或下载日期证据",
            "build_time": now_iso(),
            "note": "构建时间不等于原文更新时间",
        },
        "inputs": inputs,
        "counts": {
            "nodes": sum(len(first[s]["nodes"]) for s in SCOPE),
            "relations": sum(len(first[s]["relations"]) for s in SCOPE),
            "chunks": sum(len(first[s]["chunks"]) for s in SCOPE),
            "resources": sum(len(first[s]["resources"]) for s in SCOPE),
            "review_items": sum(len(first[s]["review_items"]) for s in SCOPE),
        },
        "boundaries": {
            "not_full_crawl": True,
            "not_description_backfill": True,
            "no_cloud_model": True,
            "no_embedding_or_vector_db": True,
            "not_m3_or_m4_acceptance": True,
            "local_only": True,
        },
        "outputs": [],
    }

    qa = run_checks(first, determinism, {"files": inputs, "generator": manifest["generator"]})

    verify_result = None
    if args.verify:
        verify_result = {
            "generated_at": now_iso(),
            "note": "抽样对照原始 json/<slug>.json 与 content/<slug>.json；未做官方画布视觉核对",
            "roadmaps": {},
        }
        total_nodes = total_edges = 0
        for slug in SCOPE:
            res = verify(slug, first[slug], {}, out_dir)
            verify_result["roadmaps"][slug] = res
            total_nodes += len(res["node_samples"])
            total_edges += len(res["edge_samples"])
        verify_result["totals"] = {"node_samples": total_nodes, "edge_samples": total_edges,
                                   "node_checks_failed": sum(
                                       1 for s in SCOPE for r in verify_result["roadmaps"][s]["node_samples"]
                                       if not r["check_pass"]),
                                   "edge_checks_failed": sum(
                                       1 for s in SCOPE for r in verify_result["roadmaps"][s]["edge_samples"]
                                       if not r["check_pass"])}
        write_json(out_dir / "qa_samples.json", verify_result)
        qa["sample_review"] = {
            "status": "run",
            "file": "qa_samples.json",
            "node_samples": total_nodes,
            "edge_samples": total_edges,
            "failures": verify_result["totals"]["node_checks_failed"] + verify_result["totals"]["edge_checks_failed"],
        }
    else:
        qa["sample_review"] = {"status": "not_run"}

    write_json(out_dir / "qa_report.json", qa)

    # 输出哈希（写入 manifest 后回填）
    outputs = []
    for name in list(kind_files.values()) + ["retrieval_cases.json", "qa_report.json"]:
        p = out_dir / name
        outputs.append({"path": name, "bytes": p.stat().st_size,
                        "lines": sum(1 for _ in p.open(encoding="utf-8")),
                        "sha256": sha256_file(p)})
    manifest["outputs"] = outputs
    write_json(out_dir / "manifest.json", manifest)
    (out_dir / "README.md").write_text(render_readme(first, manifest), encoding="utf-8")

    print(f"package: {out_dir}")
    for slug in SCOPE:
        st = first[slug]["stats"]
        print(f"  {slug}: nodes={st['kept_nodes']} chunks={st['chunks']} resources={st['resources']} "
              f"match={st['match_methods']}")
    print(f"  checks: {sum(1 for c in qa['checks'] if c['status'] == 'pass')} pass, "
          f"{len(qa['failures'])} fail, {len(qa['warnings'])} warn")
    for c in qa["failures"]:
        print(f"  FAIL [{c['id']}] {c['name']}: {c['detail']}")
    return 0 if not qa["failures"] else 1


if __name__ == "__main__":
    sys.exit(main())
