# 統計頁：SVG 拆分與素材清單

- 日期：2026-11-01
- 設計來源：`design/reference/stats-mockup-v2.png`（桌機 1586×992）、`stats-mockup-v2-mobile.png`（手機 933×1685）
- 提示詞紀錄：`stats-mockup-prompt.md`
- 原則跟現有素材一樣（`README.md` §二）：**插畫是固定素材，不能有字；所有文字、數字、比例圖都由網頁產生。**
- 不要從示意圖直接裁切素材：示意圖是不透明的 RGB，解析度也不夠，裁下來會帶到背景。要用的圖都用現有素材，或照本文件重新生成。

---

## 一、整頁拆解

| 區塊 | 元素 | 分類 | 做法 |
|---|---|---|---|
| 頁首 | 攤車 Logo | 固定・**已有** | `web/assets/logo.webp` |
| | 標題「臺灣攤商地圖・統計報表」 | 動態（文字） | 網頁文字，和總覽頁頁首共用 |
| | 分頁「地圖總覽／統計報表」 | 動態（文字＋狀態） | 網頁按鈕，圖示用 `icons.svg` 的 `home`、`chart`。**手機版也要有**（示意圖手機版漏掉了） |
| | 右上街景（101、廟、攤車） | 固定・**要補圖** | S04，選用，見 §三 |
| 背景 | 天空藍底 | 固定 | CSS `--page: #D6F3FD` |
| | 雲朵 | 固定 | 手寫 SVG（`atoms/decor.svg` 的 `cloud`），不用生圖 |
| | 左下、右下樹叢 | 固定・**要補圖** | S05，一張左下，右下用 CSS 左右翻轉 |
| ① 全台登錄進度 | 卡片、標題列 | 固定（樣式） | 和 `progress-card.svg` 同一套卡片 |
| | 卡片標題圖示（長條圖） | 固定・**已有** | `icons.svg` 的 `chart` |
| | 甜甜圈圖 | **動態** | SVG `circle` + `stroke-dasharray`，依三種狀態家數計算 |
| | 中間「62.5%」「已提交 217／347 家」 | **動態** | 網頁文字 |
| | 圖例（已完成／待確認／未提交＋家數） | **動態** | 色點用 CSS，文字和數字由網頁產生 |
| | 拿地圖的貓 | 固定・**已有** | `web/assets/mascots/cat-camera.webp`（來源 `mascot-cat-map.png`） |
| ② 各縣市提交比例 | 卡片標題圖示 | 固定・**已有** | `icons.svg` 的 `chart` |
| | 8 條 100% 堆疊長條 | **動態** | 每列一條長條，分**綠、黃、紅三段**，寬度照三種狀態的家數比例（§五）。示意圖只看得到黃紅兩段，是因為目前已完成是 0。縣市數量和排序都由資料決定 |
| | 縣市名稱、百分比 | **動態** | 網頁文字 |
| | 第一名的皇冠 | 固定 | 手寫 SVG 圖示 `crown`，加進 `icons.svg`，不用生圖 |
| ③ 市場類型比較 | 卡片標題圖示（圓餅） | 固定 | 手寫 SVG 圖示 `pie`，加進 `icons.svg` |
| | 3 個小甜甜圈＋百分比 | **動態** | 和 ① 用同一個甜甜圈組件 |
| | 類型名稱「夜市／傳統市場／美食廣場」 | **動態** | 網頁文字，對應 `markets.json` 的 `type` |
| | 燈籠、菜籃、桌椅圖示 | 固定・**要補圖** | S01～S03，見 §三 |
| ④ 待加強市場 | 卡片標題圖示（標靶） | 固定・**已有** | `icons.svg` 的 `target` |
| | 市場卡片（名稱、進度條、4/20） | **動態** | 網頁產生；列出哪幾個市場、幾個，由程式依比例排序決定 |
| | 每張卡片左邊的小攤位圖示 | 固定・**用 S01～S03** | 依該市場的類型套用，不另外畫攤位。示意圖裡三個顏色不同的小攤位只是裝飾，跟資料沒有關係 |
| | 拿大聲公的貓 | 固定・**已有** | `web/assets/mascots/cat-megaphone.webp`。手機版縮小或拿掉，讓卡片滿版 |

