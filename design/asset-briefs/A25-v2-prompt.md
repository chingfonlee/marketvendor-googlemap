# A25 第二版：總覽頁台灣底圖（給生圖 Agent）

- 日期：2026-10-31
- 取代：現行 A25（`final/map-taiwan-base.png`，SHA-256 開頭 `9b0905c4`）。第二版通過驗收前，現行檔案**不要覆蓋**。
- 差異說明：見 `docs/BASEMAP_REVIEW.md`。

## 參考圖

| 檔案 | 用途 |
|---|---|
| `design/reference/map-v2/map-taiwan-clean.png` | **外型、縣市界線、畫風**都照這張。本島輪廓、斜度、比例、在畫面中的位置維持一致（放大 2 倍到 2244×2804） |
| `design/asset-briefs/refs/overview-mockup-v1.webp` | 網頁完成後的樣子，只用來看整體感覺和留白位置。圖上的標籤、文字、建築都**不要畫** |

## 規格

- 尺寸：2244×2804，不透明 RGB PNG。
- 本島：照參考圖的輪廓，北端在右上、南端收尖，西岸弧線明顯。
- **只畫台灣本島**：不畫金門、馬祖、澎湖、綠島、蘭嶼，也不畫參考圖周圍的小島。
- **島內不放任何建築或地標**：台北 101、廟宇、牌樓、市場攤棚、教堂、燈塔、摩天輪、橋都不要。湖泊、瀑布、西岸的橘色岩山也拿掉。
- 島內只有：
  - 淺綠色平地，比參考圖淡、細節少。
  - 中間偏東一座小雪山（玉山意象），加上 3～4 組低矮的淺綠丘陵。
  - 零星的小圓樹，數量約是參考圖的三分之一。
  - **淡白色的縣市界線**，照參考圖的位置，細而柔和，只當裝飾。
  - 沿岸的沙灘和白色浪花。
- 海：明亮的藍綠色，淡淡的波紋。裝飾**只放在海上**，最多 4 個：
  - 左下一隻鯨魚
  - 右下一艘帆船
  - 兩朵雲，放在右上和左下角的邊緣
  - 不要燈塔、渡輪、海鷗、海豚
- 留白：
  - 左上約畫面寬 40%、高 30% 的海面完全空白，網頁會放標語對話框和貓。
  - 右下角約寬 25%、高 15% 的海面空白，網頁會放縮放按鈕和圖例。
- 8 個縣市標籤的大約位置要是平坦、低細節的陸地或近岸海面，不放山和樹。座標是 2244×2804 上的大約中心，不需要精確：

  | 縣市 | 大約位置 |
  |---|---|
  | 臺北 | 北端（1520, 300） |
  | 新北 | 東北角（1800, 460） |
  | 桃園 | 西北（1120, 520） |
  | 新竹市 | 西岸北段（840, 800） |
  | 臺中 | 西岸中段（760, 1200） |
  | 臺南 | 西南（660, 1800） |
  | 高雄 | 西南偏南（760, 2000） |
  | 臺東 | 東南（1440, 1900） |

- 沒有任何文字、縣市名稱、圖釘、標記、介面元素。

## Prompt

```
A soft, low-detail hand-drawn cartoon base map of Taiwan for a web app background, seen from above, portrait 4:5. Keep the main island's outline, tilt, proportions and position exactly like the reference map: north tip at the upper right, tapering south tip, curved west coast. Draw ONLY the main island of Taiwan: no Kinmen, no Matsu, no Penghu, no Green Island, no Orchid Island, no small offshore islets. On the land: pale light-green flat plains, one small snow-capped mountain slightly east of center, three or four low gentle light-green hills, a few sparse small round trees, sandy beaches and white surf along the coast, and thin soft white county border lines following the reference map, decorative only. Absolutely no buildings and no landmarks on the island: no towers, no temples, no gates, no market stalls, no churches, no lighthouses, no ferris wheel, no bridges, no lakes, no waterfalls. Bright turquoise sea with light wave lines. Only four small decorations, all in the sea near the edges: one whale at the lower left, one small sailboat at the lower right, two soft clouds at the upper right and lower left corners. Leave the upper-left sea area completely empty and the lower-right corner empty. Large calm flat areas on land for placing UI labels. No text, no letters, no numbers, no pins, no markers. Cute chibi Taiwanese illustration style, thick dark-brown outlines (#3B2A1A), flat colors with soft cel shading, warm friendly palette (grass green #7CC46A, cream #FFF8E6, sea blue #6DD7F2), rounded shapes, clean crisp line art, lighter and calmer than usual so overlaid UI labels stand out.
```

## Negative prompt

```
buildings, houses, temples, towers, Taipei 101, market stalls, lanterns, ferris wheel, lighthouse, bridge, ferry, ship, seagull, dolphin, lake, waterfall, rock spire, small islands, islets, Kinmen, Matsu, Penghu, text, letters, words, Chinese characters, numbers, labels, logo, watermark, map pins, markers, UI elements, photorealistic, 3D render, glossy gradients, blurry, noisy, distorted island shape, enlarged north
```

## 交付

- 候選圖放 `design/assets/generated/A25-v2-*.png`，選定的一張另存 `design/assets/review/A25/v2/candidate.png`。
- 自檢寫在 `design/assets/review/A25/v2/ACCEPTANCE.md`，逐條對下面的驗收項目，並附一張把 8 個標籤位置畫成框的疊圖（只放在 review 資料夾）。
- 使用者驗收通過後，才覆蓋 `design/assets/final/map-taiwan-base.png`，並記下新的 SHA-256。

## 驗收

1. 尺寸剛好 2244×2804，不透明。
2. 本島外型和參考圖一致：縮小後疊圖，形狀大致重合，北部沒有放大，也沒有拉寬。
3. 只有本島，沒有任何離島或小島。
4. 島內沒有任何建築或地標，也沒有湖泊和瀑布。
5. 有淡白色縣市界線，位置大致照參考圖，不搶眼。
6. 山只有一座小雪山加幾組低丘，8 個標籤位置都是平坦、低細節的區域。
7. 左上 40%×30% 和右下角的海面是空的。
8. 海上裝飾最多 4 個：鯨魚、帆船、兩朵雲。
9. 沒有文字、數字、圖釘或標記。
