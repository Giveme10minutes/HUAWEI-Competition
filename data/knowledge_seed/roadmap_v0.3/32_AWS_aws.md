# AWS：亚马逊云服务平台

AWS 是 Amazon 提供的云计算平台，按服务类别提供计算、存储、数据库、网络、身份与监控等能力。使用者可以通过控制台、命令行或 API 创建资源，并按需组合这些服务搭建应用。

来源：主题名称取自 roadmap.sh 的 AWS 路线索引（https://roadmap.sh/aws）；定位说明为整理者归纳。

## AWS 是什么：云服务的分类与使用方式

云平台把服务器、存储和网络等资源做成可编程的服务，使用者不必先采购硬件。AWS 的服务数量很多，学习时通常先按用途分类，再挑选少量服务完成一个小架构，而不是逐个记忆服务名。

参考：AWS 官方概览（https://docs.aws.amazon.com/whitepapers/latest/aws-overview/introduction.html）。

## AWS 的核心概念：区域、可用区与共享责任

AWS 把基础设施划分为区域，区域内部再划分为多个可用区，资源部署位置会影响延迟与容灾设计。共享责任模型说明云厂商负责底层设施安全，使用者负责账号权限、数据与配置的安全。

相关概念（5 项）：区域（资源部署的地理位置）、可用区（区域内相互隔离的机房）、VPC（隔离的虚拟网络）、IAM（身份与权限管理）、共享责任模型（安全职责划分）。

参考：AWS 官方概览（https://docs.aws.amazon.com/whitepapers/latest/aws-overview/introduction.html）。

## AWS 的计算与存储服务类别

计算服务覆盖虚拟机、容器和无服务器函数，存储服务则按对象、块和归档等形态区分。选择时主要看运行方式、数据访问模式和运维承担程度，而不是服务数量。

相关服务（6 项）：EC2（虚拟机实例）、Lambda（无服务器函数）、ECS（容器编排）、EKS（托管 Kubernetes）、S3（对象存储）、EBS（块存储卷）。

来源：主题名称取自 roadmap.sh 的 AWS 路线索引（https://roadmap.sh/aws）；服务分类为整理者归纳。

## AWS 的数据库与网络服务类别

数据库服务包括托管关系型数据库、键值数据库和内存缓存；网络服务负责域名解析、内容分发和流量入口。它们常与计算服务组合成一个完整应用。

相关服务（6 项）：RDS（托管关系型数据库）、DynamoDB（键值与文档数据库）、ElastiCache（托管内存缓存）、Route 53（DNS 与域名解析）、CloudFront（内容分发网络）、Elastic Load Balancing（负载均衡）。

来源：主题名称取自 roadmap.sh 的 AWS 路线索引（https://roadmap.sh/aws）；服务分类为整理者归纳。

## AWS 的权限与运维：IAM 与 CloudWatch

IAM 用用户、角色和策略描述谁可以对什么资源做什么，应按最小权限分配。CloudWatch 收集指标与日志，用于观察资源状态和设置告警；CloudTrail 记录账号内的 API 调用，便于审计。

相关工具（5 项）：IAM 用户（长期身份）、IAM 角色（临时授权身份）、IAM 策略（权限声明）、CloudWatch（指标、日志与告警）、CloudTrail（API 调用审计）。

来源：主题名称取自 roadmap.sh 的 AWS 路线索引（https://roadmap.sh/aws）；工具用途为整理者归纳。

## 如何开始练习 AWS

最小练习是在测试账号中创建一个仅具必要权限的 IAM 用户，启动一台最小规格实例并配置安全组，创建一个 S3 桶上传文件，再用 CloudWatch 查看一项指标，完成后删除全部资源。产出是一份资源清单和操作记录。

来源：该练习由整理者归纳设计；主题名称取自 roadmap.sh 的 AWS 路线索引（https://roadmap.sh/aws）。
