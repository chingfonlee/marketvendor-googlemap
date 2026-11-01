"""把 D1 裡的補交紀錄匯出成 CSV（docs/PLAN.md §5、任務 12）。

用法：
  python scripts/export_submissions.py            # 正式 D1，全部紀錄
  python scripts/export_submissions.py --pending  # 只匯出還沒人工處理的
  python scripts/export_submissions.py --local    # 本機 wrangler pages dev 用的 D1

輸出到 data/submissions-YYYYMMDD.csv（含 IP，data/*.csv 不進 git）。欄位和網頁模擬送出下載的 CSV 相同
（web/js/record.js 的 CSV_COLUMNS），UTF-8 加 BOM、CRLF，用 Excel 直接開不會亂碼。
要先登入 wrangler（npx wrangler login）。只讀資料庫，不改任何紀錄。
"""
import argparse
import csv
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = "googlemap-store"
COLUMNS = [
    "submitted_at", "ip", "county", "market_id", "market_name", "vendor_id", "vendor_name",
    "action", "url", "place_key", "status_before", "review_result", "reviewed_at", "note",
]


def query(sql, local):
    cmd = ["npx", "--yes", "wrangler", "d1", "execute", DB, "--local" if local else "--remote", "--json", "--command", sql]
    out = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", shell=sys.platform == "win32")
    if out.returncode != 0:
        sys.exit(f"wrangler 執行失敗：\n{out.stderr or out.stdout}")
    return json.loads(out.stdout)[0]["results"]


def write_csv(rows, path):
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, lineterminator="\r\n")
        w.writerow(COLUMNS)
        for r in rows:
            w.writerow([r.get(c) or "" for c in COLUMNS])


def main():
    ap = argparse.ArgumentParser(description="匯出補交紀錄")
    ap.add_argument("--local", action="store_true", help="讀本機 D1（wrangler pages dev）")
    ap.add_argument("--pending", action="store_true", help="只匯出 review_result 空白的紀錄")
    ap.add_argument("--out", type=Path, help="輸出檔案（預設 data/submissions-YYYYMMDD.csv）")
    args = ap.parse_args()

    where = " WHERE review_result = ''" if args.pending else ""
    rows = query(f"SELECT {', '.join(COLUMNS)} FROM submissions{where} ORDER BY id", args.local)
    out = args.out or ROOT / "data" / f"submissions-{datetime.now():%Y%m%d}.csv"
    write_csv(rows, out)
    print(f"{len(rows)} 筆 → {out}")


if __name__ == "__main__":
    main()
