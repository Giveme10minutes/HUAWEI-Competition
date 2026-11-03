# Redis（redis）

资料ID：RM-P02-REDIS ｜ 批次：RM-P02 ｜ 版本 v0.2 ｜ 整理日期：2026-11-03
类型：工具/平台 ｜ 所属：数据 ｜ 对应仓库路线：`roadmaps/redis`

## 1. 定位

内存缓存与常用数据结构服务。

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

以下名称取自本地仓库 `roadmaps/redis/content/` 的文件标题，共 **151** 个去重主题；仅作覆盖面参考，不代表必须全部学完。

| 主题 | 文件标识 |
| --- | --- |
| Active-Active geo Distribution | `active-active-geo-distribution` |
| AOF rewrite & compaction | `aof-rewrite--compaction` |
| APPEND | `append` |
| Atomicity in Redis | `atomicity-in-redis` |
| Authentication | `authentication` |
| Backup and Recovery | `backup-and-recovery` |
| Basic Commands / SET, GET | `basic-commands--set-get` |
| Batch Operations | `batch-operations` |
| BITCOUNT | `bitcount` |
| Bitmaps | `bitmaps` |
| BITOP | `bitop` |
| BITPOS | `bitpos` |
| Cache | `cache` |
| Caching | `caching` |
| Clustering | `clustering` |
| Configuring Save Interval | `configuring-save-interval` |
| Connecting using Redis CLI | `connecting-using-redis-cli` |
| Data Persistence Options | `data-persistence-options` |
| DECR | `decr` |
| DEL | `del` |
| Disaster Recovery | `disaster-recovery` |
| EVAL | `eval` |
| EVALSHA | `evalsha` |
| EXEC | `exec` |
| Expiration | `expiration` |
| EXPIRE | `expire` |
| GEOADD | `geoadd` |
| GEOSEARCH | `geosearch` |
| Geospatial Indexes | `geospatial-indexes` |
| GET | `get` |
| GETBIT | `getbit` |
| Hashes | `hashes` |
| HDEL | `hdel` |
| HEXISTS | `hexists` |
| HGET | `hget` |
| HGETALL | `hgetall` |
| High Performance and Scalability | `high-performance-and-scalability` |
| How AOF Works? | `how-aof-works` |
| How RDB Works? | `how-rdb-works` |
| HSET | `hset` |
| Hybrid Persistence | `hybrid-persistence` |
| HyperLogLog | `hyperloglog` |
| In-memory Data Structure Store | `in-memory-data-structure-store` |
| INCR | `incr` |
| INFO | `info` |
| Key-value Database | `key-value-database` |
| Leaderboards and Counters | `leaderboards-and-counters` |
| LINDEX | `lindex` |
| Lists | `lists` |
| LLEN | `llen` |
| LMOVE | `lmove` |
| LPOP | `lpop` |
| LPUSH | `lpush` |
| LRANGE | `lrange` |
| Lua Scripting | `lua-scripting` |
| Max Memory Policy | `max-memory-policy` |
| Memory Management | `memory-management` |
| Message Broker | `message-broker` |
| MONITOR | `monitor` |
| Monitoring | `monitoring` |
| More Commands - Strings | `more-commands` |
| More Commands | `more-commands` |
| More Commands - Streams | `more-commands` |
| More Commands - Geospatial Indexes | `more-commands` |
| More Commands - Hashes | `more-commands` |
| More Commands - Pub/Sub | `more-commands` |
| More Commands - Sets | `more-commands` |
| More Commands - Lists | `more-commands` |
| More Commands - Sorted Sets | `more-commands` |
| MULTI | `multi` |
| Naming Conventions | `naming-conventions` |
| Network Security | `network-security` |
| No Persistence Option | `no-persistence-option` |
| Optimistic Locking | `optimistic-locking` |
| Overview of Data Types | `overview-of-data-types` |
| Persistence Options | `persistence-options` |
| PFADD | `pfadd` |
| PFCOUNT | `pfcount` |
| PFMERGE | `pfmerge` |
| Pipelining | `pipelining` |
| Pre-compiled Binaries | `pre-compiled-binaries` |
| PUBLISH | `publish` |
| Pub/Sub Messaging | `pubsub-messaging` |
| Pub/Sub | `pubsub` |
| RDB vs AOF Tradeoffs | `rdb-vs-aof-tradeoffs` |
| Real-time Analytics | `real-time-analytics` |
| redis-benchmark | `redis-benchmark` |
| Redis Enterprise | `redis-enterprise` |
| Redis Modules | `redis-modules` |
| Redis on Flash | `redis-on-flash` |
| Redis Sentinel | `redis-sentinel` |
| Redis vs SQL/NoSQL DBs | `redis-vs-sqlnosql-dbs` |
| RedisBloom | `redisbloom` |
| RedisCommander | `rediscommander` |
| redis.conf | `redisconf` |
| RedisInsight | `redisinsight` |
| RedisJSON | `redisjson` |
| RedisTimeSeries | `redistimeseries` |
| Replication Basics | `replication-basics` |
| Retrieval by Pattern | `retrieval-by-pattern` |
| Rich Data Structures | `rich-data-structures` |
| RPOP | `rpop` |
| RPUSH | `rpush` |
| SADD | `sadd` |
| SCARD | `scard` |
| SDIFF | `sdiff` |
| Search | `search` |
| Security and Compliance | `security-and-compliance` |
| Session Management | `session-management` |
| SET | `set` |
| SETBIT | `setbit` |
| Sets | `sets` |
| Setting and Getting Keys | `setting-and-getting-keys` |
| SINTER | `sinter` |
| SISMEMBER | `sismember` |
| Slow Log Analysis | `slow-log-analysis` |
| SMEMBERS | `smembers` |
| Sorted Sets | `sorted-sets` |
| SREM | `srem` |
| SSL/TLS Encryption | `ssltls-encryption` |
| （其余 31 个略） | — |

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
