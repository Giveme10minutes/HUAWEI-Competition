# Spring Boot：简化 Spring 应用搭建的框架

Spring Boot 是构建在 Spring 之上的 Java 框架，提供自动配置、起步依赖和内嵌服务器。它让开发者用较少配置启动一个可运行的 Web 应用或微服务，同时保留 Spring 的依赖注入与生态。

来源：定位说明为整理者编写；主题名称取自 roadmap.sh 的 Spring Boot 路线索引（https://roadmap.sh/spring-boot）。

## Spring Boot 是什么：自动配置与开箱即用的 Spring

Spring Boot 根据类路径上的依赖推断常见配置，减少手写 XML 或配置类的工作。应用可以打包成可执行文件直接运行，内嵌服务器随应用启动，不需要单独部署到外部容器。

来源：主题名称取自 roadmap.sh 的 Spring Boot 路线索引（https://roadmap.sh/spring-boot）；用途说明为整理者归纳。

## Spring Boot 的自动配置与起步依赖

自动配置依据引入的库和配置项决定创建哪些 Bean，开发者可以用配置属性覆盖默认值。起步依赖把一组相关库打包成一个坐标，引入后即可获得该场景所需的依赖组合。

相关概念（5 项）：@SpringBootApplication（应用入口注解）、Auto-configuration（按条件推断配置）、Starter（场景依赖组合）、application.properties（配置属性文件）、Profile（按环境切换配置）。

来源：主题名称取自 roadmap.sh 的 Spring Boot 路线索引（https://roadmap.sh/spring-boot）；配置说明为整理者归纳。

## Spring Boot 的依赖注入与 Bean 管理

Spring 容器负责创建和组装对象，被管理的对象称为 Bean。组件通过注解声明为 Bean，控制器和服务用构造函数声明依赖，容器按类型注入；Bean 的作用域决定每次获取是否复用同一实例。

相关概念（6 项）：IoC Container（对象容器）、Bean（容器管理的对象）、@Component（通用组件声明）、@Service（业务层组件）、Constructor Injection（构造函数注入）、Bean Scope（实例作用域）。

来源：主题名称取自 roadmap.sh 的 Spring Boot 路线索引（https://roadmap.sh/spring-boot）；依赖注入说明为整理者归纳。

## Spring Boot 的 Web 开发：Spring MVC 与数据访问

Spring MVC 把请求映射到控制器方法，方法参数从网址、查询串或请求体绑定，返回值序列化为 JSON 或交给视图渲染。数据访问通常用 Spring Data JPA 配合实体类和仓库接口，把查询方法声明成接口即可使用。

相关概念（5 项）：@RestController（接口控制器）、@RequestMapping（请求映射）、Spring Data JPA（数据访问抽象）、Entity（映射表的实体）、Actuator（运行状态端点）。

来源：主题名称取自 roadmap.sh 的 Spring Boot 路线索引（https://roadmap.sh/spring-boot）；Web 与数据访问说明为整理者归纳。

## Spring Boot 生态中的常用工具

Spring Boot 的工具覆盖项目生成、构建、数据访问、安全、监控与测试，它们分属框架模块、构建工具和库。

相关工具（8 项）：Spring Initializr（项目生成器）、Maven（构建工具）、Gradle（构建工具）、Spring Data JPA（数据访问模块）、Spring Security（认证与授权框架）、Actuator（监控端点）、JUnit（测试框架）、Mockito（测试替身库）。

来源：主题名称取自 roadmap.sh 的 Spring Boot 路线索引（https://roadmap.sh/spring-boot）；分类说明为整理者归纳。

## 如何开始练习 Spring Boot

可以用项目生成器创建一个带 Web 与 JPA 依赖的工程，定义图书实体和仓库接口，再写控制器提供增删改查接口。练习时更换一次配置属性，观察自动配置和内嵌服务器如何随之变化。

来源：练习建议为整理者归纳；主题名称取自 roadmap.sh 的 Spring Boot 路线索引（https://roadmap.sh/spring-boot）。
