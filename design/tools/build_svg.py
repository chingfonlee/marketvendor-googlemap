"""產生 design/svg 底下所有 SVG。

所有組件都用設計圖（1536x1024）的頁面座標繪製；組件檔只是用 viewBox 框出頁面上的一塊區域，
所以組件檔和整頁 SVG 的位置、尺寸完全一致。手機版另有一套 390 寬的座標。
執行：python design/tools/build_svg.py
"""
import math
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "svg"
ASSET = "../../assets/"  # 所有 SVG 都在 design/svg/<分類>/ 底下
FONT = "'Noto Sans TC','PingFang TC','Microsoft JhengHei',sans-serif"

C = {
    "ink": "#2B2118",
    "brand": "#3B2A1A",
    "body": "#4B5563",
    "muted": "#6B7280",
    "placeholder": "#9CA3AF",
    "line": "#E5E7EB",
    "line_soft": "#F0F1F3",
    "field": "#F3F4F6",
    "card": "#FFFFFF",
    "page": "#D6F3FD",
    "sea": "#6DD7F2",
    "primary": "#1F6FE5",
    "primary_soft": "#E4EFFF",
    "accent": "#F08A3C",
}

# 狀態：key、顯示名稱、主色（圖釘/圓點）、淺底、文字色
STATUSES = [
    ("verified", "已完成", "#22A06B", "#DDF5E8", "#12744A"),
    ("submitted", "已提交", "#3B82F6", "#DDEBFF", "#1D5FD1"),
    ("candidate", "待確認", "#F2B200", "#FFF3C4", "#8A6100"),
    ("incomplete", "缺項", "#F97316", "#FFE8D6", "#B5490A"),
    ("not_found", "未找到", "#E5484D", "#FFE1E1", "#BF2B31"),
    ("not_submitted", "尚未提交", "#9CA3AF", "#EEF0F3", "#545C6A"),
]
S = {k: {"label": l, "main": m, "soft": s, "text": t} for k, l, m, s, t in STATUSES}
# 聯繫狀態（管理版）：與地圖狀態是兩個獨立欄位，顏色刻意避開地圖狀態色
CONTACT_STATUSES = [
    ("not_contacted", "未聯繫", "#94A3B8", "#EEF1F5", "#4B5567"),
    ("contacted", "已聯繫", "#0D9488", "#D5F5F0", "#0F766E"),
    ("tracking", "追蹤中", "#8B5CF6", "#EDE7FF", "#6D3FD6"),
    ("reminded", "已催繳", "#DB2777", "#FCE4F1", "#A3175A"),
]
SC = {k: {"label": l, "main": m, "soft": s, "text": t} for k, l, m, s, t in CONTACT_STATUSES}
ALL = {**S, **SC}

# ---- 範例資料（只用於設計稿） ----
COUNTS = {"verified": 210, "submitted": 12, "candidate": 32, "incomplete": 13, "not_found": 18, "not_submitted": 15}
TOTAL = sum(COUNTS.values())
UPDATED = "2026/10/31 10:30"
ROWS = [
    ("香香超大烤雞排", "花園夜市", "台南市", "verified"),
    ("阿明地瓜球", "花園夜市", "台南市", "submitted"),
    ("幸福滷味", "逢甲夜市", "台中市", "candidate"),
    ("大腸包小腸", "逢甲夜市", "台中市", "not_found"),
    ("QQ章魚燒", "瑞豐夜市", "高雄市", "incomplete"),
    ("古早味杏仁茶", "寧夏夜市", "台北市", "submitted"),
    ("胖胖雞蛋糕", "士林夜市", "台北市", "candidate"),
    ("阿婆蚵仔煎", "士林夜市", "台北市", "not_submitted"),
]
DETAIL = {
    "verified": {
        "name": "香香超大烤雞排", "market": "花園夜市", "city": "台南市", "status": "verified",
        "place_id": "ChIJxxxxxxxxxxxx", "checked": "2026/10/31 08:12",
        "title": "符合所有檢查項目", "sub": "店名、位置、基本資訊皆正確！",
    },
    "incomplete": {
        "name": "QQ章魚燒", "market": "瑞豐夜市", "city": "高雄市", "status": "incomplete",
        "place_id": "ChIJyyyyyyyyyyyy", "checked": "2026/10/31 08:15",
        "title": "還差 2 項就完成", "sub": "缺：營業時間、店家照片",
    },
}
# 地圖圖釘：頁面座標（圖釘圓頭中心）、狀態。位置對齊底圖上原本的圖釘
PINS = [
    (1005, 172, "candidate"), (1108, 163, "not_submitted"), (903, 230, "verified"),
    (1025, 228, "verified"), (908, 272, "submitted"), (973, 312, "not_submitted"),
    (888, 335, "verified"), (893, 402, "not_found"), (1058, 388, "incomplete"),
    (697, 491, "not_submitted"), (737, 532, "candidate"), (880, 526, "verified"),
    (680, 592, "verified"), (763, 590, "not_found"), (870, 600, "submitted"),
    (617, 655, "candidate"), (787, 648, "verified"), (644, 710, "not_submitted"),
    (592, 733, "not_found"), (627, 838, "verified"), (705, 908, "incomplete"),
]
SELECTED_PIN = (787, 648)

