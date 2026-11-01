# 統計頁示意圖（給 GPT 圖片生成）

- 日期：2026-11-01
- 用途：先看「比例類統計圖表」的整體畫面方向，確認之後才做網頁。**這張只是示意圖，不是正式素材**，所以可以畫文字和數字；正式網頁的數字一律由程式產生。
- 數字來源：`web/data/markets.json`、`meta.json`（2026-10-31 匯入，347 家）。生圖工具常把數字畫錯，只要版面和風格對就好，數字之後由網頁算。

## 版本紀錄

| 版本 | 檔案 | 結果 |
|---|---|---|
| v1 | `design/reference/stats-mockup-v1.png` | 畫風、配色、文字都通過。**縣市長條紅色沒填到底，多一段灰色**，各條總長不一樣 |
| v2 | 存成 `design/reference/stats-mockup-v2.png`（桌機）、`stats-mockup-v2-mobile.png`（手機） | 已修正 Card 2 的提示詞：每條長條總長相同，黃＋紅填滿，沒有灰底。桌機版和手機版這次一起生 |

v1 另外兩個小問題（「已完成 0」看不到綠色、右上角街景太擠）之後在網頁上處理，**不用為了這兩點重新生圖**。

v2 的手機版也一起附上 v1 桌機圖 `C:\Users\user\claudecode\googlemap-store\.claude\worktrees\vendor-confirm-screen-visual-388349\design\reference\stats-mockup-v1.png` 當參考，讓兩個尺寸的畫風一致。

## 要附上的參考圖

生圖時一起上傳，讓畫風一致：

1. `C:\Users\user\claudecode\googlemap-store\design\assets\final\mascot-cat-map.png`：吉祥物貓
2. `C:\Users\user\claudecode\googlemap-store\design\assets\final\logo-stall.png`：攤車 Logo
3. `C:\Users\user\claudecode\googlemap-store\design\asset-briefs\refs\overview-mockup-v1.webp`：總覽頁，看整體配色和卡片樣式
4. （選用）`C:\Users\user\claudecode\googlemap-store\design\assets\final\mascot-cat-megaphone.png`：拿大聲公的貓，第 4 張卡片用

## 畫面裡要有的 4 張圖表

| 區塊 | 圖表 | 內容 |
|---|---|---|
| ① 全台進度 | 甜甜圈圖 | 中間大字「62.5%」，小字「已提交 217／347 家」。三色：已完成 0（綠）、待確認 217（黃）、未提交 130（紅） |
| ② 各縣市比例 | 8 條橫向 100% 堆疊長條，依已提交比例由高到低排 | 高雄市 85%、新北市 78%、新竹市 76%、臺北市 74%、臺南市 60%、臺中市 55%、臺東縣 43%、桃園市 29% |
| ③ 市場類型比較 | 3 個小甜甜圈並排，各配一個小插圖 | 夜市 61%（燈籠）、傳統市場 58%（菜籃）、美食廣場 80%（桌椅） |
| ④ 待加強市場 | 3 張小卡片，每張有一條小進度條 | 永春市場 4/20、興國公有零售市場 4/20、臺東市觀光夜市 21/49 |

## Prompt

```
A cute, friendly statistics dashboard web page mockup for a Taiwanese market-vendor Google Maps project, desktop landscape 16:10 (1600×1000).

STYLE: match the attached mascot and logo exactly — cute chibi illustration style, thick dark-brown outlines (#3B2A1A), flat colors with soft cel shading, rounded shapes, warm and playful. Page background light sky blue (#D6F3FD) with a few soft hand-drawn clouds. Content sits on white rounded cards (16px radius, soft blue shadow). Accent orange #F08A3C, primary blue #1F6FE5. Status colors used consistently in every chart: green #22A06B = 已完成, yellow #F2B200 = 待確認, red #E5484D = 未提交. Chart shapes are chunky and rounded (rounded bar ends, thick donut rings), like a children's picture book infographic, but still clean and easy to read.

HEADER: the attached stall-cart logo at top-left with the title "臺灣攤商地圖・統計報表". Tabs "地圖總覽" / "統計報表"（selected, blue underline）.

LAYOUT (2×2 grid of cards):

Card 1 (top-left, largest) title "全台登錄進度": a big thick donut chart. Center text large "62.5%", small text below "已提交 217／347 家". Segments: yellow 217, red 130, green 0. Legend under it with colored dots: "已完成 0", "待確認 217", "未提交 130". The attached cat mascot peeks from the card corner holding a small map, cheering.

Card 2 (top-right) title "各縣市提交比例": 8 horizontal 100% stacked bars sorted high to low, county name on the left and percentage on the right: 高雄市 85%, 新北市 78%, 新竹市 76%, 臺北市 74%, 臺南市 60%, 臺中市 55%, 臺東縣 43%, 桃園市 29%. IMPORTANT: every bar has exactly the same total length and all bars start and end at the same x positions, forming a perfect aligned rectangle. Each bar has only two segments: yellow from the left edge up to the percentage, then red from there all the way to the right edge. The red segment always reaches the right end of the bar. No grey track, no empty background part, no third color, no gap after the red. Example: 高雄市 = 85% yellow + 15% red; 桃園市 = 29% yellow + 71% red. Rounded ends only on the outer left and right ends of each bar. Tiny cute crown icon next to the top one.

Card 3 (bottom-left) title "市場類型比較": three small donut charts in a row, each with a tiny cute icon above it — red paper lantern for "夜市 61%", bamboo vegetable basket for "傳統市場 58%", round table and chairs for "美食廣場 80%".

Card 4 (bottom-right) title "待加強市場": three small rounded cards stacked, each with a market name, a short chunky progress bar and a fraction: "永春市場 4/20", "興國公有零售市場 4/20", "臺東市觀光夜市 21/49". A small encouraging cat mascot with a megaphone beside them.

All text in Traditional Chinese, clear rounded sans-serif font, exactly as written above, no extra words. Generous white space, aligned grid, readable at a glance.
```

## Negative prompt

工具不支援負面提示詞時，改寫成「不要……」接在 Prompt 後面。

```
grey bar track, empty bar remainder, bars of different total lengths, realistic photo, 3D render, glossy gradients, dark mode, cluttered layout, tiny unreadable text, simplified Chinese, English labels, gibberish characters, extra charts, pie chart with 3D tilt, neon colors, harsh shadows, watermark, signature, brand logos, Google logo
```

## 手機版（v2 和桌機版一起生）

把 Prompt 第一段的尺寸改成 `mobile portrait 9:19.5 (1080×2340)`，`LAYOUT` 改成：

```
LAYOUT (single column, cards stacked top to bottom): Card 1 full width, then Card 2, then Card 3 (three donuts in one row, smaller), then Card 4. Header compact with logo and title only.
```

## 看圖時確認這幾點

1. 畫風和吉祥物、Logo 是同一套嗎？（深咖啡粗描邊、平塗、圓潤）
2. 三種狀態的顏色每張圖都一樣嗎？（綠、黃、紅）
3. 甜甜圈、橫條、小卡片這三種比例圖，哪一種最好讀？要不要換掉其中一種？
4. 可愛的程度剛好嗎？還是吉祥物、小圖示太多，搶了數字的位置？
5. 4 張卡片的排法，是你想放在網站上的樣子嗎？
