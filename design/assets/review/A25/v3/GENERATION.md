# A25 v3 製作紀錄

- 日期：2026-10-31（Asia/Taipei）。
- 規格：`design/asset-briefs/A25-v3-prompt.md`。
- 圖像修改：內建 `image_gen.imagegen`，以 v2 正式圖為輸入。先清除舊縣界、移動丘陵並清空標籤區，再移除北部兩棵殘留樹木。
- 沒有使用 API／CLI 生圖，也沒有改寫原提示詞文件。
- 縣界：依國土測繪中心 SHP 解析 19 個本島縣市，取原始共享邊界，以仿射縮放及平滑薄板樣條貼合 v2 海岸。只繪製內部共享界線，未把行政區文字畫入成品。
- 超解析：FSRCNN x2（預訓練神經網路，OpenCV dnn_superres），不是單純雙三次或雙線性插值。原圖及交付尺寸見 `technical-checks.json`。
- 工具程式：`design/tools/a25_v3_review.py`。Python 僅執行規格要求的地理資料描線、AI 超解析及驗收圖製作；地景內容修改由 imagegen 完成。
- 本輪沒有修改正式底圖。工作期間其他操作已將正式底圖換成水彩版本，且 v3 提示詞新增取消註記；v3 成果僅保留為審查稿。
- 固定比較基準為 `v2-baseline.png`（原 v2 的 SHA-256 前綴 `84d12db5`），避免受並行操作影響。
- 第一輪原始輸出：`C:/Users/user/.codex/generated_images/01a191e7-7fe8-7741-9dc9-325495f5be19/exec-ae1a34c1-12f5-43f7-8c0f-447a3ad6bec1.png`。
- 第二輪採用輸出：`C:/Users/user/.codex/generated_images/01a191e7-7fe8-7741-9dc9-325495f5be19/exec-7e989856-b518-48c9-b02c-12ffb8885ba3.png`。

## 官方資料與授權

- 資料集：[直轄市、縣市界線（TWD97 經緯度）](https://data.gov.tw/dataset/7442)，提供機關：內政部國土測繪中心，政府資料開放授權條款第 1 版。
- 實際下載：[國土測繪圖資服務雲 SHP](https://maps.nlsc.gov.tw/download/%E7%B8%A3%E5%B8%82%E7%95%8C%E7%B7%9A(TWD97%E7%B6%93%E7%B7%AF%E5%BA%A6).zip)，入口：[下載專區](https://maps.nlsc.gov.tw/pro/download.jsp)。
- 本次下載 ZIP 的實際內含版本為 `COUNTY_MOI_1090820`，即 2020-08-20；不宣稱是 2026 最新測繪成果。原始 ZIP、SHP 及相關中繼資料保存在 `source/`。
- 資料集頁面所連結 TGOS 檔案未能直接取得，因此改用同機關圖資服務雲下載。縣界是實際官方圖資，不是生成模型猜測。
- 製圖後為配合插畫輪廓有所變形，仍屬裝飾性底圖，非測量用地圖。

## AI 超解析來源

- [FSRCNN TensorFlow 預訓練模型](https://github.com/Saafke/FSRCNN_Tensorflow)，Apache-2.0。
- [模型檔](https://raw.githubusercontent.com/Saafke/FSRCNN_Tensorflow/master/models/FSRCNN_x2.pb)，保存在 `source/FSRCNN_x2.pb`；實際雜湊見 `technical-checks.json`。
- 此方法可改善輸出邊緣，但不宣稱能還原未生成的真實細節；視覺品質以 100% 裁切驗收。

## 第一輪實際提示詞

```text
Use case: precise-object-edit. A25 v3 terrain cleanup pass, not a redesign. Image 1 is the approved v2 Taiwan base map; image 2 is ONLY a cleanup guide. Keep image 1 island outline, coastline, tilt, proportions, location, art style, exact colors, sea, surf, sand, the single snow-capped mountain, whale, sailboat and ALL clouds unchanged. Generate at your maximum available resolution, requested native 2244x2804, crisp clean dark-brown outlines without blur. Make only these changes: REMOVE ALL existing thin white inland county lines completely, leaving seamless flat pale-green terrain. These old lines are geographically wrong; accurate county lines will be added from government vector data afterward, so do NOT invent any replacement lines. Remove all hills and trees that intersect ANY of image 2's eight blue rectangle areas, including those touching rectangle edges; keep a 20px safety margin. Clear the entire northwest hill group and entire southwest hill group even if part extends beyond a rectangle. Clear the west-central hill group that touches the Hsinchu rectangle and move it near the snow mountain, OUTSIDE every rectangle. Relocate the removed hill groups to the east-central interior near the snow mountain only, total 3 low hill groups, outside all blue guide areas, and keep the snow mountain untouched. The eight boxes at target resolution are (left,top,right,bottom): Taipei(1240,150,1660,350), New Taipei(1690,540,2110,740), Taoyuan(910,420,1330,620), Hsinchu(650,780,1070,980), Taichung(550,1100,970,1300), Tainan(350,1600,770,1800), Kaohsiung(490,1980,910,2180), Taitung(1230,1800,1650,2000). Within boxes ONLY flat land, existing coast, or existing sea. No trees, hills, bushes. Keep upper-left sea (0,0,880,740) and lower-right sea (1680,2380,2244,2804) empty. Never change island shape to fit boxes. Image 2 colored boxes and labels are guide only: DO NOT draw any rectangles, text or labels in the output. No white inland lines, no buildings, no landmarks, no offshore islands, no letters, numbers, pins, markers, watermark. Clean terrain image ONLY. Do not add any other subjects or modify other decorations.
```

## 第二輪實際提示詞

```text
Make a precise tiny object removal edit. Keep the ENTIRE supplied image unchanged except REMOVE the TWO NORTHERNMOST TREES. Tree 1 is near pixel (835,175), tree 2 near pixel (875,307), on this 1122x1402 input. Both are in the upper-right/northeast land. Remove their crowns, trunks, shadows and nearby tiny grass strokes and replace with seamlessly matching flat pale-green ground. There must be NO TREE ANYWHERE ABOVE y=360 on the 1122x1402 input canvas. Keep ALL other pixels/composition/style as close as possible: unchanged Taiwan coastline silhouette, position, tilt, proportions, colors, sea, surf, beaches, central snow mountain, three hill groups near mountain, remaining trees below y=360, whale, boat and ALL clouds. Do not draw county lines yet; land must have no white inland border lines. No new objects, buildings, islands, text, numbers, markers. Output at maximum available resolution with crisp outlines, ideally 2244x2804. The two specified trees are the ONLY subjects to remove.
```
