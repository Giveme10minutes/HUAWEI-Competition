# GraphQL：客户端声明字段的接口查询语言

GraphQL 是用于 API 的查询语言与运行时规范，客户端在请求中写明需要的字段，服务端按类型定义返回对应数据。它既不是界面框架，也不是数据库，需要与具体服务端实现和存储配合使用。

来源：定位说明为整理者编写；主题名称取自 roadmap.sh 的 GraphQL 路线索引（https://roadmap.sh/graphql）。

## GraphQL 是什么：由客户端声明所需字段的接口协议

使用 GraphQL 时，服务端先定义带类型的 schema，客户端再按 schema 提交查询。相比固定返回结构的接口，它让客户端只取需要的字段，减少多余数据和多次请求，但服务端需要处理查询复杂度与缓存问题。

来源：主题名称取自 roadmap.sh 的 GraphQL 路线索引（https://roadmap.sh/graphql）；用途说明为整理者归纳。

## GraphQL 的核心概念：schema、查询与变更

schema 用类型系统描述可查询的对象、字段和参数，是客户端与服务端的契约。查询用于读取数据，变更用于修改数据，订阅用于推送实时事件；片段与变量让请求可以复用和参数化。

相关概念（7 项）：Schema（接口类型契约）、Type（对象类型定义）、Query（读取操作）、Mutation（写入操作）、Subscription（实时事件流）、Directive（执行规则修饰）、Fragment（可复用字段集合）。

来源：主题名称取自 roadmap.sh 的 GraphQL 路线索引（https://roadmap.sh/graphql）；概念用途为整理者归纳。

## GraphQL 的解析器与执行：字段如何得到数据

服务端为 schema 中的字段编写解析器，执行引擎按查询形状逐个字段调用解析器并组装结果。解析器可以访问父级对象、参数和上下文，跨表或跨服务取数时要注意批量加载，避免逐条查询造成性能问题。

相关概念（5 项）：Resolver（字段解析函数）、Root Field（查询入口字段）、Arguments（字段参数）、Context（请求级共享上下文）、DataLoader（批量加载工具）。

来源：主题名称取自 roadmap.sh 的 GraphQL 路线索引（https://roadmap.sh/graphql）；执行说明为整理者归纳。

## GraphQL 的典型开发流程：schema 设计与客户端协作

开发通常先与客户端商定 schema，再实现解析器与数据访问，最后用图形化调试工具试查。上线前后要处理鉴权、分页、错误格式和查询深度限制，避免一次请求拉取过多数据。

相关步骤（5 项）：Schema 设计（约定类型与字段）、Resolver 实现（连接数据源）、Introspection（查询 schema 结构）、GraphiQL（交互式调试界面）、Pagination（分页约定）。

来源：主题名称取自 roadmap.sh 的 GraphQL 路线索引（https://roadmap.sh/graphql）；流程说明为整理者归纳。

## GraphQL 生态中的常用工具

GraphQL 的实现分布在多种语言与客户端库中，服务端组件、客户端缓存和调试工具职责不同，实际选型取决于技术栈。

相关工具（8 项）：GraphQL.js（JavaScript 参考实现）、Apollo Server（服务端框架）、Apollo Client（客户端与缓存库）、Relay（客户端框架）、URQL（轻量客户端）、GraphQL Yoga（服务端库）、Graphene（Python 实现）、DataLoader（批量加载库）。

来源：主题名称取自 roadmap.sh 的 GraphQL 路线索引（https://roadmap.sh/graphql）；分类说明为整理者归纳。

## 如何开始练习 GraphQL

可以做一个图书与作者接口：定义 Book、Author 类型和查询、变更字段，为每个字段写解析器，在调试界面里试查嵌套数据。随后加上变量、分页和一个带校验的写入操作。

来源：练习建议为整理者归纳；主题名称取自 roadmap.sh 的 GraphQL 路线索引（https://roadmap.sh/graphql）。
