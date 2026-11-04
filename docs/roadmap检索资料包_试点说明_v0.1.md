# roadmap 学习路线检索资料包试点 v0.1（2026-11-04）

本地试点记录：把 roadmap.sh 的三条路线（frontend / backend / python）从已抓取原始资料转换为可追溯、可检索的资料包。**不是知识库上传，不是 M3/M4 验收，也不是产品已接入**。

## 1. 输入与范围

- 原始资料：`references/raw/roadmap-ai/`（101 条路线，本地、被 Git 忽略）。
- 本次只处理 3 条：frontend、backend、python；其余 98 条原样保留，未删除、未改动。
- 结构来自官方画布数据 `graph/<slug>.json` 与 `json/<slug>.json`；描述与资源来自官方 content 快照 `content/<slug>.json`。
- 未重跑全站抓取，未批量补全缺失描述，未调用云端模型或 embedding。

## 2. 产物（本地，被 Git 忽略）

路径：`local_data/roadmap_pilot_v0.1/`（`.gitignore` 已有 `local_data/` 整目录规则，无需改动）

| 文件 | 用途 |
|---|---|
| `nodes.jsonl` | 每节点一行：描述、匹配方式、审核状态、结构推导字段、隔离标记 |
| `relations.jsonl` | `diagram_connection`（原图连线，原样保留）+ `inferred_grouping`（结构推导），不含 `prerequisite` |
| `chunks.jsonl` | 仅供正文检索的片段：路线名 + 知识点 + 描述 + 来源标识；只收 id 命中且有描述的节点 |
| `resources.jsonl` | 资源条目，全部 `link_status=unchecked` |
| `review_items.jsonl` | 待审核项：匹配歧义、已知错位、祖先链可疑 |
| `manifest.json` | 输入/输出 SHA-256、来源时间、计数、边界声明 |
| `qa_report.json` | 10 项确定性检查与统计 |
| `qa_samples.json` | 30 节点 / 15 边抽样核对结果 |
| `retrieval_cases.json` | 10 个中文检索案例（预期节点、证据类型、不应得出的结论） |
| `README.md` | 目录与字段说明、重跑命令 |

处理脚本：`scripts/prepare_roadmap_pilot.py`（纯标准库）。

## 3. 处理规则（已实现）

1. 节点唯一键 `(roadmap, node_id)`，不假设 node_id 跨路线唯一。
2. 描述匹配逐节点重新判定，不沿用旧的"有描述即匹配正确"：
   - 节点 id 命中 → `id`；
   - 仅归一化标题唯一匹配 → `title_fallback`（默认待审核）；
   - 标题候选多个，或候选内容条目已被其他节点占用 → `ambiguous`，**不任取第一个**；
   - 无候选 → `missing`，描述留空。
3. 父子/深度/路径一律标为结构推导（`structure_note` 写明"非官方父子事实"），并保留原 `parent_rule` 与祖先链规则序列。
4. 已知错位（backend 的 Docker、Kubernetes 在 Message Brokers 下的 Containerization 标题块，System Design 在 Architectural Patterns 下）**不重写原始结构**：自节点与后代标记 `structure_quarantined` / `structure_ancestor_quarantined`，逐条写入 `review_items.jsonl`。
5. 原图连线原样保留端点、handle、样式与原始边 id；端点落在被过滤布局节点时标 `layout_node` 并保留引用。
6. 不生成 `prerequisite`；不因官方边、实线样式、depth 或 order 推断"必须先学"。
7. 资源只标注原始类型（official/article/video/book），全部 `unchecked`，不声称已访问或已核验。
8. 时间分开记录：图抓取时间（来自原始 `source.fetched_at`）、内容快照标识（写 `unknown`，无上游版本证据）、本次构建时间（不当作原文更新时间）。

## 4. 本次结果

| 路线 | 原始节点 | 保留 | 排除 | 片段 | 资源 | id 命中 | 歧义 | 缺描述 |
|---|---|---|---|---|---|---|---|---|
| frontend | 156 | 137 | 19 | 120 | 393 | 120 | 1 | 16 |
| backend | 225 | 186 | 39 | 155 | 524 | 155 | 0 | 31 |
| python | 124 | 99 | 12 | 87 | 245 | 87 | 3 | 9 |
| 合计 | 505 | 422 | 70 | 362 | 1162 | 362 | 4 | 56 |

