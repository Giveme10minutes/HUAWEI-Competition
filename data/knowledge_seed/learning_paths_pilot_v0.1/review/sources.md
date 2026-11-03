# 来源表

整理日期：2026-11-03。本表记录 `content/` 三份正文引用的来源、核验方式与可读性。核验日期均为 2026-11-03（Asia/Shanghai）。

## 1. 官方学习资源

核验方式：用 curl 实际请求页面，读取返回的标题、正文与前置说明；HTTP 状态码与正文均可读。下表“可读性”指本轮能否打开并读到正文，不代表内容长期不变。

| 来源ID | 标题 | URL | 用途 | 核验日期 | 可读性与备注 |
| --- | --- | --- | --- | --- | --- |
| SRC-FE-01 | Your first website（MDN） | https://developer.mozilla.org/en-US/docs/Learn_web_development/Getting_started/Your_first_website | 前端阶段 1 起步：准备文件、写第一个页面并发布 | 2026-11-03 | 可正常打开，正文可读；英文；页面写明无需 Web 基础，但需会用文件系统和浏览器 |
| SRC-FE-02 | Structuring content with HTML（MDN） | https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Structuring_content | 前端阶段 1：HTML 语义、结构、链接、列表、图片、表单 | 2026-11-03 | 可正常打开，正文可读；英文；页面写明无需 HTML 基础 |
| SRC-FE-03 | CSS styling basics（MDN） | https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Styling_basics | 前端阶段 1：CSS 语法、样式与布局基础 | 2026-11-03 | 可正常打开，正文可读；英文；页面建议先完成 HTML 模块 |
| SRC-FE-04 | Dynamic scripting with JavaScript（MDN） | https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Scripting | 前端阶段 1—2：JavaScript 核心、DOM、事件、JSON、网络请求 | 2026-11-03 | 可正常打开，正文可读；英文；页面写明无需 JS 基础，但需先有 HTML 与基础 CSS |
| SRC-FE-05 | Using the Fetch API（MDN） | https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch | 前端阶段 2：`fetch` 请求、响应与错误处理 | 2026-11-03 | 可正常打开，正文可读；英文；页面未单列前置段，正文默认读者了解 JavaScript 与 Promise |
| SRC-FE-06 | Quick Start（React） | https://react.dev/learn | 前端阶段 3 可选分支：组件、JSX、props/state、列表、事件 | 2026-11-03 | 可正常打开，正文可读；英文；官方入门文档 |
| SRC-FE-07 | Quick Start（Vue.js） | https://vuejs.org/guide/quick-start.html | 前端阶段 3 可选分支：创建 Vue 应用、组件与构建方式 | 2026-11-03 | 可正常打开，正文可读；英文；页面写明构建方式需要 Node.js 及对应版本 |
| SRC-BE-01 | Server-side website programming first steps（MDN） | https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Server-side/First_steps | 后端阶段 1：服务端与客户端分工、框架概览、安全入门 | 2026-11-03 | 可正常打开，正文可读；英文；页面写明不需要服务端或编程基础，但建议先了解网站如何工作 |
| SRC-BE-02 | Overview of HTTP（MDN） | https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview | 后端阶段 1：请求/响应、方法、状态码、头部与 HTTP 流程 | 2026-11-03 | 可正常打开，正文可读；英文；协议概念页 |
| SRC-BE-03 | Anatomy of an HTTP Transaction（Node.js） | https://nodejs.org/en/learn/http/anatomy-of-an-http-transaction | 后端阶段 1 示例：用代码看请求读取、处理与返回 | 2026-11-03 | 可正常打开，正文可读；英文；示例技术，需 JavaScript/Node.js 基础 |
| SRC-BE-04 | PostgreSQL Tutorial（PostgreSQL 18） | https://www.postgresql.org/docs/current/tutorial.html | 后端阶段 2：关系数据库概念、SQL 与动手练习 | 2026-11-03 | 可正常打开，正文可读；英文；页面写明不要求 Unix 或编程经验。文档版本会随官网更新 |
| SRC-BE-05 | Tutorial - User Guide（FastAPI） | https://fastapi.tiangolo.com/tutorial/ | 后端阶段 2—3 示例：校验、错误、数据库与测试 | 2026-11-03 | 可正常打开，正文可读；英文；示例技术，需 Python 基础 |

## 2. 主题来源入口（不是教程，不作为已核对教程使用）

