"""產生統計報表頁的 SVG（PLAN §2.1、任務 15）。

設計基準是 design/reference/stats-mockup-v2.png（桌機）、stats-mockup-v2-mobile.png（手機）。
桌機用 1440x900、手機用 390 寬的頁面座標；組件檔只是用 viewBox 框出頁面上的一塊，位置和整頁一致。
數字不寫死：從 web/data/markets.json 算，規則照 design/asset-briefs/stats-page-assets.md §五，
所以這支程式同時也是網頁計算邏輯的樣本。
共用 build_svg.py 的繪圖函式。執行：python design/tools/build_stats_svg.py
"""
import json
import math

from build_svg import ICONS, C, card, circle, f, icon, image, line, rect, svg, text, tw, write, ROOT

DATA = ROOT.parent / "web" / "data"

# 統計頁只有三種狀態，顏色照 web/css/tokens.css（和 build_svg.py 的舊 6 狀態表不同）
STATUS = [
    ("verified", "已完成", "#22A06B", "#DDF5E8", "#12744A"),
    ("submitted", "待確認", "#F2B200", "#FFF3C4", "#8A6100"),
    ("not_submitted", "未提交", "#E5484D", "#FFE1E1", "#BF2B31"),
]
ST = {k: {"label": l, "main": m, "soft": s, "text": t} for k, l, m, s, t in STATUS}
KEYS = [k for k, *_ in STATUS]
TYPES = [  # 市場類型：key、顯示名稱、素材
    ("night_market", "夜市", "final/stats/stats-type-night_market.png"),
    ("traditional_market", "傳統市場", "final/stats/stats-type-traditional_market.png"),
    ("other", "美食廣場", "final/stats/stats-type-other.png"),
]
TYPE_NAME = {k: n for k, n, _ in TYPES}
TYPE_ICON = {k: p for k, _, p in TYPES}
TOP_N = 3  # 最強友善力市集列幾個（D5，設定值）
MIN_SEG = 2  # 家數 > 0 的段至少幾 px

ICONS.update({
    "pie": ["M12 3a9 9 0 1 0 9 9h-9z", "M15 3.5A9 9 0 0 1 20.5 9H15z"],
    "crown": ["M4 18h16", "M4 16 3 7l5 4 4-6 4 6 5-4-1 9z"],
})


# ---- 計算（和網頁要用的規則相同）----

def load():
    markets = json.loads((DATA / "markets.json").read_text(encoding="utf-8"))
    meta = json.loads((DATA / "meta.json").read_text(encoding="utf-8"))
    return markets, meta


def add(a, b):
    return {k: a.get(k, 0) + b.get(k, 0) for k in KEYS}


def total(c):
    return sum(c[k] for k in KEYS)


def done(c):
    """已提交 = 已完成 + 待確認（PLAN §3）。"""
    return c["verified"] + c["submitted"]


def ratio(c):
    return done(c) / total(c) if total(c) else 0


def group(markets, key):
    out = {}
    for m in markets:
        g = m[key]
        if key == "type" and g not in TYPE_NAME:  # 新類型歸到「其他」（§五.5）
            g = "other"
        out[g] = add(out.get(g, {}), m["counts"])
    return {k: v for k, v in out.items() if total(v)}


def county_rows(markets):
    """已提交比例高到低；同比例總數多的在前；再同照名稱。"""
    rows = sorted(group(markets, "county").items(), key=lambda kv: (-ratio(kv[1]), -total(kv[1]), kv[0]))
    top = ratio(rows[0][1]) if rows else 0
    return [(name, c, ratio(c) == top) for name, c in rows]


def top_rows(markets):
    """最強友善力市集：已提交比例最高的 TOP_N 個，不含 0%；同比例總數多的在前，再照 ID。"""
    rows = [m for m in markets if done(m["counts"])]
    rows.sort(key=lambda m: (-ratio(m["counts"]), -total(m["counts"]), m["id"]))
    return rows[:TOP_N]


def pct(c, digits=0):
    v = ratio(c) * 100
    return f"{v:.{digits}f}%"


# ---- 繪圖 ----

_clip = 0


