# ASP.NET Core：跨平台的 .NET Web 框架

ASP.NET Core 是 Microsoft 维护的开源 Web 框架，可在 Windows、Linux 与 macOS 上运行。它用 C# 编写，提供请求管线、依赖注入、配置系统和多种应用模板，适合构建接口服务与网页应用。

来源：定位说明为整理者编写；主题名称取自 roadmap.sh 的 ASP.NET Core 路线索引（https://roadmap.sh/aspnet-core）。

## ASP.NET Core 是什么：跨平台的服务端框架

ASP.NET Core 把一次请求抽象为经过中间件管线的处理流程，应用在其中注册路由、鉴权和业务处理。框架自带轻量服务器与依赖注入容器，既可用于小型接口，也可组织大型分层应用。

来源：主题名称取自 roadmap.sh 的 ASP.NET Core 路线索引（https://roadmap.sh/aspnet-core）；用途说明为整理者归纳。

## ASP.NET Core 的核心概念：中间件与依赖注入

中间件按注册顺序组成请求管线，每个中间件可以处理请求、调用下一个中间件或直接返回响应。依赖注入容器按生命周期管理服务，控制器、数据访问和其他组件通过构造函数声明所需依赖。

相关概念（6 项）：Middleware（请求管线组件）、RequestDelegate（表示后续处理的委托）、Service（注册到容器的服务）、Dependency Injection（依赖注入）、Service Lifetime（服务生命周期）、Filter（控制器动作前后的过滤器）。

来源：主题名称取自 roadmap.sh 的 ASP.NET Core 路线索引（https://roadmap.sh/aspnet-core）；概念用途为整理者归纳。

## ASP.NET Core 的数据访问：EF Core 与迁移

Entity Framework Core 是 .NET 的对象关系映射框架，用 C# 类表示数据表，用 LINQ 查询数据。迁移把模型变更转换成数据库结构更新，使开发库和生产库的演进可以按步骤执行。

相关概念（5 项）：DbContext（数据库会话）、Entity（映射表的实体类）、LINQ Query（类型安全查询）、Migration（结构变更脚本）、Code First（先写模型再生成结构）。

来源：主题名称取自 roadmap.sh 的 ASP.NET Core 路线索引（https://roadmap.sh/aspnet-core）；数据访问说明为整理者归纳。

## ASP.NET Core 的开发流程：项目模板与请求管线

开发通常从 dotnet 命令行或集成开发环境创建项目模板开始，在入口文件里注册服务与中间件，再编写控制器或最小接口。运行、测试和发布分别通过对应命令完成，配置从环境变量与配置文件读取。

相关步骤（5 项）：dotnet new（创建项目模板）、Program（注册服务与管线）、Controller（处理请求的控制器）、dotnet run（本地运行）、dotnet publish（生成发布产物）。

来源：主题名称取自 roadmap.sh 的 ASP.NET Core 路线索引（https://roadmap.sh/aspnet-core）；流程说明为整理者归纳。

## ASP.NET Core 生态中的常用工具

ASP.NET Core 的工具覆盖 SDK、包管理、对象映射、日志、测试与接口文档，它们分属命令行工具、库与服务端组件。

相关工具（8 项）：.NET SDK（编译与运行工具）、NuGet（包管理器）、Entity Framework Core（对象关系映射）、Kestrel（内置 Web 服务器）、Serilog（结构化日志库）、xUnit（测试框架）、Swagger（接口文档工具）、Visual Studio（集成开发环境）。

来源：主题名称取自 roadmap.sh 的 ASP.NET Core 路线索引（https://roadmap.sh/aspnet-core）；分类说明为整理者归纳。

## 如何开始练习 ASP.NET Core

可以做一个图书管理接口：用 EF Core 定义图书实体与数据库上下文，提供增删改查接口，并加上输入校验和统一错误返回。练习时观察中间件顺序对请求的影响，再用迁移更新一次表结构。

来源：练习建议为整理者归纳；主题名称取自 roadmap.sh 的 ASP.NET Core 路线索引（https://roadmap.sh/aspnet-core）。
