"""產生攤商補登頁（專屬網址 /m/<代碼>）的 SVG，桌機座標以 merchant-form-mockup.png（1448x1086）為準。
共用 build_svg.py 的繪圖函式。執行：python design/tools/build_form_svg.py
"""
from build_svg import (ALL, C, ICONS, S, card, circle, f, icon, image, line, rect, status_glyph,
                       svg, text, tw, write, ROOT, OUT)

ICONS.update({
    "bulb": ["M9 18h6", "M10 21h4",
             "M12 3a6 6 0 0 0-3.5 10.9c.6.5 1 1.2 1 2V16h5v-.1c0-.8.4-1.5 1-2A6 6 0 0 0 12 3z"],
    "shield": ["M12 3l7 3v5c0 4.5-3 8.3-7 10-4-1.7-7-5.5-7-10V6z", "M8.5 12l2.5 2.5 4.5-4.5"],
    "send": ["M21 3L10 14", "M21 3l-7 18-4-7-7-4z"],
    "help": ["c:12,12,9", "M9.5 9.5a2.5 2.5 0 1 1 3.5 2.3c-.6.3-1 .8-1 1.5v.7", "M12 17h.01"],
    "clipboard": ["r:5,4,14,17,2", "M9 4V3h6v1", "M9 10h6", "M9 14h6"],
    "refresh": ["M20 12a8 8 0 1 1-2.3-5.7", "M20 4v5h-5"],
})

W, H = 1448, 1086
M_W = 390
RED = "#E5484D"
# 範例：從名單帶入的資料
PREFILL = {"name": "香香超大烤雞排", "market": "花園夜市", "city": "台南市", "district": "北區"}
STEPS = [
    ("貼上連結", "貼上你的 Google 地圖商家連結", "link", "#F7A1AA", "#FDE2E4", RED),
    ("系統自動檢查", "自動核對店名、位置、連結格式", "search", "#3B82F6", "#DCEBFF", "#1F6FE5"),
    ("完成確認", "送出後立即看到核對結果！", "check", "#22A06B", "#DDF5E8", "#22A06B"),
]
CHECKS = ["店名是否相符", "位置是否正確", "連結格式是否有效"]

# 送出後的核對結果；項目狀態：ok / fail / wait
RESULTS = {
    "verified": {
        "status": "verified", "title": "核對通過，已完成！",
        "desc": "你的攤位已經出現在台灣攤商地圖上，謝謝你！",
        "items": [("ok", "連結格式有效", ""), ("ok", "店名相符", ""), ("ok", "位置正確", "台南市北區"),
                  ("ok", "營業時間已填寫", ""), ("ok", "店家照片", "5 張")],
        "buttons": [("在地圖上查看我的攤位", "external"), ("修改資料", "edit")],
        "foot": "之後若 Google 地圖資料有變動，系統每天會自動重新檢查。",
    },
    "incomplete": {
        "status": "incomplete", "title": "還差 2 項就完成",
        "desc": "請到 Google 商家檔案補上以下項目，補好後按「重新檢查」。",
        "items": [("ok", "連結格式有效", ""), ("ok", "店名相符", ""), ("ok", "位置正確", "台南市北區"),
                  ("fail", "營業時間未填寫", "商家檔案 → 營業時間"), ("fail", "店家照片只有 1 張", "至少需要 3 張")],
        "buttons": [("已補好，重新檢查", "refresh"), ("修改連結", "edit")],
        "foot": "系統每天也會自動重新檢查一次。",
    },
    "invalid": {
        "status": "not_found", "title": "連結無法辨識",
        "desc": "這個連結找不到 Google 地圖上的商家，請確認後重新貼上。",
        "items": [("fail", "連結格式", "需為 Google 地圖商家連結"), ("wait", "店名相符", "等待有效連結"),
                  ("wait", "位置正確", "等待有效連結")],
        "howto": ["如何取得連結：", "1. 在 Google 地圖搜尋你的店", "2. 點「分享」", "3. 按「複製連結」後貼上"],
        "buttons": [("重新貼上連結", "link"), ("需要協助", "help")],
        "foot": "",
    },
}


