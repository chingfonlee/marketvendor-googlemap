# 圖層架構（任務 3）

- 日期：2026-10-31
- 依據：[PLAN.md](PLAN.md) §2 畫面與互動、[SVG_COMPONENTS.md](SVG_COMPONENTS.md)、[BASEMAP_REVIEW.md](BASEMAP_REVIEW.md) §0
- 範圍：總覽頁的圖層、共用狀態、連動規則和檔案結構。版面尺寸和手機版排法屬於任務 5。

## 1. 頁面區塊

```
header        頁首：Logo、標題、分頁、補交入口
aside.left    左欄：進度卡（上）、篩選面板（下）
main.map      中間：地圖
aside.right   右欄：市場清單卡（上）、攤商清單（下）
```

四個區塊都讀同一份狀態（§3），彼此不直接呼叫。

## 2. 地圖的圖層

地圖由一個「地圖平面」組成。縮放和拖曳只對這個平面做 CSS `transform`，平面裡的圖層一起移動。

座標統一用底圖的 **viewBox `0 0 1024 1536`**。底圖之後換成 2048×3072 放大版也不用改座標。

由下到上：

| 層 | 元素 | 內容 | 來源 | 隨縮放移動 | 開關 |
|---|---|---|---|---|---|
| 1 | `<svg class="layer-base" viewBox="0 0 1024 1536">` | 底圖 `<image>` | `assets/map-base.webp`（由正式 PNG 轉出） | 是 | 底圖 |
| 2 | `<svg class="layer-future">`（空的） | 預留給未來的市場標記，第一版不放東西 | — | 是 | — |
| 3 | `<div class="layer-labels">` | 8 個縣市標籤 | `data/county-labels.json` | 位置會跟著移動，但標籤大小固定 | 縣市標籤 |
| 4 | `<div class="map-overlay">` | 地圖標語對話框、拿相機的貓、縮放按鈕、圖例 | HTML | **否**，固定在地圖框上 | 底圖（標語、貓）、互動（縮放）、縣市標籤（圖例） |

**為什麼標籤用 HTML 按鈕，不畫在 SVG 裡？**
- 標籤要能點、能用鍵盤選、讀屏軟體要唸得出來。`<button>` 原生就有這些功能。
- 中文字在 HTML 裡的排版和字型比 SVG `<text>` 穩定。
- 標籤的圖示（小攤車）仍然用 SVG `<symbol>`，符合元件化的原則。

**標籤的定位方式**
- 每個標籤用 `left: x/1024 %`、`top: y/1536 %` 放在平面上，跟著平面一起移動。
- 標籤再乘上 `scale(1 / 目前縮放倍率)`，所以地圖放大時標籤的大小不變，只是彼此分得更開。

**標語和貓**
- 放在左上預留的海面上，不跟著縮放。
- 地圖放大到 1.3 倍以上時淡出，避免蓋住地圖。

## 3. 共用狀態

全頁只有一份狀態，所有畫面都由它算出來：

```js
state = {
  county:   null,      // 縣市名稱，例如 "臺北市"；null 表示全台
  marketId: null,      // 市場 id，例如 "m01"；null 表示未選
  status:   "all",     // "all" | "verified" | "submitted" | "not_submitted"
  keyword:  "",        // 搜尋字
  page:     1,         // 攤商清單頁碼
  zoom:     { scale: 1, x: 0, y: 0 }
}
```

### 動作和規則

| 動作 | 觸發來源 | 狀態變化 |
|---|---|---|
| `selectCounty(c)` | 點地圖標籤、左側縣市選單、市場清單卡的縣市切換 | `county = c`，**`marketId = null`**，`page = 1` |
| `clearCounty()` | 縣市選單選「全部縣市」、點地圖空白處 | `county = null`，`marketId = null`，`page = 1` |
| `selectMarket(id)` | 點市場清單的一列、左側市場選單 | `marketId = id`，**`county` 同步成該市場所屬縣市**，`page = 1` |
| `setStatus(s)` | 狀態按鈕 | `status = s`，`page = 1` |
| `setKeyword(k)` | 搜尋框（輸入停 250ms 後才觸發） | `keyword = k`，`page = 1` |
| `setPage(n)` | 分頁器 | `page = n` |

- 點目前已選的縣市標籤：不變（不會取消選取）。要回到全台，用縣市選單或「回到全台」按鈕。
- 每次狀態改變，所有區塊依新狀態重畫。不寫「A 改了去通知 B」的程式，所以不會出現兩邊不同步。
- 狀態同步到網址 hash，例如 `#county=臺北市&market=m01&status=submitted`，重新整理或分享連結時可以還原畫面。

### 各區塊怎麼算

