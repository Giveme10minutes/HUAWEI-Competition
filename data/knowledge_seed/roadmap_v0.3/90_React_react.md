# React：构建用户界面的组件库

React 是 Meta 开源的 JavaScript 库，用于把界面拆成可组合的组件。组件根据输入数据返回界面描述，数据变化时框架更新对应的视图，这一模型也延伸到移动端与桌面端。

来源：定位说明为整理者编写；主题名称取自 roadmap.sh 的 React 路线索引（https://roadmap.sh/react）。

## React 是什么：以组件描述界面的 JavaScript 库

React 关注视图层，不规定路由、数据请求或项目结构，这些通常由配套库补齐。它用声明式写法描述界面，并由框架计算最小更新范围，开发者不必手动操作页面节点。

来源：主题名称取自 roadmap.sh 的 React 路线索引（https://roadmap.sh/react）；用途说明为整理者归纳。

## React 的核心概念：组件、Props 与 State

React 组件是返回界面描述的 JavaScript 函数，可以用 JSX 把结构写得接近 HTML。Props 由父组件传入且只读，State 表示组件内部会变化的数据；状态提升和键值标识帮助框架正确复用与更新列表项。

相关概念（6 项）：Component（界面单元）、JSX（界面描述语法）、Props（父级传入的数据）、State（组件内部状态）、Keys（列表项身份标识）、Conditional Rendering（按状态渲染不同界面）。

来源：主题名称取自 roadmap.sh 的 React 路线索引（https://roadmap.sh/react）；概念用途为整理者归纳。

## React 的副作用与 Hooks：useEffect、useMemo 与 useRef

Hooks 让函数组件拥有状态和生命周期能力，调用顺序在每次渲染中必须保持一致。useEffect 处理请求、订阅等副作用并在依赖变化时重新执行，useMemo 与 useCallback 缓存计算结果，useRef 保存不触发渲染的可变值。

相关概念（5 项）：useState（声明状态）、useEffect（处理副作用）、useMemo（缓存计算结果）、useRef（保存可变引用）、Custom Hook（复用状态逻辑）。

来源：主题名称取自 roadmap.sh 的 React 路线索引（https://roadmap.sh/react）；Hooks 说明为整理者归纳。

## React 的状态管理与路由：Context、Redux 与 React Router

组件间共享状态可以先提升到共同父级，跨层传递用 Context，规模变大后常用专门的状态管理库。路由把网址映射到页面组件，负责路径参数、嵌套页面和导航状态。

相关概念（5 项）：Context（跨层共享数据）、Redux（集中式状态管理）、Redux Toolkit（官方 Redux 工具集）、React Router（客户端路由库）、TanStack Query（服务端状态缓存库）。

来源：主题名称取自 roadmap.sh 的 React 路线索引（https://roadmap.sh/react）；状态与路由说明为整理者归纳。

## React 的开发流程与常用工具

React 项目通常用构建工具创建和运行，按页面、组件与逻辑分层组织目录，再用测试与检查工具保证质量。工具分属构建器、路由库、状态库、表单库与测试框架。

相关工具（8 项）：Vite（开发与构建工具）、React Router（路由库）、Redux Toolkit（状态管理库）、TanStack Query（数据请求缓存库）、React Hook Form（表单库）、Vitest（测试框架）、Testing Library（组件测试库）、Next.js（React 全栈框架）。

来源：主题名称取自 roadmap.sh 的 React 路线索引（https://roadmap.sh/react）；分类说明为整理者归纳。

## 如何开始练习 React

可以做一个待办应用：添加与删除任务，按完成状态筛选，用本地存储保留数据。练习时把列表与表单项拆成组件，观察 props 与 state 的分工，再用 useEffect 同步本地存储。

来源：练习建议为整理者归纳；主题名称取自 roadmap.sh 的 React 路线索引（https://roadmap.sh/react）。
