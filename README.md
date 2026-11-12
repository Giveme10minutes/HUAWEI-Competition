# 职业探索与学习行动 Agent

面向计算机相关专业大学生的职业探索助手，也是华为 ICT 大赛创新赛赛题二的项目原型。从一句「我学过一点 Python，但还不知道以后想做什么」开始，学生可以回顾自己的经历、比较感兴趣的方向，再选一项小任务亲手试试。

## 体验流程

1. **聊经历，整理线索**：说说做过什么、在哪些环节有成就感或遇到困难。点击「整理线索」，对照自己的原话审核候选线索，确认后可用于后续对话。
2. **定目标，拆行动**：请助手根据基础和可投入时间给出阶段规划。点击「整理规划」，检查并编辑行动的目标、步骤、成果和验收标准，再确认这一版。
3. **做任务，带着结果回来**：从「学习行动」选择一项任务开始学习或反馈成果。原任务要求会填入输入框，学生可以补充进展和困难，再发送给助手讨论。后续调整可保留规划版本。

可以用这三句话体验从探索到行动的过程：

> 我是大一学生，学过一点 Python。我帮班里整理过报名表，但还不知道自己更喜欢写程序还是整理数据。
>
> 我想用 Python 试着找出报名表里的重复项。帮我安排一个一周内能完成的小计划。
>
> 我已经能读入 CSV，但同一个名字前后有空格时查不出来。能带我做下一步吗？

第二轮得到回答后，点击「整理规划」，编辑并确认，再到「学习行动」打开任务。

## 项目结构

网页使用 **React、TypeScript 和 shadcn/ui**，由 **FastAPI** 提供服务。后端通过 **HTTP/SSE** 调用已部署的 **华为云 AgentArts** 应用，网页逐步展示回复。对话、线索和规划版本保存在本地 **SQLite**，线索与规划由用户确认后用于后续对话。

当前为单用户本地原型。成果反馈通过对话进行，行动栏展示当前确认版规划中的任务。上游回复是否实时增量到达，取决于已部署的工作流配置。

| 目录 | 内容 |
| --- | --- |
| `frontend/` | 对话界面、探索记录和学习行动 |
| `backend/` | Web API、AgentArts 接入与本地数据存储 |
| `prompts/`、`data/knowledge_seed/` | 提示词版本和知识资料整理样例 |
| `scripts/`、`tests/` | 启动、调试和后端测试 |
| `docs/` | 需求、工作流搭建、验证与开发记录 |

## 本地运行

已使用 Python 3.15.2 和 Node.js 24 验证。在仓库根目录安装依赖并构建前端：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-web.txt
npm --prefix frontend ci
npm --prefix frontend run build
```

首次配置时，将 [`.env.example`](.env.example) 复制为根目录的 `.env`。如已有 `.env`，直接编辑现有文件。发送消息需要已部署的 AgentArts 应用，填写以下两项：

- `AGENTARTS_LOWCODE_URL`：应用部署后提供的完整 HTTP 调用地址。
- `AGENTARTS_LOWCODE_API_KEY`：该应用的 API Key，由后端读取并保存在本地配置中。

```bash
.venv/bin/python scripts/run_web.py
```

浏览器打开 <http://127.0.0.1:8000>。数据库默认位于 `local_data/app.sqlite3`。

重新录制 Demo 前，可用根目录的 `清空Demo数据.command` 清除本地对话、线索和规划。操作细节见 [Demo 数据清理说明](docs/Demo数据一键清空.md)。

## 开发文档

- [产品需求 v0.5](docs/职业探索与学习行动Agent_需求文档_v0.1.md)
- [AgentArts 主工作流搭建说明](docs/模型主流程JSONL_v0.1_2026-11-08.md)
- [AgentArts 接入与记录联动实测](docs/Agent与探索记录联动_v0.1_2026-11-08.md)
- [开发进度](docs/progress.md) · [技术与产品决策](docs/decisions.md) · [协作约定](AGENTS.md)
