#!/usr/bin/env python3
"""从 BOSS直聘公开 SEO 聚合页采集岗位摘要（不登录、不使用账号）。

列表页已包含岗位名、薪资、城市、经验、学历、摘要、企业与行业规模；
完整正文需登录，因此只记录可见摘要并在 source_status/notes 中标注。
"""
import hashlib
import json
import os
import re
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "references", "raw", "招聘岗位_2026-11-02", "boss_listing")
OUT = os.path.join(ROOT, "references", "招聘岗位样本_2026-11-02", "boss_records.json")
COLLECTED_AT = "2026-11-02"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

LISTINGS = [
    ("餐饮服务员", "住宿和餐饮业", "https://activity.zhipin.com/zhaopin/be318c071c5ee7d81XB_3ty5FA~~/"),
    ("餐饮门店多岗", "住宿和餐饮业", "https://activity.zhipin.com/zhaopin/47ccf6a92b260bb21XZ72N27EA~~/"),
    ("客服/分拣", "交通运输、仓储和邮政业", "https://activity.zhipin.com/zhaopin/a8e984632458efb91nR-39i9GA~~/"),
    ("物流文员客服", "交通运输、仓储和邮政业", "https://activity.zhipin.com/zhaopin/36bbf44bc25026dd1nZ_2dW0Eg~~/"),
    ("活动策划", "租赁和商务服务业", "https://activity.zhipin.com/zhaopin/a3070ebe93b6275f0XZ63Nq4/"),
    ("会议活动策划", "租赁和商务服务业", "https://activity.zhipin.com/zhaopin/2291647a5d8996521Xx63dS6Fg~~/"),
    ("普工/操作工", "制造业", "https://activity.zhipin.com/zhaopin/f71c93887f87343d0nd40ty1FQ~~/"),
    ("普工/操作工", "制造业", "https://activity.zhipin.com/zhaopin/7217b36d84eac38d03162t-0GA~~/"),
    ("护士/护理", "卫生和社会工作", "https://activity.zhipin.com/zhaopin/d3123df5e4f307fe031-092_GA~~/"),
    ("护士/护理", "卫生和社会工作", "https://activity.zhipin.com/zhaopin/e94b7fdb105a295b0XV70966/"),
]


def fetch(url, retries=2):
    last = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request("https://r.jina.ai/" + url, headers={
                "User-Agent": UA, "Accept": "text/plain", "Accept-Language": "zh-CN,zh;q=0.9"})
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(2 + attempt * 3)
    raise last


def salary_and_title(raw):
    m = re.search(r"((?:\d+(?:\.\d+)?-\d+(?:\.\d+)?[Kk](?:·\d+薪)?)|\d+(?:-\d+)?元/天|面议)\s*$", raw)
    salary = m.group(1) if m else ""
    title = raw[:m.start()].strip() if m else raw.strip()
    return title, salary


def parse(text):
    jobs = []
    matches = list(re.finditer(r"\*   ### \[(.+?)\]\((https://activity\.zhipin\.com/job_detail/[^)]+)\)", text))
    for idx, m in enumerate(matches):
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        block = text[m.end():end]
        title, salary = salary_and_title(m.group(1))
        if not title or len(title) > 45:
            continue
        city = exp = edu = ""
        cm = re.search(r"\[([^\]]+)\]\(https://activity\.zhipin\.com/c[^)]+\)\s*(.*)", block)
        if cm:
            city = cm.group(1).strip()
            tail = cm.group(2).strip()
            exp_m = re.search(r"(\d+年以内|1-3年|3-5年|5-10年|10年以上|经验不限|在校/应届|应届生)", tail)
            exp = exp_m.group(1) if exp_m else ""
            edu_m = re.search(r"(初中及以下|中专/中技|高中|大专|本科|硕士|博士|学历不限)", tail)
            edu = edu_m.group(1) if edu_m else ""
        # description: line after city line, before company logo
        desc = ""
        lines = [x.strip() for x in block.splitlines() if x.strip()]
        for i, line in enumerate(lines):
            if "activity.zhipin.com/c" in line:
                for nxt in lines[i + 1:]:
                    if nxt.startswith("### ["):
                        break
                    nxt = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", nxt)
                    nxt = re.sub(r"\[[^\]]*\]\([^)]*\)", "", nxt).strip()
                    if nxt:
                        desc = nxt
                        break
                break
        comp = re.search(r"### \[([^\]]+)\]\(https://activity\.zhipin\.com/gongsi/", block)
        company = comp.group(1).strip() if comp else ""
        industry = scale = ""
        if comp:
            tail = block[comp.end():]
            im = re.search(r"([一-龥/、]+)\s+(\d+-\d+人|10000人以上|1000-9999人|500-999人|100-499人|20-99人|0-20人)", tail)
            if im:
                industry, scale = im.group(1).strip(), im.group(2)
        if len(desc) < 20 or not company:
            continue
        jobs.append({
            "title": title, "salary": salary, "city": city, "experience": exp,
            "education": edu, "description": desc, "employer": company,
            "company_industry": industry, "scale": scale,
            "source_url": m.group(2), "listing_url": "",
        })
    return jobs


def main():
    os.makedirs(RAW, exist_ok=True)
    records, seen, counter = [], set(), 0
    for label, industry, url in LISTINGS:
        try:
            body = fetch(url)
        except Exception as e:  # noqa: BLE001
            print("FAIL", label, e)
            continue
        text = body.decode("utf-8", errors="ignore")
        if "Access Verification" in text or "验证码" in text:
            print("BLOCKED", label)
            continue
        h = hashlib.sha256(url.encode()).hexdigest()[:12]
        path = os.path.join(RAW, f"{h}.txt")
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
        picked = 0
        for job in parse(text):
            key = (job["employer"], job["title"], job["city"])
            if key in seen:
                continue
            if job["title"] == "" or len(job["description"]) < 20:
                continue
            seen.add(key)
            counter += 1
            picked += 1
            job.update({
                "source_id": f"BOSS-{COLLECTED_AT.replace('-', '')}-{counter:03d}",
                "industry": industry, "function": label,
                "recruitment_type": "社会招聘（BOSS直聘公开聚合页）",
                "job_status": "未显示",
                "published_at": "未知",
                "collected_at": COLLECTED_AT,
                "source_platform": "BOSS直聘（activity.zhipin.com 公开 SEO 聚合页，经 r.jina.ai 读取）",
                "source_status": "公开聚合页摘要；完整职位正文需登录",
                "verification_status": "pending",
                "raw_path": os.path.relpath(path, ROOT),
                "notes": "BOSS直聘 SEO 聚合页可见摘要；未使用账号、未绕过验证码；薪资与城市按页面原文记录。",
            })
            records.append(job)
            if picked >= 3:
                break
        print(label, "picked", picked)
        time.sleep(1)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"collected_at": COLLECTED_AT, "count": len(records), "records": records},
                  f, ensure_ascii=False, indent=2)
    print("wrote", len(records), "BOSS records")


if __name__ == "__main__":
    main()
