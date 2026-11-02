#!/usr/bin/env python3
"""Re-fetch records whose detail came back as BOSS's "请稍候" interstitial."""
import argparse
import gzip
import hashlib
import json
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cdp_lib import open_tab, close_tab, eval_js  # noqa: E402
from boss_collect import fetch_detail, fetch_detail_html  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    ap.add_argument("--pause", type=float, default=14.0)
    args = ap.parse_args()

    raw_path = Path(args.raw)
    data = json.loads(raw_path.read_text(encoding="utf-8"))
    missing = [r for r in data["records"] if not r["detail"].get("title")]
    print(f"{len(missing)} records to re-fetch")
    if not missing:
        return

    tid, sid = open_tab(missing[0]["source_url"], wait=6.0)
    fixed = 0
    try:
        for rec in missing:
            url = rec["source_url"]
            path = "/" + url.split("zhipin.com/", 1)[-1]
            detail = {}
            for attempt in range(4):
                try:
                    detail = fetch_detail(sid, path)
                except Exception as exc:  # noqa: BLE001
                    print(f"  err {type(exc).__name__} {str(exc)[:80]}")
                    detail = {}
                if detail.get("title") and "请稍候" not in (detail.get("page_title") or ""):
                    break
                time.sleep(args.pause + attempt * 6)
            if not detail.get("title"):
                print(f"  !! still throttled: {rec['list_title']}")
                continue
            html = fetch_detail_html(sid, path)
            digest = hashlib.sha1(path.encode()).hexdigest()[:16]
            raw_name = f"{rec['keyword']}_{digest}.html.gz"
            if html:
                with gzip.open(raw_path.parent / "raw_detail_html" / raw_name, "wt", encoding="utf-8") as fh:
                    fh.write(html)
                rec["raw_html"] = f"raw_detail_html/{raw_name}"
            rec["detail"] = detail
            fixed += 1
            print(f"  ok {detail.get('title','')[:20]} | {detail.get('salary','')} | {detail.get('company_name','')[:16]}")
            time.sleep(args.pause + random.uniform(0, 6))
    finally:
        try:
            close_tab(tid)
        except Exception:  # noqa: BLE001
            pass

    data["record_count"] = len(data["records"])
    raw_path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"fixed {fixed}/{len(missing)} -> {raw_path}")


if __name__ == "__main__":
    main()
