# SwiftUI：Apple 平台的声明式界面框架

SwiftUI 是 Apple 提供的声明式界面框架，使用 Swift 描述视图层级，可用于 iOS、macOS、watchOS 与 tvOS。视图是状态的函数，数据变化时框架自动更新受影响的界面部分。

来源：定位说明为整理者编写；主题名称取自 roadmap.sh 的 SwiftUI 路线索引（https://roadmap.sh/swift-ui）。

## SwiftUI 是什么：声明式界面与状态驱动更新

使用 SwiftUI 时，开发者描述“界面应该是什么样”，而不是逐步操作视图对象。框架比较新旧视图描述并只更新差异部分，这让状态与界面保持同步，也减少了手写刷新逻辑。

来源：主题名称取自 roadmap.sh 的 SwiftUI 路线索引（https://roadmap.sh/swift-ui）；用途说明为整理者归纳。

## SwiftUI 的核心概念：视图与状态属性包装器

SwiftUI 的视图遵循 View 协议并实现 body 属性，组合成视图树。状态通过属性包装器声明：@State 保存视图私有状态，@Binding 在父子视图间共享可写值，@ObservedObject 与 @StateObject 观察引用类型模型，@EnvironmentObject 从环境注入共享对象。

相关概念（6 项）：View 协议（视图的基本抽象）、@State（视图私有状态）、@Binding（父子双向绑定）、@StateObject（创建并持有可观察模型）、@ObservedObject（观察外部模型）、@EnvironmentObject（从环境读取共享对象）。

来源：主题名称取自 roadmap.sh 的 SwiftUI 路线索引（https://roadmap.sh/swift-ui）；概念用途为整理者归纳。

## SwiftUI 的布局与导航：容器、修饰符与 NavigationStack

布局用 VStack、HStack、ZStack 等容器组合视图，再用修饰符调整间距、字体、背景和交互。导航通常由 NavigationStack 与 NavigationLink 组织页面层级，弹窗和表单则用 sheet 等呈现方式。

相关概念（5 项）：VStack（纵向排列）、HStack（横向排列）、ZStack（层叠排列）、ViewModifier（复用样式与行为）、NavigationStack（管理页面导航栈）。

来源：主题名称取自 roadmap.sh 的 SwiftUI 路线索引（https://roadmap.sh/swift-ui）；布局说明为整理者归纳。

## SwiftUI 的开发流程：Xcode 预览与工程构建

SwiftUI 项目在 Xcode 中创建，按平台配置目标并共享 Swift 源码。预览功能可以即时查看视图在多种设备和状态下的样子，构建后通过模拟器或真机运行，再按平台要求打包分发。

相关步骤（5 项）：Xcode（集成开发环境）、Preview（实时视图预览）、Target（平台构建目标）、Simulator（设备模拟器）、Archive（打包分发产物）。

来源：主题名称取自 roadmap.sh 的 SwiftUI 路线索引（https://roadmap.sh/swift-ui）；流程说明为整理者归纳。

## SwiftUI 生态中的常用工具

SwiftUI 与 Apple 平台的工具链紧密结合，涉及依赖管理、持久化、图标资源、并发与测试，它们分属框架、工具和资源库。

相关工具（8 项）：Xcode（开发与构建）、Swift Package Manager（依赖管理）、SF Symbols（系统图标资源）、Combine（响应式事件框架）、SwiftData（数据持久化框架）、Core Data（对象图与持久化框架）、XCTest（测试框架）、Instruments（性能分析工具）。

来源：主题名称取自 roadmap.sh 的 SwiftUI 路线索引（https://roadmap.sh/swift-ui）；分类说明为整理者归纳。

## 如何开始练习 SwiftUI

可以做一个习惯打卡应用：列表展示习惯，点击后切换完成状态，用 sheet 新增习惯，并把数据持久化。练习重点是让界面只依赖状态声明，观察修改 @State 后视图如何自动更新。

来源：练习建议为整理者归纳；主题名称取自 roadmap.sh 的 SwiftUI 路线索引（https://roadmap.sh/swift-ui）。
