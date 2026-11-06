# TypeScript：为 JavaScript 增加静态类型的语言

TypeScript 是在 JavaScript 之上增加静态类型语法的语言，代码经过类型检查后编译为普通 JavaScript 运行。它不改变运行时行为，主要价值在于提前发现类型错误、改善编辑器的补全与重构体验。

来源：定位说明为整理者编写；主题名称取自 roadmap.sh 的 TypeScript 路线索引（https://roadmap.sh/typescript）；用途说明为整理者归纳。

## TypeScript 是什么：类型检查与编译过程

TypeScript 源码由编译器处理，类型在编译阶段被擦除，产出的 JavaScript 交给浏览器或 Node.js 执行。类型检查与代码运行是分开的两步，因此运行时不会因为类型报错而中断。

来源：主题名称取自 roadmap.sh 的 TypeScript 路线索引（https://roadmap.sh/typescript）；编译过程的解释为整理者归纳。

## TypeScript 的核心类型系统

TypeScript 的类型系统是结构化的，只要形状匹配就视为兼容，而不是依赖显式继承。它支持接口、泛型、联合类型和类型收窄，可以在不脱离 JavaScript 生态的前提下描述复杂数据。

相关概念（7 项）：接口（描述对象形状）、类型别名（给类型起名）、泛型（参数化类型）、联合类型（多个类型之一）、类型收窄（按条件缩小类型）、字面量类型（限定具体取值）、类型断言（手动指定类型）。

来源：主题名称取自 roadmap.sh 的 TypeScript 路线索引（https://roadmap.sh/typescript）；类型系统的解释为整理者归纳。

## TypeScript 的工程化：配置、构建与检查

TypeScript 项目通过 tsconfig.json 配置编译目标、模块格式和严格程度，再借助构建工具完成打包与热更新。类型检查和代码风格检查通常拆成独立命令，在提交前运行。

相关工具（6 项）：tsc（官方编译器与类型检查）、tsconfig（编译选项配置）、Vite（开发与打包工具）、ESLint（静态检查）、typescript-eslint（类型相关规则）、DefinitelyTyped（社区类型声明）。

来源：主题名称取自 roadmap.sh 的 TypeScript 路线索引（https://roadmap.sh/typescript）；工具用途为整理者归纳。

## TypeScript 与 JavaScript 的关系

TypeScript 是 JavaScript 的超集：所有合法的 JavaScript 基本也是合法的 TypeScript，类型标注可以逐步添加。已有 JavaScript 项目可以先把文件改为 TypeScript 后缀并开启宽松检查，再逐步收紧严格选项。

来源：主题名称取自 roadmap.sh 的 TypeScript 路线索引（https://roadmap.sh/typescript）；与 JavaScript 关系的解释为整理者归纳。

## 如何开始练习 TypeScript

一个可操作的小目标是：把一段处理数组数据的 JavaScript 函数改写为 TypeScript，为参数和返回值补上类型，并开启严格模式修正报错。完成后尝试定义一个接口描述接口返回的数据结构。

来源：练习目标为整理者归纳；主题名称取自 roadmap.sh 的 TypeScript 路线索引（https://roadmap.sh/typescript）。