def ratio_bar(x, y, w, h, c):
    """100% 堆疊長條：綠、黃、紅，寬度用原始比例，外側兩端圓角。"""
    global _clip
    _clip += 1
    cid = f"rb{_clip}"
    n = total(c)
    out = [f'<defs><clipPath id="{cid}">{rect(x, y, w, h, h / 2, "#000")}</clipPath></defs>',
           f'<g clip-path="url(#{cid})">', rect(x, y, w, h, 0, C["line_soft"])]
    widths = [(k, w * c[k] / n if n else 0) for k in KEYS]
    minw = max(MIN_SEG, h / 2 + 2)  # 兩端有圓角，太窄的段會被圓角切掉，至少要比半徑多 2px
    widths = [(k, max(v, minw) if c[k] else 0) for k, v in widths]
    over = sum(v for _, v in widths) - w  # 最小寬度補出來的部分，從最寬的那段扣回
    if n and over > 0:
        big = max(range(3), key=lambda i: widths[i][1])
        widths[big] = (widths[big][0], widths[big][1] - over)
    acc = x
    for k, v in widths:
        if v:
            out.append(rect(acc, y, v + 0.6, h, 0, ST[k]["main"]))  # +0.6 避免接縫露白
            acc += v
    out.append("</g>")
    return "".join(out)


def donut(cx, cy, r, sw, c):
    n = total(c)
    circ = 2 * math.pi * r
    out = [circle(cx, cy, r, stroke=C["line_soft"], sw=sw)]
    segs = [[k, max(circ * c[k] / n, MIN_SEG)] for k in KEYS if c[k]]
    over = sum(s for _, s in segs) - circ  # 最小長度補出來的部分，從最長的那段扣回
    if over > 0:
        max(segs, key=lambda s: s[1])[1] -= over
    acc = 0.0
    for k, seg in segs:
        out.append(circle(cx, cy, r, stroke=ST[k]["main"], sw=sw,
                          extra=f' stroke-dasharray="{f(seg)} {f(circ)}" stroke-dashoffset="{f(-acc)}" '
                                f'transform="rotate(-90 {f(cx)} {f(cy)})"'))
        acc += seg
    return "".join(out)


def card_title(x, y, ic, label, size=22):
    w = tw(label, size) + 64
    return (rect(x, y - size - 8, w, size + 22, (size + 22) / 2, "#EEF6FD") +
            icon(ic, x + 14, y - size + 1, size + 2, C["primary"], 2.4) +
            text(x + 48, y, label, size, C["ink"], 900))


def cloud(x, y, s=1.0, op=0.9):
    return (f'<g transform="translate({f(x)} {f(y)}) scale({f(s)})" fill="#fff" opacity="{op}">'
            '<circle cx="20" cy="22" r="14"/><circle cx="40" cy="14" r="16"/><circle cx="60" cy="22" r="13"/>'
            '<rect x="6" y="22" width="68" height="14" rx="7"/></g>')


def bushes(w, h, bw, bh):
    bl = image(0, h - bh, bw, bh, "final/stats/stats-corner-bush.png")
    br = (f'<g transform="translate({f(w)} 0) scale(-1 1)">'
          f'{image(0, h - bh, bw, bh, "final/stats/stats-corner-bush.png")}</g>')
    return bl + br


def legend_row(x, y, w, key, n, all_n, size=17, reviewing=False, show_pct=True):
    out = [circle(x + 12, y, 9, ST[key]["main"]),
           text(x + 32, y + 6, ST[key]["label"], size, C["body"], 700)]
    if reviewing:  # 已完成 = 0 時的提示（stats-page-assets §二 特殊狀態 1）
        lx = x + 36 + tw(ST[key]["label"], size)
        out += [rect(lx, y - 11, 52, 22, 11, ST[key]["soft"]),
                text(lx + 26, y + 5, "審核中", 12, ST[key]["text"], 700, "middle")]
    out.append(text(x + w - (50 if show_pct else 0), y + 6, f"{n}", size + 1, C["ink"], 900, "end"))
    if show_pct:  # 手機版寬度不夠，不顯示百分比，避免和「審核中」重疊
        out.append(text(x + w, y + 6, f"{n / all_n * 100:.0f}%" if all_n else "0%", 13, C["muted"], 500, "end"))
    return "".join(out)


# ---- 桌機（1440x900）----

