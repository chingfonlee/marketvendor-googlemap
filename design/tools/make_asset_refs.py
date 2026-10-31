"""產生給繪圖 Agent 的素材需求包：design/asset-briefs/
- manifest.json：每項素材的規格（任務類型、輸出尺寸、保留/移除/替換、提示詞、驗收標準）
- refs/<id>-source.png：參考原圖（原始解析度）
- refs/<id>-annotated.png：標註圖（紅＝移除、綠＝保留、橘＝替換、藍＝介面區留白）
- refs/<id>-context.png：在整張設計圖中的位置（藍框）
主題：台灣「市場」——傳統市場為主，夜市為其中一種。
執行：python design/tools/make_asset_refs.py
"""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "asset-briefs"
FONT = "C:/Windows/Fonts/msjhbd.ttc"

MOCKUPS = {
    "front": "reference/mockup.webp",
    "admin": "reference/admin-mockup.webp",
    "form": "reference/merchant-form-mockup.png",
    "login": "reference/merchant-login-mockup.png",
    "map2": "reference/map-v2/map-taiwan-clean.png",
}

# 所有提示詞共用的風格與負面提示詞
STYLE = ("cute chibi Taiwanese local market illustration, thick dark-brown outlines (#3B2A1A), "
         "flat colors with soft cel shading, warm friendly palette (orange #F08A3C, lantern red #E5484D, "
         "cream #FFF8E6, grass green #7CC46A, sea blue #6DD7F2), rounded shapes, clean crisp line art")
# 文字規則：
#   fixed：固定使用、不會變動的素材，可以畫手寫字，但只能出現 allowed_text 列出的文字
#   none ：會重複使用、或旁邊要放動態內容的素材，不能有任何文字（文字由網頁產生）
_NEG_COMMON = ("logo, brand, watermark, signature, UI elements, buttons, map pins, markers, "
               "photorealistic, 3D render, glossy gradients, blurry, noisy, extra fingers")
NEGATIVE = {
    "none": "text, letters, words, Chinese characters, numbers, speech bubbles, " + _NEG_COMMON,
    "fixed": ("any text other than the exact phrases given, random or gibberish characters, "
              "misspelled characters, simplified Chinese, English words, " + _NEG_COMMON),
}
CAT = ("the same calico cat mascot: white fur, orange patch on the viewer-left ear and top-left of the head, "
       "dark grey-black patch on the viewer-right ear, pink blush cheeks, round friendly eyes")
TRANSPARENT = "isolated on a fully transparent background, no ground shadow, centered with small padding"

