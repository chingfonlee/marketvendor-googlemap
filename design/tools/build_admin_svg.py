"""產生管理版（攤商管理地圖）的 SVG，座標以 admin-mockup.webp（1536x1024）為準。
共用 build_svg.py 的繪圖函式與狀態定義。執行：python design/tools/build_admin_svg.py
"""
from build_svg import (ALL, C, S, SC, badge, card, circle, donut, f, icon, image, line,
                       map_pin, page_bg, pagination, rect, status_glyph, svg, text, write, ROOT, OUT)

# ---- 範例資料 ----
MAP_COUNTS = {"verified": 112, "submitted": 20, "candidate": 40, "incomplete": 28, "not_found": 45, "not_submitted": 55}
CONTACT_COUNTS = {"not_contacted": 52, "contacted": 196, "tracking": 24, "reminded": 28}
TOTAL = sum(MAP_COUNTS.values())
UPDATED = "2026/10/31 10:30"
MAP_NOTE = {
    "verified": "已上架", "submitted": "待核對", "candidate": "疑似找到",
    "incomplete": "資料不全", "not_found": "查無地點", "not_submitted": "尚無資料",
}
CONTACT_NOTE = {"not_contacted": "尚未聯絡", "contacted": "已聯絡攤商", "tracking": "持續追蹤", "reminded": "已再次提醒"}
ROWS = [
    ("香香超大烤雞排", "花園夜市", "verified", "contacted"),
    ("阿明地瓜球", "花園夜市", "submitted", "contacted"),
    ("幸福滷味", "逢甲夜市", "not_found", "not_contacted"),
    ("大腸包小腸", "逢甲夜市", "verified", "contacted"),
    ("QQ章魚燒", "瑞豐夜市", "incomplete", "reminded"),
    ("古早味杏仁茶", "寧夏夜市", "candidate", "not_contacted"),
    ("胖胖雞蛋糕", "士林夜市", "verified", "contacted"),
    ("阿婆蚵仔煎", "士林夜市", "not_submitted", "tracking"),
]
# 圖釘：(x, y, 地圖狀態, 聯繫狀態)，位置對齊底圖原本的圖釘
_COLOR = {"g": ("verified", "contacted"), "r": ("not_found", "reminded"), "b": ("submitted", "contacted"),
          "o": ("candidate", "not_contacted"), "p": ("incomplete", "tracking"), "n": ("not_submitted", "not_contacted")}
PINS = [(x, y, *_COLOR[c]) for x, y, c in [
    (974, 176, "g"), (957, 214, "b"), (882, 225, "r"), (1010, 210, "g"), (1010, 279, "g"), (1059, 280, "p"),
    (871, 309, "r"), (836, 337, "g"), (884, 345, "o"), (920, 360, "g"), (1010, 329, "n"), (1007, 391, "b"),
    (903, 412, "r"), (774, 450, "b"), (819, 482, "o"), (661, 492, "b"), (699, 502, "g"), (1006, 504, "p"),
    (974, 526, "g"), (884, 545, "p"), (846, 553, "g"), (650, 566, "r"), (695, 586, "g"), (762, 604, "b"),
    (630, 667, "n"), (797, 651, "r"), (860, 699, "g"), (895, 715, "p"), (742, 741, "g"), (810, 771, "n"),
    (780, 782, "g"), (727, 857, "o"),
]]
SELECTED = (695, 586)
DETAIL = {
    "name": "香香超大烤雞排", "market": "花園夜市", "address": "台南市北區海安路三段",
    "map_status": "verified", "contact": "contacted", "contacted_on": "2026/10/20", "updated": "2026/10/24 08:12",
}
TIMELINE = [
    ("contacted", "電話聯繫：已確認資料", "2026/10/24 14:20・王小明", "老闆已提供正確地址與營業時間"),
    ("verified", "系統核對通過", "2026/10/24 08:12・每日排程", "Place ID、店名、地址皆相符"),
    ("submitted", "攤商提交地圖連結", "2026/10/21 19:05・攤商自填", "連結已解析出 Place ID"),
    ("candidate", "Agent 初次比對", "2026/10/12 09:00・Agent", "找到候選地點，待確認"),
]
NOTES = [
    ("王", "王小明", "2026/10/24 14:25", ["老闆很熱情，已提供正確地址與", "營業時間，照片已更新。"], "#FFF8E6"),
    ("陳", "陳美玲", "2026/10/15 16:40", ["已用 LINE 傳送自填連結，", "老闆說週末會補上。"], "#F9FAFB"),
]


