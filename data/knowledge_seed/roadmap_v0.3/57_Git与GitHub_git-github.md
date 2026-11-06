# Git 与 GitHub：版本控制与代码托管协作

Git 是分布式版本控制系统，GitHub 是基于 Git 的代码托管与协作平台。两者常一起使用：本地用 Git 记录提交，远程用 GitHub 保存仓库、评审改动并运行自动化流程。

来源：主题名称取自 roadmap.sh 的 Git 与 GitHub 路线索引（https://roadmap.sh/git-github）；用途说明为整理者归纳。

## Git 与 GitHub 是什么：本地版本库与远程托管

Git 在本地保存完整历史，提交、分支和合并都不依赖网络；GitHub 提供远程仓库、账号权限和网页界面，让多人围绕同一仓库协作。没有 GitHub 也能使用 Git，接入平台主要是为了共享、评审和自动化。

参考：GitHub Docs（https://docs.github.com/en）。

## Git 的核心概念与常用命令

Git 用提交记录文件快照，用分支隔离并行改动，用暂存区决定哪些修改进入下一次提交。远程仓库通过抓取和推送同步，合并与变基负责把不同分支的历史接起来。

相关命令（7 项）：clone（复制远程仓库）、add（暂存改动）、commit（生成提交）、branch（管理分支）、merge（合并分支）、rebase（重排提交）、push（推送远程）。

来源：主题名称取自 roadmap.sh 的 Git 与 GitHub 路线索引（https://roadmap.sh/git-github）；命令用途为整理者归纳。

## GitHub 的协作方式：Issue、Pull Request 与评审

GitHub 用 Issue 记录任务与缺陷，用 Pull Request 提出改动并邀请评审，评审意见以行内评论呈现。合并前通常要求评审通过与自动化检查通过，合并后相关 Issue 可以被关闭。

相关环节（6 项）：Issue（记录任务与缺陷）、Pull Request（提出并讨论改动）、Code Review（行内评审）、分支保护（限制直接推送）、标签（分类与筛选）、里程碑（归组任务）。

来源：参考 GitHub Docs（https://docs.github.com/en）；主题名称取自 roadmap.sh 的 Git 与 GitHub 路线索引（https://roadmap.sh/git-github）。

## GitHub Actions：自动化检查与发布

GitHub Actions 用配置文件描述工作流，在仓库事件发生时执行任务，例如推送后运行测试、合并后构建产物、打标签时发布版本。一条工作流由触发条件、任务和步骤组成。

相关概念（5 项）：Workflow（工作流定义）、Job（任务单元）、Step（执行步骤）、Runner（执行环境）、Secret（加密配置值）。

来源：参考 GitHub Docs（https://docs.github.com/en）；用途说明为整理者归纳。

## GitHub 的仓库设置与访问控制

仓库可以设为公开或私有，并通过分支保护、成员角色和密钥扫描控制谁能修改什么。依赖更新与安全告警能提示已知漏洞，但告警的影响仍需人工判断。

相关设置（5 项）：可见性（公开或私有）、协作者（成员权限）、分支保护规则（限制合并方式）、SSH 密钥（免密推送）、安全告警（提示依赖漏洞）。

来源：参考 GitHub Docs（https://docs.github.com/en）；说明为整理者归纳。

## 如何开始练习 Git 与 GitHub

新建一个仓库，从空目录开始：初始化、提交第一个版本、开分支修改、发起 Pull Request 并自己评审一次，再合并回主分支。产出是一条可见的提交历史和一个完成合并的 Pull Request。

来源：定位说明为整理者编写；练习设计为整理者归纳。
