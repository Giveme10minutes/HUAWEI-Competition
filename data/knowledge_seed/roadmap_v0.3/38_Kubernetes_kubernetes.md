# Kubernetes：容器编排平台

Kubernetes 是开源的容器编排系统，负责在多台机器上调度容器、维持期望副本数、提供服务发现与滚动更新。它用声明式配置描述期望状态，由控制平面持续把实际状态调整到期望状态。

来源：主题名称取自 roadmap.sh 的 Kubernetes 路线索引（https://roadmap.sh/kubernetes）；定位说明为整理者归纳。

## Kubernetes 是什么：解决什么问题

手工在多台服务器上启动、重启和扩缩容器容易出错，也无法快速应对故障。Kubernetes 把容器放进集群统一调度，按配置维护副本数量，并在节点或容器异常时自动重建。

参考：Kubernetes 官方文档（https://kubernetes.io/docs/concepts/overview/）。

## Kubernetes 的核心对象：Pod、Deployment 与 Service

Pod 是最小的调度单位，包含一个或多个共享网络的容器；Deployment 管理 Pod 的副本与滚动更新；Service 为一组 Pod 提供稳定访问入口。实际应用通常由这些对象组合描述。

相关对象（6 项）：Pod（最小调度单位）、Deployment（副本与滚动更新）、ReplicaSet（维持副本数量）、Service（稳定访问入口）、Ingress（HTTP 路由规则）、Namespace（资源分组隔离）。

参考：Kubernetes 官方文档（https://kubernetes.io/docs/concepts/）。

## Kubernetes 的配置与存储：ConfigMap、Secret 与卷

应用配置和凭据不应直接写进镜像，ConfigMap 保存普通配置，Secret 保存敏感值，两者都可以挂载为文件或注入为环境变量。需要持久化的数据则通过卷和存储类声明。

相关对象（6 项）：ConfigMap（保存非敏感配置）、Secret（保存敏感配置）、Volume（容器挂载的存储）、PersistentVolume（集群级存储资源）、PersistentVolumeClaim（存储使用声明）、StorageClass（存储类型与供应方式）。

参考：Kubernetes 官方文档（https://kubernetes.io/docs/concepts/）。

## Kubernetes 的部署与扩缩容

Deployment 支持滚动更新与回滚，更新时逐步替换旧 Pod，出现问题时可以退回上一版本。扩缩容既可以手动调整副本数，也可以依据 CPU、内存等指标自动伸缩。

相关机制（6 项）：滚动更新（逐步替换 Pod）、回滚（恢复到上一版本）、HPA（按指标自动扩缩副本）、资源请求（调度所需资源）、资源限制（容器可用上限）、亲和性（控制 Pod 调度位置）。

来源：主题名称取自 roadmap.sh 的 Kubernetes 路线索引（https://roadmap.sh/kubernetes）；机制说明为整理者归纳。

## Kubernetes 的可观测性与生态工具

集群运行后需要知道 Pod 是否健康、请求是否变慢、日志在哪里。常用做法是暴露指标、集中收集日志与追踪请求，并用包管理或 GitOps 工具管理部署配置。

相关工具（6 项）：kubectl（集群命令行）、Helm（应用包管理）、Prometheus（指标采集）、Grafana（指标展示）、Fluent Bit（日志采集）、Argo CD（GitOps 持续交付）。

来源：主题名称取自 roadmap.sh 的 Kubernetes 路线索引（https://roadmap.sh/kubernetes）；工具用途为整理者归纳。

## 如何开始练习 Kubernetes

最小练习是用本地集群工具启动单节点集群，用 kubectl 创建一个 Deployment 并扩容到多个副本，再创建 Service 访问应用，修改镜像触发滚动更新并回滚。产出是一组 YAML 清单和一份操作记录。

来源：该练习由整理者归纳设计；主题名称取自 roadmap.sh 的 Kubernetes 路线索引（https://roadmap.sh/kubernetes）。