# ---- 基本繪圖 ----

def f(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def tw(s, size):
    """估算文字寬度：中日韓字元一個字寬，其餘約 0.56 字寬。"""
    return sum(size if ord(ch) > 0x2E80 else size * 0.56 for ch in s)


def text(x, y, s, size=14, fill=None, weight=400, anchor="start", extra=""):
    return (f'<text x="{f(x)}" y="{f(y)}" font-size="{f(size)}" font-weight="{weight}" '
            f'fill="{fill or C["ink"]}" text-anchor="{anchor}"{extra}>{escape(s)}</text>')


def rect(x, y, w, h, r=0, fill="none", stroke=None, sw=1, extra=""):
    st = f' stroke="{stroke}" stroke-width="{f(sw)}"' if stroke else ""
    return f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="{f(r)}" fill="{fill}"{st}{extra}/>'


def circle(cx, cy, r, fill="none", stroke=None, sw=1, extra=""):
    st = f' stroke="{stroke}" stroke-width="{f(sw)}"' if stroke else ""
    return f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}" fill="{fill}"{st}{extra}/>'


def line(x1, y1, x2, y2, stroke, sw=1):
    return f'<line x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}" stroke="{stroke}" stroke-width="{f(sw)}"/>'


_clip_n = 0


def image(x, y, w, h, name, r=0):
    """插畫素材；r>0 時裁成圓角。"""
    global _clip_n
    tag = (f'<image href="{ASSET}{name}" x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" '
           f'preserveAspectRatio="xMidYMid slice"')
    if not r:
        return tag + "/>"
    _clip_n += 1
    cid = f"clip{_clip_n}"
    return (f'<defs><clipPath id="{cid}">{rect(x, y, w, h, r, "#000")}</clipPath></defs>'
            f'{tag} clip-path="url(#{cid})"/>')


def card(x, y, w, h, r=18, fill=None):
    return rect(x, y, w, h, r, fill or C["card"], extra=' filter="url(#shadow)"')


# 24x24 線條圖示。"c:" 圓、"r:" 圓角矩形，其餘為 path
ICONS = {
    "home": ["M3 11 12 3l9 8", "M5 9.5V21h5v-6h4v6h5V9.5"],
    "users": ["c:9,8,3.5", "M2.5 20c0-3.6 2.9-6 6.5-6s6.5 2.4 6.5 6", "M16 4.5a3.5 3.5 0 0 1 0 7",
              "M18 14.2c2.1.6 3.5 2.6 3.5 5.8"],
    "chart": ["M4 20h16", "M7 20v-6", "M12 20V8", "M17 20V10"],
    "link": ["M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1.2 1.2",
             "M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1.2-1.2"],
    "user": ["c:12,8,4", "M4 21c0-4.4 3.6-7 8-7s8 2.6 8 7"],
    "search": ["c:11,11,6.5", "M16 16l5 5"],
    "pin": ["M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21z", "c:12,9.5,2.5"],
    "chevron-down": ["M6 9l6 6 6-6"],
    "chevron-left": ["M15 6l-6 6 6 6"],
    "chevron-right": ["M9 6l6 6-6 6"],
    "store": ["M4 9l1.5-5h13L20 9", "M4 9h16",
              "M4 9c0 1.7 1.3 3 3 3s2.7-1.3 2.7-3c0 1.7 1.3 3 2.7 3s2.6-1.3 2.6-3c0 1.7 1.2 3 2.8 3S20 10.7 20 9",
              "M5 12v8h14v-8"],
    "market": ["M3 10l2-6h14l2 6", "M3 10h18", "M5 10v10h14V10", "M9 20v-5h6v5"],
    "external": ["M14 4h6v6", "M20 4l-9 9", "M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5"],
    "copy": ["r:8,8,12,12,2", "M16 8V5a1 1 0 0 0-1-1H5a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h3"],
    "clock": ["c:12,12,9", "M12 7v5l3 2"],
    "target": ["c:12,12,8", "c:12,12,3"],
    "check": ["M5 12.5l4.5 4.5L19 7.5"],
    "x": ["M6 6l12 12", "M18 6L6 18"],
    "plus": ["M12 5v14", "M5 12h14"],
    "minus": ["M5 12h14"],
    "menu": ["M4 7h16", "M4 12h16", "M4 17h16"],
    "alert": ["M12 6v8", "M12 18h.01"],
    "edit": ["M4 20h4L19 9l-4-4L4 16z", "M13 7l4 4"],
    "note": ["r:5,3,14,18,2", "M9 8h6", "M9 12h6", "M9 16h4"],
    "phone": ["M6.5 3.5c.8-.8 2.1-.7 2.7.3l1.8 3c.4.7.3 1.6-.3 2.1l-1.2 1.2c1.1 2.2 2.8 3.9 5 5l1.2-1.2c.5-.6 1.4-.7 2.1-.3l3 1.8c1 .6 1.1 1.9.3 2.7l-1.4 1.4c-1.2 1.2-3 1.4-4.5.7-4.5-2.3-8.1-5.9-10.4-10.4-.7-1.5-.5-3.3.7-4.5z"],
}


