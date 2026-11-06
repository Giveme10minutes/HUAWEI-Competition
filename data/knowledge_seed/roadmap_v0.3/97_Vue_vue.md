# Vue：渐进式的前端框架

Vue 是开源的 JavaScript 前端框架，以渐进式为设计取向：可以只在页面局部引入，也可以用路由、状态管理和构建工具组成完整应用。它的响应式系统会在数据变化时自动更新相关视图。

来源：定位说明为整理者编写；主题名称取自 roadmap.sh 的 Vue 路线索引（https://roadmap.sh/vue）。

## Vue 是什么：渐进式与响应式的前端框架

Vue 的核心是模板与响应式数据，模板中的表达式会在依赖数据变化时重新求值。项目可以按需引入官方库扩展路由和状态管理，因此从小型页面到单页应用可以使用同一套模型。

来源：主题名称取自 roadmap.sh 的 Vue 路线索引（https://roadmap.sh/vue）；用途说明为整理者归纳。

## Vue 的核心概念：响应式与单文件组件

Vue 用 ref 与 reactive 创建响应式数据，用 computed 派生缓存值，用 watch 响应变化执行副作用。单文件组件把模板、逻辑和样式放在一个 .vue 文件里，组合式 API 则把相关逻辑聚合到 setup 中。

相关概念（6 项）：ref（基本值响应式引用）、reactive（对象响应式代理）、computed（缓存派生值）、watch（监听变化）、Single File Component（单文件组件）、Composition API（组合式逻辑组织）。

来源：主题名称取自 roadmap.sh 的 Vue 路线索引（https://roadmap.sh/vue）；概念用途为整理者归纳。

## Vue 的组件通信与状态管理：Props、事件与 Pinia

父组件通过 props 向子组件传值，子组件通过事件把变化通知父级，插槽用于分发可定制内容。跨组件共享状态可以提升到共同父级，规模变大后常用 Pinia 组织多个模块的状态。

相关概念（6 项）：Props（父级传入数据）、Emits（子组件事件）、Slot（内容分发）、provide（向下提供依赖）、inject（读取上层依赖）、Pinia（状态管理库）。

来源：主题名称取自 roadmap.sh 的 Vue 路线索引（https://roadmap.sh/vue）；组件通信说明为整理者归纳。

## Vue 的路由与开发流程：Vue Router 与构建工具

Vue Router 把网址映射到页面组件，支持嵌套路由、动态参数和导航守卫。项目通常用脚手架创建，由 Vite 提供开发服务器与热更新，构建时把模板和脚本打包成静态资源。

相关步骤（5 项）：create-vue（项目脚手架）、Vite（开发与构建工具）、Vue Router（官方路由库）、热更新（保存即刷新模块）、vite build（生成静态产物）。

来源：主题名称取自 roadmap.sh 的 Vue 路线索引（https://roadmap.sh/vue）；流程说明为整理者归纳。

## Vue 生态中的常用工具

Vue 的生态以官方库为主，再配合工具库、测试与文档站点生成器，它们分属框架模块、构建工具与库。

相关工具（8 项）：Vite（构建工具）、Vue Router（路由库）、Pinia（状态管理库）、VueUse（组合式工具库）、Vitest（测试框架）、Vue DevTools（浏览器调试扩展）、VitePress（文档站点生成器）、Nuxt（Vue 全栈框架）。

来源：主题名称取自 roadmap.sh 的 Vue 路线索引（https://roadmap.sh/vue）；分类说明为整理者归纳。

## 如何开始练习 Vue

可以做一个笔记应用：列表展示笔记，表单新增内容，点击条目进入详情，用本地存储保留数据。练习时用 ref 管理状态、用 computed 做筛选，再加入 Vue Router 的两个页面。

来源：练习建议为整理者归纳；主题名称取自 roadmap.sh 的 Vue 路线索引（https://roadmap.sh/vue）。
