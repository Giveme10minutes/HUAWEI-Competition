#!/usr/bin/env python3
"""采集 2026-11-02 高校就业平台岗位样本。

来源：云南大学就业信息网（云研科技平台）公开岗位页与接口，含完整职位描述。
BOSS直聘公开聚合页由 collect_boss_listing_samples_2026-11-02.py 单独采集。

只读公开页面，不使用账号、不绕过验证码。输出：
- references/raw/招聘岗位_2026-11-02/ynu/…
- references/招聘岗位样本_2026-11-02/岗位样本_原始.json / .csv（原始采集，未合并）
"""
import csv
import hashlib
import html
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(ROOT, "references", "raw", "招聘岗位_2026-11-02")
OUT_DIR = os.path.join(ROOT, "references", "招聘岗位样本_2026-11-02")
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
COLLECTED_AT = "2026-11-02"

YNUBASE = "https://jobs.ynu.edu.cn"
INDUSTRIES = [
    "农、林、牧、渔业", "采矿业", "制造业", "电力、热力、燃气及水生产和供应业",
    "建筑业", "批发和零售业", "交通运输、仓储和邮政业", "住宿和餐饮业",
    "信息传输、软件和信息技术服务业", "金融业", "房地产业", "租赁和商务服务业",
    "科学研究和技术服务业", "水利、环境和公共设施管理业", "居民服务、修理和其他服务业",
    "教育", "卫生和社会工作", "文化、体育和娱乐业",
    "公共管理、社会保障和社会组织", "国际组织", "军队",
]
TARGET_KEYWORDS = ["活动策划", "编辑", "新媒体", "律师", "护士", "普工", "服务员",
                   "物流", "销售", "平面设计"]

BOSS_LISTINGS = [
    ("餐饮服务员", "https://activity.zhipin.com/zhaopin/be318c071c5ee7d81XB_3ty5FA~~/"),
    ("物流财务/客服", "https://activity.zhipin.com/zhaopin/08f8f8f0758c2ce50nR609y6GA~~/"),
    ("物流文员客服", "https://activity.zhipin.com/zhaopin/36bbf44bc25026dd1nZ_2dW0Eg~~/"),
    ("餐饮门店多岗", "https://activity.zhipin.com/zhaopin/47ccf6a92b260bb21XZ72N27EA~~/"),
    ("客服/分拣", "https://activity.zhipin.com/zhaopin/a8e984632458efb91nR-39i9GA~~/"),
]


def now():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def request(url, timeout=40, retries=2):
    last = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": UA,
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Accept": "text/html,application/xhtml+xml,text/plain,*/*",
            })
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, r.read(), r.geturl()
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(1.5 * (attempt + 1))
    raise last


def load_json_url(url):
    status, body, _ = request(url)
    return status, json.loads(body.decode("utf-8", errors="ignore"))


def strip_tags(value):
    value = value or ""
    value = re.sub(r"<br\s*/?>", "\n", value, flags=re.I)
    value = re.sub(r"</(p|li|div|h\d)>", "\n", value, flags=re.I)
    value = re.sub(r"<[^>]+>", "", value)
    value = html.unescape(value)
    return "\n".join(line.strip() for line in value.splitlines() if line.strip())


def split_requirements(text):
    required, preferred = [], []
    for line in [x.strip(" -•·\t") for x in (text or "").splitlines() if x.strip()]:
        if re.search(r"优先|加分|更佳|preferred|plus", line, re.I):
            preferred.append(line)
        else:
            required.append(line)
    return required, preferred


def extract_graduation(text):
    hits = [x for x in (text or "").splitlines() if re.search(r"20\d\d届|应届|毕业", x)]
    return "；".join(hits[:3]) if hits else "未知"


def extract_attendance(text):
    hits = [x for x in (text or "").splitlines() if re.search(r"到岗|实习期|每周|天/周|立即入职", x)]
    return "；".join(hits[:3]) if hits else "未知"


def save_raw(platform, ident, url, body, meta):
    d = os.path.join(RAW_DIR, platform)
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, f"{ident}.html")
    if not os.path.exists(path):
        with open(path, "wb") as f:
            f.write(body)
    rel = os.path.relpath(path, ROOT)
    meta.append({
        "id": ident,
        "url": url,
        "path": rel,
        "bytes": len(body),
        "sha256": hashlib.sha256(body).hexdigest(),
        "fetched_at": now(),
    })
    return rel


# ---------- 云研平台 ----------
def ynu_list(industry=None, practice=None, keyword="", pages=3, count=30):
    rows = []
    for page in range(1, pages + 1):
        q = {"type_id": -1, "k": keyword, "city_name": "全国",
             "start_page": 1, "start": page, "count": count}
        if industry:
            q["industry"] = industry
        if practice is not None:
            q["is_practice"] = practice
        _, data = load_json_url(f"{YNUBASE}/module/getjobs?{urllib.parse.urlencode(q)}")
        rows.extend(data.get("data", []))
        time.sleep(0.35)
    return rows


def ynu_detail(pid, manifest):
    url = f"{YNUBASE}/detail/job?id={pid}"
    status, body, _ = request(url)
    raw = save_raw("ynu", str(pid), url, body, manifest)
    text = body.decode("utf-8", errors="ignore")
    i = text.find("window.PAGE_DATA = ")
    if i < 0:
        return None, raw
    data, _ = json.JSONDecoder().raw_decode(text[text.find("=", i) + 1:].lstrip())
    return data.get("job"), raw


