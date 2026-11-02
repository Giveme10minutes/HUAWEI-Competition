# 招聘平台可读性探测记录（2026-11-02）

用途：说明本轮岗位样本为什么以高校就业平台为主、BOSS直聘只取公开 SEO 页，以及鱼泡等平台为何没有进入样本。以下均为公开页面只读探测，未使用账号、未提交验证码、未使用绕过验证的服务。

| 平台 | 探测入口 | 结果 | 处理 |
| --- | --- | --- | --- |
| BOSS直聘（站内搜索） | `https://www.bosszhipin.com/web/geek/job?query=运营&city=101010100` | 跳转 `https://www.zhipin.com/web/user/` 登录/注册页 | 不使用账号，不采集 |
| BOSS直聘（公开 SEO 页） | `https://activity.zhipin.com/zhaopin/<hash>~~/`、`https://activity.zhipin.com/job_detail/<id>.html` | 可读取职位列表、城市、经验、学历、部分职位描述；详情页提示“登录查看完整内容” | 经 `r.jina.ai` 只读代理采集可见部分，标注“部分正文” |
| 鱼泡直聘（首页/SEO 页） | `https://www.yupao.com/`、`/zhaogong/...`、`/s/yp.../` | 阿里云 WAF 滑块验证；经 `r.jina.ai` 仍返回 Access Verification | 不采集，未尝试绕过 |
| 58同城 | `https://bj.58.com/job/` | 返回“请输入验证码” | 不采集 |
| 智联招聘 | `https://www.zhaopin.com/jobdetail/...` | 返回 Security Verification | 不采集 |
| 猎聘 / 职友集 / 实习僧 | 首页可访问 | 首页可读，岗位列表多为脚本渲染；本轮未逐条解析 | 作为后续候选来源，不计入本轮样本 |
| 云南大学就业信息网（云研科技平台） | `https://jobs.ynu.edu.cn/module/jobs`、`/module/getjobs`、`/detail/job?id=...` | 公开 JSON 列表与详情页可读，含职位描述、任职要求、学历、专业、发布时间、招聘状态、企业行业 | 作为本轮主样本来源 |

## 说明

- BOSS直聘公开 SEO 页的职位详情由第三方只读代理返回，可能随时变化；`source_status` 字段逐条标注“公开页部分正文，完整内容需登录”。
- 鱼泡直聘以蓝领/建筑/物流岗位为主，本轮未能取得可核验正文，因此样本中的蓝领/服务岗主要来自高校就业平台的“普工/操作工”“餐饮服务员”等岗位，不能代表鱼泡平台。
- 上述平台条款、登录要求与反爬策略可能变化；下次采集前应重新探测，不沿用本记录当作长期可用性承诺。
- 证据快照：`_blocked/boss_search_jina_2026-11-02.txt`、`_blocked/yupao_jina_2026-11-02.txt`、`_blocked/yupao_home_2026-11-02.html`。
