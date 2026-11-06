# Laravel：PHP 的全栈 Web 框架

Laravel 是用 PHP 编写的开源 Web 框架，采用模型、视图、控制器结构，并提供路由、数据库迁移、队列、认证等常用能力。它以较简洁的语法和完整的官方生态，适合快速开发 Web 应用与接口。

来源：定位说明为整理者编写；主题名称取自 roadmap.sh 的 Laravel 路线索引（https://roadmap.sh/laravel）。

## Laravel 是什么：面向 Web 应用的 PHP 框架

Laravel 把请求生命周期组织成路由、中间件、控制器和响应几个阶段，开发者主要在控制器里编排业务逻辑。框架通过服务容器管理类依赖，并用配置文件和环境变量区分不同部署环境。

来源：主题名称取自 roadmap.sh 的 Laravel 路线索引（https://roadmap.sh/laravel）；用途说明为整理者归纳。

## Laravel 的核心概念：路由、控制器与中间件

路由文件把网址和请求方法映射到控制器动作或闭包，资源路由可以一次声明一组增删改查入口。中间件在请求进入控制器前后执行鉴权、日志等逻辑，路由模型绑定则把网址参数自动解析成模型实例。

相关概念（6 项）：Route（网址与处理逻辑的映射）、Controller（组织请求处理）、Middleware（请求过滤与增强）、Route Model Binding（参数自动转模型）、Validation（请求数据校验）、Resource Route（一组 REST 路由）。

来源：主题名称取自 roadmap.sh 的 Laravel 路线索引（https://roadmap.sh/laravel）；概念用途为整理者归纳。

## Laravel 的 Eloquent ORM：模型、关系与数据库迁移

Eloquent 把数据表映射成模型类，开发者用模型方法查询和保存记录，用关联方法表达一对多、多对多等关系。迁移用 PHP 文件描述表结构变更，配合填充器生成初始数据，使数据库结构可以随代码一起演进。

相关概念（6 项）：Eloquent Model（数据表映射类）、Relationship（模型关联）、Query Builder（链式查询构造）、Migration（表结构变更）、Seeder（初始数据填充）、Factory（测试数据生成）。

来源：主题名称取自 roadmap.sh 的 Laravel 路线索引（https://roadmap.sh/laravel）；ORM 说明为整理者归纳。

## Laravel 的开发流程：Artisan 命令与 Blade 模板

Artisan 是 Laravel 的命令行工具，用于创建项目骨架、生成控制器与迁移、执行数据库操作和启动开发服务器。Blade 模板把页面拆成布局与片段，用指令处理循环、条件和数据输出。

相关步骤（5 项）：artisan serve（启动开发服务器）、artisan make（生成类与文件）、artisan migrate（执行迁移）、Blade 布局（复用页面骨架）、artisan queue（处理队列任务）。

来源：主题名称取自 roadmap.sh 的 Laravel 路线索引（https://roadmap.sh/laravel）；流程说明为整理者归纳。

## Laravel 生态中的常用工具

Laravel 的生态包括依赖管理、模板、认证、队列监控和测试工具，它们分属命令行工具、官方包与第三方库。

相关工具（8 项）：Composer（PHP 依赖管理）、Artisan（项目命令工具）、Blade（模板引擎）、Eloquent（对象关系映射）、Sanctum（接口认证包）、Livewire（服务端驱动交互组件）、PHPUnit（测试框架）、Telescope（调试与监控面板）。

来源：主题名称取自 roadmap.sh 的 Laravel 路线索引（https://roadmap.sh/laravel）；分类说明为整理者归纳。

## 如何开始练习 Laravel

可以做一个任务清单应用：用迁移建表，用 Eloquent 模型读写任务，用资源控制器提供增删改查，再用 Blade 渲染列表与表单。完成后加上表单校验和一条中间件，观察请求在各阶段的变化。

来源：练习建议为整理者归纳；主题名称取自 roadmap.sh 的 Laravel 路线索引（https://roadmap.sh/laravel）。
