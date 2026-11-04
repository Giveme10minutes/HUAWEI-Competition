#!/usr/bin/env python3
"""Create a local AgentArts workflow JSONL with one detached multi-query test node."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "local_data/workflow_backups/职业探索_协作流程_v01_20261104161152.jsonl"
DEFAULT_OUTPUT = ROOT / "local_data/multiquery_pilot_v0.1/workflow_multiquery_node_test.jsonl"
NODE_ID = "node_multiquery_pilot_v01"
NODE_NAME = "多查询扩展试验"
SOURCE_NODE_NAME = "检索关键词提取"

SYSTEM_PROMPT = """你负责为知识库生成3条互补检索查询。只输出3行查询，不编号、不解释、不回答。第一条贴近用户实际问题；第二条使用用户明确提及领域的相关技术术语；第三条换一个相关学习主题角度。只能围绕本轮明确问题扩展，不添加用户能力、公司、招聘条件或确定结论。学习问题检索主题与概念，不强改成岗位职责；不把来源、适用范围、建议等栏目拼入。保留明确技术名；个人年级和时间预算不入查询。各行独立简短，可为中文自然句。"""


def read_jsonl(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    raw_lines = path.read_text(encoding="utf-8").splitlines()
    records = [json.loads(line) for line in raw_lines if line.strip()]
    if len(records) != 4 or len(records) != len(raw_lines):
        raise ValueError(f"Expected exactly 4 non-empty JSONL records; found {len(records)}")
    return records, raw_lines


def walk_ref_node_ids(value: Any):
    if isinstance(value, dict):
        ref_id = value.get("ref_node_id")
        if ref_id is not None:
            yield ref_id
        for child in value.values():
            yield from walk_ref_node_ids(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_ref_node_ids(child)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(source: Path, output: Path) -> dict[str, Any]:
    source = source.resolve()
    output = output.resolve()
    if source == output:
        raise ValueError("Output must not overwrite the source backup")
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite existing output: {output}")

    records, _ = read_jsonl(source)
    workflow_rows = [row for row in records if row.get("resource_type") == "workflow"]
    if len(workflow_rows) != 1:
        raise ValueError(f"Expected one workflow resource; found {len(workflow_rows)}")
    workflow = workflow_rows[0]
    if workflow.get("resource_name") != "职业探索_协作流程_v01":
        raise ValueError("Source workflow name does not match the approved baseline")
    if workflow.get("resource_id") != "d747fc58-2a2e-45bc-b95a-1e943f53c58a":
        raise ValueError("Source workflow ID does not match the approved baseline")

    dsl = workflow.get("dsl")
    if not isinstance(dsl, dict):
        raise ValueError("Workflow is missing a DSL object")
    original_nodes = copy.deepcopy(dsl.get("nodes"))
    original_edges = copy.deepcopy(dsl.get("edges"))
    original_layouts = copy.deepcopy(dsl.get("layouts"))
    if not isinstance(original_nodes, list) or not isinstance(original_edges, list):
        raise ValueError("Workflow DSL is missing nodes or edges")
    if any(node.get("id") == NODE_ID for node in original_nodes):
        raise ValueError(f"Node ID already exists: {NODE_ID}")
    if any(node.get("name") == NODE_NAME for node in original_nodes):
        raise ValueError(f"Node name already exists: {NODE_NAME}")

    matches = [node for node in original_nodes if node.get("name") == SOURCE_NODE_NAME]
    if len(matches) != 1 or matches[0].get("type") != "LLM":
        raise ValueError(f"Expected one LLM node named {SOURCE_NODE_NAME!r}")
    source_node = matches[0]
    test_node = copy.deepcopy(source_node)
    test_node["id"] = NODE_ID
    test_node["name"] = NODE_NAME
    test_node["configs"]["system_prompt"] = SYSTEM_PROMPT
    test_node["configs"]["template_content"] = "{{query}}"
    test_node["configs"]["stream"] = False
    test_node["configs"]["isDefaultName"] = False

    if len(test_node.get("inputs", [])) != 1 or test_node["inputs"][0].get("name") != "query" or test_node["inputs"][0].get("type") != "string":
        raise ValueError("Copied node must have a single query String input")
    if len(test_node.get("outputs", [])) != 1 or test_node["outputs"][0].get("name") != "raw_output" or test_node["outputs"][0].get("type") != "string":
        raise ValueError("Copied node must have a single raw_output String output")

    dsl["nodes"].append(test_node)
    if not isinstance(dsl.get("layouts"), dict):
        raise ValueError("Workflow DSL layouts are missing")
    if NODE_ID in dsl["layouts"]:
        raise ValueError(f"Layout ID already exists: {NODE_ID}")
    source_layout = dsl["layouts"].get(source_node["id"])
    if not isinstance(source_layout, dict) or not {"x", "y"}.issubset(source_layout):
        raise ValueError("Source node layout is missing x/y coordinates")
    dsl["layouts"][NODE_ID] = {
        "x": source_layout["x"],
        "y": source_layout["y"] + 720,
    }

    if dsl["edges"] != original_edges:
        raise AssertionError("Existing workflow edges changed")
    if dsl["nodes"][:-1] != original_nodes:
        raise AssertionError("One or more original nodes changed")
    if test_node["configs"].get("model") != source_node["configs"].get("model"):
        raise AssertionError("Model reference changed")
    node_ids = {node.get("id") for node in dsl["nodes"]}
    dangling_refs = sorted({ref for ref in walk_ref_node_ids(dsl) if ref not in node_ids})
    if dangling_refs:
        raise ValueError(f"Workflow contains unresolved ref_node_id values: {dangling_refs}")
    if len(dsl["nodes"]) != 13 or len(dsl["edges"]) != 14:
        raise AssertionError("Expected 13 nodes and the original 14 edges")

    output.parent.mkdir(parents=True, exist_ok=True)
    review_path = output.parent / "review" / "diff_manifest.json"
    if review_path.exists():
        raise FileExistsError(f"Refusing to overwrite review manifest: {review_path}")
    output_text = "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in records) + "\n"
    output.write_text(output_text, encoding="utf-8")

    parsed_output, _ = read_jsonl(output)
    output_workflow = next(row for row in parsed_output if row.get("resource_type") == "workflow")
    output_dsl = output_workflow["dsl"]
    if len(parsed_output) != 4 or len(output_dsl["nodes"]) != 13 or len(output_dsl["edges"]) != 14:
        raise AssertionError("Generated JSONL failed structural verification")
    if output_dsl["nodes"][:-1] != original_nodes or output_dsl["edges"] != original_edges:
        raise AssertionError("Generated JSONL does not preserve the original graph")
    if output_dsl["nodes"][-1]["id"] != NODE_ID or output_dsl["nodes"][-1]["name"] != NODE_NAME:
        raise AssertionError("Generated detached node has an unexpected identity")

    manifest = {
        "source_file": str(source.relative_to(ROOT)),
        "source_sha256": sha256(source),
        "output_file": str(output.relative_to(ROOT)),
        "output_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "workflow_name": output_workflow["resource_name"],
        "workflow_id": output_workflow["resource_id"],
        "workflow_status": output_workflow.get("metadata", {}).get("status"),
        "jsonl_records": len(parsed_output),
        "original_nodes_preserved": len(original_nodes),
        "new_node": {
            "id": NODE_ID,
            "name": NODE_NAME,
            "type": test_node["type"],
            "input": "query:String <- node_start.query",
            "output": "raw_output:String",
            "system_prompt_lines": len(SYSTEM_PROMPT.splitlines()),
            "template_content": "{{query}}",
            "stream": False,
        },
        "generated_node_count": len(output_dsl["nodes"]),
        "edge_count_unchanged": len(output_dsl["edges"]),
        "layout_count": len(output_dsl["layouts"]),
        "original_edges_unchanged": output_dsl["edges"] == original_edges,
        "original_nodes_unchanged": output_dsl["nodes"][:-1] == original_nodes,
        "model_reference_preserved": test_node["configs"]["model"] == source_node["configs"]["model"],
        "all_ref_node_ids_resolve": True,
        "detached_test_node": True,
        "generated_node_added_to_edges": False,
    }
    review_path.parent.mkdir(parents=True, exist_ok=True)
    review_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = prepare(args.source, args.output)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
