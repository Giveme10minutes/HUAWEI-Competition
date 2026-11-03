# PostgreSQL DBA（postgresql-dba）

资料ID：RM-P02-POSTGRESQL_DBA ｜ 批次：RM-P02 ｜ 版本 v0.2 ｜ 整理日期：2026-11-03
类型：职业方向 ｜ 所属：数据 ｜ 对应仓库路线：`roadmaps/postgresql-dba`

## 1. 定位

数据库部署、调优、备份恢复与权限。

## 2. 学习阶段

### 阶段 1：概念与工具链

- 理解这个方向交付什么、日常在解决什么问题
- 装好最小工具链，跑通第一个可运行示例
- 知道常见术语与相邻方向的差别

### 阶段 2：核心能力

- 按主题清单挑出核心主题，逐个做出小作品
- 每个作品写清目标、做法与结果
- 遇到问题能定位是概念不清还是工具问题

### 阶段 3：工程化与协作

- 把作品做成可测试、可部署、可维护的工程
- 接入版本控制、代码规范与自动化检查
- 能在他人代码与需求约束下交付

### 阶段 4：深入与专项（可选）

- 选一条支线深入，做对比实验
- 关注性能、成本、稳定性或安全
- 形成自己的判断依据，而不是只跟教程

## 3. 主题清单（检索用）

以下名称取自本地仓库 `roadmaps/postgresql-dba/content/` 的文件标题，共 **167** 个去重主题；仅作覆盖面参考，不代表必须全部学完。

