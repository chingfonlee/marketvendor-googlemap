"""產生攤商登入頁的 SVG，桌機座標以 merchant-login-mockup.png（1536x1024）為準。

依審查報告（design/REVIEW.md）的建議，這組 SVG 一開始就加上網頁開發用的結構：
- 每個組件包在 <g id="login-..."> 裡
- 欄位、按鈕、狀態用 data-* 標記（data-field、data-state、data-action）
- 自訂的 id 一律加 login- 前綴，避免跟其他 SVG 衝突
執行：python design/tools/build_login_svg.py
"""
from build_svg import C, ICONS, circle, f, icon, image, line, rect, svg, text, tw, write, ROOT, OUT

ICONS.update({
    "lock": ["r:5,10,14,11,2", "M8 10V7a4 4 0 0 1 8 0v3", "M12 14.5v2.5"],
    "eye-off": ["M3 3l18 18", "M10.6 6.1A9.6 9.6 0 0 1 12 6c5 0 8.5 4.5 9.5 6-.5.8-1.6 2.2-3.1 3.5",
                "M6.3 7.6C4.5 8.9 3.1 10.8 2.5 12c1 1.5 4.5 6 9.5 6 1.4 0 2.7-.3 3.9-.9", "M9.9 10a3 3 0 0 0 4.2 4.1"],
    "login": ["M14 4h4a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-4", "M10 16l4-4-4-4", "M14 12H4"],
    "help": ["c:12,12,9", "M9.5 9.5a2.5 2.5 0 1 1 3.5 2.3c-.6.3-1 .8-1 1.5v.7", "M12 17h.01"],
})

W, H = 1536, 1024
M_W, M_H = 390, 844
CARD_BG = "#FDFCF9"   # 取自設計圖卡片底色
BROWN = "#4A2E1C"
SUB = "#5B4636"
FIELD_LINE = "#E4DED4"
RED = "#E5484D"
NAMES = [("香香超大烤雞排", "花園夜市"), ("阿明地瓜球", "花園夜市"), ("古早味豆花", "大東夜市"),
         ("阿婆蚵仔煎", "武聖夜市"), ("黑糖珍珠鮮奶", "花園夜市")]


def g(gid, body, **data):
    attrs = "".join(f' data-{k.replace("_", "-")}="{v}"' for k, v in data.items())
    return f'<g id="{gid}"{attrs}>{body}</g>' if gid else f"<g{attrs}>{body}</g>"


def pill_field(name, x, y, w, h, ic, label, placeholder=True, trailing=None, state="default", value=None):
    stroke = {"default": FIELD_LINE, "error": RED, "focus": C["primary"]}[state]
    sw = 1.5 if state == "default" else 2
    body = [rect(x, y, w, h, h / 2, "#fff", stroke, sw),
            icon(ic, x + 32, y + h / 2 - 13, 26, "#3F3A36", 2.2),
            text(x + 85, y + h / 2 + 7.5, value or label, 21,
                 C["ink"] if value else ("#8A8580" if placeholder else "#3F3A36"), 500)]
    if trailing == "chevron":
        body.append(icon("chevron-down", x + w - 54, y + h / 2 - 12, 24, "#3F3A36", 2.4))
    elif trailing == "eye":
        body.append(icon("eye-off", x + w - 64, y + h / 2 - 15, 30, "#3F3A36", 2))
    return g(None, "".join(body), field=name, state=state)


def desktop_card(state="default"):
    """state：default／error（密碼錯誤）／select-open（攤商名稱下拉展開）"""
    # 卡片：上緣避開看板與攤車插畫，只蓋住表單區
    out = [f'<path d="M418 376H604V342H1118V940a40 40 0 0 1-40 40H458a40 40 0 0 1-40-40z" fill="{CARD_BG}"/>',
           text(773, 412, "攤商登入", 50, BROWN, 900, "middle", ' letter-spacing="4"'),
           f'<path d="M908 372l6-10M920 380l12-6M920 394l12 2" stroke="#F2B200" stroke-width="4" stroke-linecap="round"/>',
           text(768, 450, "請選擇你的縣市、攤商名稱並輸入密碼，", 21, SUB, 500, "middle"),
           text(768, 485, "進入專屬頁面填寫 Google 地圖資料。", 21, SUB, 500, "middle")]
    county = "台南市" if state != "default" else None
    name = "香香超大烤雞排" if state == "error" else None
    out.append(pill_field("county", 471, 517, 594, 70, "pin", "選擇縣市", trailing="chevron", value=county))
    out.append(pill_field("merchant", 471, 603, 594, 70, "store", "選擇攤商名稱", trailing="chevron",
                          state="focus" if state == "select-open" else "default", value=name))
    pw_state = "error" if state == "error" else "default"
    out.append(pill_field("password", 471, 690, 594, 70, "lock", "••••••" if state == "error" else "請輸入密碼",
                          placeholder=state != "error", trailing="eye", state=pw_state))
    dy = 0
    if state == "error":
        out.append(g("login-error", circle(492, 782, 9, RED) + text(492, 787, "!", 13, "#fff", 900, "middle")
                     + text(510, 788, "密碼錯誤，請再試一次。連續錯誤 5 次將暫停登入 15 分鐘。", 15, RED, 500),
                     role="alert"))
        dy = 26
    out.append(g("login-submit", rect(471, 784 + dy, 594, 76, 38, C["primary"])
                 + icon("login", 712, 806 + dy, 32, "#fff", 2.4)
                 + text(796, 834 + dy, "登入", 24, "#fff", 700, "middle", ' letter-spacing="8"'), action="login"))
    out.append(line(471, 893 + dy, 1065, 893 + dy, "#ECE7DF", 1.5))
    out.append(g("login-help", icon("help", 581, 920 + min(dy, 14), 26, "#8A8580", 2)
                 + text(622, 940 + min(dy, 14), "忘記密碼？請聯絡主辦單位協助重設", 19, C["primary"], 700),
                 action="forgot-password"))
    if state == "select-open":
        out.append(name_dropdown(471, 680, 594))
    return g("login-card", "".join(out), state=state)


