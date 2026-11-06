# Terraform：用代码管理基础设施

Terraform 是 HashiCorp 的基础设施即代码工具，用 HCL 描述云资源与配置。它通过 plan 预览变更、通过 apply 创建或修改资源，并把资源状态记录在 state 文件中，使重复执行的结果可预期。

来源：主题名称取自 roadmap.sh 的 Terraform 路线索引（https://roadmap.sh/terraform）；定位说明为整理者归纳。

## Terraform 是什么：基础设施即代码

手动在控制台点选资源难以复现和审查，环境之间也容易出现配置漂移。Terraform 把基础设施写成版本可控的配置文件，执行前先计算差异，让变更可以被审阅、复用和回滚。

参考：Terraform 官方文档（https://developer.hashicorp.com/terraform/intro）。

## Terraform 的核心概念：Provider、资源与数据源

Provider 负责与具体平台通信，资源描述要创建或管理的对象，数据源用于读取已有信息。变量接收外部输入，输出把结果暴露给其他配置或命令。

相关概念（6 项）：Provider（平台插件与认证）、资源（被管理的对象）、数据源（读取已有信息）、变量（外部输入参数）、输出（结果暴露）、模块（可复用的配置集合）。

参考：Terraform 官方文档（https://developer.hashicorp.com/terraform/docs）。

## Terraform 的执行流程与状态

一次变更通常经过 init、fmt、validate、plan 和 apply 几步，plan 展示将要新增、修改或删除的资源。state 记录配置与真实资源的对应关系，多人协作时应使用远程状态并开启锁定。

相关命令（6 项）：terraform init（初始化插件与后端）、terraform fmt（格式化配置）、terraform validate（检查语法与引用）、terraform plan（预览变更）、terraform apply（执行变更）、terraform destroy（销毁资源）。

参考：Terraform 官方文档状态部分（https://developer.hashicorp.com/terraform/language/state）。

## Terraform 的变量、模块与环境隔离

把可变部分抽成变量、把重复结构抽成模块，可以减少复制粘贴。不同环境可以用独立的变量文件、工作区或独立状态目录隔离，避免一次操作影响多个环境。

相关机制（5 项）：输入变量（参数化配置）、局部值（复用表达式结果）、输出值（暴露模块结果）、模块（复用一组资源）、工作区（隔离多套状态）。

来源：主题名称取自 roadmap.sh 的 Terraform 路线索引（https://roadmap.sh/terraform）；说明为整理者归纳。

## Terraform 的典型使用场景与协作

Terraform 常用于创建网络、计算、存储和权限等基础设施，也用于在 CI 流程中审查变更。团队协作时通常把配置放进版本控制，用代码评审检查 plan 结果，并配合格式检查与安全扫描工具。

相关工具（6 项）：Terraform Registry（查找 Provider 与模块）、TFLint（配置静态检查）、Checkov（安全策略检查）、Trivy（配置与镜像扫描）、Terragrunt（多环境配置封装）、GitHub Actions（流水线执行）。

来源：主题名称取自 roadmap.sh 的 Terraform 路线索引（https://roadmap.sh/terraform）；工具用途为整理者归纳。

## 如何开始练习 Terraform

最小练习是用本地或容器 Provider 创建一个小资源（例如生成一个文件或启动一个容器），依次执行 init、plan、apply，修改参数后再 plan 观察差异，最后 destroy 清理。产出是配置目录、执行记录和一份状态文件说明。

来源：该练习由整理者归纳设计；主题名称取自 roadmap.sh 的 Terraform 路线索引（https://roadmap.sh/terraform）。