def ynu_record(job, raw_path, source_id, recruitment_type):
    duties = strip_tags(job.get("job_descript"))
    req_text = strip_tags(job.get("job_require"))
    required, preferred = split_requirements(req_text)
    edu = "；".join(x for x in [job.get("degree_require"), f"专业：{job.get('about_major')}" if job.get("about_major") else ""] if x)
    excerpt = (duties or req_text)[:220]
    return {
        "source_id": source_id,
        "title": (job.get("job_name") or "").strip(),
        "employer": job.get("company_name") or "",
        "industry": (job.get("company") or {}).get("industry_category") or "",
        "function": job.get("category") or "",
        "region": job.get("city_name") or "",
        "recruitment_type": recruitment_type,
        "salary_text": job.get("salary") or "",
        "job_status": job.get("job_status") or "",
        "duties": duties,
        "required_skills": "\n".join(required),
        "preferred_skills": "\n".join(preferred),
        "education_requirement": edu or "未知",
        "graduation_requirement": extract_graduation(duties + "\n" + req_text),
        "attendance_requirement": extract_attendance(duties + "\n" + req_text),
        "source_platform": "云南大学就业信息网（云研科技平台）",
        "source_url": f"{YNUBASE}/detail/job?id={job.get('publish_id')}",
        "discovery_url": "",
        "published_at": job.get("publish_time") or "未知",
        "end_date": job.get("end_time") or "",
        "collected_at": COLLECTED_AT,
        "verification_status": "pending",
        "source_status": "公开详情页可读",
        "evidence_excerpt": excerpt,
        "raw_path": raw_path,
        "notes": "高校就业平台发布的招聘岗位；原文片段取自职位描述/任职要求，未做语义补全。",
    }


def accept_ynu(job):
    if not job:
        return False
    title = (job.get("job_name") or "").strip()
    duties = strip_tags(job.get("job_descript"))
    req = strip_tags(job.get("job_require"))
    if job.get("job_status") != "招聘中":
        return False
    if any(x in title for x in ["校园招聘正式启动", "招聘简章", "宣讲会"]):
        return False
    if len(title) > 45 or not title:
        return False
    return len(duties) >= 40 and len(req) >= 20


def collect_ynu():
    records, manifest = [], []
    seen = set()
    counter = [0]

    def next_id(prefix="YNU"):
        counter[0] += 1
        return f"{prefix}-{COLLECTED_AT.replace('-', '')}-{counter[0]:03d}"

    def take(rows, limit, recruitment_type, prefer_distinct_company=True):
        used_companies = {}
        for row in rows:
            c = row.get("company_name")
            if prefer_distinct_company and used_companies.get(c, 0) >= 1:
                continue
            if row.get("publish_id") in seen:
                continue
            try:
                job, raw = ynu_detail(row.get("publish_id"), manifest)
            except Exception as e:  # noqa: BLE001
                print("detail fail", row.get("publish_id"), e)
                continue
            if not accept_ynu(job):
                continue
            seen.add(row.get("publish_id"))
            used_companies[c] = used_companies.get(c, 0) + 1
            records.append(ynu_record(job, raw, next_id(), recruitment_type))
            if len(records) >= limit:
                return
        return

    # A. 21 个行业，每行业 3 条，优先不同企业
    for industry in INDUSTRIES:
        before = len(records)
        try:
            rows = ynu_list(industry=industry, pages=3)
        except Exception as e:  # noqa: BLE001
            print("list fail", industry, e)
            continue
        take(rows, before + 3, "校园招聘（高校就业平台）")
        print("industry", industry, "->", len(records) - before)

    # B. 关键词补充：产品规划样例与蓝领/服务岗
    for kw in TARGET_KEYWORDS:
        before = len(records)
        try:
            rows = ynu_list(keyword=kw, pages=2)
        except Exception as e:  # noqa: BLE001
            print("kw fail", kw, e)
            continue
        take(rows, before + 1, "校园招聘（高校就业平台）")
        print("keyword", kw, "->", len(records) - before)

    # C. 实习岗
    before = len(records)
    try:
        rows = ynu_list(practice=1, pages=3)
        take(rows, before + 10, "实习")
    except Exception as e:  # noqa: BLE001
        print("practice fail", e)
    print("practice ->", len(records) - before)

    return records, manifest


def write_outputs(records, manifest):
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(RAW_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "岗位样本_原始.json"), "w", encoding="utf-8") as f:
        json.dump({"collected_at": COLLECTED_AT, "count": len(records),
                   "records": records}, f, ensure_ascii=False, indent=2)
    cols = ["source_id", "title", "employer", "industry", "function", "region",
            "recruitment_type", "salary_text", "job_status", "duties",
            "required_skills", "preferred_skills", "education_requirement",
            "graduation_requirement", "attendance_requirement", "source_platform",
            "source_url", "discovery_url", "published_at", "end_date", "collected_at",
            "verification_status", "source_status", "evidence_excerpt", "raw_path", "notes"]
    with open(os.path.join(OUT_DIR, "岗位样本.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in records:
            w.writerow({k: r.get(k, "") for k in cols})
    with open(os.path.join(RAW_DIR, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump({"collected_at": now(), "files": manifest}, f, ensure_ascii=False, indent=2)
    print("wrote", len(records), "records;", len(manifest), "raw files")


def main():
    ynu, m1 = collect_ynu()
    write_outputs(ynu, m1)


if __name__ == "__main__":
    main()