def gpin(x, y, s=1.0):
    """表單裡的地圖圖釘圖示（一般圖示，不使用 Google 標誌）。"""
    return (f'<g transform="translate({f(x)} {f(y)}) scale({f(s)})">'
            '<path d="M0 16C-3 11.5-9 7-9 0a9 9 0 0 1 18 0c0 7-6 11.5-9 16z" fill="#EA4335"/>'
            '<circle cx="0" cy="0" r="3.4" fill="#fff"/></g>')


# ---- 桌機版 ----

def header(w=W):
    out = [rect(0, 0, w, 88, 0, C["card"]), line(0, 88, w, 88, "#C9E9F6", 2),
           image(50, 8, 88, 76, "form-logo-stall.png"),
           text(163, 52, "攤商管理平台", 38, C["brand"], 900, extra=' letter-spacing="2"'),
           text(150, 76, "— 讓台灣夜市更熱鬧・一起把在地美味分享給更多人！—", 12.5, "#5B4636", 500)]
    for ic, label, x, wd, active in [("home", "首頁", 770, 100, False), ("edit", "攤商資料補登", 884, 183, True),
                                     ("help", "常見問題", 1082, 140, False)]:
        color = C["primary"] if active else C["ink"]
        if active:
            out.append(rect(x, 18, wd, 52, 12, C["primary_soft"]))
        out.append(icon(ic, x + 16, 32, 24, color))
        out.append(text(x + 50, 52, label, 18, color, 700))
    # 從專屬網址進來，已辨識是哪一家攤商
    out += [rect(1236, 18, 172, 52, 12, C["card"], "#CBD5E1", 1.5),
            icon("store", 1250, 32, 22, C["accent"]),
            text(1280, 51, PREFILL["name"], 15, C["ink"], 700),
            icon("chevron-down", 1384, 36, 16, C["ink"])]
    return "".join(out)


def field_label(cy, ic, color, label, required=True, x=132):
    out = [circle(x, cy, 22, "#EEF4FB"), icon(ic, x - 11, cy - 11, 22, color),
           text(x + 38, cy + 6, label, 18, C["ink"], 700)]
    if required:
        out.append(text(x + 42 + tw(label, 18), cy + 6, "*", 18, RED, 700))
    return "".join(out)


def field(x, y, w, h, value=None, placeholder=None, chevron=False):
    out = [rect(x, y, w, h, 10, C["card"], "#D1D5DB")]
    if value:
        out.append(text(x + 16, y + h / 2 + 5.5, value, 16, C["ink"], 500))
    else:
        out.append(text(x + 16, y + h / 2 + 5.5, placeholder, 15, C["placeholder"]))
    if chevron:
        out.append(icon("chevron-down", x + w - 34, y + h / 2 - 9, 18, C["ink"]))
    return "".join(out)


def link_field(variant="empty"):
    """Google 地圖連結欄：empty＝等待貼上，candidate＝Agent 找到候選地點，讓攤商一鍵確認。"""
    out = [rect(100, 620, 810, 100, 18, "#EAF4FF"),
           circle(132, 659, 22, "#fff"), icon("link", 121, 648, 22, C["primary"]),
           text(170, 661, "Google 地圖", 18, C["ink"], 700),
           text(170, 690, "商家連結", 18, C["ink"], 700), text(256, 690, "*", 18, RED, 700),
           icon("help", 280, 674, 20, C["muted"])]
    if variant == "empty":
        out += [rect(338, 634, 557, 72, 12, C["card"], "#BFD7F5", 1.5),
                gpin(372, 664),
                text(418, 665, "請貼上 Google 地圖商家連結", 15, C["placeholder"]),
                text(418, 690, "（例如：https://maps.app.goo.gl/…）", 15, C["placeholder"])]
    else:
        st = S["candidate"]
        out += [rect(338, 630, 557, 82, 12, C["card"], st["main"], 1.5),
                circle(368, 664, 16, st["soft"]), status_glyph("candidate", 368, 664, 0.9),
                f'<circle cx="368" cy="664" r="11" fill="{st["main"]}"/>', status_glyph("candidate", 368, 664, 0.85),
                text(394, 654, "我們找到可能是你的店：", 13, C["muted"]),
                text(394, 678, "香香超大烤雞排・台南市北區海安路三段", 15, C["ink"], 700),
                text(394, 700, "在 Google 地圖查看", 12.5, C["primary"], 700),
                icon("external", 508, 690, 13, C["primary"]),
                rect(762, 640, 122, 30, 8, C["primary"]),
                text(823, 660, "是我的店", 14, "#fff", 700, "middle"),
                rect(762, 676, 122, 28, 8, C["card"], C["line"], 1.5),
                text(823, 695, "不是，貼上連結", 13, C["body"], 700, "middle")]
    return "".join(out)