| 来源ID | 标题 | URL | 用途 | 核验日期 | 可读性与备注 |
| --- | --- | --- | --- | --- | --- |
| SRC-REF-01 | Frontend Developer Roadmap | https://roadmap.sh/frontend | 前端主题覆盖的入口；正文未复制其内容 | 2026-11-03 | 可打开；交互式页面，本轮只确认可达，未据此还原连线或学习顺序 |
| SRC-REF-02 | Backend Developer Roadmap | https://roadmap.sh/backend | 后端主题覆盖的入口；正文未复制其内容 | 2026-11-03 | 可打开；同上 |
| SRC-REF-03 | Frontend Beginner Roadmap | https://roadmap.sh/frontend?r=frontend-beginner | 入门变体入口，用于检查遗漏 | 2026-11-03 | 可打开；同上 |
| SRC-REF-04 | Backend Beginner Roadmap | https://roadmap.sh/backend?r=backend-beginner | 入门变体入口，用于检查遗漏 | 2026-11-03 | 可打开；同上 |

原始快照的许可说明允许分享仓库或网站链接；本包没有复制、翻译或批量改写原仓库正文、图片，也没有上传原快照。

## 3. 项目内部资料（自写或整理，不是外部权威）

| 来源ID | 标题 | 位置 | 用途 | 性质 |
| --- | --- | --- | --- | --- |
| RM-P01-MAP | 计算机方向地图 v0.1 | `data/knowledge_seed/roadmap_v0.1/00_direction_map.md` | 方向分类与五个区分问题 | 项目编排，不是行业标准分类 |
| RM-P01-FE | 方向路线：前端 v0.1 | `data/knowledge_seed/roadmap_v0.1/11_前端.md` | 前端方向定位与旧阶段参考 | 项目编排 |
| RM-P01-BE | 方向路线：后端 v0.1 | `data/knowledge_seed/roadmap_v0.1/12_后端.md` | 后端方向定位与旧阶段参考 | 项目编排 |
| RM-P02-FRONTEND_BEGINNER | 前端入门 v0.2 | `data/knowledge_seed/roadmap_v0.2/80_前端入门_frontend-beginner.md` | 检查主题遗漏 | 主题索引，通用模板 |
| RM-P02-BACKEND_BEGINNER | 后端入门 v0.2 | `data/knowledge_seed/roadmap_v0.2/74_后端入门_backend-beginner.md` | 检查主题遗漏 | 主题索引，通用模板 |
| LP-P01-FE | 前端学习路线 | `content/01_前端学习路线.md` | 本轮候选入库正文 | 项目自写建议 |
| LP-P01-BE | 后端学习路线 | `content/02_后端学习路线.md` | 本轮候选入库正文 | 项目自写建议 |
| LP-P01-COMPARE | 前后端方向比较 | `content/03_前后端方向比较.md` | 本轮候选入库正文 | 项目自写建议 |

## 4. 岗位样本（原文事实，有限使用）

| 来源ID | 标题 | URL | 采集日期 | 备注 |
| --- | --- | --- | --- | --- |
| CS-P01-BOSS-005 | 前端开发工程师（上海普鲸） | https://www.zhipin.com/job_detail/d5b92d0881fc30a10nx829W1E1BS.html | 2026-11-02T19:12:02+0800 | 本地卡片已与历史快照逐字核对；未核实当前在招 |
| CS-P01-BOSS-004 | 前端开发工程师（猎头代招，有经验） | https://www.zhipin.com/job_detail/40f32aa260b918241Xxy2d-4ElBQ.html | 2026-11-02T19:11:59+0800 | 猎头代招，真实雇主未披露；正文无职责段 |
| CS-P01-BOSS-001 | java 初级开发工程师（北京颐和盛景） | https://www.zhipin.com/job_detail/94da8555552d005c0nx-3ti1EFdZ.html | 2026-11-02T19:11:35+0800 | 正文未写年限，页面标签写 1—3 年，两者分开保留 |
| CS-P01-BOSS-010 | 后端开发实习生（北京字跳） | https://www.zhipin.com/job_detail/3b887ef391875c800nJ62t64F1RS.html | 2026-11-02T19:13:42+0800 | 实习；页面两处实习时长表述不一致，保留原文 |

岗位样本本轮未重新打开招聘页面，只使用已核对的历史快照卡片；链接用于溯源，不代表当前仍可访问或仍在招聘。单条样本不能写成行业门槛或薪资结论。

## 5. 项目自写建议的说明

`LP-P01-FE`、`LP-P01-BE`、`LP-P01-COMPARE` 的章节顺序、进入条件、产出与检查标准，都是本轮整理者根据已有资料重新编排的建议，不是：

- roadmap.sh 的官方顺序或完整路线；
- 企业招聘要求或行业标准；
- 对学习时长、薪资、就业结果的承诺；
- 对“某类学生适合某方向”的判定。

正文中标注为“示例”的技术（Node.js、FastAPI）只用于展示一条可运行路径，换成其他语言或框架时，请求处理、数据、错误处理等共性内容仍然适用。
