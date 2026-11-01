# SVG 元件清單（任務 1，第二版）

- 日期：2026-10-31
- 依據：
  - 使用者提供的新版總覽畫面圖（2026-10-31）
  - [PLAN.md](PLAN.md)（畫面、狀態、任務）
  - [`design/REVIEW.md`](../design/REVIEW.md)（27 個 SVG 的審查，不重做）
- 範圍：前台總覽頁（桌機＋手機）和攤商補交／確認頁。管理版不在第一版範圍。
- 第一版的取代內容：A／B 案已經決定，用 A25 底圖加 8 個縣市標籤；市場標記移到未來；攤商詳細卡拿掉；狀態從 6 種改成 3 種。

## 0. 分類

- **固定**：直接沿用，版面或素材不用改。
- **調整**：有現成的 SVG 或素材，要改內容、配色或結構。
- **新增**：`design/` 裡沒有，要新做。
- 形式：
  - `HTML`：改成 HTML＋CSS，SVG 只當版面參考。
  - `SVG`：保留為 SVG。
  - `模板`：用 `<template>` 或 `<symbol>`，由 JS 產生實例。
  - `PNG`：直接用圖片。
- 開關：受哪一組開發開關控制（底圖／縣市標籤／互動／統計／清單／補交）。

## 1. 固定（直接沿用）

| 元件 | 來源 | 形式 | 開關 |
|---|---|---|---|
| 色彩變數 | `atoms/color-tokens.svg` | CSS 變數 | — |
| 線條圖示 | `atoms/icons.svg`（25 個） | SVG sprite | — |
| 按鈕樣式 | `atoms/buttons.svg` | HTML＋CSS | — |
| Logo | `final/logo-stall.png` | PNG | — |
| 吉祥物插畫 | `final/mascot-*.png`：左上卡片的女孩、地圖上拿相機的貓、左下拿大聲公的貓 | PNG | 統計／底圖／清單 |
| 空狀態、錯誤 | `final/empty-state.png`、`final/error-state.png` | HTML＋PNG | 清單 |
| 補交頁背景和標題 | `final/bg-form.png`、`final/hero-form-title.png`、`final/bg-login*.png` | PNG | 補交 |

吉祥物對應：

| 畫面位置 | 最接近的現有素材 |
|---|---|
| 左上女孩 | `mascot-girl-vendor.png` 或 `mascot-girl-stall.png` |
| 地圖上的貓 | `mascot-cat-map.png` |
| 左下的貓 | `mascot-cat-megaphone.png` |

這三組對應是我依檔名推的，**需要你目視確認**。

手機和平板直向的清單版沒有地圖（[RESPONSIVE_LAYOUT.md](RESPONSIVE_LAYOUT.md) §4.5）：拿相機的貓放在進度卡右上角，拿大聲公的貓和狀態說明放在頁尾，不放女孩。

## 2. 調整