# 任務類型：inpaint（以參考圖為底局部修改，構圖不變）／extract（角色抽出到透明背景）／new（依參考重新畫）
ASSETS = [
    {
        "id": "A01", "file": "map-taiwan-market.png", "priority": "P0", "task": "inpaint",
        "title": "手繪台灣地圖底圖（市場主題）",
        "source": "map2", "crop": [0, 0, 1122, 1402],
        "output": {"width": 2244, "height": 2804, "background": "不透明（保留海洋）"},
        "keep": ["島嶼輪廓、海岸線、離島、海洋、船、鯨魚、海豚、海鷗、雲（位置完全不動）",
                 "台北 101、摩天輪、燈塔、山、湖、樹木、道路"],
        "remove": ["無（這張已經沒有文字與圖釘）"],
        "replace": ["橘框 3 處掛燈籠的夜市牌樓 → 改成傳統市場建築：有遮雨棚的公有市場、攤位擺滿蔬果與竹籃",
                    "另外 2 處夜市牌樓保留，但加上幾個小吃攤車，代表夜市"],
        "notes": ["以 map-v2/map-taiwan-clean.png 為底局部修改，等比例放大 2 倍。",
                  "海岸線與所有建築的位置不能移動：之後會在這張圖上標出每個市場的像素座標。",
                  "替換後的建築大小與原本的牌樓相同，不要佔用更多陸地。"],
        "accept": ["尺寸剛好 2244×2804", "縮小 50% 後與 source 疊圖，海岸線偏差不超過 2px",
                   "能看出 3 處傳統市場、2 處夜市", "沒有任何文字、圖釘、招牌字"],
        "boxes": "map2",
        "prompt": ("Edit this hand-drawn map of Taiwan. Keep the coastline, islands, sea, boats, animals, clouds, "
                   "Taipei 101, ferris wheel, lighthouses, mountains and trees exactly in place. Inside the three orange "
                   "boxes, replace the lantern night-market gates with traditional Taiwanese wet-market halls: "
                   "corrugated awning roofs, open stalls with baskets of vegetables, fruit and fish. Inside the two "
                   "other gates, keep the night-market gate and add two tiny snack carts. Same size as the original "
                   f"buildings. {STYLE}. Upscale 2x."),
    },
    {
        "id": "A03", "file": "bg-login.png", "priority": "P1", "task": "new",
        "title": "攤商登入頁背景（桌機，市場主題）",
        "source": "login", "crop": [0, 0, 1536, 1024],
        "output": {"width": 3072, "height": 2048, "background": "不透明"},
        "text": "fixed",
        "allowed_text": ["新鮮蔬果（左側攤位招牌）", "珍珠奶茶（右側攤位招牌）",
                         "一起讓更多人找到我們！（木製看板，放在上方攤車左邊）",
                         "完成後就能在 Google 地圖被找到喔！（右下角對話框，在貓咪旁邊）"],
        "keep": ["構圖照參考圖：左右兩側各一位攤商與攤位，上方中間一座小攤車，中間大片留白"],
        "remove": ["參考圖左上的「攤商專區」標題雲（改由 A07 疊上去）", "右上含 Google 地圖圖示的對話框", "中間的登入卡片"],
        "replace": ["左側：傳統市場的蔬果攤，攤商阿伯拿著一把青菜", "右側：夜市小吃攤，攤商拿著珍珠奶茶",
                    "背景：傍晚的市場街，遮雨棚、竹籃、紅燈籠剛點亮，遠處有更多攤位"],
        "notes": ["這張只用在桌機登入頁、不會變動，所以招牌和對話框可以畫手寫字，但只能用 allowed_text 的文字。",
                  "藍框是登入表單的位置（約 700×650），畫柔和、低細節的街道地面，不要放角色、文字或醒目物件。",
                  "左上角留空，網頁會在那裡疊上 A07 雲朵標題。"],
        "accept": ["尺寸剛好 3072×2048", "藍框範圍內沒有文字與重點物件", "圖上的文字與 allowed_text 完全一致、沒有錯字",
                   "畫面中同時看得出傳統市場與夜市"],
        "boxes": "login_layout",
        "prompt": ("Wide 3:2 background illustration of a Taiwanese local market street at golden hour. "
                   "Left side: a friendly elderly vegetable vendor at a traditional market stall with bamboo baskets "
                   "of greens and fruit under a striped awning, its signboard hand-lettered \"新鮮蔬果\". Right side: a "
                   "cheerful young night-market vendor holding a bubble tea, stall signboard hand-lettered \"珍珠奶茶\", "
                   "warm lanterns just lighting up. Top center: a small striped-awning cart with a wooden board beside it "
                   "hand-lettered \"一起讓更多人找到我們！\". Bottom right: a calico cat next to a speech bubble "
                   "hand-lettered \"完成後就能在 Google 地圖被找到喔！\". Keep the top-left corner as open sky. The center "
                   "of the image is an open, softly lit market street floor with low detail and no text, left empty for "
                   f"a login form. Traditional Chinese hand lettering, exactly these phrases and nothing else. {STYLE}."),
    },
    {
        "id": "A04", "file": "bg-login-mobile.png", "priority": "P1", "task": "new",
        "title": "攤商登入頁背景（手機直式，市場主題）",
        "source": "login", "crop": [380, 0, 1160, 960],
        "output": {"width": 780, "height": 960, "background": "不透明"},
        "text": "none",
        "keep": ["上方 1/3：一座市場小攤車與攤商，水平置中", "燈籠串與暖色天空"],
        "remove": ["任何文字、對話框、看板、卡片"],
        "replace": [],
        "notes": ["下方 2/3 會被登入卡片蓋住，畫簡單的市場地面即可。", "攤車與攤商要跟 A16 是同一組角色。",
                  "手機畫面小，標題由網頁疊上 A07，所以背景不放文字。"],
        "accept": ["尺寸剛好 780×960", "攤商完整出現在上方 0～320px 內", "沒有任何文字"],
        "prompt": ("Portrait 13:16 mobile background, Taiwanese market at golden hour. In the top third, centered: "
                   "a small market cart with a striped red-white awning and a smiling vendor girl with a cap holding "
                   "a spatula (same character as asset A16). Strings of warm lanterns across the sky. The lower two "
                   f"thirds are a plain, softly lit market floor with very little detail. {STYLE}."),
    },
    {
        "id": "A05", "file": "bg-form.png", "priority": "P1", "task": "new",
        "title": "攤商補登頁背景（市場主題）",
        "source": "form", "crop": [0, 88, 1448, 1086],
        "output": {"width": 2896, "height": 1996, "background": "不透明"},
        "text": "fixed",
        "allowed_text": ["新鮮蔬果（左側直式看板）", "市場好味道（左下直式看板）", "人氣推薦！（右側看板）"],
        "keep": ["構圖照參考圖：上方是主視覺橫幅（左邊攤商角色、右邊拿大聲公的貓），兩側是攤位與花草"],
        "remove": ["參考圖的表單卡片、說明側欄、中間標題字、右上對話框"],
        "replace": ["上方主視覺改成市場街景：遮雨棚、蔬果攤、燈籠",
                    "兩側改成市場攤位：左側蔬果與乾貨，右側小吃與飲料"],
        "notes": ["這張只用在補登頁、不會變動，兩側看板可以畫手寫字，但只能用 allowed_text 的文字。",
                  "主視覺中間（上方藍框）留一塊乾淨的天空，網頁會疊上 A06 手寫標題；副標題由網頁文字顯示。",
                  "下方藍框是表單與側欄，畫成淺色、低對比、柔焦的背景，不要文字。"],
        "accept": ["尺寸剛好 2896×1996", "藍框範圍內沒有文字", "看板文字與 allowed_text 完全一致"],
        "boxes": "form_layout",
        "prompt": ("Wide web page background, Taiwanese local market theme. Top banner area: a bright market street "
                   "with striped awnings, fruit and vegetable stalls and warm lanterns; leave a clean sky area in the "
                   f"top center with no text. Left banner edge: the vendor girl holding a skewer (asset A15). Right "
                   f"banner edge: {CAT} holding a red megaphone (asset A13). Left page edge: a vertical wooden sign "
                   "hand-lettered \"新鮮蔬果\" and a lower vertical banner hand-lettered \"市場好味道\". Right page edge: "
                   "a hanging sign hand-lettered \"人氣推薦！\". Stalls with produce, dry goods, snacks and potted flowers "
                   "along both edges. The large lower-center area is soft, low-contrast and blurred, with no text, left "
                   f"empty for a form. Traditional Chinese hand lettering, exactly these phrases and nothing else. {STYLE}."),
    },
    {
        "id": "A06", "file": "hero-form-title.png", "priority": "P1", "task": "extract",
        "title": "「攤商資料補登」手寫標題字",
        "source": "form", "crop": [505, 125, 975, 225],
        "output": {"width": 940, "height": 200, "background": "透明"},
        "text": "fixed",
        "allowed_text": ["攤商資料補登"],
        "keep": ["粗體手寫字、深咖啡色、白色外框、下方黃色底線，風格照參考圖"],
        "remove": ["背景", "下方副標題（由網頁文字顯示）"],
        "replace": [],
        "notes": ["補登頁固定使用的標題，可以手寫；會疊在 A05 主視覺中間的空白天空上。"],
        "accept": ["透明背景", "文字為「攤商資料補登」六個字，沒有錯字、沒有其他文字"],
        "prompt": ("Title lettering that reads exactly \"攤商資料補登\" in Traditional Chinese, chunky playful hand-drawn "
                   "brush lettering in dark brown with a thick white outline and a yellow highlighter underline beneath. "
                   f"No other text. {STYLE}, {TRANSPARENT}."),
    },
    {
        "id": "A07", "file": "hero-login-title.png", "priority": "P1", "task": "extract",
        "title": "「攤商專區」雲朵標題",
        "source": "login", "crop": [0, 20, 560, 215],
        "output": {"width": 1120, "height": 390, "background": "透明"},
        "text": "fixed",
        "allowed_text": ["攤商專區"],
        "keep": ["白色雲朵外形", "左側地圖與定位圖釘圖示、星星、黃色光芒", "「攤商專區」手寫字"],
        "remove": ["副標題「填寫你的 Google 地圖資料」（由網頁文字顯示）", "雲朵外的背景"],
        "replace": [],
        "notes": ["登入頁固定使用（桌機與手機共用），可以手寫。"],
        "accept": ["透明背景", "文字為「攤商專區」四個字，沒有錯字、沒有其他文字"],
        "prompt": ("A fluffy white cloud-shaped title badge with a small folded green map and a red location pin icon "
                   "on the left, a yellow sparkle and star accents, and bold hand-drawn dark-brown lettering that reads "
                   f"exactly \"攤商專區\" in Traditional Chinese. No other text. {STYLE}, {TRANSPARENT}."),
    },
    {
        "id": "A08", "file": "logo-stall.png", "priority": "P1", "task": "extract",
        "title": "攤車 Logo",
        "source": "front", "crop": [16, 8, 102, 86],
        "output": {"width": 352, "height": 312, "background": "透明"},
        "keep": ["以前台版本為準：黃色遮陽棚、綠色攤車、輪子", "車上的商品改成蔬果與小吃各半，代表市場"],
        "remove": ["背景"], "replace": [],
        "notes": ["原圖很小，請重新精繪。"],
        "accept": ["透明背景", "縮到 88×78 時仍清楚可辨"],
        "prompt": ("Logo icon: a small Taiwanese market cart with a yellow scalloped awning and a green wooden body "
                   "on two wheels, the counter filled half with fresh vegetables and fruit, half with snacks. "
                   f"Simple shapes that stay readable at 88px. {STYLE}, {TRANSPARENT}."),
    },
    {
        "id": "A09", "file": "mascot-chef.png", "priority": "P1", "task": "extract",
        "title": "綁頭巾的攤商男孩（比讚）",
        "source": "front", "crop": [256, 110, 426, 220],
        "output": {"width": 340, "height": 220, "background": "透明"},
        "keep": ["男孩、頭巾、比讚的手、愛心"], "remove": ["背景"],
        "replace": ["手上的食物改成一籃蔬果，代表市場攤商"],
        "notes": ["原圖下半身被切掉，請畫到圍裙下緣。"],
        "accept": ["透明背景"],
        "prompt": ("Chibi boy market vendor with a white headband and blue apron giving a thumbs-up, holding a small "
                   f"basket of vegetables, a little heart floating nearby, waist-up. {STYLE}, {TRANSPARENT}."),
    },
    {
        "id": "A10", "file": "mascot-cat-map.png", "priority": "P1", "task": "extract",
        "title": "拿地圖的貓咪（三花貓標準造型）",
        "source": "front", "crop": [440, 266, 614, 394],
        "output": {"width": 348, "height": 256, "background": "透明"},
        "keep": ["三花貓、攤開的地圖、愛心"], "remove": ["背景"], "replace": [],
        "notes": ["這張定下三花貓的標準造型，其他貓咪都以此為準。"],
        "accept": ["透明背景"],
        "prompt": f"{CAT}, winking and holding an open folded map, a small heart above. {STYLE}, {TRANSPARENT}.",
    },
    {
        "id": "A11", "file": "mascot-cat-wave.png", "priority": "P1", "task": "extract",
        "title": "揮手的貓咪",
        "source": "front", "crop": [1384, 878, 1524, 1018],
        "output": {"width": 280, "height": 280, "background": "透明"},
        "keep": ["三花貓、揮手的爪子、愛心"], "remove": ["左上角對話框殘留（紅框）", "背景"], "replace": [],
        "notes": ["請補完整身體。"],
        "accept": ["透明背景", "沒有對話框殘留"],
        "boxes": "cat_wave",
        "prompt": f"{CAT}, wearing a small blue apron, happily waving one paw, a heart nearby. {STYLE}, {TRANSPARENT}.",
    },
    {
        "id": "A12", "file": "mascot-cat-boat.png", "priority": "P2", "task": "extract",
        "title": "坐小船的貓咪",
        "source": "admin", "crop": [505, 385, 650, 470],
        "output": {"width": 290, "height": 170, "background": "透明"},
        "keep": ["貓咪、木船、船邊浪花"], "remove": ["上方對話框", "海面背景"], "replace": [],
        "notes": [], "accept": ["透明背景"],
        "prompt": f"{CAT}, sitting in a small wooden rowboat with little splashes. {STYLE}, {TRANSPARENT}.",
    },
    {
        "id": "A13", "file": "mascot-cat-megaphone.png", "priority": "P2", "task": "extract",
        "title": "拿大聲公的貓咪",
        "source": "form", "crop": [1160, 185, 1320, 312],
        "output": {"width": 320, "height": 254, "background": "透明"},
        "keep": ["三花貓、紅色大聲公"], "remove": ["左邊對話框殘留", "背景"], "replace": [],
        "notes": ["請補到腰部。"], "accept": ["透明背景"],
        "prompt": f"{CAT}, shouting cheerfully into a red-and-white megaphone, waist-up. {STYLE}, {TRANSPARENT}.",
    },
    {
        "id": "A14", "file": "mascot-cat-heart.png", "priority": "P1", "task": "extract",
        "title": "抱愛心的貓咪",
        "source": "form", "crop": [965, 928, 1140, 1052],
        "output": {"width": 350, "height": 248, "background": "透明"},
        "keep": ["三花貓、紅色大愛心、周圍小愛心"], "remove": ["粉紅色卡片背景"], "replace": [],
        "notes": [], "accept": ["透明背景"],
        "prompt": f"{CAT}, hugging a big red heart, small hearts floating around. {STYLE}, {TRANSPARENT}.",
    },
    {
        "id": "A15", "file": "mascot-girl-vendor.png", "priority": "P2", "task": "extract",
        "title": "拿烤串的攤商女孩",
        "source": "form", "crop": [230, 95, 470, 305],
        "output": {"width": 480, "height": 420, "background": "透明"},
        "keep": ["戴帽子的女孩、黃色光芒"], "remove": ["背景（天空、攤位、看板）"],
        "replace": ["一手拿烤串，另一手提一小袋蔬果（市場主題）"],
        "notes": ["請補到腰部。"], "accept": ["透明背景"],
        "prompt": ("Chibi girl market vendor with curly brown hair, a beige cap and a dark apron, laughing with closed "
                   "eyes, holding a grilled skewer in one hand and a small bag of vegetables in the other, yellow "
                   f"sparkle accents, waist-up. {STYLE}, {TRANSPARENT}."),
    },
    {
        "id": "A16", "file": "mascot-girl-stall.png", "priority": "P1", "task": "extract",
        "title": "攤車與拿鍋鏟的女孩",
        "source": "login", "crop": [620, 50, 960, 335],
        "output": {"width": 680, "height": 570, "background": "透明"},
        "keep": ["紅白條紋遮陽棚、攤車木框、燈籠、女孩、鍋鏟、攤車檯面"],
        "remove": ["左邊看板、右邊對話框", "背景天空"],
        "replace": ["檯面上加幾樣蔬果與小吃，代表市場"],
        "notes": ["手機版登入頁會單獨使用這張，A04 也要畫同一組角色。"],
        "accept": ["透明背景", "沒有看板與對話框"],
        "prompt": ("A small market stall with a red-and-white striped scalloped awning, two hanging lanterns and a "
                   "wooden frame; behind the counter a smiling chibi girl with a brown cap and blue overalls holds a "
                   "spatula; the counter shows a few vegetables and snacks. Blank stall, no signboard. "
                   f"{STYLE}, {TRANSPARENT}."),
    },
    {
        "id": "A17", "file": "stall-placeholder.png", "priority": "P2", "task": "new",
        "title": "攤位照片預設圖（尚未上傳照片時）",
        "source": "front", "crop": [1198, 132, 1508, 332],
        "output": {"width": 724, "height": 470, "background": "不透明"},
        "keep": ["暖色燈光的攤位場景"], "remove": ["人物、招牌文字、任何字"],
        "replace": ["改成空的市場攤位：遮雨棚、空竹籃、木檯面"],
        "notes": ["中間留一塊乾淨區域，網頁會疊上「照片準備中」文字。"],
        "accept": ["尺寸剛好 724×470", "沒有人物與文字"],
        "prompt": ("An empty Taiwanese market stall with a striped awning, empty bamboo baskets and a wooden counter, "
                   "warm light, no people. Keep the center area simple and uncluttered for an overlay label. "
                   f"{STYLE}."),
    },
    {
        "id": "A18", "file": "category/<品類>.png", "priority": "P2", "task": "new",
        "title": "商品品類圖示（市場與夜市共用）",
        "source": "front", "crop": [28, 630, 70, 936],
        "output": {"width": 128, "height": 128, "background": "透明"},
        "keep": ["風格參考左側清單的小圖示：粗線條、可愛、俯視 3/4 角度"],
        "remove": [], "replace": [],
        "notes": ["共 10 張，檔名與內容：vegetables 蔬菜、fruit 水果、meat 肉品、seafood 海鮮、"
                  "deli 熟食便當、snacks 小吃炸物、drinks 飲料、desserts 甜點糕餅、dry-goods 南北雜貨、"
                  "flowers 花卉與其他。",
                  "品類清單若與攤商名單不合，以名單為準再調整。"],
        "accept": ["每張 128×128、透明背景", "10 張風格一致，主體約佔畫面 80%"],
        "prompt": ("A set of 10 matching category icons, one subject per icon: vegetables (bok choy and carrot), "
                   "fruit (pineapple and bananas), meat (pork cut), seafood (fish and shrimp), deli (bento box), "
                   "snacks (fried chicken cutlet), drinks (bubble tea), desserts (egg cakes), dry goods (sack of rice "
                   f"and dried mushrooms), flowers (bouquet). 3/4 top view. {STYLE}, {TRANSPARENT}."),
    },
    {
        "id": "A19", "file": "illus-auto-check.png", "priority": "P2", "task": "extract",
        "title": "「系統自動核對」插圖",
        "source": "form", "crop": [1180, 728, 1368, 905],
        "output": {"width": 376, "height": 354, "background": "透明"},
        "keep": ["手機地圖、紅色定位圖釘、光芒、雲"], "remove": ["淺綠色卡片背景"],
        "replace": ["小攤位改成市場攤位（遮雨棚＋蔬果籃）"],
        "notes": ["右側與下方被切掉，請補完整。"], "accept": ["透明背景"],
        "prompt": ("A tilted smartphone showing a simple map, a big red location pin above a tiny market stall with a "
                   f"striped awning and a basket of vegetables, yellow sparkles and a small cloud. {STYLE}, {TRANSPARENT}."),
    },
    {
        "id": "A20", "file": "empty-state.png", "priority": "P2", "task": "new",
        "title": "搜尋不到結果的插圖",
        "source": "front", "crop": [440, 266, 614, 394],
        "output": {"width": 400, "height": 320, "background": "透明"},
        "keep": ["同一隻三花貓（參考 A10）"], "remove": ["任何文字"], "replace": [],
        "notes": ["貓咪拿放大鏡，看著一個空竹籃，表情疑惑但可愛。"],
        "accept": ["透明背景", "與 A10 是同一隻貓"],
        "prompt": (f"{CAT}, holding a magnifying glass and peering into an empty bamboo market basket, tilting its head "
                   f"with a puzzled but cute expression. {STYLE}, {TRANSPARENT}."),
    },
    {
        "id": "A21", "file": "error-state.png", "priority": "P2", "task": "new",
        "title": "資料載入失敗的插圖",
        "source": "front", "crop": [440, 266, 614, 394],
        "output": {"width": 400, "height": 320, "background": "透明"},
        "keep": ["同一隻三花貓（參考 A10）"], "remove": ["任何文字"], "replace": [],
        "notes": ["貓咪拿著斷掉的插頭，表情無奈但不悲傷。"],
        "accept": ["透明背景", "與 A10 是同一隻貓"],
        "prompt": (f"{CAT}, holding an unplugged power cord with a small spark, a sheepish shrug, not sad. "
                   f"{STYLE}, {TRANSPARENT}."),
    },
    {
        "id": "A22", "file": "map-city-labels.png", "priority": "P2", "task": "new",
        "title": "地圖城市名稱圖層（選用）",
        "source": "map2", "crop": [0, 0, 1122, 1402],
        "output": {"width": 2244, "height": 2804, "background": "透明"},
        "text": "fixed",
        "allowed_text": ["台北", "桃園", "新竹", "台中", "彰化", "嘉義", "台南", "高雄", "屏東", "宜蘭", "花蓮", "台東"],
        "keep": [], "remove": [], "replace": [],
        "notes": ["和 A01 完全同尺寸的透明圖層，只有城市名稱，疊在地圖上。城市位置固定，所以可以手寫。",
                  "名稱放在各城市的大致位置，靠近海岸或空曠處，不要蓋住地標建築。",
                  "市場名稱會隨資料變動，由網頁產生，不要畫在這張。"],
        "accept": ["尺寸與 A01 相同、透明背景", "只有 allowed_text 的 12 個城市名稱，沒有錯字"],
        "prompt": ("A transparent overlay layer for the hand-drawn Taiwan map (same canvas as asset A01), containing only "
                   "small rounded navy-blue label tags with white hand-lettered Traditional Chinese city names placed at "
                   "each city's approximate location: 台北, 桃園, 新竹, 台中, 彰化, 嘉義, 台南, 高雄, 屏東, 宜蘭, 花蓮, 台東. "
                   f"Nothing else on the layer. {STYLE}, {TRANSPARENT}."),
    },
    {
        "id": "A23", "file": "map-headline-front.png", "priority": "P2", "task": "new",
        "title": "前台地圖標語對話框",
        "source": "front", "crop": [462, 112, 815, 302],
        "output": {"width": 700, "height": 380, "background": "透明"},
        "text": "fixed",
        "allowed_text": ["全台市場美食地圖", "看看你的攤位", "是否已經在 Google 地圖上！"],
        "keep": ["參考圖的對話框造型：白底、深咖啡色粗外框、左下方的尾巴、左上角星星"],
        "remove": ["背景"], "replace": ["「夜市」改為「市場」"],
        "notes": ["前台地圖左上角固定的標語，可以手寫。"],
        "accept": ["透明背景", "三行文字與 allowed_text 完全一致"],
        "prompt": ("A white speech bubble with a thick dark-brown outline and a tail at the lower left, a small yellow "
                   "star at its top-left corner. Inside, three lines of hand-lettered Traditional Chinese: a large bold "
                   "title \"全台市場美食地圖\", then \"看看你的攤位\", then \"是否已經在 Google 地圖上！\". "
                   f"Exactly these words and nothing else. {STYLE}, {TRANSPARENT}."),
    },
    {
        "id": "A24", "file": "map-headline-admin.png", "priority": "P2", "task": "new",
        "title": "管理版地圖標語雲朵",
        "source": "admin", "crop": [500, 120, 840, 245],
        "output": {"width": 680, "height": 250, "background": "透明"},
        "text": "fixed",
        "allowed_text": ["全台市場攤商地圖", "管理攤商・掌握進度・連結台灣美味"],
        "keep": ["參考圖的雲朵造型：白底、深咖啡色外框、右側小愛心"],
        "remove": ["背景"], "replace": ["「夜市」改為「市場」"],
        "notes": ["管理版地圖左上角固定的標語，可以手寫。"],
        "accept": ["透明背景", "兩行文字與 allowed_text 完全一致"],
        "prompt": ("A white cloud-shaped title badge with a dark-brown outline and a small red heart on the right. "
                   "Inside, hand-lettered Traditional Chinese: a large bold title \"全台市場攤商地圖\" and a smaller "
                   "line below \"管理攤商・掌握進度・連結台灣美味\". Exactly these words and nothing else. "
                   f"{STYLE}, {TRANSPARENT}."),
    },
    {
        "id": "A25", "file": "map-taiwan-base.png", "priority": "P0", "task": "new",
        "title": "手繪台灣地圖純底圖（縣市徽章用，無地標、無市場）",
        "source": "map2", "crop": [0, 0, 1122, 1402],
        "output": {"width": 2244, "height": 2804, "background": "不透明（保留海洋）"},
        "keep": ["參考圖的本島外框：海岸線形狀、斜度、比例、在畫面中的位置都照參考圖，不能放大、拉寬或變形",
                 "參考圖的畫風：Q 版手繪、深咖啡色描邊、明亮的海、綠色陸地、山與樹的畫法"],
        "remove": ["所有建築與地標：台北 101、摩天輪、橋、寺廟、教堂、塔樓、燈塔、市場牌樓"],
        "replace": ["加上澎湖、金門、馬祖三組離島",
                    "加上綠島、蘭嶼兩座小島（屬於台東，不放徽章）"],
        "notes": ["重新繪製陸地內容，但本島外框要照參考圖：不需要逐像素相同，形狀、比例和位置要一致。北部不放大。",
                  "網頁會在每個縣市放一個徽章（攤商數＋完成比例圓環），點選後彈出市場列表。所以底圖只是背景，不能搶走徽章的注意力。",
                  "版面依 refs/A25-annotated.png：藍框是 22 個縣市徽章的大約位置，不需要精確。框內盡量是平坦、低細節的陸地或淺海，不要放山峰或大樹。",
                  "北部縣市的藍框有些落在海上或彼此靠近，這是正常的：徽章可以壓到海岸或海面，網頁會自行錯開。不要為了容納徽章而改變島的形狀。",
                  "澎湖畫在本島西側海上，大約對著雲林、嘉義。",
                  "綠島、蘭嶼畫在台東外海的東南方，照實際方向放：綠島在台東東邊，蘭嶼在更南邊。兩座島只是地圖的一部分，不放徽章，所以不需要留空白。",
                  "金門、馬祖實際距離太遠，畫在畫面左側的海上：馬祖在左上、金門在左中，各自用淡色虛線圓角框圍起來，表示不照比例。",
                  "陸地細節要少、顏色比參考圖淡一些：中央山脈用幾座淡綠色的山表現，樹木稀疏、小而低調。",
                  "海上的裝飾（船、鯨魚、海豚、雲）只能放在畫面四邊，最多 4～5 個，不能靠近任何藍框。",
                  "不要畫縣市界線、道路、文字。縣市名稱與徽章都由網頁產生。",
                  "交付後由我在圖上標出 22 個縣市徽章的實際像素位置，存成對照表。"],
        "accept": ["尺寸剛好 2244×2804",
                   "沒有任何建築、地標、文字、縣市界線、圖釘、標記",
                   "本島外框和參考圖一致（縮小 50% 疊圖，形狀重疊 93% 以上，沒有放大或拉寬），澎湖、金門、馬祖、綠島、蘭嶼都有畫",
                   "金門、馬祖各有一個淡色虛線框",
                   "layout 圖的 22 個藍框位置，大致是平坦、低細節的陸地或海面，放上徽章不會蓋住重點",
                   "陸地整體比參考圖淡、細節少，海上裝飾只在四邊"],
        "boxes": "map_layout", "fade_ref": True,
        "prompt": ("A soft, low-detail hand-drawn cartoon base map of Taiwan for an app background, seen from above. "
                   "Keep the main island's outline, tilt, proportions and position exactly like the reference map; "
                   "do not enlarge, widen or stretch any part. Pale green land with a few gentle "
                   "light-green mountains along the central spine, sparse small round trees, sandy beaches, bright "
                   "turquoise sea with light wave lines. Penghu islands drawn in the sea west of the main island. "
                   "Kinmen and Matsu drawn as small islands on the far left of the sea, each inside a faint dashed "
                   "rounded frame to show they are not to scale. Two small islands, Green Island and Orchid Island, in the sea southeast of the main island off the Taitung coast. Large calm flat areas on land for placing badges. "
                   "No buildings, no landmarks, no roads, no county borders, no text. Only a few small decorations "
                   "near the edges of the image: one boat, one whale, two clouds. "
                   f"{STYLE}, lighter and calmer than usual so overlaid UI badges stand out. Portrait 4:5."),
    },
]

