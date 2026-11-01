# 統計頁素材驗收（PLAN 任務 14）

- 日期：2026-11-01
- 候選圖：`design/assets/generated/stats-type-*.png`、`stats-corner-bush.png`（Codex 用 imagegen 生成，提示詞紀錄 `stats-generation-prompts.json`）
- 規格：`design/asset-briefs/stats-page-assets.md` §三、§四
- 審查圖：
  - `contact-sheet.png`：S01～S03 和吉祥物貓並排，上排透明格、下排頁面底色 `#D6F3FD`
  - `small-preview.png`、`small-preview-x2.png`：40×40（④ 列表）和 72×72（③ 卡片）實際大小，x2 是放大兩倍方便看
  - `bush-placement.png`：S05 放在 1586×992 頁面的左下，右下是左右翻轉，前面疊 4 張卡片

## 量測

| 圖 | 尺寸 | 模式 | 四角透明度（左上、右上、左下、右下） | 物件留白（左、右、上、下） | 半透明邊緣的白邊 |
|---|---|---|---|---|---|
| S01 燈籠 | 512×512 | RGBA | 0、0、0、0 | 8%、8%、13%、11% | 0 px |
| S02 菜籃 | 512×512 | RGBA | 0、0、0、0 | 5%、4%、13%、13% | 0 px |
| S03 桌椅 | 512×512 | RGBA | 0、0、0、0 | 7%、7%、21%、21% | 0 px |
| S05 樹叢 | 640×480 | RGBA | 0、0、**253**、0 | 0%、9%、18%、0% | 0 px |

## 驗收

| # | 項目 | 結果 |
|---|---|---|
| 1 | 透明背景，沒有白邊 | ✅ S01～S03 四角全透明。S05 左下角不透明是**規格要求的**：樹叢要貼齊左邊和下邊（§三 S05），所以只檢查其他三角，右上、左上、右下都是 0。驗收條文原本寫「四個角落」不夠精確，已改 |
| 2 | 沒有文字、數字、字母或商標 | ✅ 四張都沒有。S03 筷子筒上的紅白條紋只是花紋 |
| 3 | S01～S03 縮到 40×40 分得出來 | ✅ 紅色燈籠、綠色菜籃、木頭桌椅，靠顏色就分得出來。S03 在 40×40 時桌椅偏小（見下方「注意」） |
| 4 | S01～S03 大小、描邊、視角一致 | 🟡 描邊和視角一致。S03 物件比較扁，上下留白 21%，放在一起時看起來比另外兩張小一號 |
| 5 | 畫風和吉祥物一致 | ✅ 深咖啡粗描邊、平塗加柔和陰影，和拿地圖的貓放在一起是同一套 |
| 6 | S05 右上半邊是空的 | ✅ 右上四分之一完全沒有像素；左邊和下邊貼齊 |

## 注意

- **S03 偏小**：不用重新生圖。建議在 `scripts/build_web_assets.py` 轉 WebP 時，三張都先裁掉透明留白，再統一加相同的邊距，這樣三張的物件大小會一樣。這屬於任務 16 的轉檔步驟。
- **S05 樹叢的透明感**：`bush-placement.png` 裡卡片疊在樹叢前面，樹叢只從卡片之間和頁面角落露出來，和示意圖一樣。

## 結論（2026-11-01 使用者確認定稿）

4 張都可以用，已存成正式檔：

- `design/assets/final/stats/stats-type-night_market.png`
- `design/assets/final/stats/stats-type-traditional_market.png`
- `design/assets/final/stats/stats-type-other.png`
- `design/assets/final/stats/stats-corner-bush.png`