- 关系：`diagram_connection` 160 条（= 原图边总数，未丢边）+ `inferred_grouping` 419 条；`prerequisite` 0 条。
- 排除原因分项已写入 `qa_report.json`（布局节点 `vertical/section/horizontal/legend`、chrome 面板、构建器过滤的内容节点）。
- 待审核 7 条：4 条匹配歧义（frontend `Prompt Engineering`，python `Python`×2、`Django`）+ 3 条已知错位。
- 4 条原图连线端点落在布局节点（frontend 1、backend 3），已保留并标记，未伪造内容节点。

### 4.1 一个实测发现

初次判定时 4 个节点按"标题唯一匹配"通过了 `title_fallback`，核对后发现它们匹配到的内容条目其实属于**另一个节点**（同名主题在画布上出现两次，其中一个用 id 命中）。这类"重复占用同一条内容"未被旧规则拦截。已增加占用检测：内容条目已被 id 命中或其他兜底节点占用时，一律判为 `ambiguous` 并记入待审核。因此本次 `title_fallback` 计数为 0，`ambiguous` 为 4。

## 5. 质量检查

- 确定性检查 10/10 通过：三条路线均处理、唯一键无重复、片段可回溯、匹配方式完整且歧义未被静默消除、边端点状态明确、未补写描述、推断路径未进入检索正文、无 prerequisite、原始=保留+排除对账、重复构建哈希一致（另做了跨进程重跑，五个 jsonl 的 SHA-256 完全一致）。
- 抽样核对 30 节点 / 15 边，全部通过：逐条回查 `json/<slug>.json` 与 `content/<slug>.json`，核对 id 存在性、描述逐字一致、歧义候选、边端点与样式。
- 某类样本不存在时如实记为 `absent`（例如三条路线都没有 `description:empty`，frontend 没有 `section`/`caption-group` 规则节点）。

## 6. 检索案例

`retrieval_cases.json` 含 10 个中文案例，覆盖前端、后端、Python 具体主题、学习资源查找、跨路线近似主题（Sorting Algorithms vs Performance）、缺资料（AWS S3，超出本试点范围）、以及易误用推断层级的情形（Docker/Kubernetes 归属、System Design 先后顺序）。

- 本地没有可复用的检索器，`backend/` 未实现检索；按约定**未**引入 embedding、向量库或云服务。
- 因此 `run_status=not_run`，未做召回与答案质量评估，不声称已完成端到端 RAG。
- 附带一份"标题 + 描述子串"关键词基线（明确标注非语义检索），仅作参考，不作为检索通过证据。该基线是自证式的：案例关键词取自节点标签本身，只能说明字段可用。
- R05（Docker/Kubernetes）与 R06（System Design）的预期节点在原始内容里就没有描述（`navigation_only`），本资料只能确认其存在与结构隔离状态，无法给出解释性内容——这正是需要如实暴露的缺口。

## 7. 能力边界

**可以支持**：按路线/知识点检索官方描述与资源链接；说明某主题在某条路线中出现；区分"有官方描述的内容"与"仅有标题的导航节点"；指出某条结构归属是推导而非事实。

**不能支持**：先修关系与学习顺序；Docker/Kubernetes、System Design 的层级归属；资源链接的可用性与权威性；原文未覆盖的主题（如 AWS S3）；置信度意义上的语义检索与端到端回答质量。

## 8. 与既有资料的关系

`data/knowledge_seed/learning_paths_pilot_v0.1/` 是面向入库的前后端学习路线正文（人工撰写阶段化内容，2026-11-03）。本次是 roadmap.sh 原始资料的检索化派生，两者用途不同，未合并、未互相改写。

## 9. 重跑

```bash
python3 scripts/prepare_roadmap_pilot.py --verify
```

输入不变时，五个 jsonl 的 id、计数与正文保持一致（仅时间字段变化）。扩展到其余路线只需修改脚本中的 `SCOPE`，但需先补内容匹配与结构推导的抽检。

## 10. 未完成与需人工判断

- 4 条匹配歧义需人工确认归属，未自动通过。
- 3 处已知错位仅隔离未修正，修正需对照官方画布人工判定。
- 56 个节点无描述（`navigation_only`），未补写。
- 资源链接未核验，未批量访问。
- 未扩展到其余 98 条路线。
