# 國際友善力提升輔導・臺灣攤商地圖

夜市與市場攤商的 Google 地圖登錄成果平台。地圖上看各縣市、各市場有多少攤商已經在 Google 地圖上完成登錄；攤商可以自己確認或補交店家的 Google 地圖連結，不用註冊。

- 正式網址：<https://googlemap-store.pages.dev/>
- 補交頁：<https://googlemap-store.pages.dev/submit>
- 原始碼：<https://github.com/chingfonlee/marketvendor-googlemap>

目前資料：8 個縣市、15 個市場、347 家攤商。

---

## 1. 使用的技術

| 部分 | 技術 | 說明 |
|---|---|---|
| 網頁 | 純 HTML、CSS、JavaScript（ES modules） | 沒有框架、沒有打包工具，`web/` 資料夾直接就是網站 |
| 地圖 | 一張水彩底圖（WebP）＋HTML 縣市標籤 | 不用 Google Maps API，不會產生地圖費用；可縮放、拖曳 |
| 資料 | JSON（`web/data/`） | 由 Excel 匯入產生，網頁只讀這幾個檔案 |
| 資料匯入 | Python 3＋openpyxl | `scripts/import_excel.py`，只讀 Excel，不輸出負責人、電話、地址 |
| 素材轉檔 | Python＋Pillow | `scripts/build_web_assets.py`，PNG 轉成網頁用的 WebP 和圖示 |
| 主機 | Cloudflare Pages | 放網頁，免費額度 |
| 後端 | Cloudflare Pages Functions | `functions/api/submissions.js`，收補交紀錄 |
| 資料庫 | Cloudflare D1（SQLite） | 只存補交紀錄；攤商名單本身不在資料庫，在 JSON |
| 防機器人 | Cloudflare Turnstile | 補交頁送出前要過驗證 |
| 部署工具 | wrangler（Cloudflare 的指令工具） | 用 `npx wrangler`，不用另外安裝 |
| 測試 | Node 內建的 `node:test`＋自製瀏覽器測試頁 | 不裝任何套件 |

需要安裝的只有：

- **Python 3.11 以上**，加上 `pip install openpyxl pillow`（匯入資料、轉素材時才需要）
- **Node.js 22 以上**（跑測試、部署時才需要）

---

## 2. 資料夾

```
web/            網站本身（部署的就是這個資料夾）
  index.html      總覽頁（地圖、進度、清單）
  submit.html     補交／確認連結頁
  css/  js/       樣式和程式
  data/           網頁讀的 JSON（匯入程式產生，不要手改）
  assets/         圖片、圖示（轉檔程式產生）
functions/      後端 API（Cloudflare Pages Functions）
server/         後端的檢查規則（API 呼叫這裡）
migrations/     D1 資料庫的表格
scripts/        匯入資料、轉素材、本機預覽、匯出補交紀錄
data/           Excel 原始檔（不進 git）、人工決定、固定 ID
reports/        匯入報告
tests/          自動測試
design/         設計稿、素材原始檔、底圖和標籤座標
docs/           規格和決策文件
wrangler.toml   Cloudflare 設定（Pages 專案、D1）
```

---

## 3. 日常使用

### 3.1 更新攤商資料（Excel 改了之後）

1. 把新的 Excel 放到 `data/國際友善力_菜單審查總表_Google地圖.xlsx`。這個檔案有個資，**不會進 git**。
2. 匯入：

   ```bash
   python scripts/import_excel.py
   ```

   會更新 `web/data/*.json` 和 `reports/import-report.md`。先看報告裡的家數和警告。
3. 本機預覽，打開 <http://localhost:8765/> 看看：

   ```bash
   python scripts/serve_web.py
   ```

4. 跑測試（見 §4）。資料快照測試會因為家數改變而失敗，要照新的數字更新 `tests/data-snapshot.test.mjs`。
5. commit、推上 GitHub、部署（見 §5）。

同一份 Excel 跑兩次，輸出完全相同。店名或市場名稱改了，要在 `data/review-decisions.csv` 加一筆 `same_as`，新名稱才會沿用舊的 ID（[docs/PLAN.md](docs/PLAN.md) §4）。

### 3.2 處理攤商的補交

攤商在補交頁送出的資料存在 D1，**不會直接改網站上的狀態**，要人工確認。

1. 匯出還沒處理的紀錄（要先 `npx wrangler login`）：

   ```bash
   python scripts/export_submissions.py --pending
   ```

   輸出 `data/submissions-YYYYMMDD.csv`，有 IP，不進 git。