def form_card(link_variant="empty"):
    p = PREFILL
    out = [card(82, 305, 846, 770, 22),
           icon("clipboard", 114, 326, 44, C["primary"], 2.2),
           text(180, 357, "填寫攤商資料", 26, C["ink"], 900),
           text(180, 383, "我們已帶入你的攤商資料，請確認後貼上 Google 地圖連結。", 15, C["muted"]),
           field_label(436, "store", C["accent"], "攤商名稱"), field(338, 413, 557, 47, p["name"]),
           field_label(507, "market", RED, "夜市／商圈"), field(338, 484, 557, 47, p["market"], chevron=True),
           field_label(577, "pin", C["primary"], "所在縣市"),
           field(338, 553, 273, 47, p["city"], chevron=True), field(626, 553, 269, 47, p["district"], chevron=True),
           link_field(link_variant),
           field_label(766, "user", C["primary"], "聯絡人姓名"),
           field(338, 743, 557, 47, placeholder="請輸入聯絡人姓名"),
           field_label(837, "phone", C["primary"], "聯絡電話"),
           field(338, 814, 557, 47, placeholder="請輸入聯絡電話（例如：0912-345-678）"),
           field_label(907, "note", C["ink"], "備註（選填）", required=False),
           rect(338, 882, 557, 82, 10, C["card"], "#D1D5DB"),
           text(354, 908, "有任何想補充的資訊都可以在這裡告訴我們～", 15, C["placeholder"]),
           text(354, 932, "（例如：營業時間、招牌餐點、其他說明等）", 15, C["placeholder"]),
           text(882, 953, "0 / 300", 13, C["muted"], 400, "end"),
           # 按鈕
           rect(228, 980, 280, 70, 30, C["card"], "#94A3B8", 1.5),
           icon("note", 290, 1003, 26, C["ink"]),
           text(334, 1011, "儲存草稿", 17, C["ink"], 700),
           text(334, 1033, "下次再繼續填寫", 13, C["muted"]),
           rect(526, 980, 290, 70, 30, C["primary"]),
           icon("send", 584, 1001, 28, "#fff"),
           text(636, 1010, "送出資料", 18, "#fff", 700),
           text(636, 1033, "送出後系統立即核對", 13, "#fff", 500, extra=' opacity="0.9"')]
    return "".join(out)


def steps_card(x=955, y=322, w=416):
    out = [rect(x, y, w, 335, 18, "#FFF8E6"),
           icon("bulb", x + 20, y + 16, 32, "#F2B200"),
           text(x + 71, y + 44, "簡單三步驟・完成攤商補登", 22, C["ink"], 900),
           line(x + 43, y + 120, x + 43, y + 255, "#CBD5E1", 2).replace("/>", ' stroke-dasharray="4 5"/>')]
    for i, (title, desc, ic, num_c, soft, ic_c) in enumerate(STEPS):
        cy = y + 98 + i * 90
        out += [rect(x + 80, cy - 37, w - 86, 74, 14, "#fff"),
                circle(x + 43, cy, 23, num_c, "#fff", 3),
                text(x + 43, cy + 7, str(i + 1), 20, "#fff", 700, "middle"),
                circle(x + 115, cy, 30, soft), icon(ic, x + 99, cy - 16, 32, ic_c, 2.4),
                text(x + 167, cy - 4, title, 19, C["ink"], 700),
                text(x + 167, cy + 22, desc, 14, C["body"])]
    return "".join(out)


def check_card(x=955, y=672, w=417):
    out = [rect(x, y, w, 233, 18, "#EEF8EE"),
           icon("shield", x + 18, y + 12, 36, "#22A06B", 2.2),
           text(x + 71, y + 40, "系統將自動核對", 21, C["ink"], 900),
           text(x + 22, y + 77, "為了確保資料正確性，我們會透過", 14, C["body"]),
           text(x + 22, y + 99, "Google 地圖進行下列項目檢查：", 14, C["body"]),
           image(x + 225, y + 56, 188, 177, "form-check-illustration.png")]
    for i, label in enumerate(CHECKS):
        yy = y + 130 + i * 30
        out += [circle(x + 38, yy - 5, 10, "#22A06B"), status_glyph("verified", x + 38, yy - 5, 0.7),
                text(x + 61, yy, label, 15, C["ink"], 500)]
    return "".join(out)


