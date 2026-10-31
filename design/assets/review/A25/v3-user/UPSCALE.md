# A25 水彩底圖 FSRCNN 2 倍放大

- 日期：2026-10-31
- 環境：Windows；Python 3.14.0rc1；OpenCV 5.0.0（含 dnn_superres）；NumPy 2.5.4。
- 輸入：`design/assets/final/map-taiwan-base.png`，1024×1536，RGB。
- 輸入 SHA-256：`970a4c9bd197b4f6361dad47e6884ca7db4d52333479e4ee0d0aca72c56bd2de`。
- 模型：`design/assets/review/A25/v3/source/FSRCNN_x2.pb`。
- 模型 SHA-256：`366b33f0084c7b3f2bf6724f0a2c77bca94fcec9d7b6d72389d330073b380d5c`。
- 方法：使用 `cv2.dnn_superres.DnnSuperResImpl_create()`，`readModel()` 載入模型、`setModel('fsrcnn', 2)`，對 BGR 輸入執行一次 `upsample()`。依 OpenCV dnn_superres 的 FSRCNN 流程，Y 通道用模型放大，色度用雙三次放大後合併，再轉回 RGB 儲存；不是單純插值。
- 輸出：`upscale-fsrcnn-2048x3072.png`，2048×3072，不透明 RGB PNG，比例 2:3；沒有裁切、補邊或二次縮放，也沒有額外銳化、繪製、物件增刪或使用生圖模型。
- 輸出 SHA-256：`c3586c0f32f22435e28246df7bbfb608b0d9725b2e3a01b4e4baf5024123d6bb`。

## 檢查圖

- `upscale-compare-100pct.png`：1200×540；上方 40 px 為標題，左邊是既有雙三次版，右邊是 FSRCNN 版。兩側皆直接裁切 (1300,250)～(1900,750)，每側 600×500，不縮放，圖檔每像素對應輸出每像素。
- `upscale-content-check.png`：左邊是原圖，右邊是 FSRCNN 成品以 Lanczos 縮回 1024×1536 的檢查圖。縮小僅用於檢查，未作用於正式交付的放大圖。
- 已檢查輸出尺寸、RGB 模式、無透明通道，且來源底圖、labels JSON、既有雙三次圖在處理前後 SHA-256 相同。
- FSRCNN 超解析會改變像素估計值；是否有較清楚的輪廓與可接受的細節，應以 100% 比較圖目視判斷。正式底圖不替換，等使用者看過比較圖再決定。

## 目視檢查

- 指定 100% 裁切中，FSRCNN 版樹冠、樹幹與山脊邊緣比雙三次版略清楚；未見明顯光暈、鋸齒或色塊。
- 原圖與縮回原尺寸的成品並排檢視，構圖及可見山、樹、海浪一致，未見物件新增或消失。這是目視檢查結果，並非逐像素相同。
