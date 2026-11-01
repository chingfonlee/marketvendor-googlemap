# 網頁組成

技術選擇：純 HTML／CSS／ES modules，**沒有框架、沒有建置步驟**。理由：交給別人時只要會改 HTML 和 JSON；靜態檔可以丟到任何主機；測試不用 node_modules。除非人有特別需求，維持這個選擇。

## 1. 圖層架構與共用狀態（docs/LAYER_ARCHITECTURE.md）

### 頁面區塊
先列出幾個大區塊（例如 header、aside.left、main.map、aside.right），**各區塊都只讀同一份狀態，彼此不直接呼叫**。

### 圖面上的圖層（由下到上）

| 層 | 元素 | 隨縮放移動 |
|---|---|---|
| 1 底圖 | `<svg viewBox="0 0 W H"><image href="map-base.webp">` | 是 |
| 2 預留 | 空的 `<svg>`，給未來的標記 | 是 |
| 3 標籤 | `<div>` 裡的 HTML `<button>`，用 `left: x/W%`、`top: y/H%` 定位，再 `scale(1/縮放倍率)` 讓大小固定 | 位置會、大小不會 |
| 4 疊加 | 標語、吉祥物、縮放鈕、圖例 | 否，固定在框上 |

縮放和拖曳只對「地圖平面」做 CSS `transform`。

### 共用狀態

```js
state = { county: null, marketId: null, status: "all", keyword: "", zoom: { scale: 1, x: 0, y: 0 } }
```

- 列出每個**動作**（`selectCounty`、`clearCounty`、`selectMarket`…）的觸發來源和狀態變化，特別寫清楚連動（選市場時縣市跟著變；換縣市時市場清掉）。
- 列出每個**區塊**受哪些狀態影響、不受哪些影響（例如進度卡不受狀態篩選和搜尋影響）。
- 每次狀態改變，所有區塊依新狀態重畫，不寫「A 改了通知 B」——這樣不會出現兩邊不同步。
- 狀態同步到網址 hash，重新整理和分享連結都能還原；讀回時忽略不存在或對不上的值。
- 元素的樣式狀態（一般、滑過、選取中、變淡）列成表。變淡用實色不用透明度，避免透出底圖。

## 2. 響應式版面（docs/RESPONSIVE_LAYOUT.md）

這份文件通常最長，結構建議：0 結論先講 → 斷點 → 各版排法和尺寸 → 圖面寬度與標籤重疊檢查 → 手機版 → 平板 → 狀態變化時的版面 → 無障礙（Tab 順序、焦點、朗讀、`prefers-reduced-motion`）→ 共用尺寸 → 線框圖 → **驗收清單**（做網頁時逐條檢查）。

要點：
- 手機上大圖通常不好用。先問人：手機要不要放地圖？攤商地圖的決定是**手機和平板直向不放地圖**，改成卡片格＋清單的整頁捲動版，而且不建立地圖、不下載底圖。
- 標籤大小依「**量到的地圖顯示寬度**」切換（ResizeObserver），不要用螢幕寬度或解析度。
- 可點範圍至少 44×44px。
- 頁首用 `min-height`，系統字體放大時跟著長高；長標題用 `inline-block` 片段控制斷行；按鈕準備短版文字。
- 線框圖用 SVG 畫，放進 `docs/`，人比較容易對。
- 討論中的取捨用「決定 A、B、C…」編號記在文件裡，之後引用方便。

## 3. 資料匯入（scripts/import_*.py）

- 原始檔只讀，先複製到暫存檔再讀（避開 Excel 開檔鎖定）。
- 輸出 `web/data/*.json`（只放公開欄位）和 `reports/import-report.md`（每個分組的數量、和總表比對、警告清單）。
- **固定 ID**：第一次產生存進 `data/id-map.json`，用名稱對應；名稱改了用 `review-decisions.csv` 的 `same_as` 沿用舊 ID。ID 只是名字，程式不從 ID 拆資訊。
- 人工決定（排除、改名、確認、換連結）都在 `data/review-decisions.csv`，每筆附原因、日期。
- 跑兩次輸出要逐字相同。產生的檔案固定 LF 換行（加 `.gitattributes`）。
- 網址之類的欄位做離線格式檢查，**同一套規則網頁也要用**（之後寫測試比對兩邊結果）。

## 4. 網頁組成（web/）

```
web/
├─ index.html, submit.html
├─ css/        layout.css、各區塊 css、devtools.css
├─ js/         state.js、data.js、map.js、panels.js、submit.js、urlcheck.js、record.js、env.js、devtools.js
├─ data/       匯入程式產生的 JSON
└─ assets/     build_web_assets.py 產生的 WebP、icons.svg sprite
```

- 本機預覽用一支 `scripts/serve_web.py`。
- 照 SVG_COMPONENTS 的盤點表一個一個做，形式照表（HTML／模板／SVG／PNG）。
- 做完在瀏覽器實際打開，用尺寸模擬逐一量 RESPONSIVE_LAYOUT 的驗收清單，截圖給人看。
- 空狀態要有對應的文字（例如「這個市場還沒有攤商」），不要出現沒選項的選單或沒作用的按鈕。

## 5. 表單／補交頁

- 選單連動（例如縣市 → 市場 → 攤商），可以從總覽頁帶 `#vendor=` 進來預選。
- 欄位格式在前端檢查，錯誤訊息用白話。
- 紀錄格式（欄位、順序、時區）放在一個共用模組（`record.js`），前端、後端、CSV 匯出都用它，避免三處各寫一份。
- 後端還沒做之前用**模擬送出**：產生跟正式一樣的紀錄，存在瀏覽器，可以下載 CSV，連防重複都照做。正式環境在後端完成前一律不能送出。
- 註明會記錄什麼（例如時間和 IP）、用途是什麼。

## 6. 開發開關

- `env.js` 判斷開發環境：只有 `localhost`、`127.0.0.1`、`[::1]`、`*.localhost`、`*.test`。其他一律正式環境（要測 `localhost.example.com`、`127.0.0.2` 這類邊界）。
- 開發環境左下角有「開發」按鈕，面板裡每組開關對應 SVG_COMPONENTS 的「開關」欄：底圖、標籤、互動、統計、清單、表單送出方式（模擬／正式 API／關閉）。
- 設定存在 `localStorage`，兩頁共用；不是預設值時按鈕有提示點；底圖 SHA 不一致時有警告。
- **正式環境無法開啟**：不載入 `devtools.js`、不讀存著的設定，即使手動載入也不建立面板。這一點要寫測試。
- 用途：讓人可以一次只看一層，檢查「這個東西到底是哪個元件畫的」，也方便截圖驗收。