def icon(name, x, y, size=24, color=None, sw=2):
    parts = []
    for p in ICONS[name]:
        if p.startswith("c:"):
            cx, cy, r = p[2:].split(",")
            parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}"/>')
        elif p.startswith("r:"):
            x0, y0, w, h, r = p[2:].split(",")
            parts.append(f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="{r}"/>')
        else:
            parts.append(f'<path d="{p}"/>')
    return (f'<g transform="translate({f(x)} {f(y)}) scale({f(size / 24)})" fill="none" '
            f'stroke="{color or C["ink"]}" stroke-width="{f(sw)}" stroke-linecap="round" '
            f'stroke-linejoin="round">{"".join(parts)}</g>')


# ---- 原子元件 ----

def badge(status, x, y, w=None, h=26, size=13, with_icon=False, label=None):
    st = dict(ALL[status], label=label or ALL[status]["label"])
    w = w or tw(st["label"], size) + 24 + (16 if with_icon else 0)
    out = [rect(x, y, w, h, h / 2, st["soft"])]
    if with_icon:
        cx = x + 18
        out.append(circle(cx, y + h / 2, 9, st["main"]))
        out.append(status_glyph(status, cx, y + h / 2, 0.62))
        out.append(text(cx + 14, y + h / 2 + size * 0.36, st["label"], size, st["text"], 700))
    else:
        out.append(text(x + w / 2, y + h / 2 + size * 0.36, st["label"], size, st["text"], 700, "middle"))
    return "".join(out)


PHONE = ("M-5.5-6.2c.6-.6 1.6-.5 2 .2l1.4 2.3c.3.5.2 1.2-.2 1.6l-.9.9c.8 1.7 2.1 3 3.8 3.8l.9-.9"
         "c.4-.4 1.1-.5 1.6-.2l2.3 1.4c.7.4.8 1.4.2 2l-1.1 1.1c-.9.9-2.3 1.1-3.4.5-3.4-1.8-6.2-4.6-8-8"
         "-.6-1.1-.4-2.5.5-3.4z")


def status_glyph(status, cx, cy, s=1.0):
    """圖釘與徽章中間的白色符號，以 (cx, cy) 為中心。"""
    g = f'<g transform="translate({f(cx)} {f(cy)}) scale({f(s)})" stroke="#fff" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" fill="none">'
    body = {
        "verified": '<path d="M-5 0.5l3.5 3.5L5.5-4"/>',
        "submitted": '<path d="M0 5V-5M-4.5-0.8L0-5.3 4.5-0.8"/>',
        "candidate": '<path d="M-3.2-2.6a3.3 3.3 0 1 1 4.6 3c-1 .5-1.4 1.1-1.4 2.2"/><circle cx="0" cy="6" r="0.4"/>',
        "incomplete": '<path d="M0-5.5v6.5"/><circle cx="0" cy="5.5" r="0.4"/>',
        "not_found": '<path d="M-4-4l8 8M4-4l-8 8"/>',
        "not_submitted": '<circle cx="0" cy="0" r="3.6" fill="#fff" stroke="none"/>',
        "contacted": f'<path d="{PHONE}" fill="#fff" stroke="none"/>',
        "not_contacted": f'<path d="{PHONE}" stroke-width="1.8"/>',
        "tracking": '<circle cx="0" cy="0" r="5.6"/><path d="M0-3v3l2.2 1.6" stroke-width="2"/>',
        "reminded": '<path d="M-4.8 3h9.6M-3.6 3V-.4a3.6 3.6 0 0 1 7.2 0V3M-1.3 5.6h2.6" stroke-width="2.2"/>',
    }[status]
    return g + body + "</g>"


def map_pin(status, x, y, scale=1.0, selected=False):
    """(x, y) 是圖釘圓頭的中心，尖端在下方 22px。"""
    main = ALL[status]["main"]
    out = [f'<g transform="translate({f(x)} {f(y)}) scale({f(scale)})">']
    if selected:
        out.append(circle(0, 0, 30, main, extra=' opacity="0.14"'))
        out.append(circle(0, 0, 21, main, extra=' opacity="0.28"'))
    out.append('<ellipse cx="0" cy="23" rx="6" ry="2.2" fill="#000" opacity="0.18"/>')
    out.append(f'<path d="M0 22C-4 15-13 9.5-13 0a13 13 0 0 1 26 0c0 9.5-9 15-13 22z" fill="{main}" stroke="#fff" stroke-width="2.5"/>')
    out.append(status_glyph(status, 0, 0))
    out.append("</g>")
    return "".join(out)


def chip(label, x, y, active=False, status=None, h=32, size=14):
    w = tw(label, size) + 28 + (14 if status else 0)
    fill = C["primary"] if active else C["card"]
    stroke = None if active else C["line"]
    color = "#fff" if active else C["body"]
    out = [rect(x, y, w, h, 10, fill, stroke)]
    tx = x + 14
    if status:
        out.append(circle(x + 17, y + h / 2, 5, S[status]["main"]))
        tx += 14
    out.append(text(tx, y + h / 2 + size * 0.36, label, size, color, 700 if active else 500))
    return "".join(out), w


def donut(cx, cy, r, sw, counts, gap=2.0):
    total = sum(counts.values())
    circ = 2 * math.pi * r
    out, acc = [], 0.0
    for key, n in counts.items():
        seg = circ * n / total
        out.append(circle(cx, cy, r, stroke=S[key]["main"], sw=sw,
                          extra=f' stroke-dasharray="{f(max(seg - gap, 0.5))} {f(circ)}" '
                                f'stroke-dashoffset="{f(-acc)}" transform="rotate(-90 {f(cx)} {f(cy)})"'))
        acc += seg
    return "".join(out)


# ---- 桌機版組件（頁面座標）----

def header():
    out = [rect(0, 0, 1536, 92, 0, C["card"]), line(0, 92, 1536, 92, "#C9E9F6", 2),
           image(16, 8, 86, 78, "logo-stall.png"),
           text(116, 54, "台灣攤商地圖", 40, C["brand"], 900, extra=' letter-spacing="2"'),
           text(118, 80, "一起讓更多好味道被看見！", 15, "#5B4636", 700, extra=' letter-spacing="4"')]
    for ic, label, x, w, active in [("home", "地圖總覽", 437, 163, True),
                                    ("users", "攤商列表", 612, 160, False),
                                    ("chart", "統計報表", 775, 160, False)]:
        color = C["primary"] if active else C["ink"]
        if active:
            out.append(rect(x, 18, w, 55, 14, C["primary_soft"]))
        out.append(icon(ic, x + 24, 33, 24, color))
        out.append(text(x + 60, 53, label, 19, color, 700))
    out.append(rect(1000, 17, 341, 57, 14, C["primary"]))
    out.append(icon("link", 1018, 33, 24, "#fff"))
    out.append(text(1053, 53, "我是攤商，補上我的Google地圖連結", 17, "#fff", 700))
    out.append(rect(1354, 17, 163, 57, 14, C["card"], "#CBD5E1", 1.5))
    out.append(icon("user", 1376, 33, 24, C["ink"]))
    out.append(text(1410, 53, "管理者登入", 17, C["ink"], 700))
    return "".join(out)


def progress_card():
    out = [card(12, 105, 431, 272),
           text(34, 142, "整體進度", 22, C["ink"], 900),
           text(34, 166, f"最後更新：{UPDATED}", 13, C["muted"]),
           image(256, 110, 170, 110, "mascot-chef.png"),
           donut(113, 282, 65, 30, COUNTS),
           text(113, 288, str(TOTAL), 28, C["ink"], 900, "middle"),
           text(113, 308, "家攤商", 13, C["muted"], 500, "middle"),
           rect(205, 218, 220, 150, 12, "#F9FAFB", "#EEF0F3")]
    for i, (key, n) in enumerate(COUNTS.items()):
        y = 239 + i * 23
        out.append(circle(224, y - 5, 6, S[key]["main"]))
        out.append(text(240, y, S[key]["label"], 14, C["body"], 500))
        out.append(text(345, y, str(n), 14, C["ink"], 700, "end"))
        out.append(text(355, y, f"({round(n * 100 / TOTAL)}%)", 13, C["muted"]))
    return "".join(out)


def filter_panel():
    out = [rect(30, 400, 395, 43, 10, C["card"], "#D1D5DB"),
           icon("search", 44, 410, 22, C["muted"]),
           text(76, 428, "搜尋攤商名稱或夜市...", 15, C["placeholder"])]
    rows = [[("全部狀態", None, True), ("verified",), ("submitted",), ("candidate",)],
            [("incomplete",), ("not_found",), ("not_submitted",)]]
    for r, items in enumerate(rows):
        x = 30
        for it in items:
            if len(it) == 1:
                svg, w = chip(S[it[0]]["label"], x, 456 + r * 38, status=it[0])
            else:
                svg, w = chip(it[0], x, 456 + r * 38, active=it[2])
            out.append(svg)
            x += w + 8
    out += [rect(30, 534, 395, 40, 10, C["card"], "#D1D5DB"),
            icon("pin", 44, 544, 20, C["ink"]),
            text(72, 560, "所有縣市", 15, C["ink"], 500),
            icon("chevron-down", 396, 544, 20, C["ink"])]
    return "".join(out)


def merchant_table():
    out = [text(30, 604, f"攤商清單 ({TOTAL})", 20, C["ink"], 900),
           rect(30, 614, 395, 28, 6, C["field"]),
           text(40, 633, "攤商名稱", 14, C["muted"], 700),
           text(211, 633, "所在夜市", 14, C["muted"], 700),
           text(363, 633, "狀態", 14, C["muted"], 700, "middle")]
    for i, (name, market, _city, status) in enumerate(ROWS):
        top = 644 + i * 36
        cy = top + 18
        if i == 0:  # 目前選取的攤商
            out.append(rect(30, top + 1, 395, 34, 6, "#F2F8FF"))
        out.append(image(32, cy - 16, 34, 32, f"food/food-{i + 1:02d}.png"))
        out.append(text(76, cy + 5, name, 15, C["ink"], 500))
        out.append(text(211, cy + 5, market, 14, C["body"]))
        out.append(badge(status, 319, cy - 13, w=88))
        out.append(line(30, top + 36, 425, top + 36, C["line_soft"]))
    out.append(pagination(966, [(58, "<"), (120, "1"), (157, "2"), (190, "3"), (222, "4"),
                                (255, "5"), (293, "…"), (332, "38"), (384, ">")]))
    return "".join(out)


def pagination(cy, items):
    out = []
    for x, label in items:
        if label in "<>":
            out.append(icon("chevron-left" if label == "<" else "chevron-right", x - 10, cy - 10, 20, C["ink"]))
        elif label == "1":
            out.append(rect(x - 17, cy - 17, 34, 34, 8, C["primary"]))
            out.append(text(x, cy + 6, label, 16, "#fff", 700, "middle"))
        else:
            out.append(text(x, cy + 6, label, 16, C["body"], 500, "middle"))
    return "".join(out)


def headline_bubble():
    """地圖左上角的標語對話框（蓋在底圖原本的對話框上）。"""
    return ('<g transform="rotate(-4 640 185)">'
            '<path d="M600 248 628 296 652 246z" fill="#fff" stroke="#3B2A1A" stroke-width="2.5" stroke-linejoin="round"/>'
            + rect(470, 118, 340, 134, 46, "#fff", C["brand"], 2.5)
            + '<path d="M603 250h46" stroke="#fff" stroke-width="5"/>'
            + text(640, 172, "全台夜市美食地圖", 30, "#7A2E12", 900, "middle", ' letter-spacing="2"')
            + text(640, 206, "看看你的攤位", 20, C["brand"], 700, "middle")
            + text(640, 236, "是否已經在 Google 地圖上！", 20, C["brand"], 700, "middle")
            + "</g>")


def map_legend(x=935, y=802, w=180, h=200, size=13.5, row=22, title=True):
    out = [rect(x, y, w, h, 14, "#fff", extra=' filter="url(#shadow)"')]
    ty = y + 28
    if title:
        out.append(text(x + 16, ty, "地圖標示說明", 15, C["ink"], 700))
        ty += 30
    else:
        ty = y + 18
    for i, (key, st) in enumerate(S.items()):
        yy = ty + i * row
        out.append(map_pin(key, x + 26, yy - 6, row / 40))
        out.append(text(x + 44, yy, st["label"], size, C["body"], 500))
    return "".join(out)


def map_view():
    out = [f'<defs><clipPath id="mapclip">{rect(456, 96, 1074, 926, 24, "#000")}</clipPath></defs>',
           '<g clip-path="url(#mapclip)">',
           rect(456, 96, 1074, 926, 0, C["sea"]),
           image(456, 96, 727, 926, "map-taiwan.png"),
           image(1183, 825, 347, 197, "map-corner.png"),
           image(1404, 900, 120, 118, "mascot-cat-wave.png"),
           headline_bubble()]
    for x, y, st in PINS:
        out.append(map_pin(st, x, y, selected=(x, y) == SELECTED_PIN))
    out.append(map_legend())
    out += [rect(1131, 925, 40, 76, 10, "#fff", extra=' filter="url(#shadow)"'),
            icon("plus", 1141, 935, 20, C["ink"]), line(1137, 963, 1165, 963, C["line"]),
            icon("minus", 1141, 972, 20, C["ink"])]
    out.append('<g transform="rotate(-14 1340 900)">'
               + rect(1243, 870, 196, 60, 28, "#fff", C["brand"], 2)
               + text(1341, 895, "完成 Google 地圖申請", 15, C["brand"], 700, "middle")
               + text(1341, 917, "讓更多人找到你的美味！", 15, C["brand"], 700, "middle")
               + "</g>")
    out.append("</g>")
    return "".join(out)


def detail_content(px, top, iw, d, photo_h=200):
    """攤商詳細資料內容（不含外框），桌機卡片與手機底部面板共用。"""
    st = S[d["status"]]
    out = [image(px, top, iw, photo_h, "stall-photo-sample.png", 12)]
    y = top + photo_h
    out.append(text(px, y + 38, d["name"], 24, C["ink"], 900))
    out.append(badge(d["status"], px + iw - 92, y + 13, w=92, h=34, size=15, with_icon=True))
    y += 50
    out.append(rect(px + 1, y, 85, 30, 8, C["primary_soft"]))
    out.append(text(px + 43, y + 20, d["market"], 14, C["primary"], 700, "middle"))
    out.append(rect(px + 94, y, 84, 30, 8, C["field"]))
    out.append(icon("pin", px + 104, y + 7, 16, C["muted"]))
    out.append(text(px + 124, y + 20, d["city"], 14, C["body"], 500))
    y += 46
    k = (iw - 1) / 309  # 小地圖依素材比例縮放，避免裁掉內容
    out.append(image(px + 1, y, iw - 1, 102 * k, "minimap-sample.png", 12))
    out.append(f'<g transform="translate({f(px + 1)} {f(y)}) scale({f(k)})">'
               + rect(157, 64, 148, 32, 8, "#fff")
               + text(165, 85, "Google 地圖上查看", 13, C["primary"], 700)
               + icon("external", 283, 71, 16, C["primary"]) + "</g>")
    y += 102 * k + 27
    rows = [("store", "店名", d["name"], None), ("market", "夜市", d["market"], None),
            ("link", "地圖連結", "Google 地圖連結", C["primary"]), ("target", "Place ID", d["place_id"], None),
            ("clock", "最後檢查時間", d["checked"], None)]
    for i, (ic, label, value, color) in enumerate(rows):
        b = y + i * 35
        out.append(icon(ic, px + 6, b - 15, 19, C["accent"]))
        out.append(text(px + 39, b, label, 14, C["body"]))
        out.append(text(px + 138, b, value, 14, color or C["ink"], 700 if color else 500))
        if ic == "target":
            out.append(icon("copy", px + iw - 30, b - 15, 18, C["muted"]))
        if i < len(rows) - 1:
            out.append(line(px, b + 14, px + iw, b + 14, C["line_soft"]))
    y += 4 * 35 + 34
    out.append(rect(px, y, iw, 78, 14, st["soft"]))
    out.append(circle(px + 48, y + 39, 24, st["main"]))
    out.append(status_glyph(d["status"], px + 48, y + 39, 1.6))
    out.append(text(px + 90, y + 33, d["title"], 16, st["text"], 700))
    out.append(text(px + 90, y + 57, d["sub"], 13.5, C["body"]))
    return "".join(out)


def detail_card(variant="verified"):
    return (card(1183, 118, 340, 707)
            + detail_content(1198, 132, 310, DETAIL[variant])
            + circle(1497, 141, 18, "#fff", extra=' filter="url(#shadow)"')
            + icon("x", 1488, 132, 18, C["ink"], 2.4))


def page_bg(w, h):
    return rect(0, 0, w, h, 0, C["page"])


# ---- 手機版（390 寬）----
M_W = 390
M_S = 358 / 727  # 手機版地圖縮放比例


def m_header():
    return "".join([rect(0, 0, M_W, 64, 0, C["card"]), line(0, 64, M_W, 64, "#C9E9F6", 2),
                    image(8, 8, 54, 48, "logo-stall.png"),
                    text(68, 34, "台灣攤商地圖", 22, C["brand"], 900, extra=' letter-spacing="1"'),
                    text(69, 53, "一起讓更多好味道被看見！", 11, "#5B4636", 700, extra=' letter-spacing="2"'),
                    rect(336, 13, 40, 40, 10, C["card"], "#CBD5E1", 1.5),
                    icon("menu", 345, 22, 22, C["ink"])])


def m_cta_tabs():
    out = [rect(16, 76, 358, 50, 14, C["primary"]),
           icon("link", 44, 90, 22, "#fff"),
           text(74, 107, "我是攤商，補上我的Google地圖連結", 15, "#fff", 700),
           rect(16, 138, 358, 44, 12, C["card"], "#D6E6F2"),
           rect(20, 142, 112, 36, 9, C["primary_soft"])]
    for i, (ic, label) in enumerate([("home", "地圖總覽"), ("users", "攤商列表"), ("chart", "統計報表")]):
        cx = 16 + 358 / 6 * (2 * i + 1)
        color = C["primary"] if i == 0 else C["ink"]
        out.append(icon(ic, cx - 40, 151, 18, color))
        out.append(text(cx - 16, 166, label, 14, color, 700))
    return "".join(out)


def m_progress():
    out = [card(16, 194, 358, 196, 16),
           text(32, 224, "整體進度", 18, C["ink"], 900),
           text(32, 244, f"最後更新：{UPDATED}", 12, C["muted"]),
           image(282, 198, 84, 54, "mascot-chef.png"),
           donut(92, 318, 50, 24, COUNTS),
           text(92, 323, str(TOTAL), 22, C["ink"], 900, "middle"),
           text(92, 340, "家攤商", 11, C["muted"], 500, "middle")]
    for i, (key, n) in enumerate(COUNTS.items()):
        y = 272 + i * 20
        out.append(circle(176, y - 4.5, 5, S[key]["main"]))
        out.append(text(188, y, S[key]["label"], 13, C["body"], 500))
        out.append(text(300, y, str(n), 13, C["ink"], 700, "end"))
        out.append(text(308, y, f"({round(n * 100 / TOTAL)}%)", 12, C["muted"]))
    return "".join(out)


def m_map(top=404):
    h = 926 * M_S

    def tx(x):
        return 16 + (x - 456) * M_S

    def ty(y):
        return top + (y - 96) * M_S

    out = [f'<defs><clipPath id="mmapclip">{rect(16, top, 358, h, 16, "#000")}</clipPath></defs>',
           '<g clip-path="url(#mmapclip)">',
           image(16, top, 358, h, "map-taiwan.png"),
           f'<g transform="translate(16 {f(top)}) scale({f(M_S)}) translate(-456 -96)">{headline_bubble()}</g>']
    for x, y, st in PINS:
        out.append(map_pin(st, tx(x), ty(y), 0.72, selected=(x, y) == SELECTED_PIN))
    out.append(map_legend(250, top + 338, 118, 112, size=11, row=17, title=False))
    out.append("</g>")
    return "".join(out)


def m_list(top=876):
    out = [rect(16, top, 358, 44, 10, C["card"], "#D1D5DB"),
           icon("search", 30, top + 11, 22, C["muted"]),
           text(62, top + 28, "搜尋攤商名稱或夜市...", 15, C["placeholder"])]
    x = 16  # 狀態篩選在手機上改成可橫向捲動的一列
    for label, status, active in [("全部狀態", None, True)] + [(S[k]["label"], k, False) for k in S]:
        svg, w = chip(label, x, top + 56, active, status)
        out.append(svg)
        x += w + 8
    out += [rect(16, top + 100, 358, 44, 10, C["card"], "#D1D5DB"),
            icon("pin", 30, top + 112, 20, C["ink"]),
            text(58, top + 128, "所有縣市", 15, C["ink"], 500),
            icon("chevron-down", 344, top + 112, 20, C["ink"]),
            text(16, top + 176, f"攤商清單 ({TOTAL})", 18, C["ink"], 900)]
    for i, (name, market, city, status) in enumerate(ROWS):
        y = top + 190 + i * 70
        out.append(rect(16, y, 358, 62, 12, C["card"], "#E3EBF2"))
        out.append(image(26, y + 15, 34, 32, f"food/food-{i + 1:02d}.png"))
        out.append(text(70, y + 27, name, 15, C["ink"], 700))
        out.append(text(70, y + 47, f"{market}・{city}", 12.5, C["muted"]))
        out.append(badge(status, 284, y + 18, w=78))
    out.append(pagination(top + 776, [(70, "<"), (120, "1"), (160, "2"), (200, "3"), (240, "…"),
                                      (280, "38"), (320, ">")]))
    return "".join(out)


# ---- 輸出 ----

DEFS = ('<defs><filter id="shadow" x="-10%" y="-10%" width="120%" height="130%">'
        '<feDropShadow dx="0" dy="4" stdDeviation="8" flood-color="#0B3B5B" flood-opacity="0.12"/>'
        '</filter></defs>')


def svg(box, body, title, bg=None):
    x, y, w, h = box
    pre = rect(x, y, w, h, 0, bg) if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{f(x)} {f(y)} {f(w)} {f(h)}" '
            f'width="{f(w)}" height="{f(h)}" font-family="{FONT}">\n'
            f'<title>{escape(title)}</title>\n{DEFS}\n{pre}{body}\n</svg>\n')


