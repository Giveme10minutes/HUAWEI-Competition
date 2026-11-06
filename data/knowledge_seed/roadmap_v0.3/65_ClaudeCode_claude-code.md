# Claude Code：终端中的 AI 编程助手

Claude Code 是 Anthropic 提供的编程助手，以命令行方式在终端中运行，可以读取项目代码、修改文件、执行命令并根据结果继续操作。它通过自然语言指令工作，结果需要人工核对后再采用。

来源：主题名称取自 roadmap.sh 的 Claude Code 路线索引（https://roadmap.sh/claude-code）；参考 Claude Code 官方文档（https://docs.anthropic.com/en/docs/claude-code/overview）。

## Claude Code 是什么：在项目目录中工作的助手

在项目目录启动后，Claude Code 会读取当前代码与配置，接受对话式指令，并在获得许可后编辑文件或运行命令。它不止生成代码片段，而是围绕一次任务连续操作，直到完成或需要用户确认。

参考：Claude Code 官方文档（https://docs.anthropic.com/en/docs/claude-code/overview）。

## Claude Code 的常见使用方式

常见用法包括解释陌生代码、按描述修改多个文件、修复报错、补充测试和整理提交。使用时先说明目标与约束，再让它给出计划，确认之后再执行，可以减少返工。

相关用法（5 项）：解释代码（说明结构与调用）、批量修改（跨文件改动）、修复报错（定位并修改）、补充测试（编写用例）、整理提交（归纳改动）。

来源：主题名称取自 roadmap.sh 的 Claude Code 路线索引（https://roadmap.sh/claude-code）；用途说明为整理者归纳。

## Claude Code 的上下文与项目约定

助手每次只能看到有限的上下文，因此项目说明文件、目录结构和明确的指令会直接影响结果质量。把构建方式、代码规范和常用命令写进项目内的说明文件，可以复用到后续会话。

相关概念（5 项）：上下文窗口（单次可用信息量）、项目说明文件（记录项目约定）、会话（连续对话）、斜杠命令（内置操作入口）、权限确认（执行前询问）。

来源：主题名称取自 roadmap.sh 的 Claude Code 路线索引（https://roadmap.sh/claude-code）；参考 Claude Code 官方文档（https://docs.anthropic.com/en/docs/claude-code/overview）。

## Claude Code 的扩展与集成方式

Claude Code 可以接入外部工具和自定义能力，也能在编辑器或持续集成环境中调用。扩展前先确认它能读写的范围，避免让助手接触不该改动的目录或凭据。

相关方式（5 项）：MCP（连接外部工具）、子代理（拆分任务）、自定义技能（复用指令）、钩子（在事件前后执行）、无头模式（脚本化调用）。

来源：主题名称取自 roadmap.sh 的 Claude Code 路线索引（https://roadmap.sh/claude-code）；参考 Claude Code 官方文档（https://docs.anthropic.com/en/docs/claude-code/overview）。

## 如何开始练习 Claude Code

选一个自己的小项目，先让助手解释目录结构，再完成一个边界明确的小改动并运行测试。产出是一次可审查的代码差异，以及一份记录：哪些指令有效、哪些地方需要人工纠正。

来源：定位说明为整理者编写；练习设计为整理者归纳。
