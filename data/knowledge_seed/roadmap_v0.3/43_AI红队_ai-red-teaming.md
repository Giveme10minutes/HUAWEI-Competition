# AI 红队：在授权范围内测试 AI 系统的滥用风险

AI 红队指在获得授权的前提下，以对抗视角系统测试 AI 模型与应用，寻找有害输出、安全绕过和滥用风险。它源自传统安全红队，但在大模型场景下范围扩展到内容危害、提示注入和数据泄漏等问题，业界尚无统一界定。

参考：Microsoft Learn《Planning red teaming for large language models (LLMs) and their applications》（https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/red-teaming）。

## AI 红队是什么

常见做法是让测试者像攻击者一样使用产品，记录哪些输入能诱导出不该出现的行为，再把发现整理成可复现的案例。Microsoft 的指南强调，红队测试既覆盖基座模型，也覆盖实际应用与界面，并且不能替代系统化的测量与缓解。

参考：Microsoft Learn《Planning red teaming for large language models (LLMs) and their applications》（https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/red-teaming）。

## AI 红队的常见工作内容与交付

工作通常从确定范围与授权边界开始，明确测哪些功能、哪些危害、发现如何记录和披露，再安排开放式探索与定向复测。交付物包括测试计划、问题清单、复现步骤、危害分类和报告；报告需要区分“发现了案例”和“测出了比例”。

来源：主题名称取自 roadmap.sh 的 AI Red Teaming 路线索引（https://roadmap.sh/ai-red-teaming）；用途说明为整理者归纳。

## AI 红队涉及的技术与方法

这一方向既需要安全测试思路，也需要对模型行为和应用结构的基本理解。下列名称覆盖常见测试环节，具体方法要结合产品形态与授权范围选择。

相关方法（9 项）：威胁建模（梳理风险面）、对抗提示（诱导有害输出）、越狱测试（绕过安全限制）、提示注入（操纵上下文）、数据提取测试（探测数据泄漏）、自动化测试（批量生成用例）、人工评审（判断危害程度）、日志记录（保留复现信息）、缓解复测（验证修复效果）。

来源：主题名称取自 roadmap.sh 的 AI Red Teaming 路线索引（https://roadmap.sh/ai-red-teaming）；用途说明为整理者归纳。

## AI 红队与渗透测试、AI 安全评估的区别

传统渗透测试关注系统漏洞与权限突破；AI 红队更关注模型行为、内容危害和滥用路径；AI 安全评估则偏向可重复的指标测量。红队擅长发现未知问题，但不负责证明问题有多普遍，两者需要配合。

来源：主题名称取自 roadmap.sh 的 AI Red Teaming 路线索引（https://roadmap.sh/ai-red-teaming）；用途说明为整理者归纳。

## AI 红队尚不能确认的部分

AI 红队的范围、方法、报告规范和授权流程在不同组织间差异很大，公开资料没有统一标准。它与其他安全测试如何分工、需要哪些资质，公开资料不足以确认；本资料不提供法律意见，也不把某套工具写成通用方案。

来源：定位说明为整理者编写。
