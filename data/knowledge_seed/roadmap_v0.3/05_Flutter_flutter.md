# Flutter：用 Dart 构建跨平台界面

Flutter 是 Google 开源的界面工具包，使用 Dart 语言编写，可编译到移动端、Web 与桌面平台。它通过自带的渲染引擎绘制界面，而不是把每个组件映射为平台原生控件。

来源：定位说明为整理者编写；主题名称取自 roadmap.sh 的 Flutter 路线索引（https://roadmap.sh/flutter）。

## Flutter 是什么：自绘渲染与跨平台目标

Flutter 把界面描述为组件树，由框架在画布上自行绘制，因此不同平台上的布局与动画表现较为一致。它与依赖平台原生控件的方案不同，平台差异主要通过插件和平台通道处理。

来源：主题名称取自 roadmap.sh 的 Flutter 路线索引（https://roadmap.sh/flutter）；用途说明为整理者归纳。

## Flutter 的核心概念：Widget、状态与热重载

Flutter 的界面由 Widget 组成，Widget 是不可变的配置描述，状态变化时框架重建对应的组件子树。StatefulWidget 用 State 对象保存可变数据，热重载则在不丢失当前状态的前提下把代码改动推送到运行中的应用。

相关概念（6 项）：Widget（界面配置单元）、Element（组件树中的实例节点）、State（可变状态容器）、setState（触发重建的方法）、BuildContext（组件在树中的位置）、热重载（保留状态刷新代码）。

来源：主题名称取自 roadmap.sh 的 Flutter 路线索引（https://roadmap.sh/flutter）；概念用途为整理者归纳。

## Flutter 的开发流程：项目结构、依赖与构建

一个 Flutter 项目通常包含 lib 目录下的 Dart 代码、pubspec.yaml 依赖描述，以及各平台的宿主工程目录。开发时用命令行或集成开发环境运行调试版本，完成后按目标平台构建安装包或 Web 产物。

相关步骤（5 项）：flutter create（创建项目骨架）、pub get（拉取依赖）、flutter run（在设备上运行）、flutter doctor（检查开发环境）、flutter build（生成发布产物）。

来源：主题名称取自 roadmap.sh 的 Flutter 路线索引（https://roadmap.sh/flutter）；流程说明为整理者归纳。

## Flutter 生态中的常用工具

Flutter 项目会同时用到语言工具、包仓库、状态管理库和调试工具，它们职责不同，实际选择取决于项目规模与团队习惯。

相关工具（8 项）：Dart SDK（语言与编译器）、Flutter CLI（创建、运行与构建）、pub.dev（Dart 包仓库）、DevTools（性能与布局调试）、Provider（轻量状态共享）、Riverpod（状态管理库）、Bloc（事件驱动状态库）、Android Studio（集成开发环境）。

来源：主题名称取自 roadmap.sh 的 Flutter 路线索引（https://roadmap.sh/flutter）；分类说明为整理者归纳。

## Flutter 与 React Native 的区别

两者都用于跨平台移动开发。Flutter 用 Dart 自绘界面，界面在不同平台上更一致；React Native 用 JavaScript 与 React 组件调用平台原生视图，更贴近各平台控件。选择取决于团队语言经验与对原生能力的需求，这不是优劣排名。

来源：用途说明为整理者归纳；主题名称取自 roadmap.sh 的 Flutter 路线索引（https://roadmap.sh/flutter）。

## 如何开始练习 Flutter

可以先做一个带列表与详情页的待办应用：用 StatefulWidget 管理待办数组，用 ListView 展示条目，点击条目进入详情页，再尝试把数据保存到本地。完成后重点检查热重载是否保留状态、列表滚动是否流畅。

来源：练习建议为整理者归纳；主题名称取自 roadmap.sh 的 Flutter 路线索引（https://roadmap.sh/flutter）。
