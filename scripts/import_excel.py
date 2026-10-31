"""把「國際友善力_菜單審查總表_Google地圖.xlsx」匯入成網站讀的 JSON 和匯入報告（docs/PLAN.md §4，任務 6）。

用法：.venv/Scripts/python.exe scripts/import_excel.py [Excel 路徑]
只讀 Excel（先複製到暫存檔再讀，避開開檔鎖定），不輸出負責人、電話、地址、營業時間。
人工決定記在 data/review-decisions.csv；市場和攤商 ID 第一次產生後存進 data/id-map.json，之後不變。
Excel 改了店名或市場名稱時，用 same_as 讓新名稱沿用舊 ID（市場那一列 market_id 留空）。
同一份 Excel 跑兩次，輸出完全相同（不寫執行時間）。
"""
import csv
import hashlib
import json
import re
import shutil
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parent.parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "data" / "國際友善力_菜單審查總表_Google地圖.xlsx"
DECISIONS = ROOT / "data" / "review-decisions.csv"
ID_MAP = ROOT / "data" / "id-map.json"
LABELS = ROOT / "design" / "assets" / "final" / "map-taiwan-base.labels.json"
OUT = ROOT / "web" / "data"
REPORT = ROOT / "reports" / "import-report.md"

# Excel 的「地圖狀態」對應到網站的三種狀態（docs/PLAN.md §3）
EXCEL_STATUS = {"已完成": "verified", "待確認": "submitted", "未找到": "not_submitted"}
ORDER = ["verified", "submitted", "not_submitted"]
LABEL = {"verified": "已完成", "submitted": "待確認", "not_submitted": "未提交"}

# 市場類型決定縮圖，Excel 沒有這個欄位（docs/PLAN.md §4）
TYPES = {
    "night_market": ["m02", "m03", "m09", "m10", "m12", "m15"],
    "traditional_market": ["m01", "m04", "m06", "m07", "m08", "m13", "m14"],
    "other": ["m05", "m11"],
}
MARKET_TYPE = {m: t for t, ids in TYPES.items() for m in ids}
ACTIONS = {"exclude", "rename", "verify", "set_url", "share_place", "same_as"}
LOW_SIMILARITY = 80


def check_url(url):
    """離線檢查 Google 地圖網址，回傳（地點代碼, 問題）。地點代碼是 cid:… 或 place_id:…。"""
    u = urlsplit(url.strip())
    host, path = (u.hostname or "").lower(), u.path
    if u.scheme not in ("http", "https") or len(url) > 2048:
        return None, "不是有效的網址"
    if not (host == "maps.google.com" or host == "maps.app.goo.gl"
            or host in ("www.google.com", "google.com") and path.startswith("/maps")
            or host == "goo.gl" and path.startswith("/maps")):
        return None, "網域不是 Google 地圖"
    if host in ("maps.app.goo.gl", "goo.gl"):
        return None, "短網址，離線無法解析地點"
    q = parse_qs(u.query)
    if q.get("cid", [""])[0].isdigit():
        return f"cid:{q['cid'][0]}", None
    for k in ("place_id", "query_place_id"):
        if q.get(k):
            return f"place_id:{q[k][0]}", None
    # 長網址裡的 !1s0x…:0x…，後半段就是 cid
    m = re.search(r"!1s0x[0-9a-f]+:0x([0-9a-f]+)", url)
    if m:
        return f"cid:{int(m.group(1), 16)}", None
    return None, "網址裡找不到 cid 或 place_id"


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


warnings = []