DW, DH = 1440, 900
HEAD = 72
G = 16
CX = [24, 24 + (DW - 48 - G) / 2 + G]
CW = (DW - 48 - G) / 2
R1, R1H = 88, 380
R2, R2H = R1 + R1H + G, 330


def d_header(active="stats"):
    out = [rect(0, 0, DW, HEAD, 0, C["card"]), line(0, HEAD, DW, HEAD, "#C9E9F6", 2),
           image(24, 12, 48, 48, "logo-stall.png"),
           text(84, 36, "國際友善力提升輔導", 20, C["brand"], 900),
           text(84 + tw("國際友善力提升輔導", 20), 36, "・", 20, C["accent"], 900),
           text(84 + tw("國際友善力提升輔導・", 20), 36, "臺灣攤商地圖", 20, C["brand"], 900),
           text(84, 56, "夜市與市場 Google 地圖登錄成果平台", 12, C["body"])]
    x = 640
    for key, ic, label in [("map", "home", "地圖總覽"), ("stats", "chart", "統計報表")]:
        w = tw(label, 16) + 56
        on = key == active
        color = C["primary"] if on else C["ink"]
        if on:
            out.append(rect(x, 16, w, 40, 12, C["primary_soft"]))
        out += [icon(ic, x + 14, 26, 20, color), text(x + 42, 42, label, 16, color, 700)]
        x += w + 8
    bw = tw("我是攤商，確認或補交 Google 地圖連結", 15) + 56
    out += [rect(DW - 24 - bw, 14, bw, 44, 12, C["primary"]),
            icon("link", DW - 24 - bw + 16, 26, 20, "#fff"),
            text(DW - 24 - bw + 44, 41, "我是攤商，確認或補交 Google 地圖連結", 15, "#fff", 700)]
    return "".join(out)


def d_overview(c, updated):
    x, y, w, h = CX[0], R1, CW, R1H
    n = total(c)
    cx, cy = x + 170, y + 222
    out = [card(x, y, w, h),
           card_title(x + 24, y + 48, "chart", "全台登錄進度"),
           text(x + w - 24, y + 44, f"資料更新：{updated}", 13, C["muted"], 400, "end"),
           donut(cx, cy, 112, 40, c),
           text(cx, cy + 8, pct(c, 1), 44, C["ink"], 900, "middle"),
           text(cx, cy + 40, f"已提交 {done(c)}／{n} 家", 15, C["body"], 500, "middle"),
           image(x + 382, y + 72, 240, 177, "final/mascot-cat-map.png"),
           rect(x + 352, y + 256, w - 376, 104, 14, "#FAFBFC", "#E8EEF4")]
    for i, k in enumerate(KEYS):
        out.append(legend_row(x + 370, y + 280 + i * 30, w - 412, k, c[k], n, 16,
                              reviewing=(k == "verified" and c[k] == 0)))
    return "".join(out)


def d_county(rows):
    x, y, w, h = CX[1], R1, CW, R1H
    out = [card(x, y, w, h), card_title(x + 24, y + 48, "chart", "各縣市提交比例")]
    top = y + 92
    step = min(34, (h - 110) / max(len(rows), 1))
    bx, bw = x + 120, w - 210
    for i, (name, c, crown) in enumerate(rows):
        ry = top + i * step
        if crown:
            out.append(icon("crown", x + 20, ry - 11, 22, "#E6A400", 2.2))
        out += [text(x + 48, ry + 6, name, 16, C["ink"], 700),
                ratio_bar(bx, ry - 9, bw, 18, c),
                text(x + w - 24, ry + 7, pct(c), 18, C["ink"], 900, "end")]
    return "".join(out)


def d_types(groups):
    x, y, w, h = CX[0], R2, CW, R2H
    out = [card(x, y, w, h), card_title(x + 24, y + 48, "pie", "市場類型比較")]
    shown = [(k, n, p) for k, n, p in TYPES if k in groups]
    for i, (k, name, path) in enumerate(shown):
        cx = x + w * (2 * i + 1) / (2 * len(shown))
        c = groups[k]
        out += [image(cx - 40, y + 72, 80, 80, path),
                text(cx, y + 176, name, 17, C["ink"], 700, "middle"),
                donut(cx, y + 248, 50, 18, c),
                text(cx, y + 257, pct(c), 24, C["ink"], 900, "middle")]
    return "".join(out)


