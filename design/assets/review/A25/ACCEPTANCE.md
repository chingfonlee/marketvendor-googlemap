# A25 外型與中央山脈修正版自檢

日期：2026-10-31（台北）。本次依使用者最新修正：「臺灣形狀變形了，請依照參考圖外型重新做，中央山脈可以明顯些」。此指示優先於 manifest 原先北部放大約 1.5 倍的設定；本次不再刻意放大北部。

已更新 `../../final/map-taiwan-base.png`，選用 `../../generated/A25-badges-shape-v5.png`。使用內建 imagegen 編修，等比例整理為 2244×2804、不透明 RGB PNG。SHA-256：ACD287358CCC24DE7DFD309BD9B3FF8DD87073F6A10367014314FECE3EBA11AD。

這是外型與山脈的修正版交付，**不能視為原 manifest 所有 accept 已通過**。下列為製作方自檢，使用者尚未接受修正版。

## 最新修改檢查

- 本島外型：目視與參考圖並排，恢復細長斜向外型、東北端、西岸彎曲和南端收尖；沒有沿用上一版膨大的北部。這是依參考圖重繪，非逐像素輪廓相同的保證。
- 中央山脈：改為多組中綠色重疊山峰、深色輪廓和明暗山面，比上一版三座淡色小丘清楚；沿岸保留平地。
- 舊版：`shape-revision/before-map-taiwan-base.png`，保留不刪除。舊的全數通過紀錄封存於 `shape-revision/previous-acceptance.md`；舊外型已被使用者退回，不能當成本版驗收證據。

## 原 accept 逐條結果

| 項目 | 結果 | 證據／限制 |
|---|---|---|
| 2244×2804 | 通過 | 由尺寸整理工具檢查，24-bit RGB，不透明。 |
| 無建築、地標、文字、縣市界線、圖釘、標記 | 通過 | 整張目視；無道路、文字或介面。只有規格要求的兩個離島虛線框。 |
| 台灣外型、北部放大、五組離島 | 依最新指示調整／部分待修 | 本島恢復參考圖比例，不再放大北部；五組離島均存在。澎湖目前在西側但較原規劃偏南，綠島、蘭嶼的精確版面位置亦尚未完全對齊原橘框。 |
| 金門、馬祖各有淡色虛線框 | 通過 | 各一個淡色框。 |
| 22 原藍框位置皆平坦低細節 | 未全數通過 | 原位置的宜蘭、南投、嘉義縣、高雄、台東等仍有山麓或山峰邊緣進入。`badge-zones-contact.png` 是本版逐區裁切，不可宣稱全數留白；徽章位置需隨新圖重標或再修地形。 |
| 陸地較淡、細節少，裝飾只在四邊 | 通過 | 主島沿岸移除樹叢雜物，山脈依最新指示加強；海上裝飾為兩朵角落雲、一艘角落船、一隻角落鯨魚。 |

## 檔案

- `shape-revision/reference-before-after.png`：左參考圖、中被退回的舊版、右修正版。
- `badge-candidate-50pct.png`：本版半尺寸預覽。
- `badge-layout-overlay.png`、`badge-zones-contact.png`：原 22 區位置對照，標註只在檢查圖，正式素材沒有。
- `badge-technical-checks.json`：尺寸、22 區座標與成品 SHA-256。
- `shape-revision/initial-prompt.txt`、`refine-prompt.txt`、`zones-prompt.txt`、`mountain-layout-prompt.txt`、`selected-cleanup-prompt.txt`：實際內建 imagegen 提示詞與修正過程。主提示詞保留 manifest 的風格及 negative_prompt，並明確以使用者最新輪廓修正覆蓋北部放大規定。
- `../../generated/A25-shape-narrow-experiment.png`：未選用的狹窄山脈試稿，不是交付圖。