# 標註框（來源圖的像素座標）：remove＝紅、keep＝綠、replace＝橘、ui＝藍
BOXES = {
    "map2": {"replace": [(595, 180, 722, 252), (395, 560, 532, 638), (350, 920, 482, 1002)],
             "keep": [(840, 395, 962, 477), (330, 765, 482, 847)]},
    # A25：22 個縣市徽章的大約位置（參考圖座標，不需精確；北部的框可以落在海上）
    "map_layout": {"ui": [(845, 90, 905, 150, "基隆"), (760, 120, 820, 180, "台北"), (655, 70, 715, 130, "新北"),
                          (560, 175, 620, 235, "桃園"), (500, 275, 560, 335, "新竹縣"), (415, 255, 475, 315, "新竹市"),
                          (835, 300, 895, 360, "宜蘭"), (400, 400, 460, 460, "苗栗"), (380, 510, 440, 570, "台中"),
                          (300, 610, 360, 670, "彰化"), (540, 590, 600, 650, "南投"), (280, 715, 340, 775, "雲林"),
                          (300, 815, 360, 875, "嘉義市"), (420, 820, 480, 880, "嘉義縣"), (310, 930, 370, 990, "台南"),
                          (430, 1020, 490, 1080, "高雄"), (450, 1140, 510, 1200, "屏東"), (750, 540, 810, 600, "花蓮"),
                          (650, 880, 710, 940, "台東"), (150, 760, 210, 820, "澎湖"),
                          (70, 470, 130, 530, "金門"), (70, 150, 130, 210, "馬祖")],
                   "replace": [(760, 950, 830, 1010, "綠島（畫島，無徽章）"), (770, 1120, 850, 1190, "蘭嶼（畫島，無徽章）")]},
    "login_layout": {"ui": [(417, 340, 1120, 985)], "keep": [(0, 380, 410, 1024), (1150, 300, 1536, 1024),
                                                             (620, 50, 960, 335)]},
    "form_layout": {"ui": [(82, 305, 930, 1078), (936, 305, 1390, 1078), (488, 120, 988, 262)],
                    "keep": [(228, 92, 472, 305), (1158, 178, 1322, 310)]},
    "cat_wave": {"remove": [(1384, 878, 1440, 920)]},
}
STYLE_BOX = {"remove": ((230, 30, 40), "移除"), "keep": ((20, 160, 70), "保留"),
             "replace": ((240, 130, 20), "替換"), "ui": ((30, 90, 230), "介面區（留白）")}