### 總結

- **已有，直接用**：Logo、兩隻貓、`chart`／`home`／`target` 圖示
- **手寫 SVG，不用生圖**：雲朵、皇冠 `crown`、圓餅 `pie`、所有圖表、色點、卡片
- **要補圖（共 5 張，見 §三）**：S01～S03 市場類型圖示（必要）、S04 頁首街景（選用）、S05 樹叢（選用）
- **全部動態**：標題、分頁、所有數字、百分比、縣市名稱、市場名稱、類型名稱、圖表本身

---

## 二、SVG 組件拆分

照現有 `design/svg/` 的結構新增，座標和整頁一致：

```
StatsPage
├─ Header（沿用 components/header.svg，分頁改成「統計報表」選中）
├─ StatsOverviewCard ......... components/stats-overview-card.svg   ①
│  ├─ DonutChart（3 段）
│  ├─ StatusLegend（3 列）
│  └─ Mascot（cat-camera）
├─ CountyRatioCard ........... components/stats-county-card.svg     ②
│  └─ RatioBar × N（縣市名、黃紅堆疊條、百分比；第一名加 crown）
├─ MarketTypeCard ............ components/stats-type-card.svg       ③
│  └─ TypeDonut × 3（S01～S03 圖示、類型名、小甜甜圈）
└─ WeakMarketsCard ........... components/stats-weak-card.svg       ④
   ├─ WeakMarketRow × N（類型圖示、市場名、進度條、分數）
   └─ Mascot（cat-megaphone）

atoms/
├─ icons.svg ＋ crown、pie
├─ ratio-bar.svg：100% 堆疊長條（附 0%、29%、85%、100% 四種示範）
└─ decor.svg：cloud

pages/
├─ stats-desktop.svg：2×2 卡片
└─ stats-mobile.svg：單欄，順序 ①②③④
```

**要特別處理的狀態**（SVG 要各畫一個示範）：

1. **已完成是 0**：甜甜圈裡沒有綠色。圖例的「已完成 0」要保留，旁邊加一行小字「審核中」，不然讀者會找不到綠色。**已完成大於 0 時，這行小字自動消失。**
2. **長條 0% 和 100%**：0% 整條都是紅色，100% 整條是黃色加綠色，沒有紅色。圓角只畫在整條的左右兩端，不能在中間斷開。
3. **三段都有的長條**：例如綠 20%、黃 50%、紅 30%，給以後已完成增加時使用。
4. **市場名稱太長**：例如「興國公有零售市場」，在手機版要能完整顯示，必要時換行，不要截斷。

---

## 三、補圖提示詞

### 共通規格

- 畫風照現有吉祥物。生圖時一起上傳這 3 張參考圖：
  - `C:\Users\user\claudecode\googlemap-store\design\assets\final\mascot-cat-map.png`
  - `C:\Users\user\claudecode\googlemap-store\design\assets\final\logo-stall.png`
  - `C:\Users\user\claudecode\googlemap-store\.claude\worktrees\vendor-confirm-screen-visual-388349\design\reference\stats-mockup-v2.png`（看各圖示在畫面裡的樣子和大小）
- 全部是**透明背景 PNG**，四個角落要完全透明，物件外圍不能有白邊或光暈。
- **不能有任何文字、數字、字母或商標。**
- 候選圖存到 `design/assets/generated/stats-*.png`，使用者確認後再存到 `design/assets/final/stats/`。

共用風格句（每張 Prompt 前面都要加）：

```
cute chibi illustration matching the attached cat mascot and stall-cart logo exactly: thick dark-brown outlines (#3B2A1A), flat colors with soft cel shading, rounded chunky shapes, warm friendly palette (orange #F08A3C, lantern red #E5484D, warm yellow #F2B200, cream #FFF8E6, grass green #7CC46A, sky blue #6DD7F2), clean crisp line art, isolated single object on a fully transparent background, no ground shadow, no text, no letters, no numbers, no logos.
```