| 主题 | 文件标识 |
| --- | --- |
| ACID | `acid` |
| Adding Extensions | `adding-extra-extensions` |
| Advanced Topics in PostgreSQL Security | `advanced-topics` |
| Aggregate and Window Functions | `aggregate-and-window-functions` |
| Ansible for PostgreSQL Configuration Management | `ansible` |
| Programming Languages and PostgreSQL Automation | `any-programming-language` |
| Attributes in the Relational Model | `attributes` |
| Authentication Models | `authentication-models` |
| Awk | `awk` |
| B-Tree Indexes | `b-tree` |
| Backup Validation Procedures | `backup-validation-procedures` |
| Barman (Backup and Recovery Manager) | `barman` |
| RDBMS Concepts | `basic-rdbms-concepts` |
| BRIN (Block Range INdex) | `brin` |
| Buffer Management | `buffer-management` |
| Bulk Load Process Data | `bulk-loading--processing-data` |
| check_pgactivity | `check_pgactivity` |
| check_pgbackrest | `check_pgbackrest` |
| Checkpoints and Background Writer | `checkpoints--background-writer` |
| Chef for PostgreSQL Configuration Management | `chef` |
| Columns in PostgreSQL | `columns` |
| Configuring PostgreSQL | `configuring` |
| Connect Using psql | `connect-using-psql` |
| Constraints in PostgreSQL | `constraints` |
| Consul - an introduction in the context of load balancing | `consul` |
| Core Dumps | `core-dumps` |
| Common Table Expressions (CTEs) | `cte` |
| Data Partitioning | `data-partitioning` |
| Data Types in PostgreSQL | `data-types` |
| Databases in PostgreSQL | `databases` |
| Default Privileges in PostgreSQL | `default-privileges` |
| Depesz: A Tool for Query Analysis | `depesz` |
| Deployment in Cloud | `deployment-in-cloud` |
| Domains in PostgreSQL | `domains` |
| eBPF (Extended Berkeley Packet Filter) | `ebpf` |
| Etcd | `etcd` |
| Query Analysis: EXPLAIN in PostgreSQL | `explain` |
| explain.dalibo.com | `explaindalibocom` |
| Filtering Data in PostgreSQL | `filtering-data` |
| Schemas in PostgreSQL | `for-schemas` |
| For Tables in PostgreSQL | `fortables` |
| GDB (GNU Debugger) | `gdb` |
| Get Involved in Development | `get-involved-in-development` |
| GIN (Generalized Inverted Index) | `gin` |
| GIST Indexes | `gist` |
| Golden Signals | `golden-signals` |
| Grant and Revoke Privileges in PostgreSQL | `grant--revoke` |
| Grep Command in Log Analysis | `grep` |
| Grouping | `grouping` |
| HAProxy | `haproxy` |
| Hash Indexes | `hash` |
| Helm - Package Manager for Kubernetes | `helm` |
| High Level Database Concepts | `high-level-database-concepts` |
| HTAP | `htap` |
| Import and Export using COPY | `import--export-using-copy` |
| Indexes Use Cases | `indexes-and-their-usecases` |
| PostgreSQL Infrastructure Skills | `infrastructure-skills` |
| Installation and Setup of PostgreSQL | `installation-and-setup` |
| Introduction to PostgreSQL | `introduction` |
| iotop | `iotop` |
| Joining Tables | `joining-tables` |
| Keepalived | `keepalived` |
| Lateral Join in PostgreSQL | `lateral-join` |
| Learn SQL Concepts | `learn-sql` |
| Learn Automation in PostgreSQL | `learn-to-automate` |
| Lock Management | `lock-management` |
| Logical Replication | `logical-replication` |
| Mailing Lists | `mailing-lists` |
| liquibase, sqitch, Bytebase, ora2pg etc | `migration-related-tools` |
| Modifying Data in PostgreSQL | `modifying-data` |
| Multi-Version Concurrency Control (MVCC) | `mvcc` |
| Data Normalization: Normal Forms | `normalization--normal-forms` |
| The Relational Model: Null Values | `null` |
| Object Model in PostgreSQL | `object-model` |
| Object Privileges | `object-privileges` |
| OLAP | `olap` |
| Workload Dependent Tuning | `oltp` |
| Operators in Kubernetes Deployment | `operators` |
| Package Managers | `package-managers` |
| Alternatives to Patroni for PostgreSQL Cluster Management | `patroni-alternatives` |
| Patroni | `patroni` |
| Practical Patterns and Antipatterns for Queues in PostgreSQL | `patterns--antipatterns` |
| Per-User Per-Database Settings in PostgreSQL | `per-user-per-database-setting` |
| Profiling with Perf Tools | `perf-tools` |
| PEV2 | `pev2` |
| Backup Recovery Tools: pg_basebackup | `pg_basebackup` |
| pg_dump: A PostgreSQL Backup Tool | `pg_dump` |
| pg_dumpall: Backing Up Entire PostgreSQL Clusters | `pg_dumpall` |
| PostgreSQL Security: pg_hba.conf | `pg_hbaconf` |
| Pg_probackup | `pg_probackup` |
| pg_restore | `pg_restore` |
| Pg Stat Activity | `pg_stat_activity` |
| Pg Stat Statements | `pg_stat_statements` |
| pgBackRest: A Comprehensive Backup and Recovery Solution | `pgbackrest` |
| PgBadger | `pgbadger` |
| Connection Pooling: Alternatives to PgBouncer | `pgbouncer-alternatives` |
| PgBouncer | `pgbouncer` |
| pgcenter | `pgcenter` |
| pgCluu | `pgcluu` |
| Skytools PGQ | `pgq` |
| Physical Storage and File Layout | `physical-storage-and-file-layout` |
| PL/pgSQL - Procedural Language for PostgreSQL | `plpgsql` |
| PostgreSQL Anonymizer | `postgresql-anonymizer` |
| PostgreSQL vs NoSQL | `postgresql-vs-nosql-databases` |
| PostgreSQL vs. Other Databases | `postgresql-vs-other-rdbms` |
| Practical Patterns for Migrations | `practical-patterns--antipatterns` |
| Procedures and Functions in PostgreSQL | `procedures-and-functions` |
| Process Memory Architecture in PostgreSQL | `processes--memory-architecture` |
| Prometheus: An Effective Monitoring Tool | `prometheus` |
| Puppet: Configuration Management for PostgreSQL | `puppet` |
| Queries in PostgreSQL | `queries` |
| Query Planner in PostgreSQL | `query-planner` |
| Query Processing in PostgreSQL | `query-processing` |
| Querying Data | `querying-data` |
| RDBMS Benefits and Limitations | `rdbms-benefits-and-limitations` |
| Recursive CTE (Common Table Expressions) | `recursive-cte` |
| Troubleshooting Methods: Analyzing 'red' Situations | `red` |
| Relational Model | `relational-model` |
| Relations in the Relational Model | `relations` |
| Replication in PostgreSQL | `replication` |
| （其余 47 个略） | — |

## 4. 与相邻内容的关系

- 属于“数据”这一类；与相邻方向的差别见 `00_direction_map.md` 的区分方法。
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
