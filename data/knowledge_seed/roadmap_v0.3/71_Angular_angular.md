# Angular：TypeScript 的企业级前端框架

Angular 是 Google 维护的前端框架，使用 TypeScript 编写，内置路由、表单、HTTP 客户端与依赖注入。它提供较完整的项目约定，常用于需要长期维护和多人协作的 Web 应用。

来源：定位说明为整理者编写；主题名称取自 roadmap.sh 的 Angular 路线索引（https://roadmap.sh/angular）。

## Angular 是什么：模块化与依赖注入的前端框架

Angular 把应用拆成组件、指令、管道和服务，由依赖注入容器统一创建和提供依赖。框架负责变更检测与模板渲染，开发者主要声明数据如何流到视图、事件如何回到代码。

来源：主题名称取自 roadmap.sh 的 Angular 路线索引（https://roadmap.sh/angular）；用途说明为整理者归纳。

## Angular 的核心概念：组件、模块与依赖注入

组件由 TypeScript 类、模板和样式组成，通过输入与输出属性通信。模块用来组织一组相关的声明，独立组件则可以不依赖模块直接使用；服务存放可复用逻辑，由依赖注入按需提供。

相关概念（6 项）：Component（视图与逻辑单元）、NgModule（组织声明的模块）、Directive（扩展模板行为的指令）、Service（可注入的复用逻辑）、Dependency Injection（依赖注入机制）、Data Binding（模板与类的数据绑定）。

来源：主题名称取自 roadmap.sh 的 Angular 路线索引（https://roadmap.sh/angular）；概念用途为整理者归纳。

## Angular 的数据流：RxJS 与响应式编程

Angular 大量使用 RxJS 的 Observable 表达异步数据流，HTTP 请求、路由事件和表单变化都可以转成流再组合处理。模板里常用 async 管道订阅流，较新的写法也支持用信号表达响应式状态。

相关概念（5 项）：Observable（可订阅的数据流）、Operator（转换与组合流的函数）、Subscription（订阅与取消订阅）、async 管道（模板中订阅流）、Signal（细粒度响应式状态）。

来源：主题名称取自 roadmap.sh 的 Angular 路线索引（https://roadmap.sh/angular）；数据流说明为整理者归纳。

## Angular 的开发流程：CLI 与项目结构

Angular CLI 负责创建项目、生成组件与服务、运行开发服务器和构建产物。项目通常按功能划分子目录，路由配合懒加载把不同功能拆成独立代码块，构建时再进行优化。

相关步骤（5 项）：ng new（创建项目）、ng generate（生成组件与服务）、ng serve（开发服务器）、ng build（生产构建）、Lazy Loading（按路由延迟加载）。

来源：主题名称取自 roadmap.sh 的 Angular 路线索引（https://roadmap.sh/angular）；流程说明为整理者归纳。

## Angular 生态中的常用工具

Angular 的生态以官方包为核心，再配合状态管理、组件库和测试工具，它们分属命令行工具、库与框架模块。

相关工具（8 项）：Angular CLI（项目脚手架与构建）、RxJS（响应式编程库）、Angular Router（官方路由库）、Angular Forms（模板与响应式表单）、HttpClient（HTTP 通信模块）、Angular Material（官方组件库）、NgRx（状态管理库）、Jasmine（测试框架）。

来源：主题名称取自 roadmap.sh 的 Angular 路线索引（https://roadmap.sh/angular）；分类说明为整理者归纳。

## 如何开始练习 Angular

可以做一个带路由的小型管理页：列表页从服务获取数据，详情页通过路由参数读取编号，表单页做输入校验。练习时用一个服务封装数据访问，并体会依赖注入替换实现的便利。

来源：练习建议为整理者归纳；主题名称取自 roadmap.sh 的 Angular 路线索引（https://roadmap.sh/angular）。
