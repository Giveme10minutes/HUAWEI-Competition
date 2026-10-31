"""Check local preparation artifacts; never call a model or cloud service.

The schema walker implements only keywords used in the shipped plan schema.
It is not a general JSON Schema implementation or a production API validator.
"""
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_json(relative):
    return json.loads((ROOT / relative).read_text())


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_shape(value, schema, path="plan"):
    kind = schema.get("type")
    types = {"object": dict, "array": list, "string": str, "integer": int}
    if kind:
        require(type(value) is types[kind], f"{path}: expected {kind}")
    if "const" in schema:
        require(value == schema["const"], f"{path}: invalid constant")
    if "enum" in schema:
        require(value in schema["enum"], f"{path}: invalid enum")
    if kind == "object":
        props = schema.get("properties", {})
        require(set(schema.get("required", [])) <= set(value), f"{path}: missing fields")
        if schema.get("additionalProperties") is False:
            require(set(value) <= set(props), f"{path}: unknown fields")
        for key, child in value.items():
            if key in props:
                validate_shape(child, props[key], f"{path}.{key}")
    elif kind == "array":
        require(len(value) >= schema.get("minItems", 0), f"{path}: too few items")
        if schema.get("uniqueItems"):
            require(len({json.dumps(x, sort_keys=True) for x in value}) == len(value),
                    f"{path}: duplicate items")
        for index, child in enumerate(value):
            validate_shape(child, schema["items"], f"{path}[{index}]")
    elif kind == "string":
        require(len(value.strip()) >= schema.get("minLength", 0), f"{path}: empty text")
    elif kind == "integer":
        require(value >= schema.get("minimum", value), f"{path}: below minimum")
        require(value <= schema.get("maximum", value), f"{path}: above maximum")


def validate_plan(plan, schema, available_source_ids):
    validate_shape(plan, schema)
    tasks = plan["tasks"]
    require(len({task["task_id"] for task in tasks}) == len(tasks), "duplicate task IDs")
    require(sum(t["estimated_minutes"] for t in tasks) * 5 <= plan["available_minutes"] * 4,
            "task budget exceeds 80 percent")
    for task in tasks:
        require(set(task["source_ids"]) <= available_source_ids, "unknown source reference")


def main():
    schema = read_json("contracts/plan.schema.json")
    example = read_json("contracts/examples/plan.json")
    validate_plan(example, schema, set())
    invalid = []
    p = copy.deepcopy(example)
    p["tasks"][0]["estimated_minutes"] = p["available_minutes"]
    invalid.append(p)
    p = copy.deepcopy(example)
    p["tasks"][0]["source_ids"] = ["invented-source"]
    invalid.append(p)
    p = copy.deepcopy(example)
    p["tasks"].append(copy.deepcopy(p["tasks"][0]))
    invalid.append(p)
    p = copy.deepcopy(example)
    p["status"] = "active"
    invalid.append(p)
    p = copy.deepcopy(example)
    p["tasks"][0]["estimated_minutes"] = True
    invalid.append(p)
    p = copy.deepcopy(example)
    del p["tasks"][0]["acceptance"]
    invalid.append(p)
    for index, plan in enumerate(invalid, 1):
        try:
            validate_plan(plan, schema, set())
        except ValueError:
            continue
        raise ValueError(f"invalid fixture {index} was unexpectedly accepted")
    cases = read_json("evals/首轮人工验收案例.json")
    require(len(cases) == 15, "expected 15 preparation cases")
    require(len({case["id"] for case in cases}) == len(cases), "duplicate case IDs")
    for case in cases:
        require(case["inputs"] and case["expected_behaviors"], "incomplete test case")
        require(case["status"] == "not_run", "initial cases must not claim model success")
    print("PASS: example shape and budget; six invalid plans rejected; 15 cases are unexecuted.")
    print("This is a local preparation check, not a model, platform or product acceptance result.")


if __name__ == "__main__":
    main()
