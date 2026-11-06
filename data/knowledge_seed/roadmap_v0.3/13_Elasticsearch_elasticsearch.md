# Elasticsearch：全文检索与日志分析引擎

Elasticsearch 是一个基于 Apache Lucene 的分布式搜索与分析引擎，通过 REST 接口读写 JSON 文档。它把数据组织成索引，支持全文检索、结构化过滤和聚合统计，常用于站内搜索、日志检索与指标分析。

来源：主题名称取自 roadmap.sh 的 Elasticsearch 路线索引（https://roadmap.sh/elasticsearch）；定位说明为整理者归纳。

## Elasticsearch 是什么：解决什么问题

当数据量变大时，关系型数据库的模糊匹配往往难以兼顾速度与相关度。Elasticsearch 用倒排索引记录词项与文档的对应关系，使关键词查询可以按相关度打分返回，并把检索能力做成独立服务供应用调用。

参考：Elastic 官方文档（https://www.elastic.co/docs）。

## Elasticsearch 的核心概念与常用操作

Elasticsearch 以文档为最小数据单位，文档是 JSON 对象，若干文档组成一个索引。写入、查询和删除都通过 HTTP 请求完成，查询条件用 Query DSL 表达。

相关概念（6 项）：索引（文档集合与检索单元）、文档（JSON 形式的数据记录）、映射（字段类型与索引方式）、分片（索引的水平切分单元）、副本（分片的冗余拷贝）、倒排索引（词项到文档的映射结构）。

参考：Elastic 官方文档（https://www.elastic.co/docs）。

## Elasticsearch 的检索与聚合：查询怎么写

一次检索通常先用查询条件筛出文档，再用聚合对结果分组统计。match 会对文本分词后匹配，term 按精确值过滤，range 处理范围条件，bool 组合多个子查询；聚合则用于计数、均值、分桶等统计。

相关能力（6 项）：Query DSL（结构化查询语句）、BM25（默认相关度评分算法）、聚合（分组与指标统计）、高亮（返回命中片段）、分页（控制返回范围）、排序（按字段或相关度排列）。

参考：Elastic 官方文档（https://www.elastic.co/docs）。

## Elasticsearch 的典型使用场景

Elasticsearch 常见于需要快速找到相关记录并统计的场合，例如商品或文章搜索、集中式日志检索、按时间与维度做指标分析，以及基于向量表示的相似内容匹配。

相关场景（5 项）：站内搜索（关键词检索商品或文章）、日志分析（集中检索服务日志）、指标聚合（按时间与维度统计）、地理检索（按位置范围筛选）、向量检索（相似内容匹配）。

来源：主题名称取自 roadmap.sh 的 Elasticsearch 路线索引（https://roadmap.sh/elasticsearch）；场景说明为整理者归纳。

## Elasticsearch 与关系型数据库的区别

Elasticsearch 不是关系型数据库的替代品：它擅长检索与统计，而事务、约束和强一致写入通常仍由关系型数据库承担。常见做法是把业务数据同步到 Elasticsearch 作为检索副本，两边各做擅长的事。

来源：主题名称取自 roadmap.sh 的 Elasticsearch 路线索引（https://roadmap.sh/elasticsearch）；区别说明为整理者归纳。

## 如何开始练习 Elasticsearch

最小练习是启动一个单节点实例，创建带显式映射的索引，写入 5 条 JSON 文档，再用 match 查询、range 过滤和 terms 聚合各执行一次，观察返回结果。产出是一组可重复执行的请求命令和一份字段映射说明。

来源：该练习由整理者归纳设计；主题名称取自 roadmap.sh 的 Elasticsearch 路线索引（https://roadmap.sh/elasticsearch）。