2. 一筆一筆打開網址確認是不是那家店。
3. 確認後寫進 `data/review-decisions.csv`（例如 `verify`、`set_url`），或直接改 Excel。
4. 重新匯入、部署（§3.1），網站上的狀態才會更新。

規則（防重複、每小時上限、Turnstile）見 [docs/BACKEND.md](docs/BACKEND.md)。

---

## 4. 本機開發與測試

```bash
python scripts/serve_web.py          # 只看網頁：http://localhost:8765/
node --test "tests/*.test.mjs"       # 資料、規則、後端，約 1 秒
python tests/serve_tests.py          # 瀏覽器測試：打開 http://localhost:8766/ 自動跑
```

- 瀏覽器測試跑的時候**視窗要看得到**（不要最小化），否則地圖相關的項目會失敗。
- 在 `localhost` 打開網頁時，左下角有「開發」按鈕，可以關掉底圖、標籤等元件，補交頁可以切換「模擬送出／正式 API／關閉」。正式網址不會出現這個按鈕（[docs/SVG_COMPONENTS.md](docs/SVG_COMPONENTS.md) §6）。
- 要在本機連同後端一起跑：

  ```bash
  copy .dev.vars.example .dev.vars
  npx wrangler d1 migrations apply googlemap-store --local
  npx wrangler pages dev --port 8788
  ```

  打開 <http://127.0.0.1:8788/>，用本機的 D1，Turnstile 用 Cloudflare 的測試金鑰。

測了哪些東西見 [docs/TESTING.md](docs/TESTING.md)。

---

## 5. 部署

```bash
npx wrangler pages deploy --branch main
```

- 要加 `--branch main`，才會部署到正式網址；不加的話會用目前的 git 分支名稱，變成預覽網址。
- 網頁和後端一起上傳。D1 表格改了的話，先跑 `npx wrangler d1 migrations apply googlemap-store --remote`。
- 部署前先跑完測試、commit。

---

## 6. 交給其他人使用時要改的地方

### 6.1 只換名稱、文字

| 要改的 | 檔案 |
|---|---|
| 網站名稱 | `web/index.html`、`web/submit.html` 的 `<title>`、頁首標題、`aria-label`（兩個檔案各 3 處） |
| 副標、說明文字 | `web/index.html`（「夜市與市場 Google 地圖登錄成果平台」等）、`web/submit.html` |
| Logo、吉祥物 | 換 `design/assets/` 裡的原圖，再跑 `python scripts/build_web_assets.py` |
| 配色 | `web/css/tokens.css` |

名稱變長時，要用手機寬度（360、375）看頁首會不會被切掉，再跑瀏覽器測試。

### 6.2 換成另一批攤商資料

- **Excel 格式**要和現在一樣：
  - 第一個分頁是總表：序號、縣市、市場名稱、攤數。
  - 之後每個市場一個分頁，分頁名稱開頭是總表序號（例如 `1-永春市場`）。第 2 列是欄位名稱，要有「序號」「市場/攤鋪名稱」「地圖狀態」「Google 地圖連結」「Place ID」「Google 上的名稱」「相似度」。
  - 地圖狀態只認「已完成」「待確認」「未找到」，對應網站的已完成、待確認、未提交。
- 格式不同的話，改 `scripts/import_excel.py` 讀 Excel 的部分。
- **市場類型**（夜市／傳統市場／其他，決定市場縮圖）寫在 `scripts/import_excel.py` 的 `TYPES`，換市場時要跟著改。
- **全新的一批資料**：清空 `data/id-map.json`（改成 `{}`）和 `data/review-decisions.csv`（只留表頭），讓 ID 重新編號（照總表序號給 `m01`、`m02`…）。`TYPES` 也要照新的 ID 重填：匯入程式只會在 ID 沒列在 `TYPES` 時停下來提醒，ID 剛好和舊的重複時不會發現類型填錯。
- 匯入後更新 `tests/data-snapshot.test.mjs` 的家數。

### 6.3 增加或換縣市

縣市標籤畫在固定的底圖上，座標是手動對好的：

- 縣市清單和標籤位置：`design/assets/final/map-taiwan-base.labels.json`，匯入時會複製成 `web/data/county-labels.json`。縣市的順序就是網頁上的順序。
- 新增縣市要在這個檔案加一筆座標，對準底圖上的位置。對位方法和預覽工具見 [docs/COUNTY_LABELS.md](docs/COUNTY_LABELS.md)。
- 換底圖的話，跑 `python scripts/build_web_assets.py` 重新產生 `map-base.webp`，標籤檔裡的 `basemap_sha256` 也要更新成新底圖的值，不然開發模式會顯示紅色驚嘆號，提醒標籤位置可能對不上（[docs/COUNTY_LABELS.md](docs/COUNTY_LABELS.md)）。