def header():
    out = [rect(0, 0, 1536, 88, 0, C["card"]), line(0, 88, 1536, 88, "#C9E9F6", 2),
           image(18, 10, 86, 74, "admin-logo-stall.png"),
           text(118, 52, "攤商管理地圖", 40, C["brand"], 900, extra=' letter-spacing="2"'),
           text(113, 77, "— 讓台灣夜市更熱鬧・一起把在地美味推向全世界！—", 13, "#5B4636", 500)]
    for ic, label, x, w, active in [("home", "地圖總覽", 450, 160, True), ("users", "攤商列表", 622, 140, False),
                                    ("chart", "統計報表", 770, 140, False), ("note", "任務管理", 918, 140, False)]:
        color = C["primary"] if active else C["ink"]
        if active:
            out.append(rect(x, 22, w, 48, 12, C["primary_soft"]))
        out.append(icon(ic, x + 22, 34, 24, color))
        out.append(text(x + 56, 53, label, 18, color, 700))
    out += [rect(1083, 20, 296, 50, 12, C["primary"]),
            icon("link", 1098, 34, 22, "#fff"),
            text(1128, 51, "我是攤商，補上我的Google地圖連結", 15, "#fff", 700),
            rect(1389, 20, 136, 50, 12, C["card"], "#CBD5E1", 1.5),
            circle(1414, 45, 13, C["primary_soft"]), text(1414, 50, "王", 13, C["primary"], 700, "middle"),
            text(1434, 51, "管理員", 15, C["ink"], 700),
            icon("chevron-down", 1494, 37, 16, C["ink"])]
    return "".join(out)


def progress_card():
    pct = round(MAP_COUNTS["verified"] * 100 / TOTAL)
    out = [card(12, 100, 472, 328),
           text(30, 138, "攤商管理總覽", 24, C["ink"], 900),
           text(30, 163, f"最後更新：{UPDATED}", 13, C["muted"]),
           # 對話框（百分比是動態值，所以用向量文字）
           '<g transform="rotate(-6 365 152)">',
           '<path d="M418 196 436 220 400 200z" fill="#fff" stroke="#3B2A1A" stroke-width="2" stroke-linejoin="round"/>',
           rect(282, 104, 168, 98, 40, "#fff", C["brand"], 2),
           '<path d="M404 199l13-1" stroke="#fff" stroke-width="4"/>',
           text(366, 128, "一起完成", 13, C["brand"], 700, "middle"),
           text(366, 148, "全台夜市攤商地圖！", 13, C["brand"], 700, "middle"),
           text(386, 170, "目前已完成", 13, C["brand"], 700, "end"),
           text(390, 170, f"{pct}%", 16, S["verified"]["main"], 900),
           text(366, 190, "加油！", 13, C["brand"], 700, "middle"),
           "</g>",
           image(385, 188, 145, 124, "admin-mascot-cat-map.png"),
           donut(112, 266, 64, 30, MAP_COUNTS),
           text(112, 272, str(TOTAL), 28, C["ink"], 900, "middle"),
           text(112, 292, "攤商總數", 12, C["muted"], 500, "middle"),
           text(214, 206, "地圖狀態", 13, C["muted"], 700)]
    for i, (key, n) in enumerate(MAP_COUNTS.items()):
        y = 228 + i * 20
        out.append(circle(222, y - 4.5, 5.5, S[key]["main"]))
        out.append(text(234, y, S[key]["label"], 13.5, C["body"], 500))
        out.append(text(326, y, str(n), 13.5, C["ink"], 700, "end"))
        out.append(text(333, y, f"({round(n * 100 / TOTAL)}%)", 12.5, C["muted"]))
    out += [line(30, 350, 466, 350, C["line_soft"]),
            text(30, 374, "聯繫狀態", 13, C["muted"], 700)]
    x = 96
    for key, n in CONTACT_COUNTS.items():  # 堆疊長條
        w = 370 * n / TOTAL
        out.append(rect(x, 363, max(w - 2, 1), 14, 3, SC[key]["main"]))
        x += w
    for i, (key, n) in enumerate(CONTACT_COUNTS.items()):
        x = 30 + i * 110
        out.append(circle(x + 6, 401, 5.5, SC[key]["main"]))
        out.append(text(x + 17, 406, SC[key]["label"], 13, C["body"], 500))
        out.append(text(x + 62, 406, str(n), 13, C["ink"], 700))
    return "".join(out)


