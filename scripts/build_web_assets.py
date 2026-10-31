"""把設計素材轉成網頁用的檔案，輸出到 web/assets/。

- 底圖 PNG → map-base.webp（2048×3072），manifest.json 記下來源 PNG 的 SHA-256，
  網頁拿它和 county-labels.json 的 basemap_sha256 比對（docs/LAYER_ARCHITECTURE.md §4）。
- 吉祥物、Logo、空狀態 → 縮小的 webp。
- 市場類型縮圖：讀 design/assets/generated/market-type-*.png（不進 git），沒有就跳過。
- design/svg/atoms/icons.svg 的 25 個圖示 → icons.svg sprite，再加上縣市標籤的攤車圖示。

同樣的來源重跑，輸出相同。
"""
import hashlib
import json
import re
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
FINAL = ROOT / "design" / "assets" / "final"
GENERATED = ROOT / "design" / "assets" / "generated"
OUT = ROOT / "web" / "assets"

# (來源, 輸出, 最長邊 px)；吉祥物以 2 倍顯示尺寸輸出
IMAGES = [
    (FINAL / "logo-stall.png", "logo.webp", 128),
    (FINAL / "mascot-cat-map.png", "mascots/cat-camera.webp", 360),
    (FINAL / "mascot-cat-megaphone.png", "mascots/cat-megaphone.webp", 320),
    (FINAL / "mascot-girl-vendor.png", "mascots/girl.webp", 320),
    (FINAL / "empty-state.png", "empty-state.webp", 320),
]
MARKET_TYPES = {
    "night_market": "market-type-night-market.png",
    "traditional_market": "market-type-traditional-market.png",
    "other": "market-type-other.png",
}

# 攤車：粉白條紋遮雨棚（docs/COUNTY_LABELS.md §1），填色版，不吃 currentColor
CART = """<symbol id="cart" viewBox="0 0 24 24">
<path d="M3 9h18v9a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1z" fill="#FFF6E8"/>
<path d="M2 4h20l-1 5H3z" fill="#fff"/>
<path d="M5.3 4h3.4l-.6 5H4.6zM12 4h3.4l.4 5h-3.5zM18.7 4H22l-1 5h-2.6z" fill="#FF8FA3"/>
<path d="M2 4h20l-1 5H3zM3 9v9a1 1 0 0 0 1 1h16a1 1 0 0 0 1-1V9M7 13h10" fill="none" stroke="#7A3B12" stroke-width="1.4" stroke-linejoin="round"/>
<circle cx="7" cy="20.5" r="1.6" fill="#7A3B12"/><circle cx="17" cy="20.5" r="1.6" fill="#7A3B12"/>
</symbol>"""


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_webp(src, dest, longest, quality=86):
    im = Image.open(src)
    im = im.convert("RGBA" if im.mode in ("RGBA", "LA", "P") else "RGB")
    im.thumbnail((longest, longest), Image.LANCZOS)
    dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest, "WEBP", quality=quality, method=6)
    return list(im.size)


def build_icons():
    src = (ROOT / "design" / "svg" / "atoms" / "icons.svg").read_text(encoding="utf-8", errors="replace")
    pairs = re.findall(r'<g transform="[^"]*"([^>]*)>(.*?)</g><text[^>]*>([a-z-]+)</text>', src)
    symbols = []
    for attrs, body, name in pairs:
        attrs = attrs.replace('stroke="#2B2118"', 'stroke="currentColor"')
        symbols.append(f'<symbol id="{name}" viewBox="0 0 24 24"><g{attrs}>{body}</g></symbol>')
    symbols.append(CART)
    svg = '<svg xmlns="http://www.w3.org/2000/svg">\n' + "\n".join(symbols) + "\n</svg>\n"
    (OUT / "icons.svg").write_text(svg, encoding="utf-8", newline="\n")
    return [name for _, _, name in pairs] + ["cart"]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    base = FINAL / "map-taiwan-base.png"
    manifest = {
        "basemap": "map-base.webp",
        "basemap_source": base.name,
        "basemap_source_sha256": sha256(base),
        "basemap_size": save_webp(base, OUT / "map-base.webp", 3072, quality=82),
        "images": {},
        "market_types": {},
    }
    for src, name, longest in IMAGES:
        manifest["images"][name] = save_webp(src, OUT / name, longest)
    for key, name in MARKET_TYPES.items():
        src = GENERATED / name
        if src.exists():
            save_webp(src, OUT / "market-type" / f"{key}.webp", 256)
            manifest["market_types"][key] = f"market-type/{key}.webp"
    manifest["icons"] = build_icons()
    (OUT / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