| 區塊 | 範圍 | 受哪些狀態影響 |
|---|---|---|
| 進度卡 | 有選縣市：該縣市；沒選：全台 | `county`。**不受** `status`、`keyword`、`marketId` 影響 |
| 地圖標籤 | 固定 8 個 | `county`：選中的標籤加選取光圈，其他標籤變淡 |
| 縣市選單 | 8 個縣市加「全部縣市 (8)」 | `county` |
| 市場選單 | 有選縣市：該縣市的市場；沒選：全部 15 個 | `county`、`marketId` |
| 狀態按鈕上的數字 | 跟攤商清單同一個範圍，但不套用狀態篩選 | `county`、`marketId`、`keyword` |
| 市場清單卡 | 有選縣市：該縣市的市場；沒選：全部 15 個，依縣市分組 | `county`、`marketId`（選中的列加底色） |
| 攤商清單 | 有選市場：該市場；只選縣市：該縣市；都沒選：全台。再套用狀態和搜尋 | 全部 |

攤商清單的標題跟著範圍改，例如「臺北永春市場・攤商清單 (20)」「臺北市・攤商清單 (61)」「全台・攤商清單 (347)」。

### 標籤的樣式狀態

| 狀態 | 條件 | 樣式 |
|---|---|---|
| 一般 | 沒選縣市 | 白色圓角卡片：內縮的藍色標頭（圖示＋全名），白底市場數和攤商數（[COUNTY_LABELS.md](COUNTY_LABELS.md) §1） |
| 滑過、鍵盤焦點 | 滑鼠移上或 Tab 選到 | 稍微放大，顯示焦點框 |
| 選取中 | `county` 等於這個縣市 | 一般樣式加上光圈 |
| 變淡 | 選了別的縣市 | **淺灰藍底、灰字，不用透明度**，避免透出底下的樹和山 |

## 4. 資料檔

都由匯入程式（任務 6）產生，網頁只讀：

| 檔案 | 內容 |
|---|---|
| `data/markets.json` | 15 個市場：id、名稱、縣市、類型、攤商數、各狀態數量 |
| `data/vendors.json` | 347 家：id、市場 id、店名、狀態、Google 地圖連結 |
| `data/county-labels.json` | 從 `design/assets/final/map-taiwan-base.labels.json` 複製過來：8 個標籤座標，以及底圖的 SHA-256 |
| `data/meta.json` | 最後更新時間、總數、資料來源版本 |

網頁載入時會檢查 `county-labels.json` 裡的底圖 SHA-256 和實際使用的底圖是否一致，不一致就在開發面板顯示警告。

## 5. 檔案結構

```
web/
  index.html          總覽頁
  submit.html         補交／確認頁（任務 8）
  css/
    tokens.css        色彩、字級、間距變數（來自 atoms/color-tokens.svg）
    layout.css        四個區塊的版面（任務 5）
    components.css    標籤、卡片、按鈕、清單
  js/
    state.js          狀態和動作（§3）
    data.js           讀取 JSON、計算各範圍的統計
    map.js            地圖平面、縮放拖曳、標籤
    panels.js         進度卡、篩選、市場清單、攤商清單
    devtools.js       開發開關（任務 9），只在開發環境載入
  data/               匯入程式產生的 JSON
  assets/
    map-base.webp     底圖（網頁用壓縮版）
    icons.svg         圖示 sprite（攤車、建築、外部連結、補交等）
    market-type/      3 張市場類型縮圖
    mascots/          吉祥物
scripts/
  import_excel.py     資料匯入（任務 6）
```

- 不用框架，原生 JavaScript 模組（`<script type="module">`）。
- 不需要打包工具；Cloudflare Pages 直接部署 `web/`。

## 6. 縮放

- 方式：「＋」「－」按鈕、滑鼠滾輪、觸控雙指縮放、拖曳平移。
- 範圍 1～3 倍；拖曳時地圖不能整個拖出畫面外。
- 「回到全台」按鈕：縮放倍率回到 1。只重設地圖位置，不清除篩選。
- 選了縣市**不會自動放大**，第一版保持簡單。

## 7. 驗收

1. 地圖由 §2 的 4 層組成，座標都是 viewBox `0 0 1024 1536`。
2. 標籤是 HTML 按鈕，鍵盤可以選取，地圖放大時大小不變。
3. 全頁只有一份狀態，§3 的 6 個動作和規則都寫清楚，尤其是「切換縣市就清掉市場」和「選市場會同步縣市」。
4. 每個區塊的計算範圍都定義清楚；進度卡不受狀態篩選影響。
5. 標籤 4 種樣式狀態都定義了，變淡不用透明度。
6. 資料檔和檔案結構和任務 6、7 對得上。
