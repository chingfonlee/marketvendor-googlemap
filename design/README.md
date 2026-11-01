# 台灣攤商地圖：設計稿與組件拆分

設計來源：`reference/mockup.webp`（1536×1024 桌機版）。
SVG 由 `tools/build_svg.py` 產生，插畫由 `tools/crop_assets.py` 從設計圖裁切。修改設計請改產生器後重跑，不要直接手改 SVG：

```bash
python design/tools/crop_assets.py
python design/tools/build_svg.py
python design/tools/build_stats_svg.py   # 統計報表頁（讀 web/data/markets.json）
```

## 資料夾

| 路徑 | 內容 |
|---|---|
| `svg/pages/` | 整頁：`overview-desktop.svg`、`overview-mobile.svg`、`detail-mobile.svg` |
| `svg/components/` | 頁面上的區塊組件，座標與整頁相同 |
| `svg/atoms/` | 狀態徽章、圖釘、按鈕、圖示、色彩 tokens |
| `assets/` | 從設計圖裁切的插畫（PNG），SVG 以相對路徑引用 |
| `reference/` | 原始設計圖 |

## 組件樹（地圖總覽頁）

```
AppShell
├─ Header ................................ components/header.svg
│  ├─ Logo（logo-stall.png + 標題 + 標語）
│  ├─ NavTabs：地圖總覽 / 攤商列表 / 統計報表
│  ├─ Button.primary「我是攤商，補上我的Google地圖連結」→ 攤商自填頁
│  └─ Button.secondary「管理者登入」
├─ Sidebar（左欄）
│  ├─ ProgressCard ....................... components/progress-card.svg
│  │  ├─ DonutChart（6 種狀態）
│  │  └─ StatusLegend（數量 + 百分比）
│  ├─ FilterPanel ........................ components/filter-panel.svg
│  │  ├─ SearchInput（店名或夜市）
│  │  ├─ StatusChips（全部 + 6 種狀態）
│  │  └─ CountySelect
│  └─ MerchantTable ...................... components/merchant-table.svg
│     ├─ MerchantRow × 8（食物圖示、店名、夜市、StatusBadge）
│     └─ Pagination
├─ MapView（中間）........................ components/map-view.svg
│  ├─ 手繪地圖底圖（map-taiwan.png）
│  ├─ HeadlineBubble「全台夜市美食地圖」
│  ├─ MapPin × N（依狀態上色，選取中有光圈）
│  ├─ MapLegend ........................... components/map-legend.svg
│  └─ ZoomControls
└─ MerchantDetailCard（右側浮動）......... components/merchant-detail-card.svg
   ├─ 攤位照片 + 關閉鈕                     （缺項版：merchant-detail-card-incomplete.svg）
   ├─ 店名 + StatusBadge（含圖示）
   ├─ 夜市標籤、縣市標籤
   ├─ MiniMap + 「Google 地圖上查看」
   ├─ InfoRows：店名、夜市、地圖連結、Place ID（可複製）、最後檢查時間
   └─ CheckResultBanner（通過 / 缺項，依狀態變色）
```

### 手機版（390 寬）的差異

- 頁首只留 Logo 和選單鈕，「管理者登入」收進選單。
- 「我是攤商」按鈕放在頁首下方，全寬顯示。
- NavTabs 改成分段切換。
- 版面改成單欄：進度卡 → 地圖 → 篩選 → 清單。
- 狀態 Chip 改成可橫向捲動的一列。
- 清單改成卡片，夜市和縣市合併成一行。
- 點地圖圖釘或清單項目時，詳細資料改用底部面板（`detail-mobile.svg`），底部有「在 Google 地圖開啟」按鈕。

## 狀態（6 種）

前端、資料庫、Worker 都用同一組 key。

| key | 顯示 | 主色 | 淺底 | 文字 | 圖釘符號 | 誰寫入 |
|---|---|---|---|---|---|---|
| `verified` | 已完成 | `#22A06B` | `#DDF5E8` | `#12744A` | ✓ | 核對程式 |
| `submitted` | 已提交 | `#3B82F6` | `#DDEBFF` | `#1D5FD1` | ↑ | 攤商表單 |
| `candidate` | 待確認 | `#F2B200` | `#FFF3C4` | `#8A6100` | ? | Agent |
| `incomplete` | 缺項 | `#F97316` | `#FFE8D6` | `#B5490A` | ! | 核對程式 |
| `not_found` | 未找到 | `#E5484D` | `#FFE1E1` | `#BF2B31` | ✕ | Agent |
| `not_submitted` | 尚未提交 | `#9CA3AF` | `#EEF0F3` | `#545C6A` | ● | 初始值 |

連結解析失敗（原規劃的 `invalid`）在畫面上歸入「未找到」，詳細卡的結果區顯示「連結無法辨識，請重新貼上」。

## 畫面需要的資料欄位（給資料庫設計參考）

| 畫面元素 | 欄位 | 來源 |
|---|---|---|
| 進度卡 | 各狀態數量、總數、最後更新時間 | `merchants` 依狀態彙總 |
| 清單列 | 店名、夜市、縣市、狀態、食物圖示 | `merchants`（食物圖示可依品類對應） |
| 篩選 | 關鍵字（店名/夜市）、狀態、縣市 | 查詢參數 |
| 地圖圖釘 | 經緯度、狀態 | `merchants.lat/lng`，在前端換算到手繪地圖座標 |
| 詳細卡 | 照片、店名、夜市、縣市、Google 地圖連結、Place ID、最後檢查時間、缺項清單 | `merchants` + 最新一筆 `checks` |

Google 條款不允許長期快取店名、地址等 Places 回傳內容。詳細卡顯示的店名和地址來自**你的名單**，不是來自 Google。攤位照片由攤商上傳或你方提供，不使用 Google 的照片。

## 注意事項

- **插畫是從設計圖裁切的暫用素材。** `map-taiwan.png` 上原本就畫了圖釘、城市標籤和對話框，SVG 裡是用向量元件疊在同一位置把它們蓋住。上線前請準備一張**沒有圖釘和標語**的乾淨地圖底圖，覆蓋同名檔案即可。
- `stall-photo-sample.png`、`minimap-sample.png` 是範例。正式版的照片來自攤商上傳，小地圖改用 Google 地圖連結或 Static Map。
- 手繪地圖上的圖釘位置要從經緯度換算。需要先在底圖上標定 2～3 個已知點（例如台北 101、鵝鑾鼻）來求換算公式。
- 範例數據：已完成 210、已提交 12、待確認 32、缺項 13、未找到 18、尚未提交 15，共 300 家。
- 字型：`Noto Sans TC`。沒安裝時改用微軟正黑體，字寬會稍有差異。
