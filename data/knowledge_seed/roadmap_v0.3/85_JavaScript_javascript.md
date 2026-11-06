# JavaScript：在浏览器与 Node.js 中运行的脚本语言

JavaScript 是一种动态类型、支持函数式与面向对象风格的脚本语言，最初用于网页交互，现在也可通过 Node.js 运行在服务端。它由 ECMAScript 规范定义语言本身，宿主环境再提供操作页面或文件的能力。

来源：定位说明为整理者编写；主题名称取自 roadmap.sh 的 JavaScript 路线索引（https://roadmap.sh/javascript）；用途说明为整理者归纳。

## JavaScript 是什么：运行环境与事件循环

浏览器提供文档对象模型等接口，Node.js 提供文件、进程和网络接口，两者共享同一套语言核心。JavaScript 通过事件循环调度任务，同步代码先执行，异步回调与定时器按队列顺序处理。

来源：主题名称取自 roadmap.sh 的 JavaScript 路线索引（https://roadmap.sh/javascript）；事件循环的解释为整理者归纳。

## JavaScript 的核心语法与语言特性

JavaScript 用原型和类语法实现对象复用，用闭包保存函数外部变量，用 Promise 与 async/await 组织异步流程。类型在运行时才确定，常见陷阱来自隐式类型转换和 this 指向。

相关概念（7 项）：原型链（对象属性的查找路径）、闭包（函数保留外部作用域）、this 绑定（调用上下文）、Promise（表示异步结果）、async/await（以同步写法组织异步）、解构赋值（从对象或数组取值）、模块（拆分与复用代码）。

来源：主题名称取自 roadmap.sh 的 JavaScript 路线索引（https://roadmap.sh/javascript）；语言特性的解释为整理者归纳。

## JavaScript 的异步编程与常见任务

网页中的点击、网络请求和定时任务都以异步方式发生，理解回调、Promise 与 async/await 的衔接是写可靠交互的基础。常见任务包括操作页面元素、发送请求、读写本地存储和处理表单校验。

相关主题（6 项）：DOM 操作（读写页面元素）、Fetch（发送网络请求）、事件监听（响应用户操作）、本地存储（在浏览器保存数据）、JSON（数据序列化格式）、定时器（延迟与周期任务）。

来源：主题名称取自 roadmap.sh 的 JavaScript 路线索引（https://roadmap.sh/javascript）；常见任务为整理者归纳。

## JavaScript 的工程化：包管理、构建与检查

实际项目通常用包管理器安装依赖，用构建工具打包与转换代码，用检查工具发现语法和风格问题。浏览器兼容性和模块格式由构建流程统一处理。

相关工具（6 项）：npm（包管理与脚本）、pnpm（节省空间的包管理器）、Vite（开发服务器与打包）、ESLint（静态检查）、Prettier（统一代码格式）、Jest（单元测试框架）。

来源：主题名称取自 roadmap.sh 的 JavaScript 路线索引（https://roadmap.sh/javascript）；工具用途为整理者归纳。

## 如何开始练习 JavaScript

一个可操作的小目标是：写一个待办清单页面，支持添加、勾选和删除，并把数据保存到浏览器本地存储。完成后尝试拆分为多个模块，并为其中的数据转换函数补充测试。

来源：练习目标为整理者归纳；主题名称取自 roadmap.sh 的 JavaScript 路线索引（https://roadmap.sh/javascript）。