def write(rel, content):
    p = OUT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def atoms():
    # 狀態徽章 + 篩選 chip
    body = [text(24, 36, "狀態徽章 StatusBadge", 18, C["ink"], 900)]
    for i, key in enumerate(S):
        x = 24 + i * 120
        body.append(badge(key, x, 56, w=88))
        body.append(badge(key, x, 98, w=106, h=34, size=15, with_icon=True))
        body.append(text(x, 154, key, 11, C["muted"]))
    body.append(text(24, 200, "篩選 Chip（預設 / 選取）", 18, C["ink"], 900))
    x = 24
    for label, status, active in [("全部狀態", None, True), ("全部狀態", None, False), ("已完成", "verified", False)]:
        s, w = chip(label, x, 218, active, status)
        body.append(s)
        x += w + 12
    write("atoms/status-badges.svg", svg((0, 0, 740, 270), "".join(body), "狀態徽章與篩選 Chip", "#fff"))

    body = [text(24, 36, "地圖圖釘 MapPin", 18, C["ink"], 900)]
    for i, (key, st) in enumerate(S.items()):
        x = 60 + i * 100
        body.append(map_pin(key, x, 90))
        body.append(text(x, 140, st["label"], 13, C["body"], 500, "middle"))
    body.append(map_pin("verified", 680, 90, selected=True))
    body.append(text(680, 140, "選取中", 13, C["body"], 500, "middle"))
    write("atoms/map-pins.svg", svg((0, 0, 740, 170), "".join(body), "地圖圖釘", "#fff"))

    body = [text(24, 36, "圖示 Icons（24×24，線條 2px）", 18, C["ink"], 900)]
    for i, name in enumerate(ICONS):
        x, y = 24 + (i % 8) * 92, 60 + (i // 8) * 80
        body.append(rect(x, y, 80, 64, 10, C["field"]))
        body.append(icon(name, x + 28, y + 10, 24, C["ink"]))
        body.append(text(x + 40, y + 54, name, 10.5, C["muted"], 400, "middle"))
    write("atoms/icons.svg", svg((0, 0, 760, 60 + math.ceil(len(ICONS) / 8) * 80 + 10), "".join(body), "圖示", "#fff"))

    body = [text(24, 36, "按鈕 Buttons", 18, C["ink"], 900)]
    body.append(f'<g transform="translate(-976 40)">{rect(1000, 17, 341, 57, 14, C["primary"])}'
                f'{icon("link", 1018, 33, 24, "#fff")}{text(1053, 53, "我是攤商，補上我的Google地圖連結", 17, "#fff", 700)}</g>')
    body.append(f'<g transform="translate(-976 40)">{rect(1354, 17, 163, 57, 14, C["card"], "#CBD5E1", 1.5)}'
                f'{icon("user", 1376, 33, 24, C["ink"])}{text(1410, 53, "管理者登入", 17, C["ink"], 700)}</g>')
    body.append(text(24, 150, "導覽分頁 NavTab（選取 / 未選取）", 14, C["muted"], 700))
    body.append(f'<g transform="translate(-413 150)">{rect(437, 18, 163, 55, 14, C["primary_soft"])}'
                f'{icon("home", 461, 33, 24, C["primary"])}{text(497, 53, "地圖總覽", 19, C["primary"], 700)}'
                f'{icon("users", 636, 33, 24, C["ink"])}{text(672, 53, "攤商列表", 19, C["ink"], 700)}</g>')
    body.append(text(24, 260, "分頁 Pagination", 14, C["muted"], 700))
    body.append(pagination(296, [(34, "<"), (80, "1"), (117, "2"), (150, "3"), (188, "…"), (227, "38"), (270, ">")]))
    write("atoms/buttons.svg", svg((0, 0, 560, 330), "".join(body), "按鈕", "#fff"))

    body = [text(24, 36, "色彩 Tokens", 18, C["ink"], 900)]
    for i, (name, val) in enumerate(C.items()):
        x, y = 24 + (i % 6) * 118, 56 + (i // 6) * 92
        body.append(rect(x, y, 106, 46, 10, val, "#D1D5DB"))
        body.append(text(x, y + 62, name, 11.5, C["ink"], 700))
        body.append(text(x, y + 77, val, 11, C["muted"]))
    y0 = 56 + math.ceil(len(C) / 6) * 92 + 20
    body.append(text(24, y0, "狀態色（主色 / 淺底 / 文字）", 14, C["muted"], 700))
    for i, (key, st) in enumerate(S.items()):
        x = 24 + i * 118
        for j, k in enumerate(("main", "soft", "text")):
            body.append(rect(x + j * 36, y0 + 14, 32, 32, 8, st[k], "#D1D5DB"))
        body.append(text(x, y0 + 64, f'{st["label"]} {key}', 11, C["ink"], 700))
    write("atoms/color-tokens.svg", svg((0, 0, 740, y0 + 84), "".join(body), "色彩 Tokens", "#fff"))


def components():
    write("components/header.svg", svg((0, 0, 1536, 94), header(), "頁首 Header"))
    write("components/progress-card.svg",
          svg((0, 95, 455, 294), progress_card(), "整體進度卡 ProgressCard", C["page"]))
    write("components/filter-panel.svg",
          svg((0, 380, 455, 206), card(12, 388, 431, 190) + filter_panel(), "篩選面板 FilterPanel", C["page"]))
    write("components/merchant-table.svg",
          svg((0, 572, 455, 444), card(12, 580, 431, 424) + merchant_table(), "攤商清單 MerchantTable", C["page"]))
    write("components/map-view.svg", svg((448, 88, 1090, 942), map_view(), "地圖總覽 MapView", C["page"]))
    write("components/map-legend.svg",
          svg((921, 790, 208, 226), map_legend(), "地圖圖例 MapLegend", C["sea"]))
    for v in DETAIL:
        name = "merchant-detail-card" + ("" if v == "verified" else f"-{v}")
        write(f"components/{name}.svg",
              svg((1171, 106, 364, 733), detail_card(v), f"攤商詳細資料卡 MerchantDetailCard（{S[v]['label']}）", C["page"]))


def pages():
    body = (page_bg(1536, 1024) + header() + progress_card() + card(12, 388, 431, 616)
            + filter_panel() + merchant_table() + map_view() + detail_card())
    write("pages/overview-desktop.svg", svg((0, 0, 1536, 1024), body, "地圖總覽（桌機版）"))

    body = page_bg(M_W, 1700) + m_header() + m_cta_tabs() + m_progress() + m_map() + m_list()
    write("pages/overview-mobile.svg", svg((0, 0, M_W, 1700), body, "地圖總覽（手機版）"))

    body = (page_bg(M_W, 920) + m_header() + m_map(64)
            + rect(0, 0, M_W, 920, 0, "#0B1B2B", extra=' opacity="0.42"')
            + rect(0, 150, M_W, 790, 22, C["card"])
            + rect(171, 160, 48, 5, 2.5, "#D1D5DB")
            + detail_content(16, 176, 358, DETAIL["verified"], photo_h=170)
            + circle(352, 198, 16, "#fff", extra=' filter="url(#shadow)"')
            + icon("x", 343, 189, 18, C["ink"], 2.4)
            + rect(16, 856, 358, 48, 12, C["primary"])
            + icon("external", 106, 870, 20, "#fff")
            + text(134, 886, "在 Google 地圖開啟", 16, "#fff", 700))
    write("pages/detail-mobile.svg", svg((0, 0, M_W, 920), body, "攤商詳細資料（手機版底部面板）"))


if __name__ == "__main__":
    atoms()
    components()
    pages()
    print("\n".join(str(p.relative_to(ROOT)) for p in sorted(OUT.rglob("*.svg"))))
