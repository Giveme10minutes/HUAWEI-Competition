# Elasticsearch（elasticsearch）

资料ID：RM-P02-ELASTICSEARCH ｜ 批次：RM-P02 ｜ 版本 v0.2 ｜ 整理日期：2026-11-03
类型：工具/平台 ｜ 所属：数据 ｜ 对应仓库路线：`roadmaps/elasticsearch`

## 1. 定位

全文检索与日志分析引擎。

## 2. 学习阶段

### 阶段 1：安装与基本操作

- 安装、配置与最小可用设置
- 最常用的命令/操作
- 知道它解决什么问题

### 阶段 2：常见工作流

- 把工具接进真实项目流程
- 配置项与常见坑
- 与相邻工具的配合

### 阶段 3：进阶

- 自动化与脚本化
- 性能、安全或成本
- 团队规范与故障处理

## 3. 主题清单（检索用）

以下名称取自本地仓库 `roadmaps/elasticsearch/content/` 的文件标题，共 **113** 个去重主题；仅作覆盖面参考，不代表必须全部学完。

| 主题 | 文件标识 |
| --- | --- |
| API Keys | `api-keys` |
| Authentication | `authentication` |
| Autoscaling | `autoscaling` |
| Avg, Sum, Min, and Max Aggregations | `avg--sum--min--max` |
| BM25 Algorithm | `bm25-algorithm` |
| Boolean Data Type | `boolean` |
| Boosting Queries | `boosting-queries` |
| Bulk Indexing | `bulk-index` |
| Cardinality Aggregation | `cardinality` |
| CAT API | `cat-api` |
| Cluster Monitoring | `cluster-monitoring` |
| Cluster (System) | `cluster-system` |
| Controlling Search Results | `controlling-search-results` |
| Coordinating Nodes | `coordinating-nodes` |
| Create Index | `create-index` |
| Cross-Cluster Replication | `cross-cluster-replication` |
| Custom Analyzers | `custom-analyzers` |
| Data Nodes | `data-nodes` |
| Data Tiers | `data-tiers` |
| Data Types | `data-types` |
| Dates | `dates` |
| Delete by Query | `delete-by-query` |
| Delete Documents | `delete-documents` |
| Delete Index | `delete-index` |
| Doc Values | `doc-values` |
| Document (Row) | `document-row` |
| Dynamic Mappings | `dynamic` |
| Elastic Cloud | `elastic-cloud` |
| Elasticsearch Usecases | `elasticsearch-usecases` |
| Event Query Language (EQL) | `eql` |
| ES\|QL | `esql` |
| Exists Query | `exists-query` |
| Explicit Mappings | `explicit` |
| Fielddata | `fielddata` |
| Filter Aggregations | `filter-aggregations` |
| Filter | `filter` |
| Bool Query Filter Context | `filter` |
| Flattened Data Type | `flattened` |
| Function Score Query | `function-score-query` |
| Geo Points | `geo-points` |
| Get Document | `get-document` |
| Highlighting | `highlighting` |
| Histogram Aggregation | `histogram` |
| How Search Works | `how-search-works` |
| Hybrid Search | `hybrid-search` |
| ID (Primary Key) | `id-primary-key` |
| ID Query | `id-query` |
| Index Lifecycle Management (ILM) | `ilm` |
| Index (Database) | `index-database` |
| Index Document | `index-document` |
| Elasticsearch | `introduction` |
| JSON | `json` |
| Keyword Data Type | `keyword` |
| Kibana Console | `kibana-console` |
| KQL | `kql` |
| Latest Transformation | `latest` |
| Leaf vs. Compound Queries | `leaf-vs-compound-queries` |
| Lucene Query Syntax | `lucene` |
| Mapping Explosion | `mapping-explosion` |
| Mappings | `mappings` |
| Master-Eligible Nodes | `master-elegible-nodes` |
| Match Phrase Query | `match-phrase-query` |
| Match Query | `match-query` |
| Must Queries | `must` |
| Must_Not Queries | `must_not` |
| Nested Aggregations | `nested-aggregations` |
| Nested Data Type | `nested` |
| Node (Instance) | `node-instance` |
| Numeric Data Types | `numeric` |
| Object Data Type | `object` |
| Optimizing Bulk Indexing | `optimizing-bulk-indexing` |
| Pagination | `pagination` |
| Pipeline Aggregations | `pipeline-aggregations` |
| Pivot Transformation | `pivot` |
| Prefix Query | `prefix-query` |
| Primary Shards | `primary-shards` |
| Query DSL | `query-dsl` |
| Query | `query` |
| Range/Date Range Aggregations | `range--date-range` |
| Range Query | `range-query` |
| Reindex API | `reindex-api` |
| Replica Shards | `replica-shards` |
| REST API Basics | `rest-api-basics` |
| Roles & Users | `roles--users` |
| Rollover Policies | `rollover-policies` |
| Running Elasticsearch with Docker | `running-with-docker` |
| Search Analyzer | `search-analyzer` |
| Search Engines vs. Relational Databases | `search-engines-vs-relational-dbs` |
| Segment Merging | `segment-merging` |
| Semantic Search | `semantic-search` |
| Should Query | `should` |
| SLM | `slm` |
| Snapshots and Restores | `snapshots--restore` |
| Sorting | `sorting` |
| Source Filtering | `source-filtering` |
| Elasticsearch SQL | `sql` |
| Standard Analyzer | `standard-analyzer` |
| Stats and Extended Stats Aggregations | `stats--extended-stats` |
| c | `synonyms-graph` |
| Term Query | `term-query` |
| Terms Aggregation | `terms` |
| Text Data Type | `text` |
| The Analyze API | `the-analyze-api` |
| The ELK Stack | `the-elk-stack` |
| The Inverted Index | `the-inverted-index` |
| The "Split Brain" Problem | `the-split-brain-problem` |
| Transform API | `transform-api` |
| Understanding Similarity | `understanding-similarity` |
| Update by Query | `update-by-query` |
| Update Document | `update-document` |
| Value Count Aggregation | `value-count` |
| Vector Search | `vector-search` |
| Wildcard Query | `wildcard-query` |

## 4. 与相邻内容的关系

- 它是“数据”场景下的工具/平台，价值取决于是否接进真实流程。
- 方向地图与区分方法见 `../roadmap_v0.1/00_direction_map.md`；岗位原文条件见 `../computing_pilot_v0.1/`（两者不能互相替代）。

## 5. 本页不包含

- 学时、周数、薪资、就业率与前景判断；
- 具体资源链接、课程与书籍推荐；
- “适合什么人”的适配结论；
- 招聘要求；某方向是否好就业需查岗位原文与市场数据，本页不提供。

## 6. 来源、编排与限制

- 主题名称来自 roadmap.sh 内容仓库的本地快照（`/Users/chenyu/Downloads/developer-roadmap-master/roadmaps/`），仅读取文件标题；**未复制**其说明文字、资源链接或图片，也未使用其 URL。
- 定位、阶段划分与顺序、边界说明均为整理者自写编排，不是招聘方要求，也不是唯一正确路径。
- 技术生态变化快，工具名与主题名可能过时；引用时注明整理日期 2026-11-03。
