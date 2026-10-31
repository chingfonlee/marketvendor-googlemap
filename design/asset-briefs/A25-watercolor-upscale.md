# 水彩底圖 AI 放大（給 Codex）

- 日期：2026-10-31
- 這次只放大，**不修改畫面內容**：不加減山、樹、海浪，不畫界線或文字，也不用生圖模型重畫。

## 輸入與輸出

| 項目 | 內容 |
|---|---|
| 輸入 | `design/assets/final/map-taiwan-base.png`（1024×1536，SHA-256 `970a4c9bd197b4f6361dad47e6884ca7db4d52333479e4ee0d0aca72c56bd2de`） |
| 模型 | `design/assets/review/A25/v3/source/FSRCNN_x2.pb`（v3 用過的同一個） |
| 方法 | FSRCNN x2 跑一次；Y 通道用模型放大，色度用雙三次，做法和 OpenCV `dnn_superres` 相同。**不能只用雙三次或雙線性插值** |
| 輸出 | `design/assets/review/A25/v3-user/upscale-fsrcnn-2048x3072.png`，2048×3072、不透明 RGB，比例維持 2:3，不裁切、不補邊 |

## 一起交付

放在 `design/assets/review/A25/v3-user/`：

1. `upscale-compare-100pct.png`：同一塊區域 100% 裁切，左邊是雙三次版（`upscale-bicubic-2048x3072.png`，已經在資料夾裡），右邊是 FSRCNN 版。裁切範圍 (1300, 250)～(1900, 750)，北部有山和樹的地方。
2. `UPSCALE.md`：寫明使用的環境（Python、OpenCV 版本）、方法、輸出尺寸和輸出檔的 SHA-256。

## 規則

- 正式底圖 `design/assets/final/map-taiwan-base.png` **不要覆蓋**，等使用者看過比較圖再決定。
- 不要修改 `design/assets/final/map-taiwan-base.labels.json`：座標用 viewBox 0 0 1024 1536，換成放大版也不用改。
- 不改 `docs/` 和網頁相關檔案。

## 驗收

1. 輸出 2048×3072、不透明 RGB。
2. 縮小回 1024×1536 和原圖並排，內容完全相同，沒有新增或消失的物件。
3. 100% 比較圖上，FSRCNN 版的樹和山的輪廓比雙三次版清楚，沒有明顯的光暈、鋸齒或色塊。
