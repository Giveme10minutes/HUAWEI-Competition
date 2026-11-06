# OpenClaw：在自己机器上运行的开源 AI 助手

OpenClaw 是一个开源的个人 AI 助手项目，代码托管在 GitHub 的 openclaw/openclaw 仓库，采用 MIT 许可证，主要用 TypeScript 编写。它运行在使用者自己的设备上，通过常见的聊天应用接收指令，可处理邮件、日程等个人事务。

来源：主题名称取自 roadmap.sh 的 OpenClaw 路线索引（https://roadmap.sh/openclaw）；参考 OpenClaw 官网（https://openclaw.ai/）与 GitHub 仓库（https://github.com/openclaw/openclaw）。

## OpenClaw 是什么：本地运行的个人助手

与在网页里直接使用的聊天产品不同，OpenClaw 需要使用者自己安装并常驻运行，模型、记忆和数据都由使用者配置与保管。官网把它描述为运行在自己机器上、开源且不依赖商业托管层的助手。

参考：OpenClaw 官网（https://openclaw.ai/）。

## OpenClaw 的核心概念：网关、渠道与代理循环

OpenClaw 由一个常驻网关接收各聊天渠道的消息，再交给代理循环处理：读取上下文、调用工具、生成回复。记忆、技能与插件决定它能做什么，模型供应商则决定由哪个模型生成回答。

相关概念（6 项）：网关（常驻的消息入口）、渠道（对接聊天应用）、代理循环（任务执行流程）、记忆（保存长期信息）、技能（可复用的能力包）、插件（扩展功能模块）。

来源：主题名称取自 roadmap.sh 的 OpenClaw 路线索引（https://roadmap.sh/openclaw）；概念解释参考 OpenClaw 文档（https://docs.openclaw.ai/）。

## OpenClaw 的安装与日常操作

官方提供安装脚本和 npm 全局安装两种方式，首次运行通过引导命令完成模型与渠道配置。日常维护包括查看渠道状态、检查运行环境、更新版本和备份配置。

相关命令（5 项）：openclaw onboard（首次配置引导）、openclaw gateway（启动网关）、openclaw channels（管理聊天渠道）、openclaw doctor（检查运行状态）、openclaw update（更新版本）。

来源：参考 OpenClaw 官网安装说明（https://openclaw.ai/）；命令行名称为整理者根据公开文档归纳。

## OpenClaw 的安全与运行边界

因为助手能读取消息并执行操作，部署时要限制谁能给它发指令、它能访问哪些文件和网络。官方文档建议绑定本机地址、设置网关令牌、避免使用高权限账号运行，并在配置变更后执行安全检查。

相关做法（5 项）：网关令牌（限制访问）、发送者白名单（限定指令来源）、非 root 运行（降低权限）、只读起步（先限制操作范围）、安全审计（检查配置风险）。

来源：主题名称取自 roadmap.sh 的 OpenClaw 路线索引（https://roadmap.sh/openclaw）；安全建议参考 OpenClaw 文档（https://docs.openclaw.ai/）。

## OpenClaw 尚不能确认的部分

公开资料可以确认它是开源的本地个人助手，但不同版本的功能范围、渠道支持程度和部署要求会变化，本资料不写具体版本号，也不承诺某项功能一定可用。它与编程专用助手的差异、在团队场景中的实际效果，公开资料不足以确认，需要以官方文档和实际试用为准。

来源：定位说明为整理者编写；不确定项为整理者归纳。

## 如何开始练习 OpenClaw

在一台可恢复的机器或隔离环境里安装，先只接一个聊天渠道并限定只允许自己发消息，再完成一次“查询日程并回复”的任务。产出是一次可复现的对话记录和一份配置备份。

来源：定位说明为整理者编写；练习设计为整理者归纳。