def select(x, y, w, label, h=36):
    return (rect(x, y, w, h, 10, C["card"], "#D1D5DB") + text(x + 14, y + h / 2 + 5, label, 14, C["ink"], 500)
            + icon("chevron-down", x + w - 30, y + h / 2 - 9, 18, C["ink"]))


def filter_panel():
    return "".join([rect(28, 452, 440, 40, 10, C["card"], "#D1D5DB"),
                    icon("search", 41, 461, 22, C["muted"]),
                    text(72, 478, "搜尋攤商名稱、夜市或地點...", 15, C["placeholder"]),
                    select(28, 502, 216, "地圖狀態：全部"), select(252, 502, 216, "聯繫狀態：全部"),
                    select(28, 546, 216, "所有縣市"), select(252, 546, 216, "所有夜市")])


def merchant_table():
    out = [text(28, 614, f"攤商清單 ({TOTAL})", 20, C["ink"], 900),
           rect(20, 624, 456, 28, 6, C["field"]),
           text(34, 643, "攤商名稱", 13.5, C["muted"], 700),
           text(178, 643, "夜市", 13.5, C["muted"], 700),
           text(318, 643, "地圖狀態", 13.5, C["muted"], 700, "middle"),
           text(422, 643, "聯繫狀態", 13.5, C["muted"], 700, "middle")]
    for i, (name, market, ms, cs) in enumerate(ROWS):
        top = 654 + i * 34
        cy = top + 17
        if i == 0:
            out.append(rect(20, top + 1, 456, 32, 6, "#FFF6E5"))
        out.append(image(28, cy - 15, 32, 30, f"food/food-{i + 1:02d}.png"))
        out.append(text(68, cy + 5, name, 14, C["ink"], 500))
        out.append(text(178, cy + 5, market, 13.5, C["body"]))
        out.append(badge(ms, 274, cy - 12, w=88, h=24, size=12, with_icon=True))
        out.append(badge(cs, 378, cy - 12, w=88, h=24, size=12, with_icon=True))
        out.append(line(20, top + 34, 476, top + 34, C["line_soft"]))
    out.append(pagination(962, [(44, "<"), (89, "1"), (124, "2"), (154, "3"), (184, "4"), (214, "5"),
                                (244, "…"), (276, "38"), (320, ">")]))
    out.append(select(358, 944, 110, "每頁 8 筆"))
    return "".join(out)


def legend(mode):
    """圖例兼切換鈕：上方分段切換「地圖狀態／聯繫狀態」，圖釘跟著換色。"""
    out = [rect(886, 736, 196, 254, 14, "#fff", extra=' filter="url(#shadow)"'),
           text(902, 762, "攤商狀態圖例", 15, C["ink"], 700),
           rect(900, 772, 168, 30, 8, C["field"])]
    ax = 902 if mode == "map" else 984
    out.append(rect(ax, 774, 82, 26, 7, "#fff", extra=' filter="url(#shadow)"'))
    for i, (key, label) in enumerate([("map", "地圖狀態"), ("contact", "聯繫狀態")]):
        on = key == mode
        out.append(text(943 + i * 82, 792, label, 13, C["primary"] if on else C["muted"], 700 if on else 500, "middle"))
    items = [(k, MAP_NOTE[k]) for k in S] if mode == "map" else [(k, CONTACT_NOTE[k]) for k in SC]
    for i, (key, note) in enumerate(items):
        y = 830 + i * 26
        out.append(circle(910, y - 5, 10, ALL[key]["main"]))
        out.append(status_glyph(key, 910, y - 5, 0.7))
        out.append(text(928, y, f'{ALL[key]["label"]}（{note}）', 13, C["body"], 500))
    return "".join(out)


def map_view(mode="map"):
    out = [f'<defs><clipPath id="amap">{rect(493, 88, 1043, 928, 24, "#000")}</clipPath></defs>',
           '<g clip-path="url(#amap)">',
           rect(493, 88, 1043, 928, 0, C["sea"]),
           image(493, 88, 645, 928, "admin-map.png"),
           image(1138, 915, 398, 101, "admin-map-corner.png")]
    for x, y, ms, cs in PINS:
        out.append(map_pin(ms if mode == "map" else cs, x, y, 1.15, selected=(x, y) == SELECTED))
    out.append(legend(mode))
    out += [rect(1088, 904, 40, 86, 10, "#fff", extra=' filter="url(#shadow)"'),
            icon("plus", 1098, 916, 20, C["ink"]), line(1094, 947, 1122, 947, C["line"]),
            icon("minus", 1098, 958, 20, C["ink"]), "</g>"]
    return "".join(out)


