# Node.js：服务端 JavaScript 运行时

Node.js 是让 JavaScript 在浏览器之外运行的运行时，基于 V8 引擎，提供文件、网络、进程等接口。它常用于编写后端服务、命令行工具和构建脚本，用事件循环处理并发请求。

来源：主题名称取自 roadmap.sh 的 Node.js 路线索引（https://roadmap.sh/nodejs）；参考 Node.js 官方学习文档（https://nodejs.org/en/learn）。

## Node.js 是什么：事件循环与非阻塞 I/O

Node.js 在单线程事件循环上执行 JavaScript，把耗时的输入输出交给系统异步处理，完成后通过回调、Promise 或 await 继续。这让它在大量并发连接、少量计算的场景中较稳定，但不适合长时间占用 CPU 的任务。

参考：Node.js 官方学习文档（https://nodejs.org/en/learn）。

## Node.js 的核心模块与常见任务

内置模块覆盖文件、路径、HTTP、事件与进程等基础能力，多数任务先用内置模块就够。需要更复杂的功能时再引入第三方包，避免一开始就堆叠依赖。

相关模块（7 项）：fs（读写文件）、path（处理路径）、http（创建服务）、events（事件发布订阅）、process（读取运行环境）、stream（流式处理数据）、crypto（加密与摘要）。

来源：主题名称取自 roadmap.sh 的 Node.js 路线索引（https://roadmap.sh/nodejs）；用途说明为整理者归纳。

## Node.js 的包管理与项目结构

Node.js 用包管理器安装依赖，项目根目录的清单文件记录依赖与脚本，锁文件固定实际安装的版本。模块可以用 CommonJS 或 ES 模块写法，同一项目内需要统一。

相关工具（6 项）：npm（包管理与脚本）、pnpm（节省空间的包管理）、npx（临时执行包命令）、package.json（项目清单）、锁文件（固定依赖版本）、workspaces（多包仓库管理）。

来源：主题名称取自 roadmap.sh 的 Node.js 路线索引（https://roadmap.sh/nodejs）；用途说明为整理者归纳。

## Node.js 的 Web 框架与数据访问

多数服务用框架处理路由、中间件和请求解析，再通过数据库驱动或 ORM 访问数据。选型时看项目规模与团队熟悉度，而不是只看功能列表。

相关工具（6 项）：Express（轻量 Web 框架）、Fastify（注重性能的框架）、NestJS（结构化框架）、Prisma（数据库工具）、Mongoose（MongoDB 建模）、Sequelize（关系数据库 ORM）。

来源：主题名称取自 roadmap.sh 的 Node.js 路线索引（https://roadmap.sh/nodejs）；用途说明为整理者归纳。

## Node.js 的测试、调试与运行维护

Node.js 自带测试运行器，也可以使用第三方测试框架；调试可借助检查器或日志。生产环境需要进程管理与监控，避免异常退出后无人拉起。

相关工具（6 项）：node:test（内置测试）、Jest（测试框架）、Vitest（测试框架）、node --inspect（调试入口）、PM2（进程管理）、Winston（日志记录）。

来源：主题名称取自 roadmap.sh 的 Node.js 路线索引（https://roadmap.sh/nodejs）；用途说明为整理者归纳。

## 如何开始练习 Node.js

先用内置 http 模块写一个返回当前时间的接口，再用一个框架改写成带路由和错误处理的版本，最后补一个测试。产出是能在本地启动、返回 JSON 的两个小服务。

来源：定位说明为整理者编写；练习设计为整理者归纳。
