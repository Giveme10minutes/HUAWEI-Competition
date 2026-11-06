# Ruby on Rails：约定优于配置的全栈框架

Ruby on Rails 是用 Ruby 编写的开源全栈 Web 框架，强调约定优于配置和不要重复自己。它把数据库、路由、控制器与视图组织成统一结构，适合快速构建以数据为中心的 Web 应用。

来源：定位说明为整理者编写；主题名称取自 roadmap.sh 的 Ruby on Rails 路线索引（https://roadmap.sh/ruby-on-rails）。

## Ruby on Rails 是什么：约定优于配置的 MVC 框架

Rails 为常见任务预设了命名与目录约定，开发者按约定放置文件即可，减少手工配置。框架默认提供 MVC 分层、数据库迁移、资源路由和一套生成器，让新项目能较快跑起来。

来源：主题名称取自 roadmap.sh 的 Ruby on Rails 路线索引（https://roadmap.sh/ruby-on-rails）；用途说明为整理者归纳。

## Rails 的 MVC 结构：模型、视图与控制器

模型负责数据与业务规则，视图负责渲染页面，控制器接收请求、调用模型并选择响应。资源路由把一组网址映射到控制器的标准动作，请求经过路由、控制器与视图完成一次响应。

相关概念（6 项）：Model（数据与业务规则）、View（页面渲染）、Controller（请求处理）、Router（网址到动作的映射）、Resource Route（REST 风格路由）、Layout（页面共享外壳）。

来源：主题名称取自 roadmap.sh 的 Ruby on Rails 路线索引（https://roadmap.sh/ruby-on-rails）；MVC 说明为整理者归纳。

## Rails 的 ActiveRecord：模型、关系与迁移

ActiveRecord 把数据表映射为模型类，用关联方法表达一对一、一对多和多对多关系，用链式查询构造条件与排序。迁移用 Ruby 文件描述表结构变化，使数据库结构可以随代码版本逐步演进。

相关概念（6 项）：ActiveRecord（对象关系映射）、Association（模型关联）、Migration（结构变更）、Validation（数据校验）、Query Interface（链式查询）、Callback（模型生命周期钩子）。

来源：主题名称取自 roadmap.sh 的 Ruby on Rails 路线索引（https://roadmap.sh/ruby-on-rails）；ActiveRecord 说明为整理者归纳。

## Rails 的开发流程：生成器、Bundler 与 Rake 任务

新建项目后，Bundler 按依赖清单安装 gem，生成器可以快速产出模型、控制器和迁移骨架。开发服务器运行应用，Rake 任务执行数据库迁移、测试和自定义维护脚本，环境配置区分开发与生产。

相关步骤（5 项）：bundle install（安装依赖）、rails generate（生成代码骨架）、rails server（启动应用）、rails db:migrate（执行迁移）、rake task（运行维护任务）。

来源：主题名称取自 roadmap.sh 的 Ruby on Rails 路线索引（https://roadmap.sh/ruby-on-rails）；流程说明为整理者归纳。

## Rails 生态中的常用工具

Rails 的生态围绕依赖管理、后台任务、实时通信、认证与测试，它们分属命令行工具、官方组件和第三方 gem。

相关工具（8 项）：Bundler（依赖管理）、RubyGems（包仓库与打包工具）、Rake（任务运行工具）、ActiveJob（后台任务抽象）、ActionCable（实时通信组件）、Devise（认证库）、RSpec（测试框架）、Hotwire（服务端渲染交互方案）。

来源：主题名称取自 roadmap.sh 的 Ruby on Rails 路线索引（https://roadmap.sh/ruby-on-rails）；分类说明为整理者归纳。

## 如何开始练习 Ruby on Rails

可以做一个书店应用：用生成器创建书籍资源，执行迁移建表，在控制器里完成增删改查，再用视图渲染列表和表单。随后自定义校验与页面布局，观察约定命名如何减少配置。

来源：练习建议为整理者归纳；主题名称取自 roadmap.sh 的 Ruby on Rails 路线索引（https://roadmap.sh/ruby-on-rails）。
