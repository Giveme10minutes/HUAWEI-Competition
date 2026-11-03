# Linux（linux）

资料ID：RM-P02-LINUX ｜ 批次：RM-P02 ｜ 版本 v0.2 ｜ 整理日期：2026-11-03
类型：平台 ｜ 所属：基础设施 ｜ 对应仓库路线：`roadmaps/linux`

## 1. 定位

服务器操作系统与命令行工作方式。

## 2. 学习阶段

### 阶段 1：平台模型

- 平台的核心概念与权限模型
- 控制台/命令行基本操作
- 最小可用资源

### 阶段 2：核心服务

- 常用服务与组合方式
- 网络、存储与访问控制
- 成本与配额

### 阶段 3：工程化

- 用代码管理资源
- 监控、备份与恢复
- 多环境与团队协作

## 3. 主题清单（检索用）

以下名称取自本地仓库 `roadmaps/linux/content/` 的文件标题，共 **102** 个去重主题；仅作覆盖面参考，不代表必须全部学完。

| 主题 | 文件标识 |
| --- | --- |
| Adding Disks | `adding-disks` |
| Archiving and Compressing | `archiving-and-compressing` |
| Authentication Logs | `authentication-logs` |
| Available Memory and Disk | `available-memory--disk` |
| AWK | `awk` |
| Background and Foreground Processes | `background--foreground-processes` |
| Linux Navigation Basics: Basic Commands | `basic-commands` |
| Boot Loaders | `boot-loaders` |
| Booting Linux | `booting-linux` |
| Cgroups | `cgroups` |
| Checking Service Logs | `checking-service-logs` |
| Checking Service Status | `checking-service-status` |
| Command Help | `command-help` |
| Command Path in Shell | `command-path` |
| Conditionals | `conditionals` |
| Container Runtime | `container-runtime` |
| Containerization | `containerization` |
| Copying and Renaming Files | `copying-and-renaming` |
| Create, Update, and Delete Users | `create--delete--update` |
| Creating Files | `creating--deleting-files--dirs` |
| Creating Services | `creating-new-services` |
| Cut Command | `cut` |
| Debugging | `debugging` |
| DHCP | `dhcp` |
| Understanding Directory Hierarchy | `directory-hierarchy-overview` |
| Disks and Filesystems | `disks-and-filesystems` |
| DNS Resolution | `dns-resolution` |
| Docker | `docker` |
| Editing Files | `editing-files` |
| Environment Variables | `environment-variables` |
| Ethernet, ARP and RARP | `ethernet--arprarp` |
| Expand | `expand` |
| File Permissions | `file-permissions` |
| File Transfer | `file-transfer` |
| Filesystems | `filesystems` |
| Finding and Installing Packages | `finding--installing-packages` |
| GREP | `grep` |
| Head Command | `head` |
| ICMP | `icmp` |
| Inodes | `inodes` |
| Install, Remove, and Upgrade Packages | `install--remove--upgrade-packages` |
| IP Routing | `ip-routing` |
| join Command | `join` |
| Kill Processes | `killing-processes` |
| Listing and Finding Processes | `listing--finding-processes` |
| Listing Installed Packages | `listing-installed-packages` |
| Literals | `literals` |
| System Logs | `logs` |
| Loops | `loops` |
| LVM (Logical Volume Manager) | `lvm` |
| Permissions | `managing-permissions` |
| Mounts | `mounts` |
| Moving Files | `moving-files--directories` |
| Nano: A File Editing Tool | `nano` |
| Navigation Basics | `navigation-basics` |
| Netfilter | `netfilter` |
| Netstat | `netstat` |
| Networking | `networking` |
| NL (Number Lines) | `nl` |
| Package Management | `package-management` |
| Repositories | `package-repositories` |
| Packet Analysis | `packet-analysis` |
| Paste | `paste` |
| Ping | `ping` |
| Pipe Commands | `pipe` |
| Process Forking | `process-forking` |
| Process Management | `process-management` |
| Process Priorities | `process-priorities` |
| Process Signals | `process-signals` |
| Redirects | `redirects` |
| Server Review | `server-review` |
| Service Management | `service-management-systemd` |
| Running Services | `services-running` |
| Shell Basics | `shell-and-other-basics` |
| Shell Programming | `shell-programming` |
| Snap | `snap` |
| Soft and Hard Links | `soft-links--hard-links` |
| Sort | `sort` |
| Split Command | `split` |
| SSH | `ssh` |
| Starting / Stopping Services | `starting--stopping-services` |
| Stdout, Stdin, and Stderr | `stdout--stdin--stderr` |
| Subnetting | `subnetting` |
| Super User | `super-user` |
| Swap Space | `swap` |
| Tail Command | `tail` |
| TCP/IP | `tcpip-stack` |
| Tee | `tee` |
| Text Processing | `text-processing` |
| Tr-Command | `tr` |
| Traceroute | `traceroute` |
| Troubleshooting | `troubleshooting` |
| Ulimits | `ulimits` |
| Unexpand | `unexpand` |
| Uniq | `uniq` |
| Uptime and Load | `uptime-and-load` |
| User Management | `user-management` |
| Users and Groups | `users-and-groups` |
| Variables | `variables` |
| Vim: An Essential Tool for Editing Files | `vim` |
| WC - Text Processing | `wc` |
| Working with Files | `working-with-files` |

## 4. 与相邻内容的关系

- 它是“基础设施”场景下的工具/平台，价值取决于是否接进真实流程。
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
