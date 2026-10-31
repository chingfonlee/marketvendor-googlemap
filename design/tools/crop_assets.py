"""從設計圖裁切插畫素材到 design/assets。正式插畫到位後，直接覆蓋同名檔案即可。"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "reference" / "mockup.webp"
OUT = ROOT / "assets"

# (檔名, 左, 上, 右, 下) — 座標以 1536x1024 的設計圖為準
CROPS = [
    ("logo-stall.png", 16, 8, 102, 86),
    ("mascot-chef.png", 256, 110, 426, 220),
    ("mascot-cat-map.png", 440, 266, 614, 394),
    ("mascot-cat-wave.png", 1404, 900, 1524, 1018),
    ("map-taiwan.png", 456, 96, 1183, 1022),
    ("map-corner.png", 1183, 825, 1530, 1022),  # 地圖右下角：鯨魚、貓咪、對話框底圖
    ("stall-photo-sample.png", 1198, 132, 1508, 332),
    ("minimap-sample.png", 1199, 428, 1508, 530),
]
FOOD_ROWS = [648, 686, 724, 763, 802, 841, 880, 918]

# 管理版設計圖（admin-mockup.webp）
ADMIN_SRC = ROOT / "reference" / "admin-mockup.webp"
ADMIN_CROPS = [
    ("admin-logo-stall.png", 18, 10, 104, 84),
    ("admin-mascot-cat-map.png", 385, 188, 530, 312),
    ("admin-map.png", 493, 88, 1138, 1016),
    ("admin-map-corner.png", 1138, 915, 1536, 1016),  # 地圖右下角：貓咪與對話框底圖
    ("admin-stall-photo-sample.png", 1152, 110, 1514, 345),
]

# 攤商補登頁設計圖（merchant-form-mockup.png，1448x1086）
FORM_SRC = ROOT / "reference" / "merchant-form-mockup.png"
FORM_CROPS = [
    ("form-logo-stall.png", 50, 8, 138, 84),
    ("form-bg.png", 0, 88, 1448, 1086),  # 頁首以下整張背景（含主視覺），表單卡片以向量蓋在上面
    ("form-hero-mobile.png", 425, 92, 1000, 305),  # 手機版主視覺：標題區
    ("form-check-illustration.png", 1180, 728, 1368, 905),
    ("form-mascot-cat-heart.png", 965, 928, 1140, 1052),
]

# 攤商登入頁設計圖（merchant-login-mockup.png，1536x1024）
LOGIN_SRC = ROOT / "reference" / "merchant-login-mockup.png"
LOGIN_CROPS = [
    ("login-bg.png", 0, 0, 1536, 1024),  # 整張背景（含標題雲、看板、對話框），登入表單以向量蓋在上面
    ("login-hero-mobile.png", 620, 50, 960, 335),  # 手機版主視覺：攤車女孩
    ("login-title-cloud.png", 0, 20, 560, 215),  # 「攤商專區」標題雲
]


def main():
    im = Image.open(SRC).convert("RGB")
    for name, *box in CROPS:
        im.crop(box).save(OUT / name)
    for i, y in enumerate(FOOD_ROWS, 1):
        im.crop((32, y - 16, 66, y + 16)).save(OUT / "food" / f"food-{i:02d}.png")
    im = Image.open(ADMIN_SRC).convert("RGB")
    for name, *box in ADMIN_CROPS:
        im.crop(box).save(OUT / name)
    im = Image.open(FORM_SRC).convert("RGB")
    for name, *box in FORM_CROPS:
        im.crop(box).save(OUT / name)
    im = Image.open(LOGIN_SRC).convert("RGB")
    for name, *box in LOGIN_CROPS:
        im.crop(box).save(OUT / name)


if __name__ == "__main__":
    main()
