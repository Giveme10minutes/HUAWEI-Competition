#!/usr/bin/env python3
"""Collect a small, polite sample of BOSS Zhipin job postings via the user's
logged-in Chrome (raw CDP through scripts/cdp_daemon.py).

Why not the cloned pyppeteer project (/tmp/bosszhipin_spider)?
  - it launches its own Chrome with an empty profile, so BOSS sends it to the
    login page; the user is already logged in inside the running Chrome.
  - we only borrow its DOM knowledge (search page + job card layout) and drive
    the existing session instead. No verification code is bypassed.

Output: one JSON file with raw records + one raw HTML gzip per posting.
"""
import argparse
import gzip
import hashlib
import json
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cdp_lib import open_tab, close_tab, request, eval_js, text  # noqa: E402

LIST_JS = r"""
(() => {
  const cards = [...document.querySelectorAll('li.job-card-box')];
  return cards.map(li => {
    const a = li.querySelector('a.job-name');
    const sal = li.querySelector('.job-salary');
    return {
      title: a ? a.innerText.trim() : '',
      href: a ? a.getAttribute('href') : '',
      salary_card: sal ? sal.innerText.trim() : '',
      tags: [...li.querySelectorAll('.tag-list li')].map(x => x.innerText.trim()).filter(Boolean),
      company: (li.querySelector('.boss-name') || {}).innerText || '',
      location: (li.querySelector('.company-location') || {}).innerText || ''
    };
  }).filter(c => c.title && c.href);
})()
"""

DETAIL_JS = r"""
async (path) => {
  const res = await fetch(path, {credentials: 'include'});
  const html = await res.text();
  const doc = new DOMParser().parseFromString(html, 'text/html');
  const q = s => { const e = doc.querySelector(s); return e ? e.innerText.trim().replace(/\s+/g, ' ') : ''; };
  const qa = s => [...doc.querySelectorAll(s)].map(e => e.innerText.trim().replace(/\s+/g, ' ')).filter(Boolean);
  const banner = q('.job-banner');
  const nameRaw = q('.job-banner .name');
  const salary = q('.salary');
  let title = nameRaw;
  if (salary && nameRaw.endsWith(salary)) title = nameRaw.slice(0, -salary.length).trim();
  const meta = q('.job-banner .info-primary') || '';
  return {
    status_code: res.status,
    html_len: html.length,
    title: title,
    salary: salary,
    job_status: q('.job-status'),
    meta_text: meta,
    company_name: (q('.job-detail-company .company-name') || q('.sider-company .company-name')).replace(/^公司名称/, ''),
    company_tags: [q('.job-detail-company .company-user'),
                   q('.job-detail-company .company-type'),
                   q('.job-detail-company .company-fund')].filter(Boolean),
    jd: q('.job-sec-text'),
    address: q('.location-address'),
    boss: q('.job-boss-info'),
    banner_text: banner,
    page_title: doc.title
  };
}
"""


def fetch_detail(sid, path):
    r = request({
        "op": "call", "method": "Runtime.evaluate",
        "params": {"expression": f"({DETAIL_JS})({json.dumps(path)});",
                   "awaitPromise": True, "returnByValue": True},
        "sessionId": sid,
    })
    if r.get("ok") and r.get("result", {}).get("result", {}).get("value"):
        return r["result"]["result"]["value"]
    raise RuntimeError(f"detail eval failed: {json.dumps(r, ensure_ascii=False)[:300]}")