# ---- 讀 Excel ----
with tempfile.TemporaryDirectory() as tmp:
    copy = Path(tmp) / "src.xlsx"
    shutil.copyfile(SRC, copy)
    source_sha = hashlib.sha256(copy.read_bytes()).hexdigest()
    wb = load_workbook(copy, data_only=True)
    modified = wb.properties.modified

    # 總表：序號 -> 縣市、市場名稱、總表攤數、退攤/換攤。序號只用來對分頁，市場 ID 另外固定（見下方）
    sheets = {}
    for no, county, name, count, left, *_ in wb.worksheets[0].iter_rows(min_row=2, values_only=True):
        if isinstance(no, int):
            sheets[no] = {"county": county, "name": str(name).strip(), "listed": count, "left": left}

    rows = []  # Excel 裡的每一列攤商（含沒有序號的）
    for ws in wb.worksheets[1:]:
        sheet_no = int(ws.title.split("-", 1)[0])
        if sheet_no not in sheets:
            sys.exit(f"分頁 {ws.title} 在總表找不到序號 {sheet_no}")
        head = {v: i for i, v in enumerate(next(ws.iter_rows(min_row=2, max_row=2, values_only=True))) if v}
        for row in ws.iter_rows(min_row=3, values_only=True):
            no, name = row[head["序號"]], row[head["市場/攤鋪名稱"]]
            if no == 0 or not name:
                continue  # 序號 0 是市場本身
            rows.append({
                "sheet_no": sheet_no, "no": no if isinstance(no, int) else None, "excel_name": str(name).strip(),
                "excel_status": row[head["地圖狀態"]], "url": row[head["Google 地圖連結"]],
                "place_id": row[head["Place ID"]], "google_name": row[head["Google 上的名稱"]],
                "similarity": row[head["相似度"]],
            })
    wb.close()

with open(DECISIONS, encoding="utf-8-sig", newline="") as f:
    decisions = sorted(csv.DictReader(f), key=lambda d: d["date"])  # 同一天照檔案順序
for d in decisions:
    if d["action"] not in ACTIONS:
        sys.exit(f"review-decisions.csv 有不認得的動作：{d['action']}")


def adopt(ids, new_name, old_id, current):
    """same_as：new_name 沿用 old_id，舊名稱從對照表拿掉。舊名稱如果還在名單上就停，不然它會被換成新 ID。"""
    old_names = [k for k, v in ids.items() if v == old_id and k != new_name]
    if old_id not in ids.values():
        sys.exit(f"same_as 找不到 ID {old_id}")
    if ids.get(new_name, old_id) != old_id:
        sys.exit(f"same_as：{new_name} 已經是 {ids[new_name]}，不能再沿用 {old_id}")
    if still := [k for k in old_names if k in current]:
        sys.exit(f"same_as：{old_id} 的舊名稱 {still} 還在名單上，不能讓 {new_name} 沿用")
    for k in old_names:
        del ids[k]
    ids[new_name] = old_id


# ---- 固定 ID：市場用總表名稱對應，攤商用「市場 + Excel 店名」對應，第一次產生後存檔，之後不變也不重複使用 ----
# ID 只是名字，程式不能從 ID 拆出市場，要看 market_id 欄位
id_map = json.loads(ID_MAP.read_text(encoding="utf-8")) if ID_MAP.exists() else {}
market_ids, vendor_ids = id_map.setdefault("markets", {}), id_map.setdefault("vendors", {})
new_markets, new_ids = [], []
for d in decisions:
    if d["action"] == "same_as" and not d["market_id"]:  # 市場改名
        adopt(market_ids, d["vendor"], d["value"], {s["name"] for s in sheets.values()})
for no, s in sorted(sheets.items()):
    if s["name"] not in market_ids:
        seq = max((int(v[1:]) for v in market_ids.values()), default=0) + 1
        market_ids[s["name"]] = f"m{seq:02d}"
        new_markets.append(market_ids[s["name"]])
    s["id"] = market_ids[s["name"]]
for r in rows:
    r["market_id"] = sheets[r["sheet_no"]]["id"]
summary = {s["id"]: s for s in sheets.values()}
if len(summary) != len(sheets):
    sys.exit("兩個市場拿到同一個 ID")
if missing := sorted(set(summary) - set(MARKET_TYPE)):
    names = "、".join(f"{m} {summary[m]['name']}" for m in missing)
    sys.exit(f"總表有新市場 {names}：如果是改名，請在 review-decisions.csv 加 same_as（market_id 留空，"
             "店名填新名稱，值填舊市場 ID）；真的是新市場，就先在 TYPES 指定類型")