| 元件 | 來源 | 形式 | 要改的地方 | 開關 |
|---|---|---|---|---|
| 頁首 | `components/header.svg` | HTML | 標題改成「國際友善力・台灣攤商地圖」，副標「夜市與市場 Google 地圖登錄成果平台」。分頁只放「地圖總覽」；「統計報表」「資料管理」2026-11-01 決定先不顯示，要做時再加回（PLAN §7）。右上主按鈕連到補交頁。手機和平板直向不顯示分頁 | — |
| 進度卡 | `components/progress-card.svg` | HTML＋SVG 圓環 | 圓環從 6 段改成 3 段（已完成、待確認、未提交）；中間是總攤商數；右側 3 行圖例，顯示數量和百分比；「最後更新」時間；插畫從廚師改成女孩 | 統計 |
| 狀態徽章 | `atoms/status-badges.svg` | HTML `<span data-status>` | 只留 3 種：已完成（綠）、待確認（黃）、未提交（紅），配色照畫面圖 | 清單 |
| 篩選面板 | `components/filter-panel.svg` | HTML | 搜尋框、縣市選單、**市場選單**（新增）、4 個狀態按鈕（全部、已完成、待確認、未提交），每個按鈕下方顯示數量；拿掉市場類型篩選 | 清單 |
| 攤商清單 | `components/merchant-table.svg` | HTML `<template>` | 搬到右下；標題「市場名・攤商清單 (N)」；欄位是攤商名稱、狀態、操作；有連結的顯示「開啟 Google 地圖」圖示，沒有連結的顯示「補交」圖示，連到補交頁並預先選好這家店；**不分頁**，全部列出、往下捲動，表頭固定（任務 5 決定 I） | 清單 |
| 補交表單卡片 | `components/login-card-default.svg`、`login-card-select-open.svg`、`pages/merchant-login-*.svg` | HTML | 從登入卡片改成補交卡片：拿掉密碼欄；改成縣市、市場、攤商三層選單；顯示目前的連結；「這是我的店」和「貼上正確網址」兩個操作；網址欄和格式錯誤提示；送出後顯示「已收到」 | 補交 |
| 縮放按鈕 | `components/map-view.svg` 裡的＋／－ | HTML | 放在地圖右下；另外支援滾輪、雙指縮放和「回到全台」 | 互動 |
| 選取光圈 | `atoms/map-pins.svg` 的「選取中」 | 模板 | 從圖釘改用在縣市標籤 | 縣市標籤 |
| 總覽頁版面 | `pages/overview-desktop.svg` | 參考 | 只當驗收參考，版面以新畫面圖和 [RESPONSIVE_LAYOUT.md](RESPONSIVE_LAYOUT.md) 為準。`overview-mobile.svg` 不再參考（手機改成不放地圖的清單版） | — |

## 3. 新增

| 優先 | 元件 | 形式 | 說明 | 開關 |
|---|---|---|---|---|
| P0 | **地圖底圖** | PNG | ✅ 已改用使用者提供的水彩底圖（2048×3072，座標用 viewBox 1024×1536，沒有縣市界線），見 [BASEMAP_REVIEW.md](BASEMAP_REVIEW.md) §0 | 底圖 |
| P0 | **縣市標籤** | HTML 按鈕＋SVG 圖示 | 8 個，照完成圖的圓角卡片：上方藍底白字名稱（加小攤車圖示），下方白底顯示市場數和攤商數。依量到的地圖顯示寬度切換：≥ 565px 用桌機卡，兩行「3 個市場／61 家攤商」；< 565px 用精簡卡，一行「3 市場・61 攤」。數字由 markets.json 計算。狀態有一般、滑過（不放大，只加深陰影和邊框）、選取中（光圈）、變淡（選了別的縣市）。標籤維持固定螢幕大小，見 [COUNTY_LABELS.md](COUNTY_LABELS.md)、[RESPONSIVE_LAYOUT.md](RESPONSIVE_LAYOUT.md) §3.4 | 縣市標籤 |
| P0 | **地圖標語** | HTML（疊在地圖上） | 「全台 15 個市場、347 家攤商、Google 地圖登錄進度」。數字會變動，所以**不能用 PNG**。現有的 A23 `map-headline-front.png` 文字不同，只能拿外框當參考。清單版沒有地圖，標語文字改當進度卡的標題，不畫對話框 | 底圖 |
| P0 | **市場清單卡** | HTML `<template>` | 右上。標頭：縣市名稱、「共 N 個市場｜N 家攤商」、**⌄ 切換縣市**（展開「全部縣市」加 8 個縣市，卡片本身不收合）。每列：縮圖、市場名稱、攤商數、「完成 n｜待確認 n｜未提交 n」、箭頭；選取中的列有底色。清單版：不顯示 ⌄；第一列是「全部市場」；全台時收起成一列展開按鈕 | 清單 |
| P0 | **縣市卡片格** | HTML 按鈕 | 只用在清單版（手機、平板直向）。9 張：「全台」＋8 個縣市，手機 3×3，寬度夠時一列 9 張；樣式同縣市標籤（藍色標頭＋兩行數字）；點縣市＝選縣市，點「全台」＝回到全台；選中的加光圈，其他不變淡。見 [RESPONSIVE_LAYOUT.md](RESPONSIVE_LAYOUT.md) §4.3 | 縣市標籤 |
| P0 | 市場縮圖 | PNG | 畫面圖是市場實景照片，但目前**沒有市場照片**。改用 3 張類型插畫：夜市、傳統市場、美食廣場・商圈，由網頁依市場類型自動套用。生圖規格見 `design/asset-briefs/market-type-thumbnails.md`（Codex 出圖） | 清單 |
| P1 | 狀態說明框 | HTML | 左下，3 行文字說明三種狀態。清單版改成狀態按鈕旁的「ⓘ 狀態說明」，點了才展開 | 清單 |
| P1 | 回到頂端按鈕 | HTML | 只用在清單版：捲過攤商清單標題後出現在右下角，44×44，點了回到縣市卡片 | 清單 |
| P1 | 地圖圖例 | HTML | 「縣市標籤：有參與（8 個）、未參與（無標籤）」。取代原本 `map-legend.svg` 的 6 種狀態圖例 | 縣市標籤 |
| P1 | 載入中 | HTML | 骨架畫面 | 清單 |
| P1 | 開發測試面板 | HTML | 6 個開關，只在開發環境載入 | — |

