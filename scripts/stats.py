"""從「國際友善力_菜單審查總表_Google地圖.xlsx」算出完成度與縣市統計，寫成 docs/STATS.md。

用法：.venv/Scripts/python.exe scripts/stats.py
只讀 Excel（先複製到暫存檔再讀，避開開檔鎖定），不輸出負責人、電話、地址。
"""
import shutil
import tempfile
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "國際友善力_菜單審查總表_Google地圖.xlsx"
OUT = ROOT / "docs" / "STATS.md"

# Excel 的「地圖狀態」對應到網站的三種狀態（docs/PLAN.md §3）
STATUS = {"已完成": "已完成", "待確認": "待確認", "未找到": "未提交"}
ORDER = ["已完成", "待確認", "未提交"]

with tempfile.TemporaryDirectory() as tmp:
    copy = Path(tmp) / "src.xlsx"
    shutil.copyfile(SRC, copy)
    wb = load_workbook(copy, data_only=True)

    # 總表：序號 -> 縣市、市場名稱、總表攤數
    summary = {}
    for no, county, name, count, *_ in wb.worksheets[0].iter_rows(min_row=2, values_only=True):
        if isinstance(no, int):
            summary[no] = {"county": county, "name": name, "listed": count}

    markets = []
    for ws in wb.worksheets[1:]:
        info = summary[int(ws.title.split("-", 1)[0])]
        head = {v: i for i, v in enumerate(next(ws.iter_rows(min_row=2, max_row=2, values_only=True))) if v}
        counts = Counter()
        for row in ws.iter_rows(min_row=3, values_only=True):
            no, name = row[head["序號"]], row[head["市場/攤鋪名稱"]]
            if not isinstance(no, int) or no == 0 or not name:
                continue  # 序號 0 是市場本身；沒有序號的是退攤或放棄輔導
            counts[STATUS[row[head["地圖狀態"]]]] += 1
        markets.append({**info, "sheet": ws.title, "counts": counts, "total": sum(counts.values())})
    wb.close()

total = Counter()
by_county = defaultdict(lambda: {"markets": 0, "counts": Counter()})
for m in markets:
    total += m["counts"]
    c = by_county[m["county"]]
    c["markets"] += 1
    c["counts"] += m["counts"]
n = sum(total.values())
pct = lambda k, c=total: f"{c[k] / sum(c.values()) * 100:.1f}%" if sum(c.values()) else "-"

lines = [
    "# 攤商 Google 地圖登錄統計",
    "",
    f"- 產生時間：{datetime.now():%Y-%m-%d %H:%M}（由 `scripts/stats.py` 產生，請勿手改）",
    f"- 資料來源：`data/{SRC.name}`（不進 git）",
    "- 狀態定義見 [PLAN.md](PLAN.md) §3。完成率 = 已完成 ÷ 總數，有連結不等於完成。",
    "- 已排除：每張分頁的序號 0（市場本身）、退攤、放棄輔導。",
    "",
    "## 1. 整體完成度",
    "",
    "| 項目 | 家數 | 比例 | 說明 |",
    "|---|---:|---:|---|",
    f"| 攤商總數 | {n} | 100% | {len(markets)} 個市場、{len(by_county)} 個縣市 |",
    f"| 已完成 | {total['已完成']} | {pct('已完成')} | 連結已確認是這家店 |",
    f"| 待確認 | {total['待確認']} | {pct('待確認')} | 有連結，等確認是不是這家店 |",
    f"| 未提交 | {total['未提交']} | {pct('未提交')} | 沒有連結，要補連結 |",
    "",
    f"**完成率：{pct('已完成')}**（{total['已完成']} / {n}）；"
    f"有連結的比例：{(total['已完成'] + total['待確認']) / n * 100:.1f}%。",
    "",
    "## 2. 各縣市",
    "",
    "| 縣市 | 市集數 | 攤商數 | 已完成 | 待確認 | 未提交 | 完成率 |",
    "|---|---:|---:|---:|---:|---:|---:|",
]
for county, c in by_county.items():
    k = c["counts"]
    lines.append(f"| {county} | {c['markets']} | {sum(k.values())} | {k['已完成']} | {k['待確認']} | {k['未提交']} | {pct('已完成', k)} |")
lines.append(f"| **合計** | **{len(markets)}** | **{n}** | **{total['已完成']}** | **{total['待確認']}** | **{total['未提交']}** | **{pct('已完成')}** |")

lines += [
    "",
    "## 3. 各市集",
    "",
    "| 分頁 | 縣市 | 市集 | 總表攤數 | 分頁攤商數 | 已完成 | 待確認 | 未提交 |",
    "|---|---|---|---:|---:|---:|---:|---:|",
]
for m in markets:
    k = m["counts"]
    diff = "" if m["listed"] == m["total"] else " ⚠️"
    lines.append(f"| {m['sheet'][:2]} | {m['county']} | {m['name']} | {m['listed']} | {m['total']}{diff} | "
                 f"{k['已完成']} | {k['待確認']} | {k['未提交']} |")
listed = sum(m["listed"] for m in markets)
lines.append(f"| | | **合計** | **{listed}** | **{n}** | **{total['已完成']}** | **{total['待確認']}** | **{total['未提交']}** |")
lines += ["", "⚠️ 表示總表攤數和分頁實際攤商數不同。", ""]

OUT.write_text("\n".join(lines), encoding="utf-8", newline="\n")
print(f"寫入 {OUT}：總數 {n}，" + "、".join(f"{s} {total[s]}" for s in ORDER))
