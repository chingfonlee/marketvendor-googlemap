# 市場類型縮圖候選審查

- 日期：2026-10-31
- 狀態：已製作並檢查，待使用者視覺接受；尚未存成正式檔。
- 製作：內建 image_gen，各類型分別生成；參考既有吉祥物與攤車的深咖啡描邊、圓潤造型、暖色平塗及柔和陰影。後兩張亦參考本套夜市候選圖，以維持一致性。
- 尺寸整理：生成原圖 1586×992，僅以 Lanczos 縮為指定 640×400 並轉 RGB；沒有裁掉內容、加字或外框。原圖保存在 `source/`。

## 交付

| 類型 | generated 候選檔 | 本審查資料夾副本 |
|---|---|---|
| 夜市 | `design/assets/generated/market-type-night-market.png` | `night_market.png` |
| 傳統市場 | `design/assets/generated/market-type-traditional-market.png` | `traditional_market.png` |
| 美食廣場・商圈 | `design/assets/generated/market-type-other.png` | `other.png` |

## 驗收逐條檢查

| 項目 | 結果 | 證據與觀察 |
|---|---|---|
| 三張皆 640×400、不透明 RGB PNG | 通過程式檢查 | 三張皆為 RGB、640×400，無透明通道；雜湊見 `generation-records.json`。 |
| 沒有文字、數字、商標 | 目視通過 | 招牌空白；秤盤只有指針與刻度，沒有數字；小黑板僅有飲料圖形。審查圖上方的類型標題只用於對照，不在候選圖內。 |
| 130×80 仍能辨識類型 | 目視通過 | `small-preview.png` 的三張縮圖實際各為 130×80：夜市以深藍夜空、紅燈籠辨識；傳統市場以綠色遮棚、大片蔬果辨識；美食廣場以室內屋架、桌椅辨識。 |
| 中央 400×400 裁切保留重點 | 目視通過 | `square-crop-preview.png` 直接取各候選圖的 (120,0)～(520,400)，未縮放。燈籠與小吃、蔬果與吊秤、中央圓桌與椅子均保留；兩側次要攤位、籃子及部分外側椅緣會被裁切。 |
| 與吉祥物的風格及三張彼此一致 | 目視通過，待使用者接受 | 三張都有深咖啡描邊、圓潤攤棚、暖色木櫃及柔和陰影，視角接近；夜市保留夜間照明，另兩張以左上日光呈現。場景細節比單體吉祥物豐富，最終風格接受由使用者決定。 |
| 無大型人物、邊框、圓角 | 通過 | 三張均沒有人物，背景填滿矩形畫布，沒有外框或預製圓角。 |

## 審查圖

- `contact-sheet.png`：三張 640×400 原尺寸並排，標題放在圖片之外。
- `small-preview.png`：三張各 130×80 的實際顯示尺寸預覽。
- `square-crop-preview.png`：三張中央 400×400 裁切預覽。
- `generation-records.json`：工具、提示詞、來源、尺寸、SHA-256 與候選路徑。

## 範圍

本次只新增 `design/assets/generated/market-type-*.png` 與 `design/assets/review/market-type/`。處理前後以 SHA-256 確認既有 `design/assets/final/` 及 `docs/` 檔案未變更；未修改網頁，未建立正式市場類型素材。