def tab_bar(active):
    out = []
    for key, ic, label, x, w in [("info", "user", "基本資訊", 1153, 122), ("tasks", "edit", "任務紀錄", 1283, 113),
                                 ("notes", "note", "備註 (2)", 1404, 110)]:
        on = key == active
        out.append(rect(x, 436, w, 42, 10, C["primary"] if on else C["card"], None if on else C["line"], 1.5))
        color = "#fff" if on else C["ink"]
        out.append(icon(ic, x + 16, 448, 18, color))
        out.append(text(x + 42, 463, label, 15, color, 700))
    return "".join(out)


def info_tab():
    d = DETAIL
    out = []
    rows = [("store", "店名", 515), ("pin", "夜市／地點", 552), ("check", "地圖狀態", 594),
            ("phone", "聯繫狀態", 638), ("link", "Google 地圖", 682), ("clock", "最後更新", 726), ("note", "備註", 770)]
    for i, (ic, label, b) in enumerate(rows):
        out.append(icon(ic, 1156, b - 16, 20, C["accent"]))
        out.append(text(1193, b, label, 14, C["body"]))
        if i < len(rows) - 1:
            out.append(line(1153, b + 15, 1513, b + 15, C["line_soft"]))
    out += [text(1287, 515, d["name"], 14.5, C["ink"], 500),
            text(1287, 552, f'{d["market"]}（台南市北區）', 14.5, C["ink"], 500),
            badge(d["map_status"], 1285, 577, w=150, h=30, size=14, with_icon=True, label="已完成（已上架）"),
            badge(d["contact"], 1285, 621, w=176, h=30, size=14, with_icon=True,
                  label=f'已聯繫（{d["contacted_on"]}）'),
            icon("link", 1287, 667, 20, C["primary"]),
            text(1314, 682, "前往 Google 地圖查看", 14.5, C["primary"], 700),
            icon("external", 1468, 669, 17, C["primary"]),
            text(1287, 726, d["updated"], 14.5, C["ink"], 500),
            rect(1285, 752, 228, 84, 10, "#FFF8E6"),
            text(1297, 776, "老闆很熱情，已提供正確地址", 13.5, C["body"]),
            text(1297, 798, "與營業時間，照片已更新。", 13.5, C["body"]),
            text(1297, 820, "（2026/10/24）", 13.5, C["muted"])]
    return "".join(out)


def tasks_tab():
    out = [text(1154, 514, "聯繫與核對紀錄", 15, C["ink"], 700),
           rect(1414, 494, 99, 30, 8, C["primary_soft"]),
           icon("plus", 1424, 501, 16, C["primary"]),
           text(1444, 514, "新增紀錄", 13, C["primary"], 700),
           line(1166, 548, 1166, 790, C["line"], 2)]
    for i, (kind, title, meta, detail) in enumerate(TIMELINE):
        y = 548 + i * 74
        out.append(circle(1166, y, 11, ALL[kind]["main"], "#fff", 2.5))
        out.append(status_glyph(kind, 1166, y, 0.75))
        out.append(text(1188, y + 5, title, 14.5, C["ink"], 700))
        out.append(text(1188, y + 25, meta, 12, C["muted"]))
        out.append(text(1188, y + 46, detail, 13, C["body"]))
    return "".join(out)


def notes_tab():
    out = []
    for i, (avatar, who, when, lines, bg) in enumerate(NOTES):
        y = 494 + i * 102
        out.append(rect(1153, y, 360, 92, 12, bg, C["line_soft"]))
        out.append(circle(1173, y + 22, 12, C["primary_soft"]))
        out.append(text(1173, y + 27, avatar, 12, C["primary"], 700, "middle"))
        out.append(text(1193, y + 27, who, 14, C["ink"], 700))
        out.append(text(1501, y + 27, when, 12, C["muted"], 400, "end"))
        for j, ln in enumerate(lines):
            out.append(text(1165, y + 54 + j * 22, ln, 13.5, C["body"]))
    out += [rect(1153, 702, 360, 134, 12, C["card"], "#D1D5DB"),
            text(1167, 728, "新增備註…", 14, C["placeholder"]),
            text(1167, 822, "0 / 300", 12, C["muted"]),
            rect(1427, 796, 74, 30, 8, C["primary"]),
            text(1464, 816, "送出", 14, "#fff", 700, "middle")]
    return "".join(out)


