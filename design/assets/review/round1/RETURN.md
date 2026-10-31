# ROUND1 修正版交回紀錄

日期：2026-10-31（台北）
狀態：**已交回，待使用者以原方式再次驗收**。

本次生圖 Agent 已完整接收並讀取 `design/asset-briefs/feedback/ROUND1.md` 及同資料夾 `A01-patch-seams.png`。依兩份資料，只替換 A01 與 A18 desserts；A04 與另外 29 張 PNG 均未變動。

## A01 地圖

正式檔：`../../final/map-taiwan-market.png`，2244×2804、不透明。

- 三座市場與四台攤車沿用前版的像素內容、位置、大小；僅去背遮罩邊緣與整體做 0.6px 輕微模糊，匹配放大底圖。
- 去除七塊矩形背景。市場以原物件輪廓的透明遮罩疊回；攤車直接疊回原圖地面。
- 市場空地由內建 imagegen 生成局部乾淨背景板，只取框內作補景；以 6px 向內羽化接回原地面，北部左上樹冠用原圖恢復。沒有把整張生成圖覆蓋回地圖。
- 曾測試 Poisson 配色，但會滲入舊牌樓色線，已棄用；正式版使用乾淨背景板及透明輪廓。
- 原圖 2 倍底圖與前版各自比對，**七個原貼片矩形以外差異均為 0 pixels**。既有 `../map-preservation-check.json` 亦維持 0。
- 生圖 Agent 目視 100% 與 50% 對照：先前硬矩形邊線已消除。最終美術驗收留給使用者。

對照：
- [七處原尺寸前後對照（上舊下新）](A01-seams-before-after-100pct.png)
- [修正版 50%](A01-candidate-50pct.png)
- [去背輪廓例：北部市場](traditional-north-cutout.png)

## A18 desserts

正式檔：`../../final/category/desserts.png`，128×128、RGBA、四角 alpha=0、主體最長邊約 80%。

由內建 imagegen 重繪為淺色瓷碗豆花；紫色及米黃色芋圓、深咖啡粉圓，無文字。保留本系列深咖啡描邊及可愛平塗陰影。碗的寬扁造型與紫色配料在縮圖中區別於金黃雞排與直立飲料杯。

- [十張各以實際 48×48 並排（請以 100% 檢視）](category-row-48px.png)
- [修正版 128×128](desserts-candidate.png)

圖示辨識為目視自檢結果，不代替使用者的最終驗收。

## 技術與追溯

- `round1-checks.json`：32 張尺寸/透明背景皆通過，與 `../round1-before-hashes.json` 相比，只有 A01 與 desserts 的 SHA-256 改變，其餘 30 張（包括 A04）完全不變。
- `round1-checks-candidate.json`：七個原貼片範圍的精確框外比對。
- `generation-record.json`：本次完整提示詞、生成原檔位置與專案內副本。
- `before-map-taiwan-market.png`、`before-desserts.png`：修改前備份。
- `../../../tools/revise_round1_assets.py`：輪廓遮罩、補景、尺寸整理及候選圖產生程式。
- `../index.html`、`../contact-sheet.jpg`、`../technical-checks.json` 已更新為目前正式素材。
- 原 `ROUND1.md`、`A01-patch-seams.png`、manifest 與其他 30 張正式 PNG 均未修改。

舊硬矩形合成腳本與第一版生成紀錄保留作歷史證據；不可拿舊合成流程重建本次修正版。
