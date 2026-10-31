# 市場類型縮圖 ×3（給 Codex）

- 日期：2026-10-31
- 用途：總覽頁右上的市場清單，每一列前面的縮圖。15 個市場沒有照片，改用 3 張類型插畫，網頁依市場類型自動套用。
- 參考：
  - `design/asset-briefs/refs/overview-mockup-v1.webp` 右上「臺北市」卡片，看縮圖的大小和位置。圖上的實景照片和招牌文字都**不要照抄**。
  - 畫風照現有吉祥物：`design/assets/final/mascot-cat-map.png`、`mascot-girl-stall.png`、`logo-stall.png`。

## 三張圖

| 檔名 | 類型 | 套用的市場 | 畫面內容 |
|---|---|---|---|
| `night_market.png` | 夜市 | 華西街、南機場、旱溪、大慶、鄭仔寮花園、臺東觀光夜市（6 個） | 傍晚到夜晚的深藍紫天空；一排小吃攤，紅白條紋遮雨棚，掛著紅燈籠和暖黃燈泡；攤上有雞排、串燒、珍奶等小吃；可以有一座沒有字的入口牌樓 |
| `traditional_market.png` | 傳統市場 | 永春、五股、興國、大園、新竹東門、龍華、三民第一（7 個） | 白天的明亮光線；有屋頂或大遮雨棚的市場；蔬菜、水果、魚肉攤，竹籃和菜籃，攤位上掛著秤 |
| `other.png` | 美食廣場・商圈 | 瑞芳美食廣場、西門淺草青春新天地（2 個） | 室內或有頂棚的明亮空間；幾間小店面排在一起，前面有圓桌和椅子；有一點文創市集的感覺（盆栽、小黑板、木頭櫃台） |

三張要一眼分得出來：夜市靠**夜晚和燈籠**，傳統市場靠**白天和蔬果攤**，美食廣場靠**室內和桌椅**。

## 規格

- 尺寸：每張 **640×400**（8:5），不透明 RGB PNG。網頁顯示約 130×80，640 寬足夠高解析螢幕使用。
- **重點放在中間**：網頁可能裁成圓角，手機上也可能裁成正方形。主體要放在中間 400×400 的範圍內，四邊各留約 5% 不放重要物件。
- 縮到 130×80 還要看得懂：大色塊、簡單構圖，不要太多細小物件。
- 三張的視角、光源方向、線條粗細和配色要一致，放在一起像同一套。
- **不要文字**：招牌、旗子、價目表上都不能有字、數字或商標，可以用空白招牌或圖形代替。
- 不畫人物，或只在背景放 1～2 個很小的路人剪影，不能搶過攤位。
- 不要透明背景，不要邊框、圓角或陰影外框（圓角由網頁處理）。

## Prompt（三張共用風格，各自替換「場景」）

共用風格：

```
cute chibi Taiwanese local market illustration, thick dark-brown outlines (#3B2A1A), flat colors with soft cel shading, warm friendly palette (orange #F08A3C, lantern red #E5484D, cream #FFF8E6, grass green #7CC46A, sea blue #6DD7F2), rounded shapes, clean crisp line art, simple bold composition that stays readable as a small thumbnail, main subject centered, landscape 8:5, no text, no letters, no numbers, no logos.
```

場景：

- 夜市：`A lively Taiwanese night market street at dusk, deep blue-purple evening sky, a row of food stalls with red-and-white striped awnings, glowing red paper lanterns and warm string lights, stalls showing fried chicken, skewers and bubble tea, a simple entrance arch with a blank sign.`
- 傳統市場：`A bright Taiwanese traditional morning market in daylight, a covered market hall with a large canopy, stalls with colorful vegetables, fruits, fish and meat, bamboo baskets and hanging scales, fresh and clean.`
- 美食廣場・商圈：`A bright covered Taiwanese food court and creative market corner, several small shopfronts side by side with blank signboards, round tables and chairs in front, potted plants, small chalkboards with doodles and wooden counters, cheerful and cozy.`

## Negative prompt

```
text, letters, words, Chinese characters, numbers, prices, brand names, logos, watermark, signature, realistic photo, photorealistic, 3D render, glossy gradients, blurry, noisy, crowded people, large human figures, frame, border, rounded corners, transparent background, dark gloomy mood
```

## 交付

- 候選圖：`design/assets/generated/market-type-*.png`。
- 審查：`design/assets/review/market-type/`，內容如下：
  - 三張並排的對照圖 `contact-sheet.png`。
  - 縮到 130×80 的預覽 `small-preview.png`。
  - `ACCEPTANCE.md`，逐條對下面的驗收項目。
- 使用者接受後，存成正式檔：`design/assets/final/market-type/night_market.png`、`traditional_market.png`、`other.png`。
- 不改 `docs/`、網頁或其他素材。

## 驗收

1. 三張都是 640×400、不透明 RGB。
2. 沒有任何文字、數字或商標。
3. 縮到 130×80 時，三張還分得出夜市、傳統市場、美食廣場。
4. 主體在中間 400×400 內，裁成正方形不會切掉重點。
5. 畫風和吉祥物一致（深咖啡描邊、平塗加柔和陰影），三張彼此一致。
6. 沒有大型人物，沒有邊框或圓角。
