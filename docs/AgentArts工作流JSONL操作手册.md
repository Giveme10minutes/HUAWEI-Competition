# AgentArts 工作流 JSONL 操作手册

适用范围为 AgentArts 低码工作流草稿。项目示例来自“职业探索_协作流程_v01”的真实导出与回导记录。字段以本次导出为准，遇到新节点类型或结构变化时先取样。本手册于 2026-11-05 整理。

## 1. 导出基线，确定修改范围

1. 在当前区域的“开发中心 → 智能体管理 → 工作流”找到目标草稿，核对名称、工作流 ID 和最新保存时间。在工作流管理页导出 AgentArts `.jsonl`。
2. 把原始导出保存在 Git 忽略的 `local_data/workflow_backups/`，另选一个新文件名保存修改版。记录区域、工作流 ID、导出时间、云端保存时间及原文件 SHA-256。导出包可能含关联资源配置，分享时使用脱敏的结构摘录。
3. 写清预期差异。例如“只改 `检索关键词提取` 的系统提示词”或“新增一个 LLM 单节点试验，保留原边”。导入前再次核对保存时间。如有其他窗口的新改动，重新导出并将本次改动应用到最新副本。

官方操作见[管理工作流](https://support.huaweicloud.com/lowcode-agentarts/agentarts_05_0058.html)。

## 2. 识别实际结构

JSONL 每行是一个完整的 JSON 对象。用 Python `json.loads` 逐行读取，用 `json.dumps` 逐行写回。提示词中的换行由 JSON 序列化转义，输出仍保持一条记录一行。

| 在哪里 | 用途与检查点 |
| --- | --- |
| 外层 `resource_type`、`resource_id`、`schema_version` | 区分资源并核对目标身份与版本。更新同一个草稿时沿用其资源标识。历史基线中有两个 `model`、一个 `provider` 和一个 `workflow`，实际记录数随依赖而变。 |
| `workflow.dsl.nodes` | 节点包含 `id`、`name`、`type`、`configs`、`inputs`、`outputs`。按 ID 比较节点，名称用于辅助定位。 |
| `workflow.dsl.edges` | 现有导出使用 `source` 和 `target` 指向节点 ID。条件边还可带 `branch`、`exception_branch`，按同类边取样。 |
| `workflow.dsl.layouts` | 以节点 ID 为键，保存画布位置。复制节点时同时检查新增布局键。 |
| `inputs[].value.content` | 本项目的节点引用可见 `ref_node_id` 和 `ref_var_name`，例如知识检索的 `query` 引用上游 `raw_output`。核对生产字段、类型以及该分支能否实际产生它。 |
| `level2_resources`、`metadata`、关联资源记录 | 保存或引用平台资源。局部修改时保留原值，导入预览中单独检查模型、知识库、插件等依赖。 |

这些是本项目样本中的字段。开始节点的输入也可作为下游引用来源。其他类型的引用、条件和异常分支以同类真实导出为样本。

## 3. 修改已有节点

### 3.1 只改系统提示词

从仓库根目录运行下例。先将两个路径换成本次导出和新副本，再填入已评审的提示词。示例文本仅用于演示修改位置。脚本按名称和 `LLM` 类型定位唯一节点，写出前检查完整资源列表只有指定字段变化。

```sh
python3 - local_data/workflow_backups/current.jsonl local_data/workflow_backups/edited.jsonl <<'PY'
import copy
import json
import sys
from pathlib import Path

source, output = map(Path, sys.argv[1:])
rows = [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines() if line.strip()]
original = copy.deepcopy(rows)
workflows = [row for row in rows if row.get("resource_type") == "workflow"]
if len(workflows) != 1:
    raise SystemExit("请使用只导出一个工作流的文件")
workflow = workflows[0]
if workflow.get("resource_name") != "职业探索_协作流程_v01":
    raise SystemExit("工作流名称与示例目标不一致")
nodes = [node for node in workflow["dsl"]["nodes"]
         if node.get("name") == "检索关键词提取" and node.get("type") == "LLM"]
if len(nodes) != 1:
    raise SystemExit("目标节点无法唯一定位")
node = nodes[0]
old_value = node["configs"]["system_prompt"]
new_value = "只输出一条供知识库检索的查询。保留用户明确提出的岗位或技术条件。"
if old_value == new_value:
    raise SystemExit("系统提示词已是目标值")
node["configs"]["system_prompt"] = new_value
serialized = "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n"
node["configs"]["system_prompt"] = old_value
if rows != original:
    raise SystemExit("出现预期之外的资源或字段变化")
with output.open("x", encoding="utf-8") as file:
    file.write(serialized)
print("修改副本已保存。预期差异为目标 LLM 的 configs.system_prompt。")
PY
```

运行前还应在本地确认源文件中的 `resource_id` 与平台目标一致。写出模式 `x` 会拒绝覆盖现有文件。导入后的最小验收是读回提示词，给该节点一条真实输入并检查输出格式与查询含义。

### 3.2 只改检索阈值

定位 `KnowledgeRepo` 类型的“知识检索”。本项目导出中，检索模式、阈值、返回条数和库绑定分别在 `configs.search_mode`、`configs.recall_threshold`、`configs.top_k`、`configs.repos`。例如做阈值对照时，把阈值从实际读到的 `0.5` 改为 `0`，保留模式、返回条数、库绑定、过滤和输入引用。若实际基线有变化，先按新基线重定实验。阈值 `0` 是本项目曾用的诊断示例。

对照验证使用同一条实际查询，记录两次配置、返回片段和分数，分开判断参数保存和召回质量。历史阈值 `0` 草稿已导入，诊断运行及恢复仍待验证，详见[多查询导入与测试记录](多查询DSL本地生成_2026-11-04.md)。

## 4. 新增节点或接入分支

1. 从真实导出复制同类型节点，为副本分配唯一的 `id` 和明确的 `name`，按目标输入输出修改配置，并在 `layouts` 中补同 ID 的坐标。检查副本的模型引用和输入引用是否仍符合预期。
2. 只做单节点试验时，可以先生成游离节点。历史案例复制了 LLM“检索关键词提取”，新节点接收 `node_start.query`，输出 `raw_output`（字符串）。本地结构由 12 节点、14 边变成 13 节点、14 边，已完成导入与回读。
3. 要让节点参与整条流程，再按同类型分支样本补边。按实际 `source`、`target` 和分支字段核对执行路径，同时修改下游数据引用。逐段检查开始输入、处理节点输出、聚合及结束输出，避免只连画布线而漏改引用，或让不经过该分支的路径读取空变量。
4. 先运行受影响节点，再用一条能命中新增分支的输入验证下游是否收到正确值。若改动共用的聚合或结束节点，再用一条原路径输入核对输出。

现有[多查询生成脚本](../scripts/prepare_multiquery_workflow.py)可参考复制节点、补布局和检查差异的写法。它针对历史基线和指定工作流，要求四条资源记录、原图 12 节点与 14 边，不能直接用于任意最新草稿。[实测记录](多查询DSL本地生成_2026-11-04.md)

## 5. 给联网插件取样

1. 在目标账号、区域和低码工作流环境中确认有可用的搜索或网页读取插件。用同环境的样本配置一个节点，完成必要鉴权后做一次单节点测试，观察实际输入、输出、成功返回和失败形态。搜索结果若只有摘要和链接，按搜索线索处理。需要官方正文的场景另测正文读取。
2. 导出包含该节点的样本。对比添加前后的资源记录与节点，记录工具标识、输入映射、输出类型和相关资源引用。平台文档说明插件节点的输入输出结构取自插件定义，修改参数来源与修改插件定义是两项操作。优先保留已跑通的结构，在本地改输入映射、连线及下游引用。[官方插件节点说明](https://support.huaweicloud.com/lowcode-agentarts/agentarts_05_0072.html)
3. 将确认过的节点结构应用到最新草稿副本。检查导入预览中的依赖与鉴权状态，然后用正常查询和一个失败场景核对下游是否能分别处理。来源引用须能回到实际读取的内容。

本项目尚无已验收的联网插件导出样本。插件节点取样及运行是待验证步骤，云端浏览器沙箱在此低码工作流中的接入也待核实。

## 6. 本地检查、导入与读回

| 阶段 | 通过条件 |
| --- | --- |
| 本地格式 | 每条记录能独立解析为 JSON 对象。目标工作流 ID 和 `schema_version` 符合预期，原始备份哈希保持一致。 |
| 本地语义差异 | 只有本次指定节点字段、连线或布局发生变化。节点 ID 唯一，边端点可解析，引用的字段存在且类型匹配。其他资源记录保持一致。 |
| 导入预览 | 走“导入 → 导入 AgentArts 工作流”，核对解析列表。只勾选本次要更新的资源。勾选已有工作流会覆盖其配置。依赖导入失败或提示未配置鉴权时，先查具体资源状态。 |
| 保存证据 | 导入后重新打开目标草稿，核对 ID、保存时间、节点和字段。必要时再次导出，按节点 ID 和边的端点、分支比较，区分数组重排、平台元数据变化与实际配置差异。 |
| 运行证据 | 单节点运行核对实际输入、输出和结果内容。修改了连线时，按实际输入验证角色或节点交接。记录测试范围，分别报告保存通过、单节点通过及完整场景通过。 |

导入覆盖和关联资源失败的行为见[官方工作流管理说明](https://support.huaweicloud.com/lowcode-agentarts/agentarts_05_0058.html)。导入草稿、发布版本及部署入口分别管理，执行范围以当次授权为准。

## 7. 恢复与常见故障

需要撤回时，先导出当前草稿留证，并与改动前备份比较。如果其他窗口已经改了同一草稿，就从当前导出反向撤销本次字段或节点改动。如果确认可以整体恢复，使用改动前备份导入目标草稿，核对预览资源、依赖和鉴权，随后重开读回并验证一条受影响路径。项目已有导入更新证据，完整备份恢复尚未实测。

| 现象 | 优先排查 |
| --- | --- |
| 文件无法解析 | 检查是否把整个文件保存成 JSON 数组、把单条记录格式化为多行，或在提示词字符串中写入未转义的换行。 |
| 新节点可见但没运行 | 检查是否仍是游离节点、进入条件是否满足，以及边和变量引用是否都已更新。 |
| 插件缺参或类型不匹配 | 查看上游实际输出、运行分支、插件定义的必填项与类型，再检查鉴权。 |
| 检索节点成功但返回空数组 | 分开检查知识库自身的命中测试、实际查询、绑定、过滤、模式、阈值。一次只改一个变量。 |

交接记录应包含源文件与修改副本的路径和哈希、预期与实际差异、导入结果、读回与运行证据、剩余问题。原始导出包和运行敏感载荷留在忽略目录，提交可公开核对的脚本与脱敏记录。
