# Next.js：React 的全栈渲染框架

Next.js 是构建在 React 之上的 Web 框架，提供基于文件的路由、服务端渲染、静态生成与接口处理能力。它让同一个项目既能输出页面，也能承载服务端逻辑，常用于内容站点和全栈应用。

来源：定位说明为整理者编写；主题名称取自 roadmap.sh 的 Next.js 路线索引（https://roadmap.sh/nextjs）。

## Next.js 是什么：在 React 之上提供路由与渲染

Next.js 补齐了纯 React 应用通常需要自行搭建的部分：路由、数据获取、构建与部署约定。页面可以在构建时生成、在请求时渲染，或在客户端渲染，具体方式由组件类型和配置决定。

来源：主题名称取自 roadmap.sh 的 Next.js 路线索引（https://roadmap.sh/nextjs）；用途说明为整理者归纳。

## Next.js 的路由：App Router 与 Pages Router

App Router 用目录结构表达路由，页面文件与布局文件分别定义内容和共享外壳，动态段用方括号命名。Pages Router 是较早的路由方式，以页面文件为中心；两种方式在项目中共存时需要明确的组织约定。

相关概念（6 项）：App Router（目录式路由）、page 文件（路由页面）、layout 文件（共享布局）、Dynamic Segment（动态路径段）、Pages Router（较早的页面路由）、Route Group（不影响网址的分组）。

来源：主题名称取自 roadmap.sh 的 Next.js 路线索引（https://roadmap.sh/nextjs）；路由说明为整理者归纳。

## Next.js 的渲染方式：服务端渲染、静态生成与增量更新

服务端渲染在每次请求时生成页面，适合依赖请求上下文的内容；静态生成在构建时产出页面，适合变化较少的内容。增量静态再生成允许静态页面在后台按条件重新生成，兼顾速度与更新。

相关概念（5 项）：SSR（请求时渲染）、SSG（构建时生成）、ISR（后台增量再生成）、Server Component（服务端组件）、Client Component（客户端组件）。

来源：主题名称取自 roadmap.sh 的 Next.js 路线索引（https://roadmap.sh/nextjs）；渲染说明为整理者归纳。

## Next.js 的数据获取与服务端能力

服务端组件可以直接读取数据，客户端组件通过请求接口获取数据。路由处理器用约定文件提供接口，服务端操作把表单提交直接接到服务端函数，中间件则在请求到达页面前处理重定向与请求头。

相关概念（5 项）：fetch（服务端请求）、Route Handler（接口处理文件）、Server Actions（表单与数据变更）、Middleware（请求前置处理）、Caching（数据与页面缓存）。

来源：主题名称取自 roadmap.sh 的 Next.js 路线索引（https://roadmap.sh/nextjs）；数据获取说明为整理者归纳。

## Next.js 生态中的常用工具

Next.js 的工具覆盖图片与字体优化、类型检查、代码质量和数据访问，它们分属框架组件、工具与库，实际组合按项目选择。

相关工具（5 项）：next/image（图片优化组件）、next/font（字体优化）、TypeScript（类型系统）、ESLint（代码检查工具）、Prisma（数据访问工具）。

来源：主题名称取自 roadmap.sh 的 Next.js 路线索引（https://roadmap.sh/nextjs）；分类说明为整理者归纳。

## 如何开始练习 Next.js

可以用脚手架创建一个内容站点：首页列出文章，动态路由展示详情，用布局文件统一页头与页脚。再尝试把文章数据改为构建时读取，比较静态生成与请求时渲染的差异。

来源：练习建议为整理者归纳；主题名称取自 roadmap.sh 的 Next.js 路线索引（https://roadmap.sh/nextjs）。