def boxed(im, boxes, color, label, offset, scale=1.0, width=3):
    d = ImageDraw.Draw(im)
    fnt = ImageFont.truetype(FONT, max(13, int(15 * scale)))
    ox, oy = offset
    for b in boxes:
        x0, y0, x1, y1 = [(v - o) * scale for v, o in zip(b[:4], (ox, oy, ox, oy))]
        d.rectangle([x0, y0, x1, y1], outline=color, width=width)
        text = b[4] if len(b) > 4 else label  # 框可以自帶標籤，例如縣市名稱
        if text and len(b) > 4:  # 自帶標籤加白底，疊在複雜的底圖上才看得清楚
            tb = d.textbbox((x0 + 4, y0 + 3), text, font=fnt)
            d.rectangle([tb[0] - 2, tb[1] - 2, tb[2] + 2, tb[3] + 2], fill=(255, 255, 255))
        if text:
            d.text((x0 + 4, y0 + 3), text, fill=color, font=fnt)


def main():
    refs_dir = OUT / "refs"
    refs_dir.mkdir(parents=True, exist_ok=True)
    for old in refs_dir.glob("*.png"):  # 清掉舊版參考圖，避免殘留已取消的項目
        old.unlink()
    srcs = {k: Image.open(ROOT / v).convert("RGB") for k, v in MOCKUPS.items()}
    manifest = []
    for a in ASSETS:
        im = srcs[a["source"]]
        x0, y0, _, _ = a["crop"]
        src = im.crop(a["crop"])
        base = refs_dir / a["id"]
        src.save(f"{base}-source.png")
        refs = {"source": f"refs/{a['id']}-source.png"}
        if "boxes" in a:
            scale = 2 if src.width < 400 else 1
            ann = src.resize((src.width * scale, src.height * scale))
            if a.get("fade_ref"):  # 只看版面的參考圖：底圖淡化，讓標註更清楚
                ann = Image.blend(ann, Image.new("RGB", ann.size, "white"), 0.55)
            for kind, boxes in BOXES[a["boxes"]].items():
                color, label = STYLE_BOX[kind]
                boxed(ann, boxes, color, label, (x0, y0), scale)
            ann.save(f"{base}-annotated.png")
            refs["annotated"] = f"refs/{a['id']}-annotated.png"
        ctx = im.copy()
        boxed(ctx, [a["crop"]], (30, 90, 230), a["id"], (0, 0), 1, 5)
        ctx.thumbnail((900, 900))
        ctx.save(f"{base}-context.png")
        refs["context"] = f"refs/{a['id']}-context.png"

        item = {k: v for k, v in a.items() if k not in ("boxes", "fade_ref")}
        item["source"] = MOCKUPS[a["source"]]
        item["crop_note"] = "crop 為 [左, 上, 右, 下]，以 source 圖的像素為單位"
        item["text"] = a.get("text", "none")
        item["negative_prompt"] = NEGATIVE[item["text"]]
        item["refs"] = refs
        item["deliver_to"] = f"design/assets/final/{a['file']}"
        manifest.append(item)

    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(manifest)} assets -> {OUT}")


if __name__ == "__main__":
    main()
