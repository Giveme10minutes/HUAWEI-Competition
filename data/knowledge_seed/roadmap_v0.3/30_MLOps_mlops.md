# MLOps：把模型训练到部署串成工程链路

MLOps 指把 DevOps 的协作与自动化做法用于机器学习系统，覆盖数据、训练、模型部署和线上监控的整条链路。它不是一个单独软件，而是一组实践与工具的组合；具体落地方式随团队规模和数据形态变化。

参考：Microsoft Learn《MLOps model management with Azure Machine Learning》（https://learn.microsoft.com/en-us/azure/machine-learning/concept-model-management-and-deployment?view=azureml-api-2）。

## MLOps 是什么

机器学习系统除了代码，还依赖数据、模型文件和运行环境，任何一项变化都可能影响结果。MLOps 关注这些要素的版本、复现与追踪，让模型从实验走到生产后仍能被观察、回滚和更新；Microsoft 把它描述为基于 DevOps 原则管理模型生命周期。

参考：Microsoft Learn《MLOps model management with Azure Machine Learning》（https://learn.microsoft.com/en-us/azure/machine-learning/concept-model-management-and-deployment?view=azureml-api-2）。

## MLOps 的常见工作内容与交付

常见工作包括把数据准备、训练、评估和部署串成可重复的流水线，管理模型与环境的版本，建立上线审批和回滚路径，并监控数据漂移与运行故障。交付物可能是流水线定义、模型注册记录、部署清单、监控面板和定期重训任务。

来源：主题名称取自 roadmap.sh 的 MLOps 路线索引（https://roadmap.sh/mlops）；用途说明为整理者归纳。

## MLOps 涉及的技术与方法

这一方向把数据工程、模型训练和运维实践接在一起，工具数量多且职责容易重叠。下列名称按常见用途列出，具体团队不必全部采用。

相关技术（9 项）：版本控制（管理代码与配置）、数据版本管理（追踪数据集）、实验跟踪（记录训练结果）、模型注册表（管理模型版本）、容器（打包运行环境）、流水线编排（调度训练与部署）、持续集成与交付（自动构建发布）、监控告警（发现漂移与故障）、特征存储（复用特征）。

来源：主题名称取自 roadmap.sh 的 MLOps 路线索引（https://roadmap.sh/mlops）；用途说明为整理者归纳。

## MLOps 与 DevOps、机器学习工程的区别

DevOps 主要管理应用代码的构建、测试与发布；机器学习工程主要解决数据与模型效果问题；MLOps 把两者接起来，额外处理数据版本、模型注册、漂移监控和重训。实际团队里这些职责经常由同一批人分担，边界并不固定。

来源：主题名称取自 roadmap.sh 的 MLOps 路线索引（https://roadmap.sh/mlops）；用途说明为整理者归纳。

## MLOps 尚不能确认的部分

MLOps 的成熟度模型、团队分工和工具组合没有统一标准，不同资料给出的范围差别较大。小团队是否需要完整流水线、哪些环节值得自动化，要结合数据规模和发布频率判断；本资料不把这些实践写成必须遵循的流程。

来源：定位说明为整理者编写。