共用負面提示詞：

```
text, letters, words, Chinese characters, numbers, logo, watermark, signature, background, white background, scenery, frame, border, drop shadow, realistic, photorealistic, 3D render, glossy gradient, thin sketchy lines, blurry, cropped object
```

### S01～S03：市場類型圖示（必要）

三張是一組，要並排放在一起看。三張的視角（正面略俯視）、描邊粗細、大小和留白都要一致。

| 編號 | 檔名 | 尺寸 | 場景 Prompt（接在共用風格句後面） |
|---|---|---|---|
| S01 | `stats-type-night_market.png` | 512×512 | `A single round red Chinese paper lantern with a golden top cap and a short yellow tassel, glowing softly, with 4 short yellow sparkle strokes around it. Front view, centered.` |
| S02 | `stats-type-traditional_market.png` | 512×512 | `A single woven bamboo basket full of fresh vegetables and fruits: green leafy greens, a carrot, red tomatoes, a bell pepper. Front view slightly from above, centered.` |
| S03 | `stats-type-other.png` | 512×512 | `A small round wooden food-court table with three round wooden stools around it, a small cup holder with chopsticks on the table. Front view slightly from above, centered.` |

規格：

- 物件放在中間，**四邊各留約 10% 空白**，三張物件的大小要差不多。
- 會縮小到 **40×40**（④ 的列表）和 **72×72**（③ 的卡片）使用，縮小後要看得懂：形狀簡單、色塊大，不要太多細節。
- 燈籠用紅色、菜籃用綠色、桌椅用木頭色，讓三張一眼分得出來。

### S04：頁首街景（選用）

做不做由使用者決定。不做的話，頁首就只放 Logo、標題和分頁。

| 編號 | 檔名 | 尺寸 |
|---|---|---|
| S04 | `stats-header-scene.png` | 1200×240，透明背景 |

```
（共用風格句）A wide horizontal strip of a cute Taiwanese street skyline: from left to right a few green round trees, a small traditional temple gate with red pillars and an orange curved roof, small market stalls with striped awnings, and Taipei 101 tower slim and pastel blue in the far back on the right. Everything sits on one flat baseline at the bottom edge. The left 40% of the image is completely empty and transparent, objects gradually appear toward the right. Soft pastel colors, lighter and less saturated than the mascot so it stays in the background.
```

規格：左邊 40% 完全留空（標題會疊在上面），底部切齊，沒有地面或草皮。

### S05：角落樹叢（選用）

| 編號 | 檔名 | 尺寸 |
|---|---|---|
| S05 | `stats-corner-bush.png` | 640×480，透明背景 |

```
（共用風格句）A cluster of round fluffy green bushes for the bottom-left corner of a web page, with a few small white five-petal flowers. The bushes touch the left edge and the bottom edge of the image and fade into rounded shapes toward the upper right. The upper-right half of the image is completely empty and transparent.
```

規格：物件貼齊左邊和下邊；右下角的樹叢由網頁把這張左右翻轉使用，所以畫面不能有方向性的東西（例如光源、文字）。

---

## 四、素材驗收

1. 所有 PNG 都是透明背景，四個角落完全透明，沒有白邊。
2. 沒有任何文字、數字、字母或商標。
3. S01～S03 縮到 40×40 時，還分得出燈籠、菜籃和桌椅。
4. S01～S03 放在一起時，大小、描邊和視角都一致。
5. 畫風和兩隻貓、攤車 Logo 是同一套。
6. S04 左邊 40% 是空的；S05 右上半邊是空的。

---

## 五、資料綁定：圖表跟著資料自動調整

統計頁**不寫死任何數字、縣市、市場或比例**。網頁只讀 `web/data/markets.json`，每個市場的 `counts` 有三種狀態的家數，所有數字都從這裡加總算出來。Excel 重新匯入之後，不用改程式，圖表就會自動更新。