def detail_card(tab="info"):
    d = DETAIL
    out = [card(1138, 98, 388, 817),
           image(1152, 110, 362, 235, "admin-stall-photo-sample.png", 12),
           circle(1503, 119, 16, "#fff", extra=' filter="url(#shadow)"'),
           icon("x", 1494, 110, 18, C["ink"], 2.4),
           text(1154, 382, d["name"], 26, C["ink"], 900),
           badge(d["map_status"], 1408, 357, w=102, h=34, size=15, with_icon=True),
           rect(1154, 395, 92, 30, 8, C["primary_soft"]),
           text(1200, 415, d["market"], 14, C["primary"], 700, "middle"),
           icon("pin", 1258, 401, 18, C["muted"]),
           text(1282, 415, d["address"], 14, C["body"]),
           tab_bar(tab),
           {"info": info_tab, "tasks": tasks_tab, "notes": notes_tab}[tab](),
           # 操作列
           rect(1153, 855, 113, 46, 10, C["primary"]),
           icon("edit", 1167, 869, 18, "#fff"),
           text(1193, 884, "編輯資料", 15, "#fff", 700),
           rect(1275, 855, 121, 46, 10, C["card"], C["line"], 1.5),
           icon("x", 1286, 869, 18, S["not_found"]["main"], 2.4),
           text(1310, 884, "標記為未完成", 14, C["ink"], 700),
           rect(1405, 855, 108, 46, 10, C["card"], C["line"], 1.5),
           text(1420, 884, "更多操作", 14, C["ink"], 700),
           icon("chevron-down", 1484, 870, 16, C["ink"])]
    return "".join(out)


def contact_atoms():
    body = [text(24, 36, "聯繫狀態 ContactStatus（管理版）", 18, C["ink"], 900)]
    for i, (key, st) in enumerate(SC.items()):
        x = 24 + i * 150
        body.append(badge(key, x, 56, w=88, h=24, size=12, with_icon=True))
        body.append(badge(key, x, 92, w=110, h=34, size=15, with_icon=True))
        body.append(map_pin(key, x + 20, 162))
        body.append(text(x + 44, 168, key, 11, C["muted"]))
        body.append(text(x, 210, f'{st["main"]} / {st["soft"]} / {st["text"]}', 10.5, C["muted"]))
    write("atoms/contact-badges.svg", svg((0, 0, 620, 230), "".join(body), "聯繫狀態徽章與圖釘", "#fff"))


def main():
    contact_atoms()
    pre = "components/admin-"
    write(pre + "header.svg", svg((0, 0, 1536, 90), header(), "管理版頁首"))
    write(pre + "progress-card.svg", svg((0, 92, 496, 344), progress_card(), "攤商管理總覽卡", C["page"]))
    write(pre + "filter-panel.svg",
          svg((0, 432, 496, 160), card(12, 440, 472, 144) + filter_panel(), "管理版篩選面板", C["page"]))
    write(pre + "merchant-table.svg",
          svg((0, 584, 496, 428), card(12, 592, 472, 412) + merchant_table(), "管理版攤商清單", C["page"]))
    write(pre + "map-view.svg", svg((485, 80, 1051, 944), map_view("map"), "管理地圖（依地圖狀態）", C["page"]))
    write(pre + "map-view-contact.svg", svg((485, 80, 1051, 944), map_view("contact"), "管理地圖（依聯繫狀態）", C["page"]))
    for tab, label in [("info", "基本資訊"), ("tasks", "任務紀錄"), ("notes", "備註")]:
        write(f"{pre}detail-card-{tab}.svg",
              svg((1126, 86, 410, 841), detail_card(tab), f"攤商詳細資料卡：{label}", C["page"]))
    body = (page_bg(1536, 1024) + header() + progress_card() + card(12, 440, 472, 564)
            + filter_panel() + merchant_table() + map_view() + detail_card())
    write("pages/admin-map-desktop.svg", svg((0, 0, 1536, 1024), body, "攤商管理地圖（管理版）"))


if __name__ == "__main__":
    main()
    print("\n".join(str(p.relative_to(ROOT)) for p in sorted(OUT.rglob("*admin*.svg")) + [OUT / "atoms/contact-badges.svg"]))
