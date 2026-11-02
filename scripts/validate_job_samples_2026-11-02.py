#!/usr/bin/env python3
"""校验、去重并生成岗位样本台账。

输入：references/招聘岗位样本_2026-11-02/岗位样本.json
输出：岗位样本.csv、来源台账.csv、来源索引.md、统计.json
"""
import csv
import hashlib
import json
import os
import re
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "references", "招聘岗位样本_2026-11-02")
RAW = os.path.join(ROOT, "references", "raw", "招聘岗位_2026-11-02")

BOSS_INDUSTRY = {
    "餐饮服务员": "住宿和餐饮业",
    "餐饮门店多岗": "住宿和餐饮业",
    "物流财务/客服": "交通运输、仓储和邮政业",
    "物流文员客服": "交通运输、仓储和邮政业",
    "客服/分拣": "交通运输、仓储和邮政业",
}


def boss_to_record(x):
    desc = clean(x.get("description"))
    duty_m = re.search(r"(岗位职责|工作内容|职位描述|工作职责)\s*[:：]?", desc)
    req_m = re.search(r"(任职要求|岗位要求|任职资格|招聘要求|要求)\s*[:：]", desc)
    duties, req_text = desc, ""
    if duty_m and req_m and req_m.start() > duty_m.start():
        duties = desc[duty_m.end():req_m.start()].strip(" ：:；;")
        req_text = desc[req_m.end():].strip()
    elif req_m and not duty_m:
        duties = desc[:req_m.start()].strip(" ：:；;")
        req_text = desc[req_m.end():].strip()
    elif duty_m and not req_m:
        duties = desc[duty_m.end():].strip(" ：:；;")
    if len(duties) < 30:
        duties = desc
    required, preferred = [], []
    for seg in re.split(r"(?<=[。；;！!])|\s+(?=\d+[.、)])", req_text or ""):
        seg = seg.strip(" -•·\t。；;")
        if len(seg) < 2:
            continue
        if re.search(r"优先|加分|更佳|preferred|plus", seg, re.I):
            preferred.append(seg)
        else:
            required.append(seg)
    if not required and not preferred:
        # 聚合页摘要常把职责与要求写成一段；只提取含条件词的短句，职责保留原文。
        for seg in re.split(r"(?<=[。；;！!])|\s+(?=\d+[.、)])", desc):
            seg = seg.strip(" -•·\t。；;")
            if len(seg) < 4:
                continue
            if re.search(r"优先|加分|更佳", seg):
                preferred.append(seg)
            elif re.search(r"学历|经验|岁|资格证|执业证|证书|能力|熟悉|掌握|具备|要求", seg) and not re.search(r"负责|策划|执行|撰写|协助|参与|跟进|维护", seg):
                required.append(seg)
    edu = "；".join(v for v in [x.get("education"), f"经验：{x.get('experience')}" if x.get("experience") else ""] if v) or "未显示"
    return {
        "source_id": x["source_id"],
        "title": clean(x.get("title")),
        "employer": clean(x.get("employer")),
        "industry": x.get("industry", ""),
        "function": x.get("function", ""),
        "region": clean(x.get("city")),
        "recruitment_type": x.get("recruitment_type", "社会招聘（BOSS直聘公开聚合页）"),
        "salary_text": x.get("salary", ""),
        "job_status": "未显示",
        "duties": duties,
        "required_skills": "\n".join(required),
        "preferred_skills": "\n".join(preferred),
        "education_requirement": edu,
        "graduation_requirement": extract_graduation(desc),
        "attendance_requirement": extract_attendance(desc),
        "source_platform": x.get("source_platform", ""),
        "source_url": x.get("source_url", ""),
        "discovery_url": x.get("listing_url", ""),
        "published_at": "未知",
        "end_date": "",
        "collected_at": x.get("collected_at", ""),
        "verification_status": "pending",
        "source_status": x.get("source_status", ""),
        "evidence_excerpt": desc[:220],
        "raw_path": x.get("raw_path", ""),
        "notes": x.get("notes", ""),
    }