# 同一個市場裡店名重複，人工決定和 ID 就對不上，直接停
dup = [k for k, n in Counter((r["market_id"], r["excel_name"]) for r in rows).items() if n > 1]
if dup:
    sys.exit(f"同一市場有重複店名：{dup}")

# ---- 人工決定 ----
by_key = {(r["market_id"], r["excel_name"]): r for r in rows}
excluded, shared, applied = {}, [], []
for d in decisions:
    key = (d["market_id"], d["vendor"])
    if d["action"] == "same_as" and not d["market_id"]:
        applied.append(d)
        continue
    r = by_key.get(key)
    if r is None:
        warnings.append(f"人工決定找不到攤商：{d['market_id']} {d['vendor']}（{d['action']}）")
        continue
    applied.append(d)
    if d["action"] == "exclude":
        excluded[key] = d["reason"]
    elif d["action"] == "rename":
        r["name"] = d["value"]
    elif d["action"] == "set_url":
        r["url"], r["verified"] = d["value"], False
    elif d["action"] == "verify":
        r["verified"] = True
    elif d["action"] == "share_place":
        if (d["market_id"], d["value"]) not in by_key:
            warnings.append(f"共用地點找不到另一家：{d['market_id']} {d['value']}")
        shared.append({key, (d["market_id"], d["value"])})
    elif d["action"] == "same_as":  # 攤商改名：新店名沿用舊 ID
        if not d["value"].startswith(f"{d['market_id']}-"):
            sys.exit(f"same_as：{d['value']} 不是 {d['market_id']} 的攤商 ID")
        current = {n for (m, n) in by_key if m == d["market_id"]}
        adopt(vendor_ids.setdefault(d["market_id"], {}), d["vendor"], d["value"], current)

for r in rows:
    key = (r["market_id"], r["excel_name"])
    if r["no"] is None and key not in excluded:
        excluded[key] = "沒有序號（未記在 review-decisions.csv）"
        warnings.append(f"{r['market_id']} {r['excel_name']} 沒有序號，已排除，但沒有記在 review-decisions.csv")
vendors_raw = [r for r in rows if (r["market_id"], r["excel_name"]) not in excluded]

# ---- 狀態與網址 ----
place_users = defaultdict(list)
for r in vendors_raw:
    r.setdefault("name", r["excel_name"])
    if r["excel_status"] not in EXCEL_STATUS:
        sys.exit(f"不認得的地圖狀態：{r['market_id']} {r['excel_name']} {r['excel_status']!r}")
    url, key = (r["url"] or "").strip() or None, None
    if url:
        key, problem = check_url(url)
        if problem and problem.startswith("短網址"):
            warnings.append(f"{r['market_id']} #{r['no']} {r['name']}：{problem}")
        elif problem:
            warnings.append(f"{r['market_id']} #{r['no']} {r['name']}：{problem}，當作未提交")
            url = None
        if key is None and url and r["place_id"]:
            key = f"place_id:{r['place_id']}"
    r["url"], r["place_key"] = url, key
    if key:
        place_users[key].append((r["market_id"], r["excel_name"]))

    verified = r.get("verified", r["excel_status"] == "已完成")
    if verified and not url:
        warnings.append(f"{r['market_id']} #{r['no']} {r['name']}：標成已完成但沒有連結，當作未提交")
        verified = False
    r["status"] = "verified" if verified else "submitted" if url else "not_submitted"
    if (r["excel_status"] == "未找到") != (url is None) and "verified" not in r:
        warnings.append(f"{r['market_id']} #{r['no']} {r['name']}：Excel 狀態「{r['excel_status']}」和連結有無不一致")

for key, users in sorted(place_users.items()):
    if len(users) > 1 and not any(set(users) <= s for s in shared):
        names = "、".join(f"{m} {n}" for m, n in users)
        warnings.append(f"不同攤商用同一個地點 {key}：{names}")

