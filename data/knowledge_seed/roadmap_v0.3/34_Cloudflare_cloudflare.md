# Cloudflare：边缘网络与安全平台

Cloudflare 通过分布在不同地点的边缘网络，为网站和应用提供 DNS 解析、缓存加速、安全防护与边缘计算能力。接入后，访问流量先到达边缘节点，再由节点回源到源站服务器。

来源：主题名称取自 roadmap.sh 的 Cloudflare 路线索引（https://roadmap.sh/cloudflare）；定位说明为整理者归纳。

## Cloudflare 是什么：解决什么问题

网站直接暴露源站时，容易受到流量攻击，也难以让各地访问者都获得较低延迟。Cloudflare 在源站前增加一层代理，承担 DNS、缓存、TLS 终止和攻击过滤，源站只需处理回源请求。

参考：Cloudflare 开发者文档（https://developers.cloudflare.com/）。

## Cloudflare 的核心概念：DNS、代理与缓存

接入站点需要把域名的名称服务器指向 Cloudflare，随后在 DNS 记录中决定是否开启代理。开启代理的记录会经过边缘网络，可以享受缓存与防护；缓存是否命中取决于文件类型、缓存规则和 TTL。

相关概念（6 项）：名称服务器（接管域名解析）、DNS 记录（域名到地址的映射）、代理状态（流量是否经过边缘）、缓存规则（控制哪些请求缓存）、TTL（缓存有效期）、缓存清除（让旧缓存失效）。

参考：Cloudflare 开发者文档（https://developers.cloudflare.com/）。

## Cloudflare 的安全能力

边缘节点可以在请求到达源站前拦截恶意流量，常见能力包括 DDoS 缓解、Web 应用防火墙、机器人管理和 TLS 配置。访问控制类产品则把内部应用藏在身份验证之后，而不是直接暴露在公网。

相关能力（6 项）：DDoS 防护（吸收流量攻击）、WAF（按规则拦截请求）、Bot Management（识别自动化流量）、SSL/TLS（加密与证书管理）、Zero Trust（按身份控制访问）、速率限制（限制请求频率）。

来源：主题名称取自 roadmap.sh 的 Cloudflare 路线索引（https://roadmap.sh/cloudflare）；能力说明为整理者归纳。

## Cloudflare Workers：在边缘运行代码

Workers 让 JavaScript 或 TypeScript 代码运行在边缘节点，可就近处理请求、改写响应或调用其他服务。它配套键值存储、对象存储和数据库等绑定，适合轻量接口与中间层逻辑。

相关组件（6 项）：Workers（边缘函数运行时）、Workers KV（低延迟键值存储）、R2（对象存储）、D1（SQL 数据库）、Durable Objects（有状态协调对象）、Wrangler（本地开发与部署命令行）。

参考：Cloudflare Workers 文档（https://developers.cloudflare.com/workers/）。

## Cloudflare 的典型使用场景

Cloudflare 常见于网站加速与防护、跨地域访问优化、静态资源分发，以及把轻量逻辑放到边缘执行。是否启用某项能力取决于业务对缓存一致性、合规和源站架构的要求。

相关场景（5 项）：网站加速（缓存静态资源）、DDoS 防护（抵御流量攻击）、全球负载均衡（按策略分配流量）、边缘接口（就近处理请求）、零信任访问（保护内部应用）。

来源：主题名称取自 roadmap.sh 的 Cloudflare 路线索引（https://roadmap.sh/cloudflare）；场景说明为整理者归纳。

## 如何开始练习 Cloudflare

最小练习是用 Wrangler 创建一个 Worker 项目，在本地开发模式中让 fetch 处理函数返回一段 JSON，再修改为读取请求路径并返回不同内容。若已有测试域名，可以把它接入并观察 DNS 与缓存行为；产出是一个可本地运行的 Worker 和一份请求响应记录。

来源：该练习由整理者归纳设计；主题名称取自 roadmap.sh 的 Cloudflare 路线索引（https://roadmap.sh/cloudflare）。