def thanks_card(x=955, y=920, w=417):
    return "".join([rect(x, y, w, 135, 18, "#FFF0F2"),
                    image(x + 10, y + 8, 175, 124, "form-mascot-cat-heart.png"),
                    text(x + 195, y + 37, "感謝你一起推廣", 19, "#8A2432", 900),
                    text(x + 195, y + 65, "台灣夜市的在地美味！", 19, "#8A2432", 900),
                    text(x + 192, y + 98, "通過核對後，攤位就會出現在", 13, C["body"]),
                    text(x + 192, y + 120, "台灣攤商地圖上，讓更多人找到你！", 13, C["body"])])


def side_panel():
    return (rect(938, 305, 450, 770, 22, "#fff", extra=' opacity="0.92" filter="url(#shadow)"')
            + steps_card() + check_card() + thanks_card())


def result_panel(key, x, y, w, h, mobile=False):
    """送出後的核對結果，桌機放在表單卡位置，手機為整頁。"""
    r = RESULTS[key]
    st = S[r["status"]]
    cx = x + w / 2
    pad = 20 if mobile else 64
    out = [card(x, y, w, h, 22),
           circle(cx, y + 80, 52, st["soft"]), circle(cx, y + 80, 38, st["main"]),
           status_glyph(r["status"], cx, y + 80, 2.6),
           text(cx, y + 168, r["title"], 24 if mobile else 28, C["ink"], 900, "middle")]
    desc = r["desc"]
    if mobile and tw(desc, 14) > w - 40:  # 手機版說明拆兩行
        cut = desc.index("，") + 1
        out += [text(cx, y + 198, desc[:cut], 14, C["body"], 400, "middle"),
                text(cx, y + 220, desc[cut:], 14, C["body"], 400, "middle")]
        yy = y + 246
    else:
        out.append(text(cx, y + 204, desc, 15, C["body"], 400, "middle"))
        yy = y + 236
    # 攤商摘要
    out += [rect(x + pad, yy, w - 2 * pad, 64, 14, C["field"]),
            circle(x + pad + 32, yy + 32, 20, "#fff"), icon("store", x + pad + 21, yy + 21, 22, C["accent"]),
            text(x + pad + 64, yy + 28, PREFILL["name"], 16, C["ink"], 700),
            text(x + pad + 64, yy + 50, f'{PREFILL["market"]}・{PREFILL["city"]}{PREFILL["district"]}', 13, C["muted"])]
    if not mobile:
        link = "maps.app.goo.gl/AbC123" if key != "invalid" else "goo.gl/xxxx（無法辨識）"
        out += [icon("link", x + w - pad - 250, yy + 23, 18, C["primary"]),
                text(x + w - pad - 226, yy + 38, link, 14, C["primary"] if key != "invalid" else RED, 700)]
    yy += 92
    out.append(text(x + pad, yy, "核對項目", 15, C["muted"], 700))
    yy += 16
    row_h = 44 if mobile else 46
    for state, label, note in r["items"]:
        color = {"ok": S["verified"]["main"], "fail": S[r["status"]]["main"] if key == "invalid" else S["incomplete"]["main"],
                 "wait": S["not_submitted"]["main"]}[state]
        glyph = {"ok": "verified", "fail": "not_found" if key == "invalid" else "incomplete", "wait": "not_submitted"}[state]
        bg = {"ok": "#fff", "fail": S["incomplete"]["soft"] if key != "invalid" else S["not_found"]["soft"],
              "wait": "#fff"}[state]
        out += [rect(x + pad, yy, w - 2 * pad, row_h - 6, 10, bg, C["line_soft"]),
                circle(x + pad + 22, yy + (row_h - 6) / 2, 11, color),
                status_glyph(glyph, x + pad + 22, yy + (row_h - 6) / 2, 0.75),
                text(x + pad + 44, yy + (row_h - 6) / 2 + 5, label, 15, C["ink"], 700 if state == "fail" else 500)]
        if note:
            out.append(text(x + w - pad - 14, yy + (row_h - 6) / 2 + 5, note, 13, C["muted"], 400, "end"))
        yy += row_h
    if r.get("howto"):
        yy += 6
        out.append(rect(x + pad, yy, w - 2 * pad, 26 + 22 * len(r["howto"]), 12, "#EAF4FF"))
        for i, ln in enumerate(r["howto"]):
            out.append(text(x + pad + 16, yy + 28 + i * 22, ln, 14, C["ink"] if i else C["primary"], 700 if not i else 400))
        yy += 26 + 22 * len(r["howto"])
    # 按鈕
    by = y + h - (150 if mobile else 110)
    (b1, i1), (b2, i2) = r["buttons"]
    if mobile:
        boxes = [(x + pad, by, w - 2 * pad, 52), (x + pad, by + 62, w - 2 * pad, 48)]
    else:
        bw = (w - 2 * pad - 16) / 2
        boxes = [(x + pad, by, bw, 54), (x + pad + bw + 16, by, bw, 54)]
    for i, ((bx, byy, bw_, bh), label, ic) in enumerate(zip(boxes, (b1, b2), (i1, i2))):
        primary = i == 0
        out.append(rect(bx, byy, bw_, bh, 14, C["primary"] if primary else C["card"], None if primary else "#94A3B8", 1.5))
        tx = bx + bw_ / 2 - (tw(label, 16) + 28) / 2
        color = "#fff" if primary else C["ink"]
        out.append(icon(ic, tx, byy + bh / 2 - 10, 20, color))
        out.append(text(tx + 28, byy + bh / 2 + 6, label, 16, color, 700))
    if r["foot"]:
        out.append(text(cx, y + h - (16 if mobile else 26), r["foot"], 12.5 if mobile else 13.5, C["muted"], 400, "middle"))
    return "".join(out)