def top_row(x, y, w, m, size=16, iconsize=40, h=72):
    c = m["counts"]
    out = [rect(x, y, w, h, 14, "#fff", "#E3EAF2", 1.5),
           image(x + 12, y + (h - iconsize) / 2, iconsize, iconsize, TYPE_ICON.get(m["type"], TYPE_ICON["other"])),
           text(x + 24 + iconsize, y + h / 2 - 5, m["name"], size, C["ink"], 700)]
    fx = x + w - 16
    frac = f"{done(c)}/{total(c)}"
    bx = x + 24 + iconsize
    out += [ratio_bar(bx, y + h / 2 + 8, fx - tw(frac, size) - 16 - bx, 12, c),
            text(fx, y + h / 2 + 19, frac, size, C["ink"], 800, "end")]
    return "".join(out)


def d_top(rows):
    x, y, w, h = CX[1], R2, CW, R2H
    out = [card(x, y, w, h), card_title(x + 24, y + 48, "crown", "最強友善力市集")]
    if not rows:  # 沒有任何市場提交（stats-page-assets §五.5）
        out.append(text(x + 24, y + 140, "還沒有市場提交，一起加油！", 20, C["ink"], 900))
    for i, m in enumerate(rows):
        out.append(top_row(x + 24, y + 76 + i * 80, w - 250, m))
    out.append(image(x + w - 216, y + 110, 200, 159, "final/mascot-cat-megaphone.png"))
    return "".join(out)


def desktop(markets, meta):
    allc = {k: 0 for k in KEYS}
    for m in markets:
        allc = add(allc, m["counts"])
    upd = meta["updated"][:10]
    parts = {
        "overview": d_overview(allc, upd),
        "county": d_county(county_rows(markets)),
        "types": d_types(group(markets, "type")),
        "top": d_top(top_rows(markets)),
    }
    bg = (rect(0, 0, DW, DH, 0, C["page"]) + cloud(560, 6, 0.8) + cloud(1150, 30, 0.6) +
          bushes(DW, DH, 320, 240))
    return bg, parts


# ---- 手機（390 寬）----

MW = 390
MX, MCW = 16, 358


def m_header(active="stats"):
    out = [rect(0, 0, MW, 64, 0, C["card"]),
           image(12, 12, 40, 40, "logo-stall.png"),
           text(60, 29, "國際友善力提升輔導", 15, C["brand"], 900),
           text(60 + tw("國際友善力提升輔導", 15), 29, "・", 15, C["accent"], 900),
           text(60, 49, "臺灣攤商地圖", 15, C["brand"], 900),
           rect(MW - 12 - 84, 10, 84, 44, 12, C["primary"]),
           text(MW - 12 - 42, 37, "確認連結", 14, "#fff", 700, "middle"),
           # 精簡版分頁（D2）：頁首下方一排，兩格各半，每格高 44
           rect(0, 64, MW, 48, 0, C["card"]), line(0, 112, MW, 112, "#C9E9F6", 2)]
    for i, (key, ic, label) in enumerate([("map", "home", "地圖總覽"), ("stats", "chart", "統計報表")]):
        x = i * MW / 2
        on = key == active
        color = C["primary"] if on else C["body"]
        lw = tw(label, 15) + 28
        sx = x + (MW / 2 - lw) / 2
        out += [icon(ic, sx, 77, 20, color), text(sx + 28, 93, label, 15, color, 800 if on else 600)]
        if on:
            out.append(rect(x + 24, 106, MW / 2 - 48, 4, 2, C["primary"]))
    return "".join(out)


def m_overview(c, updated, y):
    h = 268
    n = total(c)
    cx, cy = MX + 96, y + 150
    out = [card(MX, y, MCW, h), card_title(MX + 16, y + 40, "chart", "全台登錄進度", 18),
           image(MX + MCW - 104, y + 8, 92, 68, "final/mascot-cat-map.png"),
           donut(cx, cy, 70, 26, c),
           text(cx, cy + 6, pct(c, 1), 28, C["ink"], 900, "middle"),
           text(cx, cy + 28, f"已提交 {done(c)}／{n}", 12, C["body"], 500, "middle")]
    for i, k in enumerate(KEYS):
        out.append(legend_row(MX + 186, y + 112 + i * 34, MCW - 198, k, c[k], n, 14,
                              reviewing=(k == "verified" and c[k] == 0), show_pct=False))
    out.append(text(MX + 16, y + h - 14, f"資料更新：{updated}", 12, C["muted"]))
    return "".join(out), h


