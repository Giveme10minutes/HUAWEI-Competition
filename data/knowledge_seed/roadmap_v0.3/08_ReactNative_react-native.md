# React Native：用 React 模型构建移动应用

React Native 是 Meta 开源的移动应用框架，使用 JavaScript 或 TypeScript 编写 React 组件。组件最终渲染为平台原生视图，因此界面观感接近原生应用，同时复用 React 的组件与状态模型。

来源：定位说明为整理者编写；主题名称取自 roadmap.sh 的 React Native 路线索引（https://roadmap.sh/react-native）。

## React Native 是什么：JavaScript 与原生视图的衔接

React Native 在 JavaScript 线程中运行 React 组件树，再通过桥接机制把界面更新交给平台原生视图。较新的架构用更直接的接口和并发渲染减少通信开销，具体实现随框架演进而变化。

来源：主题名称取自 roadmap.sh 的 React Native 路线索引（https://roadmap.sh/react-native）；用途说明为整理者归纳。

## React Native 的核心概念：组件、状态与原生模块

React Native 提供 View、Text、Image、FlatList 等核心组件，它们分别对应平台上的容器、文本、图片和列表。组件用 props 接收数据、用 state 与 Hooks 管理交互；需要调用平台能力时，通过原生模块或平台特定代码扩展。

相关概念（6 项）：核心组件（跨平台基础控件）、Props（父组件传入的数据）、State（组件内部可变数据）、Hooks（复用状态与副作用逻辑）、原生模块（调用平台接口）、平台特定代码（按系统分支实现）。

来源：主题名称取自 roadmap.sh 的 React Native 路线索引（https://roadmap.sh/react-native）；概念用途为整理者归纳。

## React Native 的开发流程：Metro、快速刷新与设备调试

开发时 Metro 打包器负责把 JavaScript 代码打包并提供给应用，快速刷新在保存文件后更新界面。可以直接用 React Native CLI 管理原生工程，也可以用 Expo 托管构建与设备预览，两者在原生定制能力上取舍不同。

相关步骤（5 项）：Metro（JavaScript 打包器）、快速刷新（保存即更新界面）、React Native CLI（原生工程脚手架）、Expo（托管开发与构建平台）、LogBox（运行日志与警告面板）。

来源：主题名称取自 roadmap.sh 的 React Native 路线索引（https://roadmap.sh/react-native）；流程说明为整理者归纳。

## React Native 生态中的常用工具

React Native 的工具覆盖脚手架、导航、状态管理、本地存储和测试，它们分属库、平台与命令行工具，实际组合按项目需要选择。

相关工具（8 项）：Expo（开发与构建平台）、React Native CLI（原生工程命令）、Metro（打包器）、React Navigation（页面导航库）、Redux（状态管理库）、AsyncStorage（键值存储库）、Jest（测试框架）、React Native Testing Library（组件测试库）。

来源：主题名称取自 roadmap.sh 的 React Native 路线索引（https://roadmap.sh/react-native）；分类说明为整理者归纳。

## React Native 与 Flutter 的区别

两者都面向跨平台移动开发。React Native 复用 React 与 JavaScript 生态，界面落在平台原生视图上；Flutter 用 Dart 自绘界面，跨平台一致性更强。差异主要在语言、渲染方式和原生集成成本，不构成优劣排名。

来源：用途说明为整理者归纳；主题名称取自 roadmap.sh 的 React Native 路线索引（https://roadmap.sh/react-native）。

## 如何开始练习 React Native

可以用 Expo 创建一个笔记应用：列表页展示笔记，详情页编辑内容，用本地存储保存数据。练习时观察快速刷新是否生效、FlatList 滚动是否正常，并尝试调用一个设备能力接口。

来源：练习建议为整理者归纳；主题名称取自 roadmap.sh 的 React Native 路线索引（https://roadmap.sh/react-native）。
