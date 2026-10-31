# A25 縣市徽章底圖交付自檢

日期：2026-10-31（台北）。依本次更新後 task=new 的 manifest 與 README 製作，使用內建 imagegen。source 僅參考畫風，annotated 僅參考版面。以下是製作方自檢，供使用者最後目視驗收。

交付：`../../final/map-taiwan-base.png`。

## accept 逐條結果

| 項目 | 結果 | 檢查方式與說明 |
|---|---|---|
| 尺寸剛好 2244×2804 | 通過 | 程式核對精確尺寸；RGB PNG，全圖不透明。 |
| 無建築、地標、文字、縣市界線、圖釘、標記 | 通過 | 全圖目視：無建築、道路、城市字、徽章或介面元素。兩個離島虛線框是規格要求的比例示意。 |
| 台灣可辨識、北部明顯放大，五組離島齊全 | 通過 | 北部加寬、南部收尖；澎湖在西側，馬祖左上、金門左中，綠島與蘭嶼在東南外海，蘭嶼更南。北部約 1.5 倍為視覺示意，非地理測量比例。 |
| 金門、馬祖各有淡色虛線框 | 通過 | 各一個淺色圓角虛線框，沒有名稱或圖例。 |
| 22 個藍框位置平坦、低細節，不蓋住重點 | 通過 | 從 make_asset_refs.py 讀取全部 22 個矩形，產生逐區裁切與疊圖檢查。均為平地、沙灘或海面；無山峰、大樹或建築。沿海保留海岸及低對比浪線；離島的徽章可置於鄰近海面，不要求徽章全部位於陸地。 |
| 陸地較淡、細節少，海上裝飾只在四邊 | 通過 | 主島只有三組柔和丘陵，沿岸清空大型樹木；裝飾共四個：上方左右各一朵雲、左下船、右下鯨魚。 |

## 22 區目視檢查

基隆、台北、新北、桃園、新竹縣、新竹市、宜蘭、苗栗、台中、彰化、南投、雲林、嘉義市、嘉義縣、台南、高雄、屏東、花蓮、台東、澎湖、金門、馬祖：均通過低細節、無重點物件遮擋的自檢。

## 檔案與製作紀錄

- `badge-layout-overlay.png`：22 區版面疊圖，藍框與名稱只在驗收圖，正式素材沒有。
- `badge-zones-contact.png`：22 區逐一裁切的檢查圖。
- `badge-candidate-50pct.png`：50% 預覽。
- `badge-technical-checks.json`：精確尺寸、不透明格式、22 區座標與成品 SHA-256。
- `badge-generation-prompts.json`：manifest 原提示詞、負面提示詞與第一次精簡提示詞。
- `badge-final-cleanup-prompt.txt`、`badge-geography-cleanup-prompt.txt`、`badge-penghu-cleanup-prompt.txt`：後續精簡與離島修正的實際完整提示詞。
- 原始生成版本：`../../generated/A25-badges-v1.png` 至 `A25-badges-v5.png`。選用 v5，以高品質等比例縮放整理為指定尺寸。
- `../../../tools/package_a25_badges.ps1`：尺寸整理與版面檢查圖產生工具。

此資料夾中較早的 `candidate.png`、`candidate-50pct.png`、`preservation-check.json`、`scope-conflicts.png` 及 `../../generated/A25.png` 是上一版 inpaint 任務的歷史中間檔，不屬於這次交付或本次驗收證據。本次沒有逐像素保留舊地圖的要求。徽章的正式像素座標仍由使用者在成品上標定。
