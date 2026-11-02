#!/usr/bin/env python3
"""Merge the per-batch job sample tables into one master CSV with unique ids.

Each batch keeps its own directory (own README, ledger, raw snapshots). This
script only *reads* them and writes a single combined table for downstream use
(agent knowledge base, statistics, manual review). It never modifies the source
CSVs.

Usage:
    python3 -I scripts/job_samples_merge.py
    python3 -I scripts/job_samples_merge.py --out references/xxx.csv
"""
import argparse
import csv
import os
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (dataset label, id prefix, directory, csv file name)
BATCHES = [
    ("第一批_91条", "F1", "references/招聘岗位样本_2026-11-02", "岗位样本.csv"),
    ("BOSS_通用行业", "B1", "references/招聘岗位样本_BOSS_通用行业_2026-11-02",
     "岗位样本_BOSS通用行业_2026-11-02.csv"),
    ("BOSS_计算机", "B2", "references/招聘岗位样本_BOSS_计算机_2026-11-02",
     "岗位样本_BOSS计算机_2026-11-02.csv"),
    ("BOSS_其他行业", "B3", "references/招聘岗位样本_BOSS_其他行业_2026-11-02",
     "岗位样本_BOSS其他行业_2026-11-02.csv"),
]

# 两批数据的 industry 口径不同：第一批是国标行业门类，BOSS 批次是采集时的
# 关键词分类（混有职能）。这里只做一层「导航用」的大类归并，原始值保留在
# industry 列，不做改写。
INDUSTRY_GROUP = {
    "互联网/软件开发": "信息技术", "互联网/数据": "信息技术",
    "互联网/算法": "信息技术", "互联网/测试": "信息技术",
    "互联网/运维": "信息技术", "互联网/安全": "信息技术",
    "IT服务/实施": "信息技术", "信息传输、软件和信息技术服务业": "信息技术",
    "金融业": "金融", "金融/银行": "金融", "金融/保险": "金融",
    "卫生和社会工作": "医疗健康", "医疗/护理": "医疗健康",
    "教育": "教育", "教育/幼教": "教育", "教育培训": "教育",
    "建筑业": "建筑与房地产", "建筑/施工": "建筑与房地产", "房地产业": "建筑与房地产",
    "制造业": "制造业", "机械/制造": "制造业", "生产制造/技工": "制造业",
    "电力、热力、燃气及水生产和供应业": "能源电力", "能源/电力": "能源电力",
    "采矿业": "能源电力",
    "化工/材料": "化工材料",
    "电子/电气/通信": "信息技术",
    "汽车/新能源": "汽车",
    "交通运输、仓储和邮政业": "交通物流", "物流/仓储": "交通物流",
    "住宿和餐饮业": "住宿餐饮", "餐饮": "住宿餐饮", "酒店/旅游": "住宿餐饮",
    "批发和零售业": "批发零售",
    "居民服务、修理和其他服务业": "生活服务", "美容/美发": "生活服务",
    "文化、体育和娱乐业": "文化传媒", "广告/传媒": "文化传媒",
    "租赁和商务服务业": "商务服务", "财务/审计/税务": "商务服务",
    "人力资源": "商务服务", "行政/后勤": "商务服务", "法律": "商务服务",
    "翻译/语言": "商务服务", "外贸/采购": "商务服务", "销售/商务": "商务服务",
    "客服": "商务服务", "客服/运营": "商务服务", "运营": "商务服务",
    "产品/项目管理": "商务服务", "设计": "商务服务",
    "农、林、牧、渔业": "农林牧渔",
    "科学研究和技术服务业": "公共管理与科研",
    "水利、环境和公共设施管理业": "公共管理与科研",
    "公共管理、社会保障和社会组织": "公共管理与科研",
}

COLUMNS = [
    "sample_id", "dataset", "source_id", "title", "employer", "industry",
    "industry_group",
    "function", "region", "recruitment_type", "duties", "required_skills",
    "preferred_skills", "education_requirement", "graduation_requirement",
    "attendance_requirement", "salary_text", "job_status", "source_platform",
    "source_url", "discovery_url", "published_at", "end_date", "collected_at",
    "verification_status", "source_status", "evidence_excerpt", "raw_path",
    "notes",
]


def load(label, prefix, directory, filename):
    path = os.path.join(ROOT, directory, filename)
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    out = []
    for r in rows:
        rec = {c: (r.get(c) or "").strip() for c in COLUMNS}
        rec["sample_id"] = f"{prefix}-{rec['source_id']}"
        rec["dataset"] = label
        rec["industry_group"] = INDUSTRY_GROUP.get(rec["industry"], "")
        out.append(rec)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="references/岗位样本_总表_2026-11-02.csv")
    args = ap.parse_args()

    rows, per_dataset = [], {}
    for label, prefix, directory, filename in BATCHES:
        batch = load(label, prefix, directory, filename)
        per_dataset[label] = len(batch)
        rows.extend(batch)

    # QC: unique ids / urls, no empty title or employer
    ids = Counter(r["sample_id"] for r in rows)
    urls = Counter(r["source_url"] for r in rows if r["source_url"])
    dup_ids = [k for k, n in ids.items() if n > 1]
    dup_urls = [k for k, n in urls.items() if n > 1]
    unmapped = sorted({r["industry"] for r in rows if not r["industry_group"]})
    empty_title = [r["sample_id"] for r in rows if not r["title"]]
    empty_employer = [r["sample_id"] for r in rows if not r["employer"]]

    out_path = os.path.join(ROOT, args.out)
    with open(out_path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)

    print(f"wrote {len(rows)} rows -> {args.out}")
    for label, n in per_dataset.items():
        print(f"  {label}: {n}")
    print("  行业分类:", len({r["industry"] for r in rows}))
    print("  平台:", dict(Counter(r["source_platform"] for r in rows)))
    print("  核验状态:", dict(Counter(r["verification_status"] for r in rows)))
    print("  行业大类:", dict(Counter(r["industry_group"] for r in rows)))
    print(f"QC 重复 sample_id={len(dup_ids)} 重复 URL={len(dup_urls)} "
          f"空标题={len(empty_title)} 空公司={len(empty_employer)} "
          f"未映射行业={len(unmapped)}")
    if unmapped:
        print("  ! 未映射:", unmapped)
    for name, bad in (("sample_id", dup_ids), ("url", dup_urls),
                      ("title", empty_title), ("employer", empty_employer)):
        if bad:
            print(f"  ! {name}: {bad[:5]}")
    return 0 if not (dup_ids or dup_urls or empty_title or empty_employer or unmapped) else 1


if __name__ == "__main__":
    raise SystemExit(main())
