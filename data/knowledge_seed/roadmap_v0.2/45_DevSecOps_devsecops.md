# DevSecOps（devsecops）

资料ID：RM-P02-DEVSECOPS ｜ 批次：RM-P02 ｜ 版本 v0.2 ｜ 整理日期：2026-11-03
类型：新兴/专项 ｜ 所属：安全 ｜ 对应仓库路线：`roadmaps/devsecops`

## 1. 定位

把安全检查接进开发与交付流程。

## 2. 学习阶段

### 阶段 1：概念与边界

- 它解决什么问题，不解决什么问题
- 与相邻概念的区别
- 常见术语

### 阶段 2：典型工作流

- 跑通一个最小可用流程
- 评估效果与失败样例
- 成本、延迟与风险

### 阶段 3：评估与落地

- 建立评测方法
- 在真实约束下迭代
- 写清局限与适用条件

## 3. 主题清单（检索用）

以下名称取自本地仓库 `roadmaps/devsecops/content/` 的文件标题，共 **94** 个去重主题；仅作覆盖面参考，不代表必须全部学完。

| 主题 | 文件标识 |
| --- | --- |
| Access Control Lists (ACLs) | `acls` |
| Alert Types | `alert-types` |
| Asymmetric Encryption | `asymmetric` |
| Attack Surface Mapping | `attack-surface-mapping` |
| Audit & Compliance Mapping | `audit--compliance-mapping` |
| Authentication | `authentication` |
| Authorization | `authorization` |
| Automated Patching | `automated-patching` |
| Bash Scripting | `bash` |
| bcrypt | `bcrypt` |
| Build Pipeline Hardening | `build-pipeline-hardening` |
| Burp Suite | `burp-suite` |
| Certificate Lifecycle | `certificate-lifecycle` |
| CIA Triad | `cia-triad` |
| Cloud Security | `cloud-security` |
| Container Security | `container-security` |
| Containment | `containment` |
| Cryptographic Hashing | `cryptographic-hashing` |
| Cloud Security Posture Management (CSPM) | `cspm` |
| DDoS Mitigation Strategy | `ddos-miligation-strategy` |
| Defense in Depth | `defense-in-depth-concepts` |
| Dependency Risk Management | `dependency-risk-management` |
| DevSecOps vs. DevOps | `devsecops-vs-devops` |
| DNS | `dns` |
| Docker Security | `docker` |
| EDR Strategy | `edr-strategy` |
| Encryption | `encryption` |
| Endpoint Detection | `endpoint-detection` |
| Enterprise Operations | `enterprise-operations` |
| Firewalls | `firewalls` |
| Forensics | `forensics` |
| Go Programming Language | `go` |
| HTTP | `http` |
| IAM | `iam` |
| Identity and Access Management (IAM) | `iam` |
| Identity Basics | `identity-basics` |
| Intrusion Detection Systems | `ids` |
| Image Scanning | `image-scanning` |
| Incident Response | `incident-response` |
| Input Validation Patterns | `input-validation-patterns` |
| DevSecOps | `introduction` |
| Intrusion Prevention Systems | `ips` |
| IR Lifecycle | `ir-lifecycle` |
| ISO 27001 | `iso-27001` |
| JavaScript and Node.js | `javascript--nodejs` |
| Key Management Service | `key-management-service` |
| Kubernetes Security | `kubernetes` |
| Large Scale Identity Strategy | `large-scale-identity-strategy` |
| Programming Languages | `learn-a-programming-language` |
| Least Privilege | `least-privilege` |
| Log Analysis | `log-analysis` |
| Monitoring | `monitoring` |
| Multi-Region Security Planning | `multi-region-security-planning` |
| Nessus | `nessus` |
| Network Segmentation | `network-segmentation` |
| Networking Basics | `networking-basics` |
| NIST Cybersecurity Framework | `nist` |
| Nmap Basics | `nmap-basics` |
| Nmap | `nmap` |
| OpenVAS | `openvas` |
| OWASP Top 10 | `owasp-top-10` |
| PASTA | `pasta` |
| PKI Design and Failover | `pki-design-and-failover` |
| PowerShell | `powershell` |
| Python in DevSecOps | `python` |
| Qualys | `qualys` |
| Response Strategy | `response-strategy` |
| Risk Quantification | `risk-quantification` |
| Role-Based Access Control | `role-based-access` |
| Root Cause Analysis | `root-cause-analysis` |
| Ruby in DevSecOps | `ruby` |
| Rust | `rust` |
| SBOMs | `sboms` |
| Scripting Knowledge | `scripting-knowledge` |
| Secure API Design | `secure-api-design` |
| Secure Coding | `secure-coding` |
| Secure Network Zoning | `secure-network-zoning` |
| SHA-256 | `sha-256` |
| SIEM | `siem` |
| SOAR Automation | `soar-automation` |
| SOAR Concepts | `soar-concepts` |
| SOC 2 | `soc-2` |
| SQL Injection Prevention | `sql-injection-prevention` |
| STRIDE | `stride` |
| Supply Chain Security | `supply-chain-security` |
| Symmetric Encryption | `symmetric` |
| Threat Modeling Workflows | `threat-modeling-workflows` |
| Threat Modeling | `threat-modeling` |
| TLS | `tls` |
| Text Editors: Vim, Nano, and Emacs | `vim--nano--emacs` |
| VLANs | `vlans` |
| Wireshark Basics | `wireshark-basics` |
| Cross-Site Scripting (XSS) Prevention | `xss-prevention` |
| Zero Trust Concepts | `zero-trust-concepts` |

## 4. 与相邻内容的关系

- 它属于“安全”下的新兴/专项内容，边界和工具仍在变化。
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