def m_county(rows, y):
    step = 34
    h = 76 + step * len(rows)
    out = [card(MX, y, MCW, h), card_title(MX + 16, y + 40, "chart", "各縣市提交比例", 18)]
    for i, (name, c, crown) in enumerate(rows):
        ry = y + 84 + i * step
        if crown:
            out.append(icon("crown", MX + 6, ry - 9, 18, "#E6A400", 2.2))
        out += [text(MX + 28, ry + 5, name, 14, C["ink"], 700),
                ratio_bar(MX + 88, ry - 7, MCW - 150, 14, c),
                text(MX + MCW - 14, ry + 6, pct(c), 15, C["ink"], 900, "end")]
    return "".join(out), h


def m_types(groups, y):
    h = 236
    out = [card(MX, y, MCW, h), card_title(MX + 16, y + 40, "pie", "市場類型比較", 18)]
    shown = [(k, n, p) for k, n, p in TYPES if k in groups]
    for i, (k, name, path) in enumerate(shown):
        cx = MX + MCW * (2 * i + 1) / (2 * len(shown))
        c = groups[k]
        out += [image(cx - 28, y + 60, 56, 56, path),
                text(cx, y + 134, name, 14, C["ink"], 700, "middle"),
                donut(cx, y + 182, 34, 12, c),
                text(cx, y + 188, pct(c), 17, C["ink"], 900, "middle")]
    return "".join(out), h


def m_top(rows, y):
    h = 72 + 72 * max(len(rows), 1)
    out = [card(MX, y, MCW, h), card_title(MX + 16, y + 40, "crown", "最強友善力市集", 18),
           image(MX + MCW - 84, y + 4, 72, 57, "final/mascot-cat-megaphone.png")]
    if not rows:
        out.append(text(MX + 16, y + 110, "還沒有市場提交，一起加油！", 16, C["ink"], 900))
    for i, m in enumerate(rows):
        out.append(top_row(MX + 12, y + 64 + i * 72, MCW - 24, m, 15, 36, 64))
    return "".join(out), h


def mobile(markets, meta):
    allc = {k: 0 for k in KEYS}
    for m in markets:
        allc = add(allc, m["counts"])
    upd = meta["updated"][:10]
    y = 128
    parts = {}
    for key, fn in [("overview", lambda y: m_overview(allc, upd, y)),
                    ("county", lambda y: m_county(county_rows(markets), y)),
                    ("types", lambda y: m_types(group(markets, "type"), y)),
                    ("top", lambda y: m_top(top_rows(markets), y))]:
        body, h = fn(y)
        parts[key] = (body, y, h)
        y += h + 16
    mh = y + 24
    bg = rect(0, 0, MW, mh, 0, C["page"]) + bushes(MW, mh, 160, 120)
    return bg, parts, mh


# ---- 原子：特殊狀態示範 ----