def fetch_detail_html(sid, path):
    expr = ("(async (p) => { const r = await fetch(p, {credentials:'include'});"
            " return await r.text(); })(" + json.dumps(path) + ")")
    r = request({
        "op": "call", "method": "Runtime.evaluate",
        "params": {"expression": expr, "awaitPromise": True, "returnByValue": True},
        "sessionId": sid,
    })
    try:
        return r["result"]["result"]["value"] or ""
    except Exception:
        return ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True, help="JSON plan file: [{keyword, industry, city, per_keyword}]")
    ap.add_argument("--out", required=True, help="output directory")
    ap.add_argument("--max-per-keyword", type=int, default=4)
    ap.add_argument("--pause", type=float, default=2.2)
    args = ap.parse_args()

    plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    outdir = Path(args.out)
    rawdir = outdir / "raw_detail_html"
    rawdir.mkdir(parents=True, exist_ok=True)

    records = []
    errors = []

    for step, item in enumerate(plan, 1):
        kw, city = item["keyword"], item["city"]
        industry = item.get("industry", "")
        print(f"[{step}/{len(plan)}] {kw} @ {city}", flush=True)
        url = f"https://www.zhipin.com/web/geek/jobs?query={kw}&city={city}"
        tid = sid = None
        try:
            tid, sid = open_tab(url, wait=6.0)
            for _ in range(6):
                if eval_js(sid, "document.querySelectorAll('li.job-card-box').length"):
                    break
                time.sleep(1.5)
            page_title = eval_js(sid, "document.title") or ""
            cards = eval_js(sid, LIST_JS) or []
            print(f"    list cards: {len(cards)}", flush=True)
            if not cards:
                body = (text(sid) or "")[:200].replace("\n", " | ")
                errors.append({"keyword": kw, "error": "no cards", "body": body})
                continue

            for card in cards[: args.max_per_keyword]:
                path = card["href"]
                if path.startswith("http"):
                    path = "/" + path.split("zhipin.com/", 1)[-1]
                detail = {}
                for attempt in range(3):
                    try:
                        detail = fetch_detail(sid, path)
                    except Exception as exc:  # noqa: BLE001
                        errors.append({"keyword": kw, "href": path, "error": str(exc)[:200]})
                        detail = {}
                    if detail.get("title") and "请稍候" not in (detail.get("page_title") or ""):
                        break
                    # BOSS answers throttled requests with a "请稍候" interstitial
                    time.sleep(10 + attempt * 8)
                if not detail.get("title"):
                    errors.append({"keyword": kw, "href": path, "error": "throttled_or_empty"})
                    continue
                html = fetch_detail_html(sid, path)
                digest = hashlib.sha1(path.encode()).hexdigest()[:16]
                raw_name = f"{kw}_{digest}.html.gz"
                if html:
                    with gzip.open(rawdir / raw_name, "wt", encoding="utf-8") as fh:
                        fh.write(html)
                rec = {
                    "keyword": kw,
                    "industry_label": industry,
                    "city_param": city,
                    "list_page_title": page_title,
                    "source_url": "https://www.zhipin.com" + path,
                    "list_title": card["title"],
                    "list_tags": card["tags"],
                    "list_company": card["company"],
                    "list_location": card["location"],
                    "salary_card": card["salary_card"],
                    "detail": detail,
                    "raw_html": f"raw_detail_html/{raw_name}" if html else "",
                    "collected_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                }
                records.append(rec)
                print(f"    - {detail.get('title','')[:24]} | {detail.get('salary','')} | "
                      f"{(detail.get('company_name') or '')[:18]}", flush=True)
                time.sleep(args.pause + random.uniform(-0.5, 0.9))
        except Exception as exc:  # noqa: BLE001
            errors.append({"keyword": kw, "error": f"{type(exc).__name__}: {exc}"[:300]})
            print(f"    ! {exc}", flush=True)
        finally:
            if tid:
                try:
                    close_tab(tid)
                except Exception:  # noqa: BLE001
                    pass
        payload_ck = {
            "collected_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "source": "https://www.zhipin.com (logged-in desktop search, job_detail pages)",
            "record_count": len(records),
            "errors": errors,
            "records": records,
        }
        (outdir / "boss_jobs_raw.json").write_text(
            json.dumps(payload_ck, ensure_ascii=False, indent=1), encoding="utf-8")
        time.sleep(3.0 + random.uniform(0, 2.0))

    payload = {
        "collected_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "source": "https://www.zhipin.com (logged-in desktop search, job_detail pages)",
        "record_count": len(records),
        "errors": errors,
        "records": records,
    }
    (outdir / "boss_jobs_raw.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"done: {len(records)} records, {len(errors)} errors -> {outdir/'boss_jobs_raw.json'}", flush=True)


if __name__ == "__main__":
    main()
