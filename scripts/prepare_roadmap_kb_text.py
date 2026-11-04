#!/usr/bin/env python3
"""Build and verify a small plain-text roadmap knowledge package.

The script only transforms the twenty reviewed short summaries from
roadmap_m3_topic_pilot_v0.2. It does not copy source resource lists or long
descriptions into uploadable text files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "references/raw/roadmap-ai"
PILOT = ROOT / "local_data/roadmap_m3_topic_pilot_v0.2"
PILOT_V01_REVIEW = ROOT / "local_data/roadmap_m3_topic_pilot_v0.1/review/selection_and_checks.json"
DEFAULT_OUTPUT = ROOT / "local_data/roadmap_kb_text_v0.3"
ROUTES = {
    "frontend": ("前端", "Frontend Developer", "https://roadmap.sh/frontend"),
    "backend": ("后端", "Backend Developer", "https://roadmap.sh/backend"),
    "python": ("Python", "Python Developer", "https://roadmap.sh/python"),
}
BOUNDARY = "主题范围参考，不构成岗位标准、固定顺序、学时承诺或个性化方案。"
PROVENANCE = "依据节点描述的中文短摘要"
RESOURCE_LINK_RE = re.compile(
    r"https?://|www\.|youtube|udemy|coursera|教程|课程资源|learning resource", re.I
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def verify_source_hashes() -> tuple[dict[str, str], dict[str, str], dict[str, Any], dict[str, Any]]:
    old_manifest = load_json(PILOT / "manifest.json")
    review = load_json(PILOT / "review/candidate_review.json")
    expected = old_manifest.get("source_snapshot", {})
    input_hashes: dict[str, str] = {}
    raw_hashes: dict[str, str] = {}
    for path in (PILOT / "manifest.json", PILOT / "review/candidate_review.json", PILOT_V01_REVIEW):
        input_hashes[str(path.relative_to(ROOT))] = sha256_file(path)
    for route in ROUTES:
        if route not in expected:
            raise ValueError(f"旧 manifest 缺少路线 {route}，停止生成")
        for group in ("content", "graph", "json"):
            path = SOURCE_ROOT / group / f"{route}.json"
            digest = sha256_file(path)
            old_digest = expected[route].get("raw_sha256", {}).get(group)
            review_digest = review.get("source_snapshot", {}).get(route, {}).get("raw_sha256", {}).get(group)
            if not old_digest or digest != old_digest or review_digest != old_digest:
                raise ValueError(f"源文件哈希与已审核 manifest/review 不一致：{path.relative_to(ROOT)}")
            rel_path = str(path.relative_to(ROOT))
            input_hashes[rel_path] = digest
            raw_hashes[rel_path] = digest
        summary_path = PILOT / "content" / f"roadmap_{route}_topics_v0.2.md"
        summary_text = summary_path.read_text(encoding="utf-8")
        input_hashes[str(summary_path.relative_to(ROOT))] = sha256_file(summary_path)
        for item in review.get("selected_nodes", []):
            if item.get("route") != route:
                continue
            matching_blocks = []
            for block in re.split(r"(?m)^## ", summary_text)[1:]:
                lines = block.splitlines()
                node_match = re.search(r"(?m)^- node_id：`?([^`\n]+)`?$", block)
                if node_match and node_match.group(1) == item.get("node_id"):
                    first_paragraph = next((line.strip() for line in lines[1:] if line.strip() and not line.startswith("- ")), "")
                    matching_blocks.append((lines[0].strip(), first_paragraph))
            if (len(matching_blocks) != 1 or matching_blocks[0][0] != item.get("chinese_title")
                    or matching_blocks[0][1] != item.get("summary")):
                raise ValueError(f"v0.2 正文摘要/ID 与已审核 review 不一致：{route}/{item.get('node_id')}")
    return input_hashes, raw_hashes, old_manifest, review


def validate_candidates(review: dict[str, Any]) -> list[dict[str, Any]]:
    candidates = review.get("selected_nodes")
    if not isinstance(candidates, list) or len(candidates) != 20:
        raise ValueError("已审核清单不是 20 条，停止生成")
    counts = {route: 0 for route in ROUTES}
    excluded = load_json(PILOT_V01_REVIEW)
    quarantine = {
        (item.get("roadmap"), item.get("node_id"))
        for key in ("excluded_ambiguous_nodes", "excluded_quarantined_nodes")
        for item in excluded.get(key, [])
    }
    output: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    for item in candidates:
        route = item.get("route")
        node_id = item.get("node_id")
        if route not in ROUTES or not node_id:
            raise ValueError(f"路线或 node_id 缺失：{item!r}")
        key = (route, node_id)
        if key in seen or key in quarantine:
            raise ValueError(f"重复、歧义或隔离节点：{route}/{node_id}")
        seen.add(key)
        if item.get("status") != "selected" or not item.get("selection_reason"):
            raise ValueError(f"节点未被明确选入或缺少理由：{route}/{node_id}")
        graph = load_json(SOURCE_ROOT / "graph" / f"{route}.json")
        content = load_json(SOURCE_ROOT / "content" / f"{route}.json")
        raw_json = load_json(SOURCE_ROOT / "json" / f"{route}.json")
        graph_matches = [n for n in graph.get("nodes", []) if n.get("id") == node_id]
        if len(graph_matches) != 1:
            raise ValueError(f"graph 中 node_id 不唯一或不存在：{route}/{node_id}")
        graph_node = graph_matches[0]
        content_node = content.get(node_id)
        if not isinstance(content_node, dict):
            raise ValueError(f"content 未找到 node_id：{route}/{node_id}")
        if not any(n.get("id") == node_id for n in raw_json.get("nodes", [])):
            raise ValueError(f"原始 roadmap JSON 未找到 node_id：{route}/{node_id}")
        if graph_node.get("type") not in {"topic", "subtopic"}:
            raise ValueError(f"节点类型不是 topic/subtopic：{route}/{node_id}")
        if graph_node.get("label") != item.get("graph_label"):
            raise ValueError(f"graph label 与审核清单不一致：{route}/{node_id}")
        if content_node.get("title") != item.get("content_title"):
            raise ValueError(f"content title 与审核清单不一致：{route}/{node_id}")
        if content_node.get("desc") != item.get("description_evidence"):
            raise ValueError(f"原始描述与审核证据不一致：{route}/{node_id}")
        if not item.get("summary", "").strip():
            raise ValueError(f"缺少已核对短摘要：{route}/{node_id}")
        if item.get("ambiguity_quarantine_check") != "未出现在 v0.1 review 的歧义及隔离名单中":
            raise ValueError(f"缺少非歧义/未隔离核对：{route}/{node_id}")
        graph_url = graph.get("url")
        graph_date = graph.get("source", {}).get("fetched_at")
        route_title, _, route_url = ROUTES[route]
        if graph_url != route_url or graph_date != review["source_snapshot"][route]["graph_fetched_at"]:
            raise ValueError(f"路线 URL 或图快照时间不匹配：{route}")
        if item.get("source_url") != route_url:
            raise ValueError(f"审核清单来源 URL 不匹配：{route}/{node_id}")
        if item.get("content_id_title_and_desc_match") is not True:
            raise ValueError(f"候选清单未确认内容 ID/title/desc 对应：{route}/{node_id}")

        item = dict(item)
        item["route_title_zh"] = route_title
        item["graph_fetched_at_verified"] = graph_date
        output.append(item)
        counts[route] += 1
    if counts != {"frontend": 7, "backend": 6, "python": 7}:
        raise ValueError(f"路线数量不符合已审核 7/6/7：{counts}")
    return output


def render_text(item: dict[str, Any]) -> str:
    route = item["route"]
    route_zh, _, route_url = ROUTES[route]
    graph_date = item["graph_fetched_at_verified"][:10]
    return (
        f"主题：{item['chinese_title']}（{item['source_title']}）\n"
        f"所属路线：{route_zh}（{route}）\n"
        f"主题说明：{item['summary'].strip()}\n"
        f"来源：{route_url}\n"
        f"原始节点标识：{item['node_id']}\n"
        f"图快照：{graph_date}\n"
        "描述版本：未知\n"
        f"整理性质：{PROVENANCE}\n"
        f"使用边界：{BOUNDARY}\n"
    )


def validate_text_files(output: Path, expected: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    manifest = load_json(output / "manifest.json")
    files = manifest.get("outputs", [])
    if len(files) != 20:
        raise ValueError(f"manifest 输出文件数应为 20，实际 {len(files)}")
    file_paths = [output / entry["path"] for entry in files]
    if len(set(file_paths)) != 20 or any(not path.is_file() for path in file_paths):
        raise ValueError("输出文件路径重复或文件缺失")
    route_counts = {route: 0 for route in ROUTES}
    verified: list[dict[str, Any]] = []
    expected_by_id = {(x["route"], x["node_id"]): x for x in expected or []}
    for entry, path in zip(files, file_paths):
        raw = path.read_bytes()
        text = raw.decode("utf-8")
        if sha256_bytes(raw) != entry.get("sha256") or len(raw) != entry.get("bytes") or len(text) != entry.get("characters"):
            raise ValueError(f"文件 hash/字节/字符计数不一致：{path.name}")
        if re.search(r"\|.*\|", text) or re.search(r"(?m)^\s*\|", text) or "```" in text or "<" in text or ">" in text:
            raise ValueError(f"发现表格、代码围栏或 HTML 形态内容：{path.name}")
        without_source = re.sub(r"(?m)^来源：https://roadmap\.sh/[a-z-]+\n", "", text)
        if RESOURCE_LINK_RE.search(without_source):
            raise ValueError(f"发现资源列表/额外 URL 文本：{path.name}")
        match = re.search(r"(?m)^所属路线：([^（]+)（([a-z-]+)）$", text)
        id_match = re.search(r"(?m)^原始节点标识：([A-Za-z0-9_-]+)$", text)
        summary_match = re.search(r"(?m)^主题说明：(.+)$", text)
        route = next((r for r, (zh, _, _) in ROUTES.items() if match and match.group(1) == zh and match.group(2) == r), None)
        if not route or not id_match or not summary_match:
            raise ValueError(f"字段不完整或路线无法识别：{path.name}")
        route_counts[route] += 1
        source_url = ROUTES[route][2]
        if f"来源：{source_url}\n" not in text:
            raise ValueError(f"来源 URL 不匹配：{path.name}")
        source_title = re.search(r"(?m)^主题：.+（(.+)）$", text)
        if not source_title:
            raise ValueError(f"原始标题字段缺失：{path.name}")
        key = (route, id_match.group(1))
        if expected is not None:
            item = expected_by_id.get(key)
            if item is None or summary_match.group(1) != item["summary"] or source_title.group(1) != item["source_title"]:
                raise ValueError(f"导出文件与已审摘要/ID不匹配：{path.name}")
        verified.append({"path": str(path.relative_to(output)), "route": route, "node_id": id_match.group(1)})
    if route_counts != {"frontend": 7, "backend": 6, "python": 7}:
        raise ValueError(f"文件路线数量不符合 7/6/7：{route_counts}")
    readme = (output / "README.md").read_text(encoding="utf-8")
    for phrase in ("许可尚未确认", "尚未上传", "尚未验证平台解析", "20 个独立 UTF-8 文本文件", "data/knowledge_seed/roadmap_v0.2"):
        if phrase not in readme:
            raise ValueError(f"README 缺少边界说明：{phrase}")
    return verified


def generate(output: Path) -> None:
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"拒绝覆盖非空输出目录：{output}")
    input_hashes, raw_hashes, old_manifest, candidate_review = verify_source_hashes()
    candidates = validate_candidates(candidate_review)
    output.mkdir(parents=True, exist_ok=True)
    (output / "content").mkdir()
    (output / "review").mkdir()

    file_entries = []
    evidence_entries = []
    for index, item in enumerate(candidates, 1):
        route_zh = ROUTES[item["route"]][0]
        title = re.sub(r"[^\w\u4e00-\u9fff-]", "", item["chinese_title"]).replace(" ", "")
        filename = f"{route_zh}_{index:02d}_{title}.txt"
        path = output / "content" / filename
        text = render_text(item)
        data = text.encode("utf-8")
        path.write_bytes(data)
        file_entries.append({
            "path": f"content/{filename}",
            "route": item["route"],
            "node_id": item["node_id"],
            "sha256": sha256_bytes(data),
            "bytes": len(data),
            "characters": len(text),
            "han_characters": sum("\u4e00" <= ch <= "\u9fff" for ch in text),
        })
        evidence_entries.append({
            "route": item["route"],
            "node_id": item["node_id"],
            "source_title": item["source_title"],
            "graph_label": item["graph_label"],
            "content_title": item["content_title"],
            "description_evidence": item["description_evidence"],
            "summary": item["summary"],
            "selection_reason": item["selection_reason"],
            "source_url": item["source_url"],
            "graph_snapshot": item["graph_fetched_at_verified"],
            "node_type": item["node_type"],
            "id_description_match_verified": True,
            "ambiguity_quarantine": item["ambiguity_quarantine_check"],
            "output_path": f"content/{filename}",
        })

    review_path = output / "review/evidence.json"
    review_doc = {
        "package": "roadmap_kb_text_v0.3",
        "purpose": "20条已审核短摘要的来源匹配证据与范围说明；该文件不上传知识库",
        "input_package": "local_data/roadmap_m3_topic_pilot_v0.2",
        "input_hashes": input_hashes,
        "raw_source_hashes": raw_hashes,
        "selected_counts": {"frontend": 7, "backend": 6, "python": 7, "total": 20},
        "selection_basis": "沿用已审核的 v0.2 20 条主题（7/6/7），按既有 selection_reason 编入扁平文本；未以标题扩展说明。",
        "items": evidence_entries,
        "not_selected": candidate_review.get("reviewed_not_selected", []),
        "known_exclusions": load_json(PILOT_V01_REVIEW).get("excluded_ambiguous_nodes", [])
        + load_json(PILOT_V01_REVIEW).get("excluded_quarantined_nodes", []),
        "scope_gaps": [
            "仅含已审核的 20 条主题说明性小样，不覆盖三条路线全部主题。",
            "本包不补齐后端完整技术栈；data/knowledge_seed/roadmap_v0.2 是不同的 97 份主题索引材料。",
            "未纳入其他未选主题；未带入节点资源链接、教程列表、长描述、parent/depth/order 或先修推断。",
        ],
        "limitations": ["来源许可未确认。", "未上传云端，未验证解析效果或模型检索效果。"],
    }
    dump_json(review_path, review_doc)

    readme = """# Roadmap 主题文本小样 v0.3