def reclassify(record):
    title = record.get("title", "")
    if record.get("source_id", "").startswith("BOSS-"):
        if "财务" in title or "会计" in title:
            record["industry"], record["function"] = "租赁和商务服务业", "财务"
        elif any(k in title for k in ["物业", "水电", "工程主管"]):
            record["industry"], record["function"] = "房地产业", "物业/维修"
        elif any(k in title for k in ["剪辑", "拍摄", "短视频"]):
            record["industry"], record["function"] = "文化、体育和娱乐业", "视频剪辑"
        elif record.get("function") == "客服/分拣":
            record["function"] = "快递/物流/分拣"
        if len(title) > 24 or title.count(" ") > 3 or "洗浴" in title:
            record["title"] = record["function"]
    return record


def is_announcement(title):
    return bool(re.search(r"校园招聘|招聘公告|专场活动公告|招才引智|宣讲会", title or ""))


def clean(value):
    value = value or ""
    value = re.sub(r"[ \t]+", " ", value)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()


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


def main():
    with open(os.path.join(OUT, "岗位样本_原始.json"), encoding="utf-8") as f:
        payload = json.load(f)
    records = payload["records"]
    boss_path = os.path.join(OUT, "boss_records.json")
    if os.path.exists(boss_path):
        with open(boss_path, encoding="utf-8") as f:
            records += [boss_to_record(x) for x in json.load(f)["records"]]

    deduped, seen, seen_ids, dropped = [], set(), set(), []
    for r in records:
        for key in ("title", "employer", "region", "duties", "required_skills",
                    "preferred_skills", "education_requirement", "evidence_excerpt",
                    "notes", "source_status"):
            r[key] = clean(r.get(key))
        r = reclassify(r)
        sid = r.get("source_id", "")
        if (r.get("source_platform", "").find("job_detail") >= 0
                or ("公开 SEO 页" in r.get("source_platform", "") and "聚合页" not in r.get("source_platform", ""))
                or r.get("duties", "").startswith("Title:")):
            dropped.append(sid + ":旧详情页解析")
            continue
        if is_announcement(r.get("title")):
            dropped.append(sid + ":公告")
            continue
        if sid.startswith("BOSS-") and len(r.get("duties", "")) < 30:
            dropped.append(sid + ":正文过短")
            continue
        if sid in seen_ids:
            dropped.append(sid + ":重复编号")
            continue
        seen_ids.add(sid)
        key = (r.get("employer", ""), r.get("title", ""), r.get("region", ""))
        if key in seen:
            dropped.append(r.get("source_id"))
            continue
        seen.add(key)
        if not r.get("required_skills"):
            r["required_skills"] = "未明确列出（见职位描述）"
        if not r.get("preferred_skills"):
            r["preferred_skills"] = "未明确列出"
        deduped.append(r)

    cols = ["source_id", "title", "employer", "industry", "function", "region",
            "recruitment_type", "salary_text", "job_status", "duties",
            "required_skills", "preferred_skills", "education_requirement",
            "graduation_requirement", "attendance_requirement", "source_platform",
            "source_url", "discovery_url", "published_at", "end_date", "collected_at",
            "verification_status", "source_status", "evidence_excerpt", "raw_path", "notes"]
    with open(os.path.join(OUT, "岗位样本.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows({k: r.get(k, "") for k in cols} for r in deduped)

    with open(os.path.join(OUT, "岗位样本.json"), "w", encoding="utf-8") as f:
        json.dump({"collected_at": payload.get("collected_at"),
                   "count": len(deduped), "records": deduped},
                  f, ensure_ascii=False, indent=2)

    # 来源台账：逐条来源与原始快照
    with open(os.path.join(RAW, "manifest.json"), encoding="utf-8") as f:
        manifest = {x["url"].replace("https://r.jina.ai/", ""): x
                    for x in json.load(f).get("files", [])}
    with open(os.path.join(OUT, "来源台账.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["source_id", "source_platform", "source_url", "collected_at",
                    "source_status", "raw_path", "sha256", "bytes", "fetched_at"])
        for r in deduped:
            m = manifest.get(r["source_url"], {}) if not r["source_id"].startswith("BOSS-") else {}
            sha, size = m.get("sha256", ""), m.get("bytes", "")
            if not sha and r.get("raw_path"):
                p = os.path.join(ROOT, r["raw_path"])
                if os.path.exists(p):
                    with open(p, "rb") as fh:
                        blob = fh.read()
                    sha, size = hashlib.sha256(blob).hexdigest(), len(blob)
            w.writerow([r["source_id"], r["source_platform"], r["source_url"],
                        r["collected_at"], r["source_status"], r["raw_path"],
                        sha or "未找到", size, m.get("fetched_at", "")])

    # 统计
    stats = {
        "count": len(deduped),
        "dropped_duplicates": dropped,
        "by_platform": dict(Counter(r["source_platform"] for r in deduped)),
        "by_industry": dict(Counter(r["industry"] for r in deduped).most_common()),
        "by_recruitment_type": dict(Counter(r["recruitment_type"] for r in deduped)),
        "unique_employers": len({r["employer"] for r in deduped}),
        "unknown_published_at": sum(1 for r in deduped if r["published_at"] in ("", "未知")),
        "boss_partial": sum(1 for r in deduped if r["source_id"].startswith("BOSS-")),
    }
    with open(os.path.join(OUT, "统计.json"), "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    # 来源索引
    lines = [
        "# 招聘岗位样本来源索引",
        "",
        f"采集日期：{payload.get('collected_at')}｜共 {len(deduped)} 条｜不同企业 {stats['unique_employers']} 家",
        "",
        "用途：为职业方向比较、能力差距和阶段任务提供可追溯的岗位原文样本。按“能读到职责与要求”选取，不追求统计代表性，不能据此推断行业薪资、岗位数量或录用难度。",
        "",
        "## 字段与审核",
        "",
        "- 字段对应 `data/templates/job_import.csv`，并增加 `salary_text`、`job_status`、`source_platform`、`source_status`、`raw_path`、`notes`。",
        "- `verification_status` 均为 `pending`：页面可读，但尚未逐条人工复核企业资质与当前在招状态。",
        "- 必需与优先条件按原文是否出现“优先/加分”拆分；原文没有“优先”表述时，`preferred_skills` 记“未明确列出”，不反推。",
        "- `published_at` 为平台原文显示的发布日期；BOSS直聘公开页不显示发布日期，记“未知”。",
        "- “毕业届别/到岗要求”只在原文出现时摘录，否则记“未知”。",
        "",
        "## 平台分布",
        "",
        "| 平台 | 条数 | 说明 |",
        "| --- | --- | --- |",
    ]
    for p, n in stats["by_platform"].items():
        lines.append(f"| {p} | {n} | {'部分正文，完整内容需登录' if 'BOSS' in p else '公开详情页可读'} |")
    lines += ["", "## 行业分布", "", "| 行业 | 条数 |", "| --- | --- |"]
    for ind, n in stats["by_industry"].items():
        lines.append(f"| {ind} | {n} |")
    lines += ["", "## 逐条索引", "",
              "| 编号 | 岗位 | 企业 | 行业 | 地区 | 类型 | 发布 | 来源 |",
              "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in deduped:
        title = r["title"].replace("|", "／")
        employer = r["employer"].replace("|", "／")
        lines.append(
            f"| {r['source_id']} | {title} | {employer} | {r['industry']} | "
            f"{r['region'].replace('|', '／')} | {r['recruitment_type']} | "
            f"{r['published_at']} | [原文]({r['source_url']}) |")
    lines += ["", "## 限制", "",
              "1. 主样本来自云南大学就业信息网的公开校园招聘岗位，企业所在地域与招聘对象受该平台影响，不能代表全国岗位市场。",
              "2. BOSS直聘只取到公开 SEO 页的可见部分；薪资、发布日期、完整职责常需登录，样本中已标注，不补猜。",
              "3. 鱼泡直聘、58同城、智联招聘在本轮返回验证码或登录页，未采集；详见 `references/raw/招聘岗位_2026-11-02/_platform_access_2026-11-02.md`。",
              "4. 岗位样本不等于职业介绍；单个招聘广告不能代表完整职业，使用时应与职业介绍、从业者经历和本人核实结合。",
              ""]
    with open(os.path.join(OUT, "来源索引.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(json.dumps(stats, ensure_ascii=False, indent=2))
    print("outputs:", OUT)


if __name__ == "__main__":
    main()
