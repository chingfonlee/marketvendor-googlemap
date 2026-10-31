# 縣市標籤位置（任務 4）

- 日期：2026-10-31
- 底圖：`design/assets/final/map-taiwan-base.png`，水彩版 2048×3072，SHA-256 開頭 `c3586c0f`
- 座標檔：`design/assets/final/map-taiwan-base.labels.json`（網頁使用時複製成 `web/data/county-labels.json`）
- 疊圖工具：`design/tools/label_overlay.ps1`

## 1. 位置

座標是 viewBox `0 0 1024 1536` 上的標籤中心點，照總覽完成圖大約排。底圖沒有縣市界線，所以不需要對齊真實縣界。

| 縣市 | 標籤文字 | x | y | 位置說明 |
|---|---|---|---|---|
| 臺北市 | 臺北 | 720 | 150 | 北端 |
| 新北市 | 新北 | 900 | 290 | 東北海岸，一半在海上 |
| 桃園市 | 桃園 | 540 | 300 | 西北 |
| 新竹市 | 新竹 | 400 | 450 | 西岸北段 |
| 臺中市 | 臺中 | 300 | 640 | 西岸中段 |
| 臺南市 | 臺南 | 220 | 960 | 西南海岸 |
| 高雄市 | 高雄 | 290 | 1180 | 西南偏南 |
| 臺東縣 | 臺東 | 760 | 1050 | 東南海岸，一半在海上 |

保留區（不放標籤）：左上 (0, 0, 420, 400) 放標語和貓，右下 (820, 1380, 1024, 1536) 放縮放按鈕和圖例。

## 2. 桌機和手機都不重疊

標籤在螢幕上維持固定大小（[LAYER_ARCHITECTURE.md](LAYER_ARCHITECTURE.md) §2），所以地圖顯示得越小，標籤佔的地圖範圍越大。用全台檢視（縮放 1 倍）這個最擠的情況檢查：

| 情況 | 地圖顯示寬度 | 標籤大小（螢幕） | 換算成地圖單位 | 重疊 | 超出地圖邊界 |
|---|---|---|---|---|---|
| 桌機 | 約 600px | 96×34px | 164×58 | 無 | 無 |
| 手機 | 343px（375 寬減兩側邊距） | 72×28px | 215×84 | 無 | 無 |
| 手機點擊範圍 | 343px | 72×44px（觸控最小 44px） | 215×131 | 無 | 無 |

- 間距最近的是臺北和新北：上下差 140，大於手機點擊範圍的 131，所以點得到、不會誤點。
- 桃園和臺北、新竹和桃園的上下差都是 150。

**結論：手機版不需要另外錯開位置，桌機和手機共用同一組座標。** PLAN 原本列的「手機版北部錯開位置」不用做。

唯一的小地方：手機上新竹的**點擊範圍**（看不見）上緣碰到左上保留區的一角，但標籤本身沒有碰到。手機版的標語怎麼擺屬於任務 5，到時一併確認。

疊圖：

- 桌機尺寸：`design/assets/review/A25/v3-user/label-overlay.png`
- 手機點擊範圍：`design/assets/review/A25/v3-user/label-overlay-mobile.png`

重新產生的指令：

```
powershell -NoProfile -ExecutionPolicy Bypass -File design/tools/label_overlay.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File design/tools/label_overlay.ps1 -Out design/assets/review/A25/v3-user/label-overlay-mobile.png -BoxW 215 -BoxH 131
```

## 3. 之後要改位置

1. 只改 `map-taiwan-base.labels.json` 裡的 x、y。
2. 重新產生疊圖確認。
3. 換底圖時，同時更新檔案裡的 `basemap_sha256`；網頁會檢查這個值和實際底圖是否一致（LAYER_ARCHITECTURE §4）。

## 4. 驗收

1. 8 個縣市都有座標，位置大致對應完成圖。
2. 桌機和手機的尺寸下都不重疊，也不超出地圖邊界。
3. 不碰左上和右下的保留區（手機點擊範圍的一角除外，任務 5 確認）。
4. 座標檔記錄底圖的 SHA-256。