`content/` 下有 20 个独立 UTF-8 文本文件（前端 7、后端 6、Python 7）。每个文件仅含一个已审核主题的短摘要、来源路线 URL、原始节点 ID 与范围边界。

本包是三条路线的少量主题说明性小样，不是全站内容，也不代表三路线完整主题覆盖；不补齐后端全部技术栈。它不同于 `data/knowledge_seed/roadmap_v0.2` 中的 97 份主题索引材料。

文件名中的数字仅作文件管理定位，不表示学习顺序。README、review 与 manifest 仅供本地说明和核验，不上传知识库。

内容来自路线节点描述整理，来源许可尚未确认。尚未上传知识库，尚未验证平台解析或检索效果。若后续试验，仅上传 `content/` 中的 20 个 `.txt`；不要上传 `review/` 或 `manifest.json`。

`review/` 保存来源匹配和选入理由核对证据，仅供本地审核。`manifest.json` 记录输入与输出哈希、文件计数及验证状态。
"""
    (output / "README.md").write_text(readme, encoding="utf-8")

    manifest = {
        "package": "roadmap_kb_text_v0.3",
        "status": {"not_uploaded": True, "not_tested": True},
        "created_at": "2026-11-04",
        "input_package": "local_data/roadmap_m3_topic_pilot_v0.2",
        "input_hashes": input_hashes,
        "raw_source_hashes": raw_hashes,
        "selection_counts": {"total": 20, "by_route": {"frontend": 7, "backend": 6, "python": 7}},
        "outputs": file_entries,
        "review": {"path": "review/evidence.json", "sha256": sha256_file(review_path), "bytes": review_path.stat().st_size},
        "readme": {"path": "README.md", "sha256": sha256_file(output / "README.md"), "bytes": (output / "README.md").stat().st_size},
        "limitations": ["许可未确认", "未上传", "尚未验证平台解析", "非全站、非三路线完整主题覆盖"],
    }
    dump_json(output / "manifest.json", manifest)
    validate_text_files(output, candidates)
    print(f"生成并验证完成：{output}")
    print("文本文件：20（frontend 7 / backend 6 / python 7）")


def verify(output: Path) -> None:
    input_hashes, raw_hashes, _, candidate_review = verify_source_hashes()
    if not output.is_dir():
        raise FileNotFoundError(f"输出目录不存在：{output}")
    manifest = load_json(output / "manifest.json")
    if manifest.get("input_hashes") != input_hashes or manifest.get("raw_source_hashes") != raw_hashes:
        raise ValueError("当前原始来源哈希与包 manifest 不一致")
    candidates = validate_candidates(candidate_review)
    verified = validate_text_files(output, candidates)
    review_info = manifest.get("review", {})
    review_path = output / review_info.get("path", "")
    readme_info = manifest.get("readme", {})
    readme_path = output / readme_info.get("path", "")
    for path, expected_hash in ((review_path, review_info.get("sha256")), (readme_path, readme_info.get("sha256"))):
        if not path.is_file() or sha256_file(path) != expected_hash:
            raise ValueError(f"README 或 review 哈希不匹配：{path}")
    print(f"只读验证通过：{output}")
    print(f"核对文件：{len(verified)}；路线计数：frontend 7 / backend 6 / python 7")
    print(f"输入文件哈希匹配：{len(input_hashes)} 项（原始来源 {len(raw_hashes)} 项）；状态 not_uploaded/not_tested")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="输出目录；默认 local_data/roadmap_kb_text_v0.3")
    parser.add_argument("--verify", action="store_true", help="只读验证已生成的包和来源哈希")
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    try:
        if args.verify:
            verify(output)
        else:
            generate(output)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"停止：{exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
