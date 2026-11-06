# Kotlin：运行在 JVM 上的静态类型编程语言

Kotlin 由 JetBrains 主导开发，源代码可以编译为 JVM 字节码，也能通过 Kotlin/Native 和 Kotlin/JS 面向其他平台。它在 Android 开发中被官方支持，也可用于服务端程序，并强调与既有 Java 代码的互操作。

来源：定位说明为整理者编写；主题名称取自 roadmap.sh 的 Kotlin 路线索引（https://roadmap.sh/kotlin）。

## Kotlin 的核心语法与编程概念

Kotlin 用可空类型区分“可能为空”和“一定不为空”的值，用 `val` 与 `var` 区分只读绑定和可变绑定，并通过数据类、扩展函数减少样板代码。入门阶段可先写一个命令行程序，再逐步加入这些特性。

相关概念（7 项）：可空类型（编译期空值检查）、智能转换（判断后自动收窄类型）、数据类（自动生成常用方法）、扩展函数（为已有类型添加方法）、密封类（受限的继承层次）、高阶函数（函数作为参数或返回值）、类型推断（省略显式类型标注）。

来源：主题名称取自 roadmap.sh 的 Kotlin 路线索引（https://roadmap.sh/kotlin）；用途说明为整理者归纳。

## Kotlin 的协程与异步编程

协程把可暂停的计算写成接近顺序执行的代码，由调度器决定在哪个线程上恢复执行，从而减少回调嵌套。使用时要选择协程作用域与调度器，并关注取消传播和异常处理。

相关概念（6 项）：挂起函数（可暂停并恢复的函数）、协程作用域（管理任务生命周期）、调度器（指定执行所用线程）、协程构建器（启动协程的函数）、Flow（按需发射的数据流）、结构化并发（父任务等待子任务结束）。

来源：主题名称取自 roadmap.sh 的 Kotlin 路线索引（https://roadmap.sh/kotlin）；用途说明为整理者归纳。

## Kotlin 的平台支持：JVM、Android 与多平台

同一份 Kotlin 代码可以面向 JVM、Android、浏览器和原生平台编译，平台差异由对应的标准库和目标实现承载。跨平台项目通常把共享逻辑放在公共模块，再为各平台编写实际界面或系统调用。

相关方案（6 项）：Kotlin/JVM（服务端与桌面运行环境）、Kotlin/Android（Android 应用目标）、Kotlin/JS（浏览器目标）、Kotlin/Native（编译为原生机器码）、Kotlin Multiplatform（共享业务逻辑）、Compose Multiplatform（跨平台声明式界面）。它们属于不同的编译目标或框架，不是同一层概念。

来源：主题名称取自 roadmap.sh 的 Kotlin 路线索引（https://roadmap.sh/kotlin）；用途说明为整理者归纳。

## Kotlin 的工程化：构建、测试与代码质量

Kotlin 项目通常由构建工具管理依赖和编译任务，用测试框架验证行为，再用静态检查和格式化工具保持风格一致。这些工具职责不同，小型练习项目不必全部配置。

相关工具（7 项）：Gradle（构建与依赖管理）、Maven（另一种构建工具）、kotlinx.serialization（序列化库）、JUnit（单元测试框架）、Detekt（静态分析工具）、ktlint（代码格式化检查）、Dokka（API 文档生成）。

其中 Gradle、Maven 是构建工具，其余是库或检查工具。

来源：主题名称取自 roadmap.sh 的 Kotlin 路线索引（https://roadmap.sh/kotlin）；用途说明为整理者归纳。

## 如何开始练习 Kotlin

可以先用 IntelliJ IDEA 或 Android Studio 新建一个 Gradle 项目，目标是写一个读取文本文件并统计词频的命令行程序。完成后为统计函数补一个单元测试，再用协程并发处理多个文件，观察取消与异常的行为。

参考：主题名称取自 roadmap.sh 的 Kotlin 路线索引（https://roadmap.sh/kotlin）；练习目标为整理者归纳。
