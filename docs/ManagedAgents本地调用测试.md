# Managed Agents 本地调用测试

后续更新：已完成真实云端连通与基础对话检查，结果及问题见 [首次云端调用测试](首次云端调用测试_2026-11-02.md)。下文“未验证”描述为最初准备状态，当前实测以该记录为准。

记录日期：2026-11-02。当前状态：用户确认已简单创建智能体；未验证云端调用，不代表正式产品已开工或完成验收。

## 官方依据与本地资料

- [创建 Managed Agents](https://support.huaweicloud.com/qs-agentarts/agentarts_04_0003.html)，读取时页面更新时间为 2026-10-26。
- [页面读取快照](../references/official/agentarts/2026-11-02/agentarts_04_0003.web.txt)：网页读取工具返回的正文与链接，含导航、行号等，不是原始 HTML。
- [官方 Python 客户端原件](../references/official/agentarts/2026-11-02/managed_agents_client.py)：从页面下载链接取得，未修改。

官方说明本阶段用 WebSocket 调测脚本快速体验；不能将模型供应商的 OpenAI 协议当成 Managed Agents 的调用协议。原始网页及整本 PDF 的直接下载均返回安全验证页，已删除无效文件；本次保存了网页读取快照，未取得有效 PDF 或网页图片离线包。

## 1. 找到调用信息

进入 AgentArts 的“托管与运行 → 智能体运行时”，找到对应智能体：

1. 复制运行时名称，官方说明通常以 `managed-` 开头。
2. 打开运行时详情，复制访问域名。
3. 按页面指引从 URN 进入工作负载身份详情，取得智能体的 API Key。

这里需要智能体入站调用密钥，不是添加模型时使用的 MaaS 密钥。调用地址按页面实际值填写：`ws://{endpoint}/runtimes/{runtime_name}/ws`。若控制台提供 `wss://`，保留其协议；脚本不擅自改协议。

## 2. 准备 Python 环境

在项目根目录运行（官方要求 Python 3.10+）：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r scripts/requirements-agentarts.txt
```

依赖范围是本项目测试入口的选择，官方原件仅标注 `websockets>=10.0`。安装后记录实际版本，不将版本范围写作已验证全部版本。

## 3. 设置配置并首次调用

下面适用于本机 zsh；输入密钥时终端不显示内容，密钥不写进命令历史。只填 API Key 本身，不添加 `Bearer`。

```bash
export AGENTARTS_WS_URL='ws://替换为访问域名/runtimes/替换为运行时名称/ws'
read -rs 'AGENTARTS_API_KEY?粘贴智能体 API Key 后回车：'
export AGENTARTS_API_KEY
echo
python scripts/test_managed_agent.py --message '你好，请用一句话介绍你能帮助我做什么。'
```

脚本读取环境变量，**不自动加载 `.env` 文件**。`.env.example` 只列字段，不含真实凭据。不要把密钥发到聊天、截图或提交到仓库。

不调用云端也可以先检查地址格式：

```bash
python scripts/test_managed_agent.py --dry-run
```

## 4. 验证多轮上下文

先保留同一个会话 ID，逐条运行：

```bash
python scripts/test_managed_agent.py --session-id smoke-001 --message '我给当前探索任务取名为青石。请记住这个名字。'
python scripts/test_managed_agent.py --session-id smoke-001 --message '我刚才给探索任务取了什么名字？'
```

观察第二次是否准确回答“青石”。更换会话 ID 开始独立测试；会话内上下文不等于业务数据库已保存。脚本默认生成新会话 ID，不传相同 ID 时不能测试连续对话。

连通与上下文确认后，再用 `evals/首轮人工验收案例.json` 的 E01 分轮发送消息，不必现在执行全部产品验收。

## 5. 如何判断结果

必须连接成功、收到服务端就绪事件、收到正常结束信号及非空文本，脚本才报告连通测试通过。整个调用默认 120 秒超时。返回码 0 表示连通成功或离线参数检查成功（按输出区分），1 为调用失败，2 为配置错误。连接断开或超时不代表云端任务一定已停止，重试前查看平台状态。

官方客户端会自动同意工具权限、自动选交互问题的第一项；本项目入口遇到这两类事件会停止并提示回平台人工处理。普通文本追问可用相同会话 ID 手工发送下一轮。脚本不会自动判断职业建议质量，不会自动跑完整案例，也不把回答“已保存”当成数据库写入证明。

失败时：先核对域名、运行时名称、API Key、运行时状态和网络条件，再查平台运行记录。为了避免泄露鉴权信息，脚本只显示受控错误或异常类型，不打印完整握手内容。

将实际模型、配置版本、会话 ID、匿名输入输出、耗时和结果记入 `evals/runs/`（已被 Git 忽略），可使用 `evals/运行记录模板.md`。真实云端调用待配置后执行。

## 本次离线验证记录

2026-11-02，Python 3.15.2 / websockets 15.0.1：参数预检查、帮助入口及项目准备材料检查通过。以模拟 WebSocket 帧检查了 8 项：最终文本替代增量文本（不重复拼接）、旧格式最终回复、服务端失败、工具授权请求、交互选择题、空回复、提前断开、超时；均符合预期。模拟检查未访问真实运行时，不证明平台连通、会话记忆或回答质量。依赖已安装在本项目 `.venv` 中。