# ---- 手機版 ----

def m_header():
    return "".join([rect(0, 0, M_W, 64, 0, C["card"]), line(0, 64, M_W, 64, "#C9E9F6", 2),
                    image(10, 8, 56, 48, "form-logo-stall.png"),
                    text(72, 36, "攤商管理平台", 21, C["brand"], 900, extra=' letter-spacing="1"'),
                    text(73, 54, "一起把在地美味分享給更多人！", 10.5, "#5B4636", 700),
                    rect(336, 13, 40, 40, 10, C["card"], "#CBD5E1", 1.5),
                    icon("menu", 345, 22, 22, C["ink"])])


def m_hero():
    return image(0, 64, M_W, 144, "form-hero-mobile.png")


def m_steps(y=220):
    out = [rect(16, y, 358, 84, 16, "#FFF8E6")]
    for i, (title, _desc, ic, num_c, soft, ic_c) in enumerate(STEPS):
        cx = 16 + 358 / 6 * (2 * i + 1)
        if i:
            out.append(line(cx - 119 + 22, y + 30, cx - 22, y + 30, "#CBD5E1", 2).replace("/>", ' stroke-dasharray="3 4"/>'))
        out += [circle(cx, y + 30, 17, num_c, "#fff", 2.5),
                text(cx, y + 36, str(i + 1), 16, "#fff", 700, "middle"),
                text(cx, y + 68, {"系統自動檢查": "自動檢查"}.get(title, title), 14, C["ink"], 700, "middle")]
    return "".join(out)


def m_label(y, label, required=True):
    out = [text(32, y, label, 14.5, C["ink"], 700)]
    if required:
        out.append(text(36 + tw(label, 14.5), y, "*", 14.5, RED, 700))
    return "".join(out)


