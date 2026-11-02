#!/usr/bin/env python3
"""Map boss_jobs_raw.json into the project job sample CSV schema."""
import argparse
import csv
import json
from pathlib import Path

FIELDS = [
    "source_id", "title", "employer", "industry", "function", "region",
    "recruitment_type", "duties", "required_skills", "preferred_skills",
    "education_requirement", "graduation_requirement", "attendance_requirement",
    "source_url", "published_at", "collected_at", "verification_status",
    "evidence_excerpt", "salary_text", "job_status", "source_platform",
    "source_status", "raw_path", "notes",
]

EDU = ("学历不限", "初中及以下", "中专/中技", "高中", "大专", "本科", "硕士", "博士")
EXP = ("经验不限", "在校/应届", "1年以内", "1-3年", "3-5年", "5-10年", "10年以上")


def split_meta(meta, salary):
    """Pull (city, experience, education) out of the banner text."""
    text = meta
    if salary:
        text = text.replace(salary, " ")
    tokens = [t for t in text.split() if t]
    city = exp = edu = ""
    for t in tokens:
        if not exp and t in EXP and "招聘" not in t:
            exp = t
        elif not edu and t in EDU:
            edu = t
        elif not city and ("·" in t or t.endswith("市") or 2 <= len(t) <= 4) and t not in ("招聘中", "感兴趣", "立即沟通", "完善在线简历", "上传附件简历"):
            city = t
    return city, exp, edu


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    data = json.loads(Path(args.raw).read_text(encoding="utf-8"))
    rows = []
    ledger = []
    skipped = 0
    for rec in data["records"]:
        d = rec["detail"]
        if not (d.get("title") or "").strip():
            # BOSS answered with its "请稍候" throttle page: keep it out of the
            # sample table, it is still listed in the raw JSON.
            skipped += 1
            continue
        city, exp, edu = split_meta(d.get("meta_text", ""), d.get("salary", ""))
        if not exp:
            for t in rec.get("list_tags", []):
                if t in EXP:
                    exp = t
        if not edu:
            for t in rec.get("list_tags", []):
                if t in EDU:
                    edu = t
        jd = (d.get("jd") or "").strip()
        i = len(rows) + 1
        rows.append({
            "source_id": f"BOSS-{i:03d}",
            "title": d.get("title") or rec.get("list_title", ""),
            "employer": d.get("company_name") or rec.get("list_company", ""),
            "industry": rec.get("industry_label", ""),
            "function": rec.get("keyword", ""),
            "region": rec.get("list_location") or city,
            "recruitment_type": "全职",
            "duties": jd[:600],
            "required_skills": "",
            "preferred_skills": "",
            "education_requirement": edu,
            "graduation_requirement": "",
            "attendance_requirement": "",
            "source_url": rec.get("source_url", ""),
            "published_at": "",
            "collected_at": rec.get("collected_at", ""),
            "verification_status": "pending",
            "evidence_excerpt": jd[:300],
            "salary_text": d.get("salary", ""),
            "job_status": d.get("job_status", ""),
            "source_platform": "BOSS直聘",
            "source_status": "ok" if d.get("status_code") == 200 else f"http_{d.get('status_code')}",
            "raw_path": rec.get("raw_html", ""),
            "notes": " | ".join(filter(None, [
                f"experience={exp}" if exp else "",
                f"address={d.get('address','')}" if d.get("address") else "",
                # 招聘者姓名属于个人信息，不写入样本表；只保留岗位发布信息
                f"contact_role={(d.get('boss','').split('·')[-1].strip() if '·' in d.get('boss','') else '')}",
                " ".join(t for t in (d.get("company_tags") or []) if not t.startswith("法定代表人")),
            ])),
        })

        ledger.append({
            "source_id": f"BOSS-{i:03d}",
            "title": rows[-1]["title"],
            "employer": rows[-1]["employer"],
            "source_platform": "BOSS直聘",
            "source_url": rec.get("source_url", ""),
            "collected_at": rec.get("collected_at", ""),
            "http_status": d.get("status_code"),
            "detail_html_bytes": d.get("html_len"),
            "raw_path": rec.get("raw_html", ""),
            "verification_status": "pending",
        })

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    ledger_path = out.with_name("来源台账_BOSS直聘_2026-11-02.csv")
    with ledger_path.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(ledger[0].keys()) if ledger else ["source_id"])
        writer.writeheader()
        writer.writerows(ledger)
    print(f"wrote {len(rows)} rows -> {out} (skipped {skipped} throttled records)")
    print(f"wrote {len(ledger)} ledger rows -> {ledger_path}")


if __name__ == "__main__":
    main()
