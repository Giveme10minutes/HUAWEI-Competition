#!/usr/bin/env python3
"""Create and verify a full local text + raw review package for roadmap-ai.

No network access is used. The source JSON objects are preserved in review JSONL;
human-readable files are views over those raw records and node-ID joins.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "references/raw/roadmap-ai"
DEFAULT_OUTPUT = ROOT / "local_data/roadmap_full_v0.4"
PILOT_REVIEW = ROOT / "local_data/roadmap_m3_topic_pilot_v0.1/review/selection_and_checks.json"

# Historical review flags, included here so this generator does not depend on
# loading or modifying any ignored pilot package at runtime.
KNOWN_FLAGS = {
    ("frontend", "k4hMVVBMatedUq5EKiMo4"): ("歧义隔离", "内容匹配歧义：排除，未猜测匹配"),
    ("python", "hIQe_B-68ENL-GFg6GmnD"): ("歧义隔离", "内容匹配歧义：排除，未猜测匹配"),
    ("python", "iogwMmOvub2ZF4zgg6WyF"): ("歧义隔离", "内容匹配歧义：排除，未猜测匹配"),
    ("python", "U0fJo2a3vnaodNJhfZ78I"): ("歧义隔离", "内容匹配歧义：排除，未猜测匹配"),
    ("backend", "ruK1Bf7XVIgOHguNFxYlY"): ("已知错位隔离", "System Design 被归入 Architectural Patterns；模块归属未经核实"),
    ("backend", "94oRYuULJPdOMI1wihFrU"): ("已知错位隔离", "Docker 被归到 Message Brokers 下的 Containerization 标题块；官方 JSON 中无对应 topic 节点"),
    ("backend", "vDaxr8AIaPbG_3mHr0N6X"): ("已知错位隔离", "Kubernetes 被归到 Message Brokers 下的 Containerization 标题块；官方 JSON 中无对应 topic 节点"),
}

LAYOUT_ONLY_TYPES = {"vertical", "horizontal"}
RICH_NODE_TYPES = {
    "doc", "paragraph", "text", "heading", "bulletList", "orderedList", "listItem",
    "hardBreak", "blockquote", "codeBlock", "link",
}
RICH_MARK_TYPES = {"bold", "italic", "underline", "code", "strike", "link"}


class PackageError(Exception):
    pass


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha(path.read_bytes())


def json_no_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise PackageError(f"JSON 对象存在重复字段 {key!r}，无法无损处理")
        result[key] = value
    return result


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=json_no_duplicate_keys)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PackageError(f"JSON 无法解码：{path.relative_to(ROOT)}: {exc}") from exc


def json_line(record: Any) -> str:
    return json.dumps(record, ensure_ascii=False, separators=(",", ":"))


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, records: list[Any]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json_line(record) + "\n")


def rich_text(value: Any, unsupported: list[dict[str, Any]], route: str, question_title: str) -> str:
    """Render ProseMirror-like JSON to readable text while retaining links/lists."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "".join(rich_text(v, unsupported, route, question_title) for v in value)
    if not isinstance(value, dict):
        return str(value)

    kind = value.get("type")
    children = value.get("content", [])
    rendered_children = [rich_text(x, unsupported, route, question_title) for x in children] if isinstance(children, list) else []
    child_text = "".join(rendered_children)
    attrs = value.get("attrs") if isinstance(value.get("attrs"), dict) else {}
    marks = value.get("marks") if isinstance(value.get("marks"), list) else []

    if kind == "text":
        text = str(value.get("text", ""))
        for mark in marks:
            if not isinstance(mark, dict):
                continue
            mark_kind = mark.get("type")
            mark_attrs = mark.get("attrs") if isinstance(mark.get("attrs"), dict) else {}
            if mark_kind == "link":
                href = mark_attrs.get("href")
                text = f"[{text}]({href})" if href else text
            elif mark_kind == "bold":
                text = f"**{text}**"
            elif mark_kind == "italic":
                text = f"_{text}_"
            elif mark_kind == "underline":
                text = f"__{text}__"
            elif mark_kind == "code":
                text = f"`{text}`"
            elif mark_kind == "strike":
                text = f"~~{text}~~"
            elif mark_kind not in RICH_MARK_TYPES:
                unsupported.append({"route": route, "question_title": question_title, "rich_type": "mark:" + str(mark_kind), "raw": mark})
        return text
    if kind == "link":
        href = attrs.get("href")
        if href:
            already_linked = re.fullmatch(r"\[(.*)\]\((.+)\)", child_text, flags=re.S)
            if already_linked and already_linked.group(2) == href:
                return child_text
            return f"[{child_text}]({href})"
        return child_text
    if kind == "hardBreak":
        return "\n"
    if kind == "paragraph":
        return child_text + "\n\n"
    if kind == "heading":
        level = attrs.get("level", 2)
        return f"{'#' * max(1, min(6, int(level) if str(level).isdigit() else 2))} {child_text}\n\n"
    if kind == "bulletList":
        return child_text + "\n"
    if kind == "orderedList":
        return child_text + "\n"
    if kind == "listItem":
        return "- " + child_text + "\n"
    if kind == "blockquote":
        return "> " + child_text + "\n\n"
    if kind == "codeBlock":
        return child_text + "\n\n"
    if kind == "doc":
        return child_text

    if kind:
        unsupported.append({"route": route, "question_title": question_title, "rich_type": str(kind), "raw": value})
        # Visible fallback prevents unsupported structured content from vanishing.
        if child_text.strip():
            return child_text
        fallback = value.get("text")
        return str(fallback) if fallback is not None else f"[未支持富文本节点：{kind}，原始结构见 review/questions.jsonl]"
    # Unknown wrapper without a type: retain readable children and record shape.
    unsupported.append({"route": route, "question_title": question_title, "rich_type": "<missing-type>", "raw": value})
    return child_text or json_line(value)