# ---- 攤商 ID ----
for r in vendors_raw:
    ids = vendor_ids.setdefault(r["market_id"], {})
    if r["excel_name"] not in ids:
        seq = max((int(v.rsplit("v", 1)[1]) for v in ids.values()), default=0) + 1
        ids[r["excel_name"]] = f"{r['market_id']}-v{seq:03d}"
        new_ids.append(ids[r["excel_name"]])
    r["id"] = ids[r["excel_name"]]

for name, mid in sorted(market_ids.items(), key=lambda kv: kv[1]):
    if mid not in summary:
        warnings.append(f"市場 ID {mid}（{name}）這次沒有用到：總表改名或刪除了嗎？如果是改名，請加 same_as")
in_use = {(r["market_id"], r["excel_name"]) for r in vendors_raw}
for mid, ids in sorted(vendor_ids.items()):
    unused = {vid: name for name, vid in ids.items() if (mid, name) not in in_use}
    for vid, name in sorted(unused.items()):
        warnings.append(f"ID {vid}（{name}）這次沒有用到：名單刪除或改名了嗎？ID 保留不重複使用。"
                        "如果是改名，請在 review-decisions.csv 加 same_as（店名填新名稱，值填這個 ID）")
    # 同一個市場同時有新 ID 和沒用到的舊 ID，很可能是 Excel 改了店名。
    # 只印在終端機：第二次跑時已經不算新 ID，寫進報告會讓兩次輸出不同
    born = [r for r in vendors_raw if r["id"] in new_ids and r["market_id"] == mid]
    if unused and born:
        new = "、".join(f"{r['id']} {r['excel_name']}" for r in born)
        old = "、".join(f"{v} {n}" for v, n in sorted(unused.items()))
        print(f"⚠️ {mid} 可能有改名：新的 {new}；沒用到的 {old}")
id_map = {
    "markets": dict(sorted(market_ids.items(), key=lambda kv: kv[1])),
    "vendors": {m: dict(sorted(ids.items(), key=lambda kv: kv[1])) for m, ids in sorted(vendor_ids.items())},
}

# ---- 輸出 ----
markets = []
for mid, info in sorted(summary.items()):
    vs = [r for r in vendors_raw if r["market_id"] == mid]
    counts = Counter(r["status"] for r in vs)
    markets.append({
        "id": mid, "name": info["name"], "county": info["county"], "type": MARKET_TYPE[mid],
        "vendor_count": len(vs), "counts": {s: counts[s] for s in ORDER},
    })
    if len(vs) != info["listed"]:
        warnings.append(f"{mid} {info['name']}：總表 {info['listed']} 攤，匯入 {len(vs)} 家")

total = Counter(r["status"] for r in vendors_raw)
vendors = [{"id": r["id"], "market_id": r["market_id"], "name": r["name"], "status": r["status"], "url": r["url"]}
           for r in sorted(vendors_raw, key=lambda r: r["id"])]
meta = {
    "updated": modified.strftime("%Y-%m-%dT%H:%M:%SZ") if modified else None,  # Excel 檔內記的最後修改時間
    "source": SRC.name,
    "source_sha256": source_sha,
    "decisions": len(applied),
    "total": len(vendors),
    "counts": {s: total[s] for s in ORDER},
    "markets": len(markets),
    "counties": len({m["county"] for m in markets}),
}

write_json(OUT / "markets.json", markets)
write_json(OUT / "vendors.json", vendors)
write_json(OUT / "meta.json", meta)
write_json(OUT / "county-labels.json", json.loads(LABELS.read_text(encoding="utf-8")))
write_json(ID_MAP, id_map)