### 6.4 部署到另一個 Cloudflare 帳號

現在的設定綁在原本的 Cloudflare 帳號。換人管理時：

1. 登入新帳號：`npx wrangler login`。
2. 建立 D1：`npx wrangler d1 create <資料庫名稱>`，把回傳的 `database_id` 和名稱填進 `wrangler.toml`；名稱也要改 `scripts/export_submissions.py` 的 `DB`。
3. 建立表格：`npx wrangler d1 migrations apply <資料庫名稱> --remote`。
4. 建立 Pages 專案：`npx wrangler pages project create <專案名稱> --production-branch main`，`wrangler.toml` 的 `name` 改成同一個名稱。網址會是 `<專案名稱>.pages.dev`。
5. 在 Cloudflare 後台建立 **Turnstile** 小工具，網域填上一步的網址：
   - **網站金鑰**（公開的）填進 `web/js/env.js` 的 `TURNSTILE_PROD_KEY`。
   - **秘密金鑰**用 `npx wrangler pages secret put TURNSTILE_SECRET --project-name <專案名稱>` 設定，不要寫進任何檔案。
6. 部署（§5），在正式網址送一筆測試，再用 `export_submissions.py` 確認收到。

沒設秘密金鑰時，API 一律回 503、不收資料，不會在沒有防機器人的情況下上線。完整步驟和規則見 [docs/BACKEND.md](docs/BACKEND.md)。

### 6.5 其他可以調的設定

| 設定 | 位置 |
|---|---|
| 防重複時間（24 小時）、每 IP 每小時上限（10 筆） | `web/js/record.js` 的 `DEDUPE_MS`、`HOURLY_LIMIT` |
| 哪些網址算開發環境 | `web/js/env.js` 的 `IS_DEV` |
| 網址格式檢查（接受哪些 Google 地圖網址） | `web/js/urlcheck.js`；匯入程式的 `check_url` 要跟著改 |
| 手機、平板、桌機的版面切換寬度 | `web/css/layout.css`，規格在 [docs/RESPONSIVE_LAYOUT.md](docs/RESPONSIVE_LAYOUT.md) |

---

## 7. 個資

- 攤商 Excel 有負責人、電話等個資，`data/*.xlsx` 不進 git。網站的 JSON 只有店名、狀態和 Google 地圖連結。
- 補交頁不收聯絡資料，只記送出時間和 IP，用來防重複和濫用。匯出的 CSV 有 IP，`data/*.csv` 不進 git。
- `.env`、`.dev.vars` 不進 git。

---

## 8. 文件

| 文件 | 內容 |
|---|---|
| [docs/PLAN.md](docs/PLAN.md) | 整體規格、互動規則、任務清單 |
| [docs/BACKEND.md](docs/BACKEND.md) | 補交後端、匯出、上線步驟 |
| [docs/RESPONSIVE_LAYOUT.md](docs/RESPONSIVE_LAYOUT.md) | 各尺寸的版面 |
| [docs/LAYER_ARCHITECTURE.md](docs/LAYER_ARCHITECTURE.md) | 地圖圖層和程式架構 |
| [docs/SVG_COMPONENTS.md](docs/SVG_COMPONENTS.md) | 畫面元件、開發開關 |
| [docs/COUNTY_LABELS.md](docs/COUNTY_LABELS.md) | 縣市標籤的位置 |
| [docs/TESTING.md](docs/TESTING.md) | 測試內容和結果 |
| [docs/ACCEPTANCE.md](docs/ACCEPTANCE.md) | 網頁整體驗收紀錄 |
| [docs/DATA_ISSUES.md](docs/DATA_ISSUES.md) | 資料問題和處理結果 |
| [design/README.md](design/README.md) | 設計稿和素材 |

---

## 9. 授權

[MIT License](LICENSE)：可以自由使用、修改、再散布，包括商業用途，只要保留版權和授權聲明。

圖片：`design/assets/` 和 `web/assets/` 裡的插畫（背景、吉祥物、Logo、地圖底圖等 PNG／WebP）由 ChatGPT 生成。`design/svg/` 的設計稿和元件由 `design/tools/` 的程式產生。