### 1. 名詞定義

| 名詞 | 算法 |
|---|---|
| 總數 | `verified + submitted + not_submitted` |
| 已提交 | `verified + submitted`（已完成也算已提交） |
| 已提交比例 | 已提交 ÷ 總數 |

### 2. 每張圖表怎麼算

| 圖表 | 範圍 | 怎麼畫 | 會跟著變的地方 |
|---|---|---|---|
| ① 大甜甜圈 | 全部市場加總 | 綠、黃、紅三段，弧長 = 各狀態家數 ÷ 總數 × 圓周 | 三段的比例、中間的百分比、「已提交 X／Y 家」、圖例的家數 |
| ② 縣市長條 | 依 `county` 分組加總 | 綠、黃、紅三段，寬度 = 各狀態家數 ÷ 該縣市總數 × 100% | 每段的寬度、右邊的百分比、**有幾列**（縣市增減）、**排序** |
| ③ 類型小甜甜圈 | 依 `type` 分組加總 | 和 ① 同一個組件 | 三段的比例、百分比、**有幾個**（某類型沒有市場時就不顯示） |
| ④ 待加強市場 | 每個市場 | 和 ② 同一個長條組件；右邊顯示「已提交／總數」 | 進度條寬度、分數、**列出哪些市場** |

### 3. 排序和挑選規則

- **② 縣市排序**：已提交比例由高到低。比例相同時，總數多的排前面；再相同就照縣市名稱排。
- **② 皇冠**：給比例最高的縣市；如果有好幾個縣市並列第一，**每個都有皇冠**。
- **④ 待加強市場**：已提交比例**最低的 3 個**市場。比例相同時，未提交家數多的排前面。
  - 比例 100% 的市場不列入，所以有可能不到 3 個。
  - 如果全部市場都 100%，就不顯示列表，改顯示一句「所有市場都已提交」，大聲公貓保留。
  - 要改成列 5 個，只要改一個設定值，不要寫死在畫面裡。

### 4. 數字顯示

- **① 中間的大字**：顯示到小數點一位，例如 62.5%。
- **其他百分比**：四捨五入到整數，例如 85%。
- **長條和甜甜圈的寬度**：用**沒有四捨五入的原始比例**，這樣三段加起來剛好是 100%，不會多出空白或超出去。
- **很小的段**：家數大於 0 但算出來不到 2px 時，至少畫 2px，讓人看得到有這一段；家數是 0 的段完全不畫。

### 5. 特殊狀況

| 狀況 | 顯示 |
|---|---|
| 已完成 = 0 | 不畫綠色段；① 的圖例「已完成 0」旁邊加小字「審核中」 |
| 已完成 > 0 | 每張圖都自動出現綠色段，「審核中」小字消失 |
| 某縣市或某類型總數是 0 | 那一列或那一個甜甜圈不顯示 |
| 全部總數是 0（資料讀不到） | 整頁顯示現有的 `empty-state.webp`，不畫圖表 |
| 出現新的市場類型（不是 night_market／traditional_market／other） | 類型名稱用「其他」，圖示用 S03 |
| 縣市變多（超過 8 個） | ② 長條往下增加，卡片跟著變高；桌機版右邊卡片變高時，左邊卡片不跟著拉長 |

### 6. 測試

實作時要寫自動測試，用**假資料**確認圖表會跟著變，不能只用目前的真實資料測：

1. 目前資料：62.5%、各縣市百分比、待加強 3 個市場，都和示意圖一樣。
2. 把某市場的 `verified` 改成大於 0：綠色段出現，「審核中」消失，已提交比例照算法包含已完成。
3. 某縣市比例改成 0% 和 100%：長條全紅、沒有紅色，排序跟著變。
4. 兩個縣市比例一樣：排序照規則，皇冠規則正確。
5. 全部市場 100%：④ 顯示「所有市場都已提交」。
6. 加一個新縣市、新類型：② 多一列，新類型歸到「其他」。
7. 每一條長條、每一個甜甜圈，三段加起來都等於 100%。