# ---- 匯入報告 ----
n = len(vendors)
listed = sum(m["listed"] for m in summary.values())
lines = [
    "# 匯入報告",
    "",
    "- 由 `scripts/import_excel.py` 產生，請勿手改。同一份 Excel 重跑，內容完全相同。",
    f"- 資料來源：`data/{SRC.name}`（不進 git），SHA-256 `{source_sha[:12]}`，Excel 內記的修改時間 {meta['updated']}",
    f"- 套用人工決定 {len(applied)} 筆（`data/review-decisions.csv`）",
    f"- 輸出：`web/data/markets.json`、`vendors.json`、`meta.json`、`county-labels.json`；不含負責人、電話、地址、營業時間。",
    "",
    "## 1. 總數",
    "",
    "| 項目 | 家數 |",
    "|---|---:|",
    f"| 總表攤數合計 | {listed} |",
    f"| 匯入攤商 | {n} |",
] + [f"| {LABEL[s]}（`{s}`） | {total[s]} |" for s in ORDER] + [
    f"| 三種狀態加總 | {sum(total.values())} {'✅' if sum(total.values()) == n == listed else '⚠️'} |",
    f"| 排除 | {len(excluded)} |",
    "",
    f"完成率 {total['verified'] / n * 100:.1f}%（{total['verified']} / {n}）。",
    "",
    "## 2. 各市場",
    "",
    "| ID | 縣市 | 市場 | 類型 | 總表攤數 | 匯入 | 已完成 | 待確認 | 未提交 |",
    "|---|---|---|---|---:|---:|---:|---:|---:|",
]
for m in markets:
    c, info = m["counts"], summary[m["id"]]
    mark = "" if m["vendor_count"] == info["listed"] else " ⚠️"
    lines.append(f"| {m['id']} | {m['county']} | {m['name']} | {m['type']} | {info['listed']} | {m['vendor_count']}{mark} | "
                 + " | ".join(str(c[s]) for s in ORDER) + " |")
lines.append(f"| | | **合計** | | **{listed}** | **{n}** | " + " | ".join(f"**{total[s]}**" for s in ORDER) + " |")

lines += ["", "## 3. 排除", "", "| 市場 | 店名 | 原因 |", "|---|---|---|"]
lines += [f"| {mid} | {name} | {reason} |" for (mid, name), reason in sorted(excluded.items())]
left = [f"{mid} {s['name']} {s['left']}" for mid, s in sorted(summary.items()) if s["left"]]
lines += ["", f"總表「退攤/換攤」欄有填的市場：{'、'.join(left) or '無'}。"]

lines += ["", "## 4. 人工決定", "", "| 日期 | 動作 | 市場 | 店名 | 值 | 原因 |", "|---|---|---|---|---|---|"]
lines += [f"| {d['date']} | {d['action']} | {d['market_id']} | {d['vendor']} | {d['value']} | {d['reason']} |" for d in applied]

low = [r for r in vendors_raw if r["status"] == "submitted"
       and not (isinstance(r["similarity"], (int, float)) and r["similarity"] >= LOW_SIMILARITY)]
lines += ["", f"## 5. 名稱相似度低於 {LOW_SIMILARITY} 或空白的候選連結（{len(low)} 筆，確認時優先處理）", "",
          "| ID | 序號 | 名單名稱 | Google 上的名稱 | 相似度 |", "|---|---:|---|---|---:|"]
cell = lambda v: str(v or "").replace("|", "\\|")  # Google 上的名稱有的含 |，會切斷表格
lines += [f"| {r['id']} | {r['no']} | {cell(r['name'])} | {cell(r['google_name'])} | {r['similarity'] if r['similarity'] is not None else '空白'} |"
          for r in sorted(low, key=lambda r: r["id"])]

lines += ["", f"## 6. 警告（{len(warnings)} 筆）", ""]
lines += [f"- {w}" for w in warnings] or ["- 無"]
lines.append("")

# 新 ID 數只印在終端機：第二次跑會是 0，寫進報告就違反「跑兩次輸出相同」
REPORT.parent.mkdir(parents=True, exist_ok=True)
with open(REPORT, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(lines))

print(f"匯入 {n} 家（總表 {listed}）：" + "、".join(f"{LABEL[s]} {total[s]}" for s in ORDER)
      + f"；排除 {len(excluded)}；警告 {len(warnings)}；新 ID {len(new_ids)}")
