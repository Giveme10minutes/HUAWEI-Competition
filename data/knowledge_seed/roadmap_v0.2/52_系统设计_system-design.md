# 系统设计（system-design）

资料ID：RM-P02-SYSTEM_DESIGN ｜ 批次：RM-P02 ｜ 版本 v0.2 ｜ 整理日期：2026-11-03
类型：基础能力 ｜ 所属：架构 ｜ 对应仓库路线：`roadmaps/system-design`

## 1. 定位

大规模系统的组件划分、数据流与权衡。

## 2. 学习阶段

### 阶段 1：概念

- 核心概念与术语
- 典型例子与反例
- 常见误解

### 阶段 2：练习方法

- 分主题练习，记录错因
- 能解释为什么这样做
- 从例题迁移到新问题

### 阶段 3：应用与自检

- 在真实项目中使用
- 与相邻知识串起来
- 定期复盘薄弱点

## 3. 主题清单（检索用）

以下名称取自本地仓库 `roadmaps/system-design/content/` 的文件标题，共 **131** 个去重主题；仅作覆盖面参考，不代表必须全部学完。

| 主题 | 文件标识 |
| --- | --- |
| Ambassador | `ambassador` |
| Anti-Corruption Layer | `anti-corruption-layer` |
| Application Caching | `application-caching` |
| Application Layer | `application-layer` |
| Async Request Reply | `async-request-reply` |
| Asynchronism | `asynchronism` |
| Availability in Numbers | `availability-in-numbers` |
| Availability Monitoring | `availability-monitoring` |
| Availability Patterns | `availability-patterns` |
| Availability vs Consistency | `availability-vs-consistency` |
| Availability | `availability` |
| Back Pressure | `back-pressure` |
| Backends for Frontend | `backends-for-frontend` |
| Background Jobs | `background-jobs` |
| Bulkhead | `bulkhead` |
| Busy Database | `busy-database` |
| Busy Frontend | `busy-frontend` |
| Cache Aside | `cache-aside` |
| Cache-Aside | `cache-aside` |
| Caching | `caching` |
| CAP Theorem | `cap-theorem` |
| CDN Caching | `cdn-caching` |
| Chatty I/O | `chatty-io` |
| Choreography | `choreography` |
| Circuit Breaker | `circuit-breaker` |
| Claim Check | `claim-check` |
| Client Caching | `client-caching` |
| Cloud Design Patterns | `cloud-design-patterns` |
| Communication | `communication` |
| Compensating Transaction | `compensating-transaction` |
| Competing Consumers | `competing-consumers` |
| Compute Resource Consolidation | `compute-resource-consolidation` |
| Consistency Patterns | `consistency-patterns` |
| Content Delivery Networks | `content-delivery-networks` |
| CQRS | `cqrs` |
| Data Management | `data-management` |
| Database Caching | `database-caching` |
| Databases | `databases` |
| Denormalization | `denormalization` |
| Deployment Stamps | `deployment-stamps` |
| Design and Implementation | `design--implementation` |
| Document Store | `document-store` |
| Domain Name System | `domain-name-system` |
| Event-Driven | `event-driven` |
| Event Sourcing | `event-sourcing` |
| Eventual Consistency | `eventual-consistency` |
| External Configuration Store | `external-config-store` |
| Extraneous Fetching | `extraneous-fetching` |
| Fail-Over | `fail-over` |
| Federated Identity pattern | `federated-identity` |
| Federation | `federation` |
| Gatekeeper | `gatekeeper` |
| Gateway Aggregation | `gateway-aggregation` |
| Gateway Offloading | `gateway-offloading` |
| Gateway Routing | `gateway-routing` |
| Geodes | `geodes` |
| Graph Databases | `graph-databases` |
| GraphQL | `graphql` |
| gRPC | `grpc` |
| Health Endpoint Monitoring | `health-endpoint-monitoring` |
| Health Monitoring | `health-monitoring` |
| High availability | `high-availability` |
| Horizontal Scaling | `horizontal-scaling` |
| How to approach System Design? | `how-to-approach-system-design` |
| HTTP | `http` |
| Idempotent Operations | `idempotent-operations` |
| Improper Instantiation | `improper-instantiation` |
| Index Table | `index-table` |
| Instrumentation | `instrumentation` |
| Introduction | `introduction` |
| Key-Value Store | `key-value-store` |
| Latency vs Throughput | `latency-vs-throughput` |
| Layer 4 Load Balancing | `layer-4-load-balancing` |
| Layer 7 Load Balancing | `layer-7-load-balancing` |
| LB vs Reverse Proxy | `lb-vs-reverse-proxy` |
| Leader Election | `leader-election` |
| Load Balancers | `load-balancers` |
| Load Balancing Algorithms | `load-balancing-algorithms` |
| Materialized View | `materialized-view` |
| Message Queues | `message-queues` |
| Messaging | `messaging` |
| Microservices | `microservices` |
| Monitoring | `monitoring` |
| Monolithic Persistence | `monolithic-persistence` |
| No Caching | `no-caching` |
| Noisy Neighbor | `noisy-neighbor` |
| Performance Antipatterns | `performance-antipatterns` |
| Performance Monitoring | `performance-monitoring` |
| Performance vs Scalability | `performance-vs-scalability` |
| Pipes and Filters | `pipes--filters` |
| Priority Queue | `priority-queue` |
| Publisher/Subscriber | `publishersubscriber` |
| Pull CDNs | `pull-cdns` |
| Push CDNs | `push-cdns` |
| Queue-Based load leveling | `queue-based-load-leveling` |
| Refresh Ahead | `refresh-ahead` |
| Reliability Patterns | `reliability-patterns` |
| Replication | `replication` |
| Resiliency | `resiliency` |
| REST | `rest` |
| Retry Storm | `retry-storm` |
| Retry | `retry` |
| Returning Results | `returning-results` |
| RPC | `rpc` |
| Schedule Driven | `schedule-driven` |
| Scheduling Agent Supervisor | `scheduler-agent-supervisor` |
| Security Monitoring | `security-monitoring` |
| Security | `security` |
| Sequential Convoy | `sequential-convoy` |
| Service Discovery | `service-discovery` |
| Sharding | `sharding` |
| Sidecar | `sidecar` |
| SQL Tuning | `sql-tuning` |
| SQL vs NoSQL | `sql-vs-nosql` |
| Static Content Hosting | `static-content-hosting` |
| Strangler fig | `strangler-fig` |
| Strong Consistency | `strong-consistency` |
| Synchronous I/O | `synchronous-io` |
| Task Queues | `task-queues` |
| TCP | `tcp` |
| （其余 11 个略） | — |

## 4. 与相邻内容的关系

- 它是所有方向共用的基础能力（架构），不单独对应岗位。
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
