# A25 第三版：修正解析度、縣市界線、標籤區（給生圖 Agent）

- 日期：2026-10-31
- 基礎：v2 正式底圖 `design/assets/final/map-taiwan-base.png`（SHA-256 開頭 `84d12db5`）。**v3 是 v2 的修正版，不是重新設計**：外型、畫風、配色、雪山、鯨魚、帆船、雲都照 v2。
- 第三版通過使用者驗收前，**不要覆蓋**正式底圖。

## 只修三件事

### 1. 原生解析度

v2 是 1122×1402 用雙三次插值放大 2 倍，線條偏軟。

- v3 要直接產生 2244×2804；如果工具做不到這個尺寸，就用工具能產生的最大尺寸，再用 AI 超解析放大（例如 Real-ESRGAN 類的方法）。
- **不能只用雙三次或雙線性插值放大**。
- 放大後，深咖啡描邊在 100% 檢視時要清楚銳利，不能糊，也不能有鋸齒或色塊。

### 2. 縣市界線照真實縣界

v2 的白線是生成時隨意畫的，跟真實縣界對不上。

- 先取得真實的縣市界線，作為描線底稿。建議用政府資料開放平台的「直轄市、縣市界線」。
- 把縣界縮放、旋轉，對齊 v2 的本島外型，再照著描出淡白色的線。手繪外型和真實海岸線不會完全一樣，界線的端點一律接到 v2 的海岸線上。
- 本島 19 個縣市都要分開：基隆市、臺北市、新北市、桃園市、新竹縣、新竹市、苗栗縣、臺中市、彰化縣、南投縣、雲林縣、嘉義縣、嘉義市、臺南市、高雄市、屏東縣、宜蘭縣、花蓮縣、臺東縣。
- 重點：
  - 臺北市完全被新北市包住。
  - 基隆市在東北角，靠海。
  - 新竹市是西岸一小塊，被新竹縣包住。
  - 嘉義市是一小塊，被嘉義縣包住。
  - 臺東縣是東岸南段的長條形。
- 線的樣式照 v2：淡白色、細、柔和，只當裝飾。

### 3. 標籤區要淨空，而且不能重疊

網頁會在 8 個縣市放標籤，所以下面這 8 個區域裡**不放山、丘陵和樹**，只留平地、沙灘或近岸海面。

- 每區是 420×200 的長方形，數字是 2244×2804 上的中心點。
- 這些區域彼此不重疊，也不碰左上的保留區。
- 標籤可以壓到海岸和近岸海面，所以有的區域會跨過海岸線，這是正常的，**不要為了這個改變島的外型**。

| 縣市 | 中心點 | 範圍（左, 上, 右, 下） | 位置說明 |
|---|---|---|---|
| 臺北 | (1450, 250) | (1240, 150, 1660, 350) | 北端內陸 |
| 新北 | (1900, 640) | (1690, 540, 2110, 740) | 東北海岸，可跨到海面 |
| 桃園 | (1120, 520) | (910, 420, 1330, 620) | 西北；**v2 這裡有一組小丘，要移走** |
| 新竹市 | (860, 880) | (650, 780, 1070, 980) | 西岸，可跨到海面 |
| 臺中 | (760, 1200) | (550, 1100, 970, 1300) | 西岸中段 |
| 臺南 | (560, 1700) | (350, 1600, 770, 1800) | 西南海岸，可跨到海面 |
| 高雄 | (700, 2080) | (490, 1980, 910, 2180) | 西南偏南；**v2 這裡有一組小丘，要移走** |
| 臺東 | (1440, 1900) | (1230, 1800, 1650, 2000) | 東南海岸，可跨到海面 |

- 移走的小丘可以改放在中央山脈一帶，也就是雪山附近、島的中間偏東，但不能進入上面任何一區。
- 留白區：
  - 左上 (0, 0, 880, 740) 的海面全空，放標語和貓。
  - 右下 (1680, 2380, 2244, 2804) 的海面全空，放縮放按鈕和圖例。

## 其他維持 v2

尺寸 2244×2804、不透明 RGB；只有本島；島內沒有建築和地標；海上裝飾維持 v2 的鯨魚、帆船和雲；沒有文字、數字、圖釘或標記。

## Prompt（以 v2 為輸入圖做修正）

```
Edit the provided Taiwan base map. Keep everything the same: island outline, tilt, proportions and position, art style, colors, the snow-capped mountain, the whale, the sailboat and the clouds. Make only these changes: (1) Render at native 2244x2804 resolution with crisp, clean dark-brown outlines; no blur and no soft upscaling artifacts. (2) Redraw the thin soft white county border lines so they follow Taiwan's real county boundaries, fitted to this island outline: Taipei City fully enclosed by New Taipei City, Keelung City at the northeast tip, Hsinchu City as a small coastal area enclosed by Hsinchu County, Chiayi City as a small area enclosed by Chiayi County, Taitung County as a long strip on the southeast coast; every border line ends at the coastline. (3) Remove the small hills in the northwest (Taoyuan area) and in the southwest (Kaohsiung area) and keep those areas flat plain land; any moved hills go near the central mountain only. Keep the label areas along the coast and in the north flat with no hills and no trees. Keep the upper-left sea and the lower-right corner of the sea completely empty. No buildings, no landmarks, no offshore islands, no text, no letters, no numbers, no pins, no markers.
```

## Negative prompt

```
buildings, temples, towers, landmarks, market stalls, lighthouse, bridge, offshore islands, islets, hills in label areas, trees in label areas, random border lines, text, letters, Chinese characters, numbers, labels, logo, watermark, map pins, markers, UI elements, blurry, soft upscaling, jagged lines, color banding, distorted island shape, enlarged north
```

## 交付

- 候選圖：`design/assets/generated/A25-v3-*.png`；選定的一張另存 `design/assets/review/A25/v3/candidate.png`。
- 自檢：`design/assets/review/A25/v3/ACCEPTANCE.md`，逐條對下面的驗收項目。附上以下 4 張檢查圖，都只放在 review 資料夾：
  1. `label-layout-overlay.png`：用**本文件的 8 個新範圍**和兩個留白區畫框，不要用 v2 的舊座標。
  2. `county-border-overlay.png`：把真實縣界疊在候選圖上的對照。
  3. `crop-100pct.png`：北端和西南海岸各一塊 100% 裁切，用來看線條銳利度。
  4. `v2-v3-diff.png`：v2 和 v3 並排，確認只改了這三件事。
- 寫明實際產生的原始解析度，以及用了什麼放大方法。
- 使用者驗收通過後，才覆蓋 `final/map-taiwan-base.png`，並記下新的 SHA-256；v2 備份到 `review/A25/v3/previous-map-taiwan-base.png`。

## 驗收

1. 2244×2804、不透明；寫明原生解析度和放大方法，沒有只用雙三次或雙線性插值放大。
2. 100% 檢視時，描邊清楚銳利，沒有糊邊、鋸齒或色塊。
3. 外型、畫風、配色、雪山和海上裝飾與 v2 一致（v2-v3 並排比對）。
4. 縣界疊圖：19 個縣市都分得出來；臺北被新北包住，新竹市被新竹縣包住，嘉義市被嘉義縣包住；界線端點接到海岸。
5. 8 個標籤範圍內沒有山、丘陵和樹，範圍彼此不重疊。
6. 左上 (0, 0, 880, 740) 和右下 (1680, 2380, 2244, 2804) 是空的海面。
7. 只有本島，島內沒有建築和地標；沒有文字、數字、圖釘或標記。