def clean_line(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def edge_style_text(edge: dict[str, Any]) -> str:
    # Keep both original visual style objects and any explicit application-level style.
    data = edge.get("data") if isinstance(edge.get("data"), dict) else {}
    return f"style={clean_line(edge.get('style'))}; data.edgeStyle={clean_line(data.get('edgeStyle'))}"


def point_key(node: dict[str, Any]) -> tuple[float, float, str]:
    pos = node.get("position") if isinstance(node.get("position"), dict) else {}
    try:
        y = float(pos.get("y", 0))
        x = float(pos.get("x", 0))
    except (TypeError, ValueError):
        y, x = 0.0, 0.0
    return y, x, str(node.get("id", ""))


def raw_label(node: dict[str, Any]) -> Any:
    data = node.get("data") if isinstance(node.get("data"), dict) else {}
    return data.get("label", data.get("title", data.get("text")))


def has_readable_payload(node: dict[str, Any], content_entry: dict[str, Any] | None) -> bool:
    if content_entry and (content_entry.get("title") or content_entry.get("desc") or content_entry.get("links")):
        return True
    ntype = node.get("type")
    data = node.get("data") if isinstance(node.get("data"), dict) else {}
    label = raw_label(node)
    if ntype in LAYOUT_ONLY_TYPES:
        if isinstance(label, str) and label.strip() and label.strip().lower() not in {"...", "…", "vertical", "horizontal", "vertical node", "horizontal node", "layout"}:
            return True
    elif label not in (None, "", [], {}):
        return True
    for key in ("description", "title", "text", "href", "url", "links", "items", "options", "legends", "legend", "content"):
        val = data.get(key)
        if val not in (None, "", [], {}):
            return True
    return False


def render_node_auxiliary(node: dict[str, Any]) -> list[str]:
    data = node.get("data") if isinstance(node.get("data"), dict) else {}
    lines = []
    for key in ("legend", "href"):
        if data.get(key) not in (None, "", [], {}):
            lines.append(f"原始 {key}：{clean_line(data[key])}")
    if node.get("type") in {"linksgroup", "todo", "checklist", "resourceButton", "section", "paragraph"}:
        for key, value in data.items():
            if key in {"label", "legend", "href", "style", "color"} or value in (None, "", [], {}):
                continue
            if isinstance(value, (str, list, dict, int, float, bool)):
                lines.append(f"原始可读字段 {key}：{clean_line(value)}")
    return lines


def render_resource_links(links: Any) -> list[str]:
    if links is None:
        return []
    result = ["全部资源链接（原 content 按 ID 匹配；未截断）："]
    if not isinstance(links, list):
        result.append("原始 links JSON：" + json_line(links))
        return result
    if not links:
        result.append("（无）")
        return result
    for i, link in enumerate(links, 1):
        if isinstance(link, (list, tuple)) and len(link) >= 3:
            result.append(f"{i}. 类型={clean_line(link[0])}；标题={clean_line(link[1])}；URL={clean_line(link[2])}")
        else:
            result.append(f"{i}. 原始资源记录={json_line(link)}")
    return result


def render_question(question: dict[str, Any], route: str, unsupported: list[dict[str, Any]]) -> str:
    title = question.get("title", "（无标题）")
    qtype = question.get("type", "（无类型）")
    desc = rich_text(question.get("description"), unsupported, route, str(title))
    return (
        f"问题类型：{clean_line(qtype)}\n"
        f"问题：{clean_line(title)}\n"
        f"回答原文投影：\n{desc if desc else '（无描述）'}\n"
        "来源性质：路线页面提供的问题与建议，不是强制要求或个人结论。\n"
    )


def rich_text_tokens(value: Any) -> tuple[list[str], list[str]]:
    texts: list[str] = []
    hrefs: list[str] = []
    def walk(v: Any) -> None:
        if isinstance(v, dict):
            if v.get("type") == "text" and isinstance(v.get("text"), str):
                texts.append(v["text"])
            attrs = v.get("attrs")
            if v.get("type") == "link" and isinstance(attrs, dict) and isinstance(attrs.get("href"), str):
                hrefs.append(attrs["href"])
            for mark in v.get("marks", []) if isinstance(v.get("marks"), list) else []:
                if isinstance(mark, dict) and mark.get("type") == "link":
                    mark_attrs = mark.get("attrs") if isinstance(mark.get("attrs"), dict) else {}
                    if isinstance(mark_attrs.get("href"), str):
                        hrefs.append(mark_attrs["href"])
            for child in v.values():
                walk(child)
        elif isinstance(v, list):
            for child in v:
                walk(child)
    if isinstance(value, str):
        texts.append(value)
    else:
        walk(value)
    return texts, hrefs


def readable_node_blocks(body: str) -> dict[str, str]:
    blocks: dict[str, str] = {}
    for chunk in re.split(r"(?m)^===== 原始节点 \d+ =====\s*$", body)[1:]:
        match = re.search(r"(?m)^节点 ID：(.+)$", chunk)
        if match:
            blocks[match.group(1)] = chunk
    return blocks


def unmatched_content_blocks(body: str) -> dict[str, str]:
    blocks: dict[str, str] = {}
    for chunk in body.split("===== 未匹配 content 记录 =====")[1:]:
        match = re.search(r"(?m)^原 content ID：(.+)$", chunk)
        if match:
            blocks[match.group(1)] = chunk
    return blocks


def detect_duplicate_ids(route: str, raw: dict[str, Any], graph: dict[str, Any], content: dict[str, Any]) -> None:
    for collection_name, collection in (("raw nodes", raw.get("nodes", [])), ("graph nodes", graph.get("nodes", []))):
        values = [x.get("id") for x in collection if isinstance(x, dict) and x.get("id") is not None]
        duplicates = [k for k, count in Counter(values).items() if count > 1]
        if duplicates:
            raise PackageError(f"{route} {collection_name} 存在重复 ID，停止以免有损处理：{duplicates[:10]}")
    if not isinstance(content, dict):
        raise PackageError(f"{route} content 根结构不是对象，停止")


def safe_slug(route: dict[str, Any]) -> str:
    slug = route.get("slug")
    if not isinstance(slug, str) or not re.fullmatch(r"[a-z0-9-]+", slug):
        raise PackageError(f"路线 slug 非法：{slug!r}")
    return slug


def discover_and_load() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    index_path = SOURCE / "index.json"
    index = read_json(index_path)
    roads = index.get("roadmaps") if isinstance(index, dict) else None
    if not isinstance(roads, list) or len(roads) != 101:
        raise PackageError("index.json 的 roadmaps 不是 101 条，停止以待确认")
    slugs = [safe_slug(x) for x in roads]
    if len(set(slugs)) != len(slugs):
        raise PackageError("index.json 有重复 slug，停止")

    sets = {kind: {p.stem for p in (SOURCE / kind).glob("*.json")} for kind in ("json", "graph", "content")}
    expected_json = set(slugs) | {"_fetch_report"}
    if sets["json"] != expected_json:
        raise PackageError(f"json 文件集合与 index 不符：extra={sorted(sets['json']-expected_json)[:12]}, missing={sorted(expected_json-sets['json'])[:12]}")
    if sets["graph"] != set(slugs):
        raise PackageError(f"graph 文件集合与 index 不符：extra={sorted(sets['graph']-set(slugs))[:12]}, missing={sorted(set(slugs)-sets['graph'])[:12]}")
    if not sets["content"].issubset(set(slugs)):
        raise PackageError(f"content 出现索引外文件：{sorted(sets['content']-set(slugs))[:12]}")

    loaded: list[dict[str, Any]] = []
    for route in roads:
        slug = safe_slug(route)
        raw = read_json(SOURCE / "json" / f"{slug}.json")
        graph = read_json(SOURCE / "graph" / f"{slug}.json")
        cpath = SOURCE / "content" / f"{slug}.json"
        content = read_json(cpath) if cpath.exists() else {}
        if not isinstance(raw, dict) or not isinstance(graph, dict):
            raise PackageError(f"{slug} 原始 JSON 或 graph 根结构不为对象")
        if not isinstance(raw.get("nodes"), list) or not isinstance(raw.get("edges"), list):
            raise PackageError(f"{slug} 原始 JSON 缺 nodes/edges 数组")
        detect_duplicate_ids(slug, raw, graph, content)
        loaded.append({"index": route, "raw": raw, "graph": graph, "content": content, "has_content_file": cpath.exists()})

    fetch_report = SOURCE / "json/_fetch_report.json"
    if fetch_report.exists():
        read_json(fetch_report)
    return index, loaded


def input_file_hashes() -> dict[str, str]:
    files = [SOURCE / "index.json"]
    for group in ("json", "content", "graph"):
        files.extend(sorted((SOURCE / group).glob("*.json")))
    return {str(path.relative_to(ROOT)): sha_file(path) for path in files}


def make_route_files(route_data: dict[str, Any], output: Path, unsupported: list[dict[str, Any]]) -> dict[str, Any]:
    route = route_data["index"]
    slug = safe_slug(route)
    raw = route_data["raw"]
    graph = route_data["graph"]
    content = route_data["content"]
    route_dir = output / "routes" / slug
    route_dir.mkdir(parents=True)

    nodes: list[dict[str, Any]] = raw.get("nodes", [])
    edges: list[dict[str, Any]] = raw.get("edges", [])
    questions: list[dict[str, Any]] = raw.get("questions", []) or []
    by_raw_id = {n.get("id"): n for n in nodes}
    graph_nodes = graph.get("nodes", []) or []
    graph_by_id = {n.get("id"): n for n in graph_nodes}
    raw_ids = set(by_raw_id)
    content_ids = set(content)
    direct_ids = raw_ids & content_ids
    orphan_ids = content_ids - raw_ids
    unmatched_content = {k: content[k] for k in content if k in orphan_ids}
    node_types = Counter(n.get("type", "<missing>") for n in nodes)
    content_links = sum(len(entry.get("links") or []) if isinstance(entry, dict) and isinstance(entry.get("links"), list) else 0 for entry in content.values())
    questions_by_type = Counter(q.get("type", "<missing>") for q in questions)
    source_url = route.get("url") or raw.get("url") or f"https://roadmap.sh/{slug}"
    route_title = raw.get("title")
    if isinstance(route_title, dict):
        route_title = route_title.get("page") or route_title.get("card")
    route_title = route_title or route.get("title") or slug
    description = raw.get("description")
    related = raw.get("relatedRoadmaps", []) or []
    ai_courses = raw.get("aiCourses", []) or []
    fetched_at = graph.get("source", {}).get("fetched_at")

    overview: list[str] = [
        f"路线：{route_title}（{slug}）",
        f"来源：{source_url}",
        f"原始 JSON：references/raw/roadmap-ai/json/{slug}.json",
        f"图候选来源：references/raw/roadmap-ai/graph/{slug}.json",
        f"图快照时间：{fetched_at or '未知'}",
        "原始路线说明（逐字保留）：",
        description if isinstance(description, str) and description else ("原始 description JSON：" + json_line(description) if description is not None else "（原始 description 缺失）"),
        "相关路线（原始 relatedRoadmaps）：",
        json.dumps(related, ensure_ascii=False, indent=2) if related else "（无）",
        "原始 AI 课程题目（仅题目，不表示已取得课程正文）：",
    ]
    if isinstance(ai_courses, list) and ai_courses:
        overview.extend(f"{i}. {json_line(item)}" for i, item in enumerate(ai_courses, 1))
    else:
        overview.append("（无）")
    overview.append("原始图例（来自原始 legend 节点及其 data；只作来源标注）：")
    raw_legend_nodes = [n for n in nodes if n.get("type") == "legend"]
    if raw_legend_nodes:
        for legend_node in raw_legend_nodes:
            data = legend_node.get("data") if isinstance(legend_node.get("data"), dict) else {}
            overview.append("原始 legend data：" + json_line(data))
    else:
        overview.append("（原始 JSON 无 legend 节点）")
    overview.append("graph 候选图例（派生补充，未经人工审核）：")
    legends = graph.get("legend", []) or []
    if legends:
        for legend in legends:
            overview.append("- " + json_line(legend))
    else:
        overview.append("（无 graph legend 记录）")
    overview.extend([
        "问答部分：来自原始 questions；文本投影保留段落、列表和链接 URL。问答内容属于来源建议，不是强制要求或个人结论。原始富文本完整值见 review/questions.jsonl。",
        "FAQ 与主问题（按原数组顺序）：",
    ])
    if questions:
        for i, question in enumerate(questions, 1):
            overview.extend([f"问题记录 {i}：", render_question(question, slug, unsupported), ""])
    else:
        overview.append("（没有 questions）")
    (route_dir / "00_路线总览.txt").write_text("\n".join(overview) + "\n", encoding="utf-8")

    body: list[str] = [
        f"路线主题与原始节点正文：{route_title}（{slug}）",
        "以下按原始坐标 y/x 展示，不表示学习先后或先修关系。原始完整 node 对象另存 review/raw_nodes.jsonl。",
        "content 只按同路线原始 node_id 连接；标题相同不作为关联依据。没有匹配 content 的节点明确标记无正文。",
    ]
    display_nodes = sorted(nodes, key=point_key)
    rendered_count = 0
    review_only_count = 0
    for node in display_nodes:
        nid = node.get("id")
        ntype = node.get("type", "<missing>")
        entry = content.get(nid) if nid in direct_ids else None
        if not has_readable_payload(node, entry if isinstance(entry, dict) else None):
            review_only_count += 1
            continue
        rendered_count += 1
        data = node.get("data") if isinstance(node.get("data"), dict) else {}
        body.extend([
            "",
            f"===== 原始节点 {rendered_count} =====",
            f"节点 ID：{nid}",
            f"节点类型：{ntype}",
            f"来源路线：{source_url}",
            f"原始标签：{raw_label(node) if isinstance(raw_label(node), str) else clean_line(raw_label(node))}",
        ])
        if isinstance(entry, dict):
            body.append(f"content 标题（按 ID）：{clean_line(entry.get('title'))}")
            if isinstance(entry.get("desc"), str) and entry.get("desc").strip():
                body.append("content 原始描述（按 ID，未截断）：")
                body.append(entry["desc"])
            else:
                body.append("content 原始描述：无正文（来源数据缺失或为空）")
            body.extend(render_resource_links(entry.get("links")))
        else:
            body.append("content 原始描述：无正文（无同 ID content 记录；未按标题匹配）")
            body.extend(render_resource_links(None))
        # Show readable auxiliary fields for special/source metadata nodes;
        # full raw data and geometry stay in review/raw_nodes.jsonl.
        body.extend(render_node_auxiliary(node))
        if ntype == "section":
            body.append("节点说明：section 容器；坐标范围和潜在包含项仅为布局线索。")
    (route_dir / "01_主题正文.txt").write_text("\n".join(body).rstrip() + "\n", encoding="utf-8")

    edge_lines = [
        f"路线连接与原始边：{slug}",
        f"原始边数量：{len(edges)}。仅记录图中连接关系与显示样式，不将实线或虚线解释为严格先修、必须顺序或课程安排。",
        "端点 ID 即使指向 layout/label/section 等非正文节点也完整保留。缺失端点另在 manifest 计数。",
    ]
    endpoint_missing = 0
    for i, edge in enumerate(edges, 1):
        src, tgt = edge.get("source"), edge.get("target")
        src_node, tgt_node = by_raw_id.get(src), by_raw_id.get(tgt)
        src_label = raw_label(src_node) if src_node else None
        tgt_label = raw_label(tgt_node) if tgt_node else None
        if src_node is None or tgt_node is None:
            endpoint_missing += 1
        edge_lines.append(
            f"{i}. source ID={clean_line(src)}；source label={clean_line(src_label)}；"
            f"target ID={clean_line(tgt)}；target label={clean_line(tgt_label)}；{edge_style_text(edge)}；"
            f"原始 edge data={json_line(edge.get('data'))}"
        )
    (route_dir / "02_路线连接.txt").write_text("\n".join(edge_lines) + "\n", encoding="utf-8")

    candidate_lines = [
        f"派生候选层级：{slug}",
        f"候选 graph 节点数：{len(graph_nodes)}；此文件来自本地生成的 graph，parent/depth/order 均非官方原始字段，未经本轮人工审核。",
        "不能由候选层级推导先修、学习顺序、学时或岗位要求；原始坐标仅为布局信息。",
    ]
    graph_ids = set(graph_by_id)
    candidate_lines.append(f"与 raw nodes 比较：候选 graph 有但 raw 无的 ID={len(graph_ids-raw_ids)}；raw 有但 graph 未收录的 ID={len(raw_ids-graph_ids)}。")
    candidate_lines.append("候选节点列表按 graph order 排列，仅便于对照；每项列出 parent/depth/order/parent_rule 原值：")
    for gn in sorted(graph_nodes, key=lambda x: (x.get("order") if isinstance(x.get("order"), (int,float)) else 10**12, str(x.get("id")))):
        nid = gn.get("id")
        parent_id = gn.get("parent")
        flag = KNOWN_FLAGS.get((slug, nid))
        parent_flag = KNOWN_FLAGS.get((slug, parent_id)) if parent_id is not None else None
        notes = []
        if flag:
            notes.append("本节点标记=" + flag[0] + "；原因=" + flag[1])
        if parent_flag:
            notes.append("候选 parent 落在已知隔离节点；此路径需复核，不作事实")
        depth = gn.get("depth") if isinstance(gn.get("depth"), int) and gn.get("depth") >= 0 else 0
        candidate_lines.append(
            f"{'  ' * min(depth, 20)}{gn.get('label') or '（无标签）'}｜节点 ID={clean_line(nid)}；type={clean_line(gn.get('type'))}；"
            f"parent ID={clean_line(parent_id)}；parent label={clean_line(graph_by_id.get(parent_id, {}).get('label'))}；"
            f"depth={clean_line(gn.get('depth'))}；order={clean_line(gn.get('order'))}；"
            f"parent_rule={clean_line(gn.get('parent_rule'))}；候选备注={'；'.join(notes) if notes else '无已知隔离标记'}"
        )
    (route_dir / "03_候选层级.txt").write_text("\n".join(candidate_lines) + "\n", encoding="utf-8")

    unmatched_lines = [
        f"未匹配 content 正文：{slug}",
        f"共 {len(orphan_ids)} 条 content ID 在同路线 raw nodes 中找不到。保留原 ID、title、完整 desc 和全部 links；不按标题兜底。",
    ]
    for nid in sorted(orphan_ids):
        entry = content[nid]
        unmatched_lines.extend(["", "===== 未匹配 content 记录 =====", f"原 content ID：{nid}", f"来源路线：{source_url}", f"content 标题：{clean_line(entry.get('title'))}"])
        desc = entry.get("desc")
        unmatched_lines.append("content 原始描述（未截断）：")
        unmatched_lines.append(desc if isinstance(desc, str) and desc else "（无正文）")
        unmatched_lines.extend(render_resource_links(entry.get("links")))
    if not orphan_ids:
        unmatched_lines.append("（无未匹配 content 记录）")
    (route_dir / "04_未匹配正文.txt").write_text("\n".join(unmatched_lines).rstrip() + "\n", encoding="utf-8")

    return {
        "slug": slug,
        "route_title": route_title,
        "url": source_url,
        "source_fetched_at": fetched_at,
        "has_content_file": route_data["has_content_file"],
        "raw_node_count": len(nodes),
        "raw_node_types": dict(sorted(node_types.items())),
        "raw_edge_count": len(edges),
        "raw_edge_missing_endpoint_count": endpoint_missing,
        "content_entry_count": len(content),
        "content_direct_id_match_count": len(direct_ids),
        "content_orphan_id_count": len(orphan_ids),
        "raw_node_without_content_count": len(raw_ids - content_ids),
        "content_nonempty_desc_count": sum(1 for x in content.values() if isinstance(x, dict) and isinstance(x.get("desc"), str) and x.get("desc").strip()),
        "content_link_count": content_links,
        "question_count": len(questions),
        "question_types": dict(sorted(questions_by_type.items())),
        "ai_course_title_count": len(raw.get("aiCourses", []) or []) if isinstance(raw.get("aiCourses", []) or [], list) else 0,
        "graph_candidate_node_count": len(graph_nodes),
        "graph_ids_not_in_raw_count": len(graph_ids - raw_ids),
        "raw_ids_not_in_graph_count": len(raw_ids - graph_ids),
        "readable_node_count": rendered_count,
        "layout_only_review_node_count": review_only_count,
        "routes_files": [
            f"routes/{slug}/00_路线总览.txt", f"routes/{slug}/01_主题正文.txt",
            f"routes/{slug}/02_路线连接.txt", f"routes/{slug}/03_候选层级.txt",
            f"routes/{slug}/04_未匹配正文.txt",
        ],
    }


def build_package(output: Path) -> None:
    if output.exists() and any(output.iterdir()):
        raise PackageError(f"拒绝覆盖非空目录：{output}")
    index, routes = discover_and_load()
    source_hashes = input_file_hashes()
    output.mkdir(parents=True, exist_ok=True)
    (output / "routes").mkdir()
    (output / "review").mkdir()

    raw_node_records: list[dict[str, Any]] = []
    raw_edge_records: list[dict[str, Any]] = []
    content_records: list[dict[str, Any]] = []
    question_records: list[dict[str, Any]] = []
    graph_records: list[dict[str, Any]] = []
    unsupported: list[dict[str, Any]] = []
    all_raw_node_types: Counter[str] = Counter()
    all_edge_styles: Counter[str] = Counter()
    all_edge_types: Counter[str] = Counter()
    all_question_types: Counter[str] = Counter()
    missing_edge_endpoints: list[dict[str, Any]] = []
    orphan_total = 0
    raw_no_content_total = 0
    direct_total = 0
    raw_node_total = 0
    raw_edge_total = 0
    content_total = 0
    question_total = 0
    desc_nonempty_total = 0
    link_total = 0
    route_stats = []

    for route_data in routes:
        slug = safe_slug(route_data["index"])
        raw = route_data["raw"]
        graph = route_data["graph"]
        content = route_data["content"]
        for node in raw.get("nodes", []):
            raw_node_records.append({"route": slug, "raw": node})
            all_raw_node_types[node.get("type", "<missing>")] += 1
        for edge in raw.get("edges", []):
            raw_edge_records.append({"route": slug, "raw": edge})
            style = edge.get("style") if isinstance(edge.get("style"), dict) else {}
            all_edge_styles[str(style.get("strokeDasharray", "<missing>"))] += 1
            all_edge_types[str(edge.get("type", "<none>"))] += 1
            node_ids = {n.get("id") for n in raw.get("nodes", [])}
            missing = [endpoint for endpoint in (edge.get("source"), edge.get("target")) if endpoint not in node_ids]
            if missing:
                missing_edge_endpoints.append({
                    "route": slug,
                    "raw_edge": edge,
                    "missing_endpoint_ids": missing,
                    "note": "原始边原样保留；端点在同路线 raw nodes 中不存在，未修补或推测",
                })
        for node_id, entry in content.items():
            content_records.append({"route": slug, "node_id": node_id, "raw": entry})
            if isinstance(entry, dict):
                desc_nonempty_total += bool(isinstance(entry.get("desc"), str) and entry.get("desc").strip())
                link_total += len(entry.get("links") or []) if isinstance(entry.get("links"), list) else 0
        for q in raw.get("questions", []) or []:
            question_records.append({"route": slug, "raw": q})
            question_total += 1
            all_question_types[str(q.get("type", "<missing>"))] += 1
        for node in route_data["graph"].get("nodes", []) or []:
            graph_records.append({"route": slug, "raw": node})
        stats = make_route_files(route_data, output, unsupported)
        route_stats.append(stats)
        raw_node_total += stats["raw_node_count"]
        raw_edge_total += stats["raw_edge_count"]
        content_total += stats["content_entry_count"]
        direct_total += stats["content_direct_id_match_count"]
        orphan_total += stats["content_orphan_id_count"]
        raw_no_content_total += stats["raw_node_without_content_count"]

    write_jsonl(output / "review/raw_nodes.jsonl", raw_node_records)
    write_jsonl(output / "review/raw_edges.jsonl", raw_edge_records)
    write_jsonl(output / "review/content_records.jsonl", content_records)
    write_jsonl(output / "review/questions.jsonl", question_records)
    write_jsonl(output / "review/graph_candidate_nodes.jsonl", graph_records)
    route_metadata_records = [
        {"route": safe_slug(rd["index"]), "raw_metadata": {k: v for k, v in rd["raw"].items() if k not in {"nodes", "edges", "questions"}}}
        for rd in routes
    ]
    write_jsonl(output / "review/route_metadata.jsonl", route_metadata_records)
    write_jsonl(output / "review/unsupported_richtext.jsonl", unsupported)
    write_jsonl(output / "review/missing_edge_endpoints.jsonl", missing_edge_endpoints)

    index_lines = [
        "roadmap.sh 全路线本地整理索引",
        f"路线数：{len(route_stats)}。仅按索引列出；不表示学习顺序或主题完整审核。",
        "各路线文件均包含：路线总览、原始主题正文、原始连接、未人工审核的候选层级、未匹配 content。",
    ]
    for i, stats in enumerate(route_stats, 1):
        index_lines.append(
            f"{i}. {stats['route_title']}（{stats['slug']}）｜{stats['url']}｜"
            f"raw nodes {stats['raw_node_count']} / edges {stats['raw_edge_count']} / content {stats['content_entry_count']} / questions {stats['question_count']}｜"
            f"routes/{stats['slug']}/"
        )
    (output / "路线索引.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")

    readme = """# roadmap.sh 全路线本地整理包 v0.4

本包按本地快照整理 101 条路线的原始节点、连接、content 正文与 questions，提供可读文本和原始 JSONL 审计记录。本包是本地来源整理，不代表已人工逐项审核，也没有上传知识库或进行 M3/模型检索测试。

## 目录

- `路线索引.md`：索引中的全部路线及各路线记录数量。
- `routes/<slug>/00_路线总览.txt`：来源、快照、原始路线说明、相关路线、图例与全部 questions 文本投影。
- `routes/<slug>/01_主题正文.txt`：按原始坐标排序的节点文本、content 按同路线 ID 关联后的完整描述与全部资源链接。坐标仅作展示顺序，不代表先修或学习顺序。
- `routes/<slug>/02_路线连接.txt`：逐条保留原始边端点 ID、标签和显示样式；实线/虚线不被解释为严格先修。
- `routes/<slug>/03_候选层级.txt`：graph 推导的 parent/depth/order 与 parent_rule，未经人工审核，不作为事实。
- `routes/<slug>/04_未匹配正文.txt`：raw node 中不存在相同 ID 的 content 记录，保留原 ID、完整描述和全部链接；不按标题兜底。
- `review/`：原始 nodes、edges、content、questions、route metadata 和 graph candidate nodes 的 JSONL 记录；questions 原始富文本用于追溯。纯布局且无可读文字的节点仍完整保留在 `raw_nodes.jsonl`。
- `manifest.json`：输入哈希、输出哈希和路线/全局计数。

## 来源与边界

来源快照来自本地 `references/raw/roadmap-ai/`，原始文件哈希列于 manifest。来源许可尚未确认，resources 链接尚未逐条核实可用性；不得将全量包批量上传到知识库。无 content 文件的 5 条路线不补造正文；content ID 不匹配的记录单独保留。原始路线说明、节点建议、连接样式和派生候选层级是不同信息类型，不能混作普遍事实或学习要求。

FAQ/主问题的文本投影尽量保留段落、列表、换行与链接 URL；原始结构完整存于 `review/questions.jsonl`。若发现无法投影的富文本节点，会在文本中给出标记并记录到 `review/unsupported_richtext.jsonl`，不会静默丢弃。
"""
    (output / "README.md").write_text(readme, encoding="utf-8")

    global_stats = {
        "route_count": len(route_stats),
        "raw_node_count": raw_node_total,
        "raw_node_types": dict(sorted(all_raw_node_types.items())),
        "raw_edge_count": raw_edge_total,
        "raw_edge_missing_endpoint_count": len(missing_edge_endpoints),
        "raw_edge_style_strokeDasharray": dict(sorted(all_edge_styles.items())),
        "raw_edge_type": dict(sorted(all_edge_types.items())),
        "content_entry_count": content_total,
        "content_direct_id_match_count": direct_total,
        "content_unmatched_id_count": orphan_total,
        "raw_nodes_without_content_count": raw_no_content_total,
        "content_nonempty_desc_count": int(desc_nonempty_total),
        "content_resource_link_count": link_total,
        "question_count": question_total,
        "question_types": dict(sorted(all_question_types.items())),
        "ai_course_title_count": sum(len(rd["raw"].get("aiCourses", []) or []) if isinstance(rd["raw"].get("aiCourses", []) or [], list) else 0 for rd in routes),
        "graph_candidate_node_count": len(graph_records),
        "unsupported_richtext_record_count": len(unsupported),
    }
    manifest = {
        "package": "roadmap_full_v0.4",
        "status": {"local_only": True, "uploaded": False, "platform_parsing_tested": False, "model_retrieval_tested": False, "manual_full_reviewed": False, "source_license_confirmed": False},
        "source_root": "references/raw/roadmap-ai",
        "generated_from_index_at": index.get("generated_at"),
        "source_file_hashes": source_hashes,
        "set_differences": {
            "index_route_count": len(route_stats),
            "json_files": len({Path(p).stem for p in source_hashes if p.startswith("references/raw/roadmap-ai/json/")}),
            "json_extra_nonroute": ["_fetch_report"],
            "graph_route_count": len({Path(p).stem for p in source_hashes if p.startswith("references/raw/roadmap-ai/graph/")}),
            "content_route_count": len({Path(p).stem for p in source_hashes if p.startswith("references/raw/roadmap-ai/content/")}),
            "routes_without_content": sorted({x["slug"] for x in route_stats if not x["has_content_file"]}),
        },
        "global_counts": global_stats,
        "routes": route_stats,
        "output_hashes": {},
        "limitations": [
            "完整本地整理不等于人工全量审核。",
            "来源许可未确认，不能据此将整包批量上传。",
            "resource links 未逐条核实可用性。",
            "graph parent/depth/order 是派生候选层级，不是官方原始关系或先修事实。",
            "文本投影之外的 questions 原始富文本保存在 review/questions.jsonl；unsupported 类型另有记录。",
        ],
    }
    write_json(output / "manifest.json", manifest)
    output_hashes: dict[str, dict[str, Any]] = {}
    for path in sorted(output.rglob("*")):
        if path.is_file() and path.name != "manifest.json":
            raw = path.read_bytes()
            output_hashes[str(path.relative_to(output))] = {"sha256": sha(raw), "bytes": len(raw), "characters": len(raw.decode("utf-8")) if path.suffix in {".txt", ".md", ".jsonl"} else None}
    manifest["output_hashes"] = output_hashes
    write_json(output / "manifest.json", manifest)
    print(f"已生成本地全量包：{output}")
    print(f"路线 {len(route_stats)} / raw nodes {raw_node_total} / edges {raw_edge_total} / content {content_total} / questions {question_total}")
    print(f"未匹配 content {orphan_total} / 富文本未支持类型 {len(unsupported)} / 输出文件 {len(output_hashes)}")


def verify_package(output: Path) -> None:
    if not output.is_dir():
        raise PackageError(f"输出目录不存在：{output}")
    index, routes = discover_and_load()
    manifest = read_json(output / "manifest.json")
    expected_sources = input_file_hashes()
    if manifest.get("source_file_hashes") != expected_sources:
        raise PackageError("源文件哈希已变化或 manifest 输入记录不一致")
    expected_routes = [safe_slug(r["index"]) for r in routes]
    route_dirs = sorted(p.name for p in (output / "routes").iterdir() if p.is_dir())
    if route_dirs != sorted(expected_routes):
        raise PackageError(f"路线目录集合不匹配：expected={len(expected_routes)}, actual={len(route_dirs)}")
    # Independently derive core record counts and ID sets from source and JSONL.
    raw_node_ids = {(safe_slug(rd["index"]), n.get("id")) for rd in routes for n in rd["raw"].get("nodes", [])}
    content_ids = {(safe_slug(rd["index"]), nid) for rd in routes for nid in rd["content"]}
    raw_node_lines = (output / "review/raw_nodes.jsonl").read_text(encoding="utf-8").splitlines()
    raw_edge_lines = (output / "review/raw_edges.jsonl").read_text(encoding="utf-8").splitlines()
    content_lines = (output / "review/content_records.jsonl").read_text(encoding="utf-8").splitlines()
    question_lines = (output / "review/questions.jsonl").read_text(encoding="utf-8").splitlines()
    graph_lines = (output / "review/graph_candidate_nodes.jsonl").read_text(encoding="utf-8").splitlines()
    if len(raw_node_lines) != len(raw_node_ids):
        raise PackageError("raw_nodes JSONL 行数与原始唯一 ID 集不匹配")
    if len(raw_edge_lines) != sum(len(rd["raw"].get("edges", [])) for rd in routes):
        raise PackageError("raw_edges JSONL 行数与原始边数不匹配")
    if len(content_lines) != len(content_ids):
        raise PackageError("content_records JSONL 行数与源 content ID 集不匹配")
    if len(question_lines) != sum(len(rd["raw"].get("questions", []) or []) for rd in routes):
        raise PackageError("questions JSONL 行数与原始 questions 数量不匹配")
    if len(graph_lines) != sum(len(rd["graph"].get("nodes", []) or []) for rd in routes):
        raise PackageError("graph candidate JSONL 行数与 graph 节点数不匹配")
    # Exact semantic record comparison: all raw original objects must be present.
    def jsonl_records(path: Path) -> list[dict[str, Any]]:
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    if jsonl_records(output / "review/raw_nodes.jsonl") != [{"route": safe_slug(rd["index"]), "raw": n} for rd in routes for n in rd["raw"].get("nodes", [])]:
        raise PackageError("raw_nodes JSONL 与源对象存在差异")
    if jsonl_records(output / "review/raw_edges.jsonl") != [{"route": safe_slug(rd["index"]), "raw": e} for rd in routes for e in rd["raw"].get("edges", [])]:
        raise PackageError("raw_edges JSONL 与源对象存在差异")
    if jsonl_records(output / "review/content_records.jsonl") != [{"route": safe_slug(rd["index"]), "node_id": nid, "raw": entry} for rd in routes for nid, entry in rd["content"].items()]:
        raise PackageError("content_records JSONL 与源对象存在差异")
    if jsonl_records(output / "review/questions.jsonl") != [{"route": safe_slug(rd["index"]), "raw": q} for rd in routes for q in rd["raw"].get("questions", []) or []]:
        raise PackageError("questions JSONL 与源对象存在差异")
    if jsonl_records(output / "review/graph_candidate_nodes.jsonl") != [{"route": safe_slug(rd["index"]), "raw": n} for rd in routes for n in rd["graph"].get("nodes", []) or []]:
        raise PackageError("graph candidate JSONL 与源对象存在差异")
    expected_metadata = [
        {"route": safe_slug(rd["index"]), "raw_metadata": {k: v for k, v in rd["raw"].items() if k not in {"nodes", "edges", "questions"}}}
        for rd in routes
    ]
    if jsonl_records(output / "review/route_metadata.jsonl") != expected_metadata:
        raise PackageError("route metadata JSONL 与源对象顶层字段不一致")
    expected_missing_edges = []
    for rd in routes:
        slug = safe_slug(rd["index"])
        node_ids = {n.get("id") for n in rd["raw"].get("nodes", [])}
        for edge in rd["raw"].get("edges", []):
            missing = [endpoint for endpoint in (edge.get("source"), edge.get("target")) if endpoint not in node_ids]
            if missing:
                expected_missing_edges.append({"route": slug, "raw_edge": edge, "missing_endpoint_ids": missing, "note": "原始边原样保留；端点在同路线 raw nodes 中不存在，未修补或推测"})
    if jsonl_records(output / "review/missing_edge_endpoints.jsonl") != expected_missing_edges:
        raise PackageError("缺失边端点 review 与源数据不一致")
    # Verify human-readable route records against source data and recompute output digests.
    for rd in routes:
        slug = safe_slug(rd["index"])
        d = output / "routes" / slug
        files = [d / f"{name}" for name in ("00_路线总览.txt", "01_主题正文.txt", "02_路线连接.txt", "03_候选层级.txt", "04_未匹配正文.txt")]
        if any(not f.is_file() for f in files):
            raise PackageError(f"{slug} 缺少路线文本文件")
        body = files[1].read_text(encoding="utf-8")
        # Every non-layout raw node with readable content must appear in display text.
        content = rd["content"]
        raw_nodes = rd["raw"].get("nodes", [])
        readable_ids = {n.get("id") for n in raw_nodes if has_readable_payload(n, content.get(n.get("id")))}
        missing_ids = [nid for nid in readable_ids if f"节点 ID：{nid}\n" not in body]
        if missing_ids:
            raise PackageError(f"{slug} 01正文缺少 {len(missing_ids)} 个应展示节点 ID")
        node_blocks = readable_node_blocks(body)
        for nid in readable_ids:
            entry = content.get(nid)
            if not isinstance(entry, dict):
                continue
            block = node_blocks.get(nid, "")
            desc = entry.get("desc")
            if isinstance(desc, str) and desc.strip() and desc not in block:
                raise PackageError(f"{slug}/{nid} 01正文缺少完整 content desc")
            for link in entry.get("links", []) if isinstance(entry.get("links"), list) else []:
                if isinstance(link, (list, tuple)) and len(link) >= 3:
                    for value in link[:3]:
                        rendered_value = clean_line(value)
                        if rendered_value not in block:
                            raise PackageError(f"{slug}/{nid} 01正文缺少完整资源字段：{rendered_value}")
                elif json_line(link) not in block:
                    raise PackageError(f"{slug}/{nid} 01正文缺少原始资源记录")
        if len(rd["raw"].get("edges", [])) and len(files[2].read_text(encoding="utf-8").splitlines()) < len(rd["raw"].get("edges", [])) + 3:
            raise PackageError(f"{slug} 路线连接行数不足")
        orphan_path = files[4].read_text(encoding="utf-8")
        orphan_blocks = unmatched_content_blocks(orphan_path)
        for nid in content:
            if (slug, nid) not in raw_node_ids:
                block = orphan_blocks.get(nid, "")
                if not block:
                    raise PackageError(f"{slug} 未匹配正文遗漏 ID：{nid}")
                entry = content[nid]
                desc = entry.get("desc") if isinstance(entry, dict) else None
                if isinstance(desc, str) and desc.strip() and desc not in block:
                    raise PackageError(f"{slug}/{nid} 04未匹配正文缺少完整 desc")
                for link in entry.get("links", []) if isinstance(entry, dict) and isinstance(entry.get("links"), list) else []:
                    if isinstance(link, (list, tuple)) and len(link) >= 3:
                        if any(clean_line(value) not in block for value in link[:3]):
                            raise PackageError(f"{slug}/{nid} 04未匹配正文缺少资源 title/URL")
                    elif json_line(link) not in block:
                        raise PackageError(f"{slug}/{nid} 04未匹配正文缺少原始资源记录")
        questions_view = files[0].read_text(encoding="utf-8")
        ai_courses = rd["raw"].get("aiCourses", []) or []
        for course in ai_courses if isinstance(ai_courses, list) else []:
            if clean_line(course) not in questions_view:
                raise PackageError(f"{slug} 总览遗漏原始 aiCourses 题目：{course}")
        for q in rd["raw"].get("questions", []) or []:
            if q.get("title") is not None and clean_line(q.get("title")) not in questions_view:
                raise PackageError(f"{slug} 总览遗漏 question 标题：{q.get('title')}")
            text_tokens, hrefs = rich_text_tokens(q.get("description"))
            for token in text_tokens:
                if token and token not in questions_view:
                    raise PackageError(f"{slug} 总览遗漏 question 文本叶子：{token[:80]}")
            for href in hrefs:
                if href not in questions_view:
                    raise PackageError(f"{slug} 总览遗漏 question 链接 URL：{href}")
    actual_hashes = {}
    for path in sorted(output.rglob("*")):
        if path.is_file() and path.name != "manifest.json":
            data = path.read_bytes()
            actual_hashes[str(path.relative_to(output))] = {"sha256": sha(data), "bytes": len(data), "characters": len(data.decode("utf-8")) if path.suffix in {".txt", ".md", ".jsonl"} else None}
    if actual_hashes != manifest.get("output_hashes"):
        raise PackageError("输出文件集合或哈希与 manifest 不一致")
    counts = manifest.get("global_counts", {})
    if counts.get("raw_node_count") != len(raw_node_ids) or counts.get("raw_edge_count") != len(raw_edge_lines) or counts.get("content_entry_count") != len(content_ids):
        raise PackageError("manifest 全局源计数与实际数据不一致")
    if counts.get("raw_edge_missing_endpoint_count") != len(expected_missing_edges):
        raise PackageError("manifest 缺失边端点计数与实际数据不一致")
    if counts.get("content_unmatched_id_count") != len(content_ids - raw_node_ids):
        raise PackageError("manifest 全局 content orphan 计数与实际 ID 集不一致")
    if counts.get("content_direct_id_match_count") != len(content_ids & raw_node_ids):
        raise PackageError("manifest 全局 content 直接 ID 匹配计数与实际 ID 集不一致")
    route_manifest = {x.get("slug"): x for x in manifest.get("routes", [])}
    if set(route_manifest) != set(expected_routes):
        raise PackageError("manifest route 计数记录与索引 route 集不一致")
    for rd in routes:
        slug = safe_slug(rd["index"])
        raw = rd["raw"]
        graph = rd["graph"]
        content = rd["content"]
        stat = route_manifest[slug]
        raw_ids = {n.get("id") for n in raw.get("nodes", [])}
        route_content_ids = set(content)
        route_questions = raw.get("questions", []) or []
        expected_counts = {
            "raw_node_count": len(raw.get("nodes", [])),
            "raw_node_types": dict(sorted(Counter(n.get("type", "<missing>") for n in raw.get("nodes", [])).items())),
            "raw_edge_count": len(raw.get("edges", [])),
            "content_entry_count": len(content),
            "content_direct_id_match_count": len(raw_ids & route_content_ids),
            "content_orphan_id_count": len(route_content_ids - raw_ids),
            "raw_node_without_content_count": len(raw_ids - route_content_ids),
            "content_nonempty_desc_count": sum(1 for x in content.values() if isinstance(x, dict) and isinstance(x.get("desc"), str) and x.get("desc").strip()),
            "content_link_count": sum(len(x.get("links") or []) if isinstance(x, dict) and isinstance(x.get("links"), list) else 0 for x in content.values()),
            "question_count": len(route_questions),
            "question_types": dict(sorted(Counter(str(q.get("type", "<missing>")) for q in route_questions).items())),
            "ai_course_title_count": len(raw.get("aiCourses", []) or []) if isinstance(raw.get("aiCourses", []) or [], list) else 0,
            "graph_candidate_node_count": len(graph.get("nodes", []) or []),
            "has_content_file": rd["has_content_file"],
        }
        for key, expected_value in expected_counts.items():
            if stat.get(key) != expected_value:
                raise PackageError(f"manifest {slug}.{key} 与源数据重算结果不一致")
    print(f"verify 通过：routes={len(expected_routes)}, raw_nodes={len(raw_node_ids)}, raw_edges={len(raw_edge_lines)}, content={len(content_ids)}, questions={len(question_lines)}")
    print(f"输入哈希 {len(expected_sources)} 项一致；输出校验 {len(actual_hashes)} 个文件；未匹配正文 {len(content_ids-raw_node_ids)} 条")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="输出目录；默认 local_data/roadmap_full_v0.4")
    parser.add_argument("--verify", action="store_true", help="只读复核源哈希、原始记录和生成文件")
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    try:
        if args.verify:
            verify_package(output)
        else:
            build_package(output)
    except (OSError, ValueError, KeyError, TypeError, PackageError) as exc:
        print(f"停止：{exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
