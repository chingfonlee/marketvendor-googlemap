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

## 2. 調整

| 元件 | 來源 | 形式 | 要改的地方 | 開關 |
|---|---|---|---|---|
| 頁首 | `components/header.svg` | HTML | 標題改成「國際友善力・台灣攤商地圖」，副標「夜市與市場 Google 地圖登錄成果平台」。分頁「地圖總覽、統計報表、資料管理」中，第一版只有地圖總覽能用，另外兩個顯示為停用。右上主按鈕連到補交頁 | — |
| 進度卡 | `components/progress-card.svg` | HTML＋SVG 圓環 | 圓環從 6 段改成 3 段（已完成、待確認、未提交）；中間是總攤商數；右側 3 行圖例，顯示數量和百分比；「最後更新」時間；插畫從廚師改成女孩 | 統計 |
| 狀態徽章 | `atoms/status-badges.svg` | HTML `<span data-status>` | 只留 3 種：已完成（綠）、待確認（黃）、未提交（紅），配色照畫面圖 | 清單 |
| 篩選面板 | `components/filter-panel.svg` | HTML | 搜尋框、縣市選單、**市場選單**（新增）、4 個狀態按鈕（全部、已完成、待確認、未提交），每個按鈕下方顯示數量；拿掉市場類型篩選 | 清單 |
| 攤商清單 | `components/merchant-table.svg` | HTML `<template>` | 搬到右下；標題「市場名・攤商清單 (N)」；欄位是攤商名稱、狀態、操作；有連結的顯示「開啟 Google 地圖」圖示，沒有連結的顯示「補交」圖示，連到補交頁並預先選好這家店；分頁器 | 清單 |
| 補交表單卡片 | `components/login-card-default.svg`、`login-card-select-open.svg`、`pages/merchant-login-*.svg` | HTML | 從登入卡片改成補交卡片：拿掉密碼欄；改成縣市、市場、攤商三層選單；顯示目前的連結；「這是我的店」和「貼上正確網址」兩個操作；網址欄和格式錯誤提示；送出後顯示「已收到」 | 補交 |
| 縮放按鈕 | `components/map-view.svg` 裡的＋／－ | HTML | 放在地圖右下；另外支援滾輪、雙指縮放和「回到全台」 | 互動 |
| 選取光圈 | `atoms/map-pins.svg` 的「選取中」 | 模板 | 從圖釘改用在縣市標籤 | 縣市標籤 |
| 總覽頁版面 | `pages/overview-desktop.svg`、`overview-mobile.svg` | 參考 | 只當驗收參考，版面以新畫面圖為準 | — |

## 3. 新增

| 優先 | 元件 | 形式 | 說明 | 開關 |
|---|---|---|---|---|
| P0 | **地圖底圖** | PNG | A25 需要重做，見 [BASEMAP_REVIEW.md](BASEMAP_REVIEW.md) | 底圖 |
| P0 | **縣市標籤** | 模板（SVG 圖層） | 8 個，只顯示名稱：藍底白字加小攤車圖示（照畫面圖的標頭部分）。狀態有一般、滑過、選取中（光圈）、變淡（選了別的縣市）。跟底圖同一個 viewBox，標籤維持固定螢幕大小 | 縣市標籤 |
| P0 | **地圖標語** | HTML（疊在地圖上） | 「全台 15 個市場、346 家攤商、Google 地圖登錄進度」。數字會變動，所以**不能用 PNG**。現有的 A23 `map-headline-front.png` 文字不同，只能拿外框當參考 | 底圖 |
| P0 | **市場清單卡** | HTML `<template>` | 右上。標頭：縣市名稱、「共 N 個市場｜N 家攤商」、收合按鈕。每列：縮圖、市場名稱、攤商數、「完成 n｜待確認 n｜未提交 n」、箭頭；選取中的列有底色 | 清單 |
| P0 | 市場縮圖 | PNG | 畫面圖是市場實景照片，但目前**沒有市場照片**。第一版先用夜市和傳統市場兩種類型插畫代替（DECISIONS 的燈籠攤車、遮雨棚加菜籃），需要生圖 | 清單 |
| P1 | 狀態說明框 | HTML | 左下，3 行文字說明三種狀態 | 清單 |
| P1 | 地圖圖例 | HTML | 「縣市標籤：有參與（8 個）、未參與（無標籤）」。取代原本 `map-legend.svg` 的 6 種狀態圖例 | 縣市標籤 |
| P1 | 手機底部面板 | HTML | 可拖拉，依序是市場清單 → 攤商清單，有返回鍵。外框可參考 `pages/detail-mobile.svg` | 清單 |
| P1 | 載入中 | HTML | 骨架畫面 | 清單 |
| P1 | 開發測試面板 | HTML | 6 個開關，只在開發環境載入 | — |

## 4. 第一版不用

| 項目 | 原因 |
|---|---|
| `merchant-detail-card*.svg`、`pages/detail-mobile.svg` 的詳細卡內容 | 詳細卡移到未來擴充 |
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
| 縣市標籤 | 縣市標籤圖層、地圖圖例 |
| 互動 | 點選、縮放、地圖和選單的連動 |
| 統計 | 進度卡 |
| 清單 | 篩選面板、市場清單卡、攤商清單、空狀態 |
| 補交 | 補交頁（模擬送出／正式 API） |