## 4. 第一版不用

| 項目 | 原因 |
|---|---|
| `merchant-detail-card*.svg`、`pages/detail-mobile.svg` | 詳細卡移到未來擴充；手機也不做底部面板，改成清單版 |
| `pages/overview-mobile.svg` | 手機改成不放地圖的清單版 |
| `atoms/map-pins.svg` 的圖釘（選取光圈除外） | 不做市場和攤商圖釘 |
| `atoms/contact-badges.svg` | 聯繫狀態不在第一版 |
| `components/map-legend.svg` | 6 種狀態圖例改成縣市圖例 |
| `components/admin-*.svg`、`pages/admin-map-desktop.svg` | 管理版不在第一版 |
| `final/map-taiwan-market.png`（A01）、`final/map-city-labels.png`（A22） | 底圖改用重做的 A25 |
| `final/category/*.png` 品類圖示 | 正式 Excel **沒有品類欄位**，沒辦法對應每家店。畫面圖每列前面的食物圖示先拿掉；以後補了品類資料再加回 |

## 5. 素材替換表（設計稿暫用 → 正式）

| 暫用素材 | 正式 | 狀態 |
|---|---|---|
| `assets/map-taiwan.png` | A25 重做版 | 等任務 2 |
| `assets/logo-stall.png` | `final/logo-stall.png` | 可替換 |
| `assets/mascot-chef.png` | 女孩插畫（見 §1） | 待你確認 |
| `assets/mascot-cat-wave.png` | `final/mascot-cat-map.png`、`mascot-cat-megaphone.png` | 待你確認 |
| `assets/food/*.png` | 不用（沒有品類資料） | — |
| `assets/stall-photo-sample.png`、`minimap-sample.png`、`map-corner.png` | 不用 | — |
| `map-view.svg` 的標語對話框 | HTML 標語 | 要新做 |

## 6. 開發開關對應

| 開關 | 控制的元件 |
|---|---|
| 底圖 | 底圖、地圖標語、地圖上的貓 |
| 縣市標籤 | 縣市標籤圖層、地圖圖例、清單版的縣市卡片格 |
| 互動 | 點選、縮放、地圖和選單的連動。關掉時地圖、縣市卡片、選單、搜尋、狀態按鈕、市場清單都不能操作，畫面停在目前的篩選；攤商清單的連結照常可以點 |
| 統計 | 進度卡 |
| 清單 | 篩選面板、市場清單卡、攤商清單、空狀態 |
| 補交 | 補交頁的送出方式：模擬送出（預設）／正式 API（`POST /api/submissions`，任務 12 才建立）／關閉（和目前正式環境一樣） |

- 開啟方式：本機預覽時畫面左下角有「開發」按鈕，點開是開關面板。有開關不是預設值時按鈕上有橘點；底圖和 `county-labels.json` 的 SHA-256 不一致時按鈕上有紅色驚嘆號，面板裡顯示警告。
- 設定存在瀏覽器（`localStorage` 的 `gm-dev`），總覽頁和補交頁共用，重新整理後還在。補交頁換送出方式會自動重新載入。
- 「開發環境」指網址是 `localhost`、`127.0.0.1`、`[::1]`、`*.localhost`、`*.test`（`web/js/env.js`）。其他網址一律是正式環境：不載入 `devtools.js`、不讀存著的設定、補交頁不能送出（任務 12 建好後端後改成正式 API）。
