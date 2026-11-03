# Terraform（terraform）

资料ID：RM-P02-TERRAFORM ｜ 批次：RM-P02 ｜ 版本 v0.2 ｜ 整理日期：2026-11-03
类型：工具/平台 ｜ 所属：云与运维 ｜ 对应仓库路线：`roadmaps/terraform`

## 1. 定位

用代码声明并管理云资源。

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

以下名称取自本地仓库 `roadmaps/terraform/content/` 的文件标题，共 **109** 个去重主题；仅作覆盖面参考，不代表必须全部学完。

| 主题 | 文件标识 |
| --- | --- |
| -replace option in apply | `-replace-option-in-apply` |
| Authentication | `authentication` |
| Basic Syntax | `basic-syntax` |
| Best Practices for State | `best-practices-for-state` |
| CaC vs IaC | `cac-vs-iac` |
| Checkov | `checkov` |
| CI / CD Integration | `ci--cd-integration` |
| Circle CI | `circle-ci` |
| Clean Up | `clean-up` |
| Compliance / Sentinel | `compliance--sentinel` |
| Configuring Providers | `configuring-providers` |
| Contract Testing | `contract-testing` |
| count | `count` |
| Creating Local Modules | `creating-local-modules` |
| Creation / Destroy Time | `creation--destroy-time` |
| Custom Provisioners | `custom-provisioners` |
| Data Sources | `data-sources` |
| depends_on | `depends_on` |
| Deployment Workflow | `deployment-workflow` |
| Deployment | `deployment` |
| End to End Testing | `end-to-end-testing` |
| Enterprise Features | `enterprise-features` |
| Environment Variables | `environment-variables` |
| file provisioner | `file-provisioner` |
| for_each | `for_each` |
| Format & Validate | `format--validate` |
| GitHub Actions | `github-actions` |
| GitLab CI | `gitlab-ci` |
| graph | `graph` |
| HashiCorp Configuration Language (HCL) | `hashicorp-config-language-hcl` |
| HCP | `hcp` |
| Import Existing Resources | `import-existing-resources` |
| Infracost | `infracost` |
| Input Variables | `input-variables` |
| Inputs / Outputs | `inputs--outputs` |
| Inspect / Modify State | `inspect--modify-state` |
| Installing Terraform | `installing-terraform` |
| Integration Testing | `integration-testing` |
| Introduction | `introduction` |
| Jenkins | `jenkins` |
| KICS | `kics` |
| lifecycle | `lifecycle` |
| list | `list` |
| local-exec provisioner | `local-exec-provisioner` |
| Local Values | `local-values` |
| Meta Arguments | `meta-arguments` |
| Modules Best Practices | `modules-best-practices` |
| Modules | `modules` |
| mv | `mv` |
| Output Syntax | `output-syntax` |
| output | `output` |
| Outputs | `outputs` |
| Parallelism | `parallelism` |
| Preconditions | `preconditions` |
| Project Initialization | `project-initialization` |
| provider | `provider` |
| Providers | `providers` |
| Provisioners | `provisioners` |
| Published Modules Usage | `published-modules-usage` |
| remote-exec provisioner | `remote-exec-provisioner` |
| Remote State | `remote-state` |
| Resource Behavior | `resource-behavior` |
| Resource Lifecycle | `resource-lifecycle` |
| Resources | `resources` |
| rm | `rm` |
| Root vs Child Modules | `root-vs-child-modules` |
| Run Tasks | `run-tasks` |
| Scaling Terraform | `scaling-terraform` |
| Secret Management | `secret-management` |
| Security | `security` |
| Sensitive Data | `sensitive-data` |
| Sensitive Outputs | `sensitive-outputs` |
| show | `show` |
| Splitting Large State | `splitting-large-state` |
| Splitting State Files | `splitting-state-files` |
| state force-unlock | `state-force-unlock` |
| State Locking | `state-locking` |
| state pull / push | `state-pull--push` |
| state replace-provider | `state-replace-provider` |
| State | `state` |
| Template Files | `template-files` |
| terraform apply | `terraform-apply` |
| terraform destroy | `terraform-destroy` |
| terraform fmt | `terraform-fmt` |
| terraform plan | `terraform-plan` |
| Terraform Registry | `terraform-registry` |
| terraform validate | `terraform-validate` |
| Terragrunt | `terragrunt` |
| Terrascan | `terrascan` |
| Testing Modules | `testing-modules` |
| Testing | `testing` |
| TFLint | `tflint` |
| Trivy | `trivy` |
| Type Constraints | `type-constraints` |
| Unit Testing | `unit-testing` |
| Benefits of Terraform | `usecases-and-benefits` |
| Validation Rules | `validation-rules` |
| Variable Definition File | `variable-definition-file` |
| Variables | `variables` |
| VCS Integration | `vcs-integration` |
| Version Management | `version-management` |
| Versioning | `versioning` |
| Versions | `versions` |
| What and when to use HCP? | `what-and-when-to-use-hcp` |
| What is HCL? | `what-is-hcl` |
| What is Infrastructure as Code? | `what-is-infrastructure-as-code` |
| What is Terraform? | `what-is-terraform` |
| When to Use? | `when-to-use` |
| Workspaces | `workspaces` |

## 4. 与相邻内容的关系

- 它是“云与运维”场景下的工具/平台，价值取决于是否接进真实流程。
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