def m_form(y=318):
    p = PREFILL
    out = [card(16, y, 358, 900, 18),
           text(32, y + 38, "填寫攤商資料", 20, C["ink"], 900),
           text(32, y + 62, "已帶入你的攤商資料，請確認後貼上連結。", 12.5, C["muted"]),
           m_label(y + 98, "攤商名稱"), field(32, y + 108, 326, 44, p["name"]),
           m_label(y + 178, "夜市／商圈"), field(32, y + 188, 326, 44, p["market"], chevron=True),
           m_label(y + 258, "所在縣市"),
           field(32, y + 268, 159, 44, p["city"], chevron=True), field(199, y + 268, 159, 44, p["district"], chevron=True),
           rect(24, y + 326, 342, 132, 14, "#EAF4FF"),
           m_label(y + 352, "Google 地圖商家連結"),
           icon("help", 200, y + 338, 18, C["muted"]),
           rect(32, y + 364, 326, 80, 12, C["card"], "#BFD7F5", 1.5),
           gpin(58, y + 398, 0.9),
           text(80, y + 398, "請貼上 Google 地圖商家連結", 14, C["placeholder"]),
           text(80, y + 421, "（例如：https://maps.app.goo.gl/…）", 12.5, C["placeholder"]),
           m_label(y + 490, "聯絡人姓名"), field(32, y + 500, 326, 44, placeholder="請輸入聯絡人姓名"),
           m_label(y + 570, "聯絡電話"), field(32, y + 580, 326, 44, placeholder="例如：0912-345-678"),
           m_label(y + 650, "備註（選填）", required=False),
           rect(32, y + 660, 326, 84, 10, C["card"], "#D1D5DB"),
           text(46, y + 686, "有任何想補充的資訊都可以告訴我們～", 14, C["placeholder"]),
           text(346, y + 734, "0 / 300", 12, C["muted"], 400, "end"),
           rect(32, y + 768, 326, 56, 14, C["primary"]),
           icon("send", 120, y + 784, 24, "#fff"),
           text(154, y + 803, "送出資料", 17, "#fff", 700),
           text(230, y + 803, "立即核對", 12.5, "#fff", 500, extra=' opacity="0.85"'),
           rect(32, y + 834, 326, 48, 14, C["card"], "#94A3B8", 1.5),
           icon("note", 140, y + 846, 22, C["ink"]),
           text(170, y + 864, "儲存草稿", 16, C["ink"], 700)]
    return "".join(out)


def m_check(y=1232):
    out = [rect(16, y, 358, 168, 16, "#EEF8EE"),
           icon("shield", 30, y + 14, 30, "#22A06B", 2.2),
           text(70, y + 38, "系統將自動核對", 18, C["ink"], 900),
           text(32, y + 66, "我們會透過 Google 地圖檢查以下項目：", 13, C["body"]),
           image(262, y + 60, 108, 102, "form-check-illustration.png")]
    for i, label in enumerate(CHECKS):
        yy = y + 98 + i * 26
        out += [circle(42, yy - 5, 9, "#22A06B"), status_glyph("verified", 42, yy - 5, 0.62),
                text(60, yy, label, 14, C["ink"], 500)]
    return "".join(out)


def main():
    pre = "components/merchant-"
    write(pre + "form-header.svg", svg((0, 0, W, 90), header(), "攤商補登頁首"))
    write(pre + "form-card.svg", svg((70, 293, 870, 793), form_card(), "攤商資料表單", C["page"]))
    write(pre + "form-link-candidate.svg",
          svg((90, 610, 830, 120), link_field("candidate"), "地圖連結欄：Agent 候選地點", "#fff"))
    write(pre + "form-side-panel.svg", svg((926, 293, 474, 793), side_panel(), "補登說明側欄", C["page"]))
    for key, label in [("verified", "通過"), ("incomplete", "缺項"), ("invalid", "連結無效")]:
        write(f"{pre}result-{key}.svg",
              svg((70, 293, 870, 793), result_panel(key, 82, 305, 846, 770), f"核對結果：{label}", C["page"]))

    bg = image(0, 88, W, 998, "form-bg.png")
    write("pages/merchant-form-desktop.svg",
          svg((0, 0, W, H), bg + header() + form_card() + side_panel(), "攤商資料補登（桌機版）"))
    write("pages/merchant-result-desktop.svg",
          svg((0, 0, W, H), bg + header() + result_panel("incomplete", 82, 305, 846, 770) + side_panel(),
              "攤商資料補登：核對結果（桌機版）"))

    body = (rect(0, 0, M_W, 1420, 0, C["page"]) + m_header() + m_hero() + m_steps() + m_form() + m_check())
    write("pages/merchant-form-mobile.svg", svg((0, 0, M_W, 1420), body, "攤商資料補登（手機版）"))
    for key in RESULTS:
        body = rect(0, 0, M_W, 844, 0, C["page"]) + m_header() + result_panel(key, 16, 80, 358, 748, mobile=True)
        write(f"pages/merchant-result-{key}-mobile.svg", svg((0, 0, M_W, 844), body, f"核對結果（手機版）：{key}"))


if __name__ == "__main__":
    main()
    print("\n".join(str(p.relative_to(ROOT)) for p in sorted(OUT.rglob("merchant-*.svg"))))
