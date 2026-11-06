# Django：Python 的全栈 Web 框架

Django 是用 Python 编写的开源 Web 框架，遵循“自带常用组件”的设计，内置对象关系映射、后台管理、表单、认证与安全防护。它适合需要快速搭建数据驱动网站或接口服务的项目。

来源：定位说明为整理者编写；主题名称取自 roadmap.sh 的 Django 路线索引（https://roadmap.sh/django）。

## Django 是什么：自带常用组件的全栈框架

Django 把常见的 Web 开发任务做成框架内置能力，开发者按项目与应用分层组织代码。它采用模型、模板、视图的结构，并用统一的路由配置把网址映射到处理函数。

来源：主题名称取自 roadmap.sh 的 Django 路线索引（https://roadmap.sh/django）；用途说明为整理者归纳。

## Django 的核心概念：模型、视图与模板

模型用 Python 类描述数据表与关系，视图接收请求并返回响应，模板负责把数据渲染成页面。路由配置把网址匹配到视图；类视图则把常用的增删改查流程封装成可复用的基类。

相关概念（6 项）：Model（数据模型）、View（请求处理逻辑）、Template（页面渲染模板）、URLconf（网址路由配置）、Class-Based View（可复用的类视图）、Middleware（请求与响应钩子）。

来源：主题名称取自 roadmap.sh 的 Django 路线索引（https://roadmap.sh/django）；概念用途为整理者归纳。

## Django 的 ORM 与迁移：用 Python 操作数据库

Django ORM 把数据库操作写成 Python 调用，查询结果以模型对象或查询集返回，可以继续过滤、排序和聚合。迁移把模型定义的变更记录成文件，再按顺序应用到数据库，使结构演进可追踪。

相关概念（5 项）：QuerySet（惰性查询集合）、Manager（模型查询入口）、Migration（结构变更记录）、makemigrations（生成迁移文件）、migrate（应用迁移）。

来源：主题名称取自 roadmap.sh 的 Django 路线索引（https://roadmap.sh/django）；ORM 说明为整理者归纳。

## Django 的 admin 与表单：后台管理与数据校验

Django 会依据模型自动生成管理后台，注册模型后即可增删改查数据，适合早期内容维护。表单系统把提交数据绑定到 Python 表单或模型表单，统一做字段校验并返回错误信息。

相关概念（5 项）：admin.py（注册后台模型）、ModelAdmin（后台展示配置）、Form（表单定义与校验）、ModelForm（由模型生成表单）、cleaned_data（校验后的数据）。

来源：主题名称取自 roadmap.sh 的 Django 路线索引（https://roadmap.sh/django）；后台与表单说明为整理者归纳。

## Django 生态中的常用工具

Django 项目会配合项目管理命令、接口扩展、数据库驱动、调试面板和测试工具使用，这些条目分属命令行工具、第三方库与调试工具，实际组合按项目需要选择。

相关工具（7 项）：manage.py（项目管理命令）、Django REST Framework（接口开发库）、psycopg（PostgreSQL 驱动）、Celery（异步任务队列）、Django Debug Toolbar（调试面板）、pytest（测试框架）、Gunicorn（应用服务器）。

来源：主题名称取自 roadmap.sh 的 Django 路线索引（https://roadmap.sh/django）；分类说明为整理者归纳；工具清单为整理者补充。

## 如何开始练习 Django

可以做一个带后台的博客：定义文章与分类模型，生成迁移，注册到管理后台，再写列表页和详情页模板。完成后尝试增加表单提交与字段校验，体会模型、视图、模板三者的配合。

来源：练习建议为整理者归纳；主题名称取自 roadmap.sh 的 Django 路线索引（https://roadmap.sh/django）。