def atoms():
    cases = [("0%（全部未提交）", {"verified": 0, "submitted": 0, "not_submitted": 20}),
             ("29%（桃園市）", {"verified": 0, "submitted": 12, "not_submitted": 29}),
             ("85%（高雄市）", {"verified": 0, "submitted": 34, "not_submitted": 6}),
             ("100%（沒有紅色）", {"verified": 0, "submitted": 21, "not_submitted": 0}),
             ("三段：已完成 20%、待確認 50%、未提交 30%", {"verified": 4, "submitted": 10, "not_submitted": 6}),
             ("很小的段：1／200 家已完成，至少畫到看得見", {"verified": 1, "submitted": 120, "not_submitted": 79})]
    body = [text(24, 36, "比例條 RatioBar（100% 堆疊，寬度用原始比例）", 18, C["ink"], 900)]
    for i, (label, c) in enumerate(cases):
        y = 70 + i * 44
        body += [text(24, y + 5, label, 14, C["body"], 500), ratio_bar(360, y - 8, 340, 18, c),
                 text(776, y + 6, pct(c), 16, C["ink"], 900, "end")]
    y0 = 360
    body.append(text(24, y0, "甜甜圈 Donut：已完成 = 0（顯示「審核中」）／已完成 > 0", 18, C["ink"], 900))
    for i, c in enumerate([{"verified": 0, "submitted": 217, "not_submitted": 130},
                           {"verified": 60, "submitted": 157, "not_submitted": 130}]):
        x = 24 + i * 400
        body += [donut(x + 80, y0 + 110, 60, 22, c), text(x + 80, y0 + 118, pct(c, 1), 22, C["ink"], 900, "middle")]
        for j, k in enumerate(KEYS):
            body.append(legend_row(x + 160, y0 + 72 + j * 32, 200, k, c[k], total(c), 14,
                                   reviewing=(k == "verified" and c[k] == 0)))
    y1 = 590
    body += [text(24, y1, "圖示", 18, C["ink"], 900),
             icon("crown", 24, y1 + 20, 32, "#E6A400", 2.2), text(70, y1 + 42, "crown（第一名）", 14, C["body"]),
             icon("pie", 230, y1 + 20, 32, C["primary"], 2.4), text(276, y1 + 42, "pie（市場類型）", 14, C["body"]),
             rect(430, y1 + 10, 120, 52, 8, C["page"]), cloud(450, y1 + 16, 1.0, 1),
             text(566, y1 + 42, "cloud（背景裝飾）", 14, C["body"])]
    y2 = 690
    body += [text(24, y2, "最強友善力市集：沒有任何市場提交時的空狀態", 18, C["ink"], 900),
             rect(24, y2 + 16, 520, 64, 14, "#fff", "#E3EAF2", 1.5),
             text(44, y2 + 55, "還沒有市場提交，一起加油！", 18, C["ink"], 900)]
    y3 = 800
    body += [text(24, y3, "地圖頁進度卡的入口連結（入口 B）", 18, C["ink"], 900),
             rect(24, y3 + 16, 300, 44, 12, C["primary_soft"]),
             text(44, y3 + 44, "看完整統計", 15, C["primary"], 800),
             icon("chevron-right", 44 + tw("看完整統計", 15) + 6, y3 + 28, 20, C["primary"], 2.4),
             text(340, y3 + 44, "放在進度卡底部，整列可點，高 44", 13, C["muted"])]
    write("atoms/stats-atoms.svg", svg((0, 0, 800, 870), "".join(body), "統計頁原子元件與特殊狀態", "#fff"))


def main():
    markets, meta = load()
    bg, parts = desktop(markets, meta)
    head = d_header()
    write("pages/stats-desktop.svg", svg((0, 0, DW, DH), bg + head + "".join(parts.values()), "統計報表・桌機 1440x900"))
    boxes = {"overview": (CX[0], R1, CW, R1H), "county": (CX[1], R1, CW, R1H),
             "types": (CX[0], R2, CW, R2H), "top": (CX[1], R2, CW, R2H)}
    names = {"overview": "全台登錄進度 StatsOverviewCard", "county": "各縣市提交比例 CountyRatioCard",
             "types": "市場類型比較 MarketTypeCard", "top": "最強友善力市集 TopMarketsCard"}
    for k, (x, y, w, h) in boxes.items():
        write(f"components/stats-{k}-card.svg", svg((x - 12, y - 10, w + 24, h + 30), parts[k], names[k], C["page"]))
    write("components/stats-header.svg", svg((0, 0, DW, HEAD + 2), head, "頁首（統計報表分頁選中）"))

    mbg, mparts, mh = mobile(markets, meta)
    mhead = m_header()
    write("pages/stats-mobile.svg", svg((0, 0, MW, mh), mbg + mhead + "".join(b for b, _, _ in mparts.values()),
                                        f"統計報表・手機 390x{f(mh)}"))
    write("components/stats-header-mobile.svg", svg((0, 0, MW, 114), mhead, "手機頁首＋精簡版分頁"))
    atoms()
    print("ok", ", ".join(f"{k}" for k in boxes), f"mobile height {f(mh)}")


if __name__ == "__main__":
    main()