def name_dropdown(x, y, w, size=1.0):
    """攤商名稱下拉：先選縣市，再從該縣市的攤商中搜尋。"""
    item_h = 48 * size
    h = 64 * size + item_h * len(NAMES) + 8
    out = [rect(x, y, w, h, 18, "#fff", FIELD_LINE, 1.5, ' filter="url(#shadow)"'),
           rect(x + 12, y + 12, w - 24, 44 * size, 12, C["field"]),
           icon("search", x + 26, y + 12 + 22 * size - 10, 20, C["muted"]),
           text(x + 56, y + 12 + 22 * size + 5.5, "搜尋攤商名稱", 16 * size, C["placeholder"])]
    for i, (name, market) in enumerate(NAMES):
        iy = y + 64 * size + i * item_h
        hl = i == 0
        item = []
        if hl:
            item.append(rect(x + 8, iy, w - 16, item_h, 10, C["primary_soft"]))
        item.append(text(x + 28, iy + item_h / 2 + 6, name, 18 * size, C["primary"] if hl else C["ink"], 700 if hl else 500))
        item.append(text(x + w - 28, iy + item_h / 2 + 5, market, 14 * size, C["muted"], 400, "end"))
        out.append(g(None, "".join(item), option=name))
    return g("login-merchant-options", "".join(out), role="listbox")


def mobile_page(state="default"):
    out = [rect(0, 0, M_W, M_H, 0, "#F6E3C7"),
           # 手機版沿用桌機背景，縮小一半並取中間攤車區域；標題改用向量
           g("login-hero", image(-220, -24, 768, 512, "login-bg.png")
             + rect(8, 10, 168, 48, 24, "#fff", extra=' opacity="0.95"')
             + icon("pin", 24, 23, 22, RED, 2.2)
             + text(54, 41, "攤商專區", 18, BROWN, 900, extra=' letter-spacing="2"'))]
    card = [rect(16, 216, 358, 660, 28, CARD_BG, extra=' filter="url(#shadow)"'),
            text(195, 268, "攤商登入", 34, BROWN, 900, "middle", ' letter-spacing="3"'),
            text(195, 300, "請選擇縣市、攤商名稱並輸入密碼，", 15, SUB, 500, "middle"),
            text(195, 324, "進入專屬頁面填寫 Google 地圖資料。", 15, SUB, 500, "middle")]
    for i, (name, ic, label, trailing) in enumerate([("county", "pin", "選擇縣市", "chevron"),
                                                     ("merchant", "store", "選擇攤商名稱", "chevron"),
                                                     ("password", "lock", "請輸入密碼", "eye")]):
        y = 350 + i * 72
        body = [rect(32, y, 326, 58, 29, "#fff", FIELD_LINE, 1.5),
                icon(ic, 52, y + 18, 22, "#3F3A36", 2.2),
                text(88, y + 35, label, 17, "#8A8580", 500)]
        if trailing == "chevron":
            body.append(icon("chevron-down", 316, y + 19, 20, "#3F3A36", 2.4))
        else:
            body.append(icon("eye-off", 312, y + 16, 26, "#3F3A36", 2))
        card.append(g(None, "".join(body), field=name, state="default"))
    card += [g("login-submit", rect(32, 574, 326, 62, 31, C["primary"]) + icon("login", 150, 591, 26, "#fff", 2.4)
               + text(214, 614, "登入", 21, "#fff", 700, "middle", ' letter-spacing="6"'), action="login"),
             line(32, 664, 358, 664, "#ECE7DF", 1.5),
             g("login-help", icon("help", 54, 688, 22, "#8A8580", 2)
               + text(84, 705, "忘記密碼？請聯絡主辦單位協助重設", 15, C["primary"], 700), action="forgot-password"),
             text(195, 760, "完成後就能在 Google 地圖被找到喔！", 14, SUB, 500, "middle")]
    # 卡片上移，蓋住背景圖裡原本的標題
    out.append(g("login-card", "".join(card), state=state).replace(
        '<g id="login-card"', '<g id="login-card" transform="translate(0 -62)"', 1))
    return "".join(out)


def main():
    bg = g("login-bg", image(0, 0, W, H, "login-bg.png"))
    for state, label in [("default", "預設"), ("error", "密碼錯誤"), ("select-open", "攤商名稱下拉展開")]:
        write(f"components/login-card-{state}.svg",
              svg((400, 330, 736, 670), image(0, 0, W, H, "login-bg.png") + desktop_card(state), f"攤商登入卡片：{label}"))
    write("pages/merchant-login-desktop.svg", svg((0, 0, W, H), bg + desktop_card(), "攤商登入（桌機版）"))
    write("pages/merchant-login-mobile.svg", svg((0, 0, M_W, M_H), mobile_page(), "攤商登入（手機版）"))


if __name__ == "__main__":
    main()
    print("\n".join(str(p.relative_to(ROOT)) for p in sorted(OUT.rglob("*login*.svg"))))
