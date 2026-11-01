# 補交紀錄的後端（任務 12）

- 日期：2026-11-01
- 對應 [PLAN.md](PLAN.md) §5、§6 任務 12。
- 決定（2026-11-01）：存在 **D1**；用 **Cloudflare Pages + wrangler 上傳**部署（不連 GitHub）；CSV 用**本機指令**匯出，網路上沒有讀紀錄的網址。

## 1. 檔案

| 檔案 | 內容 |
|---|---|
| `wrangler.toml` | Pages 專案 `googlemap-store`：網頁是 `web/`，D1 綁定 `DB` |
| `migrations/0001_submissions.sql` | D1 表格 `submissions`：§5 的 14 個欄位，加上流水號 `id` 和查詢用的 `submitted_ms` |
| `functions/api/submissions.js` | `POST /api/submissions`。`GET` 回 405，紀錄不能從網路上讀 |
| `server/submission.js` | 檢查和寫入的規則（§2），測試時可以單獨跑 |
| `web/js/record.js` | 紀錄格式、防重複和上限的數字，網頁和後端共用 |
| `scripts/export_submissions.py` | 從 D1 匯出 CSV（§4） |
| `.dev.vars.example` | 本機用的 Turnstile 測試金鑰，複製成 `.dev.vars`（不進 git） |

## 2. 規則

API 只採用瀏覽器送來的**攤商代號、操作、網址**三個欄位。縣市、市場、店名、送出前狀態由伺服器從公開資料（`web/data/*.json`，跟網頁一起部署）填；IP 取 `CF-Connecting-IP`；人工處理欄一律空白。

依序檢查，任何一項不過就不存：

| 檢查 | 回應 |
|---|---|
| 內容超過 8 KB | 413 |
| 不是 JSON、找不到攤商、操作不是 `confirm`／`update` | 400 |
| 確認：這家店沒有連結，或已經是「已完成」 | 400 |
| 貼新網址：格式不對（和網頁同一份 `urlcheck.js`），或和目前的連結是同一家店 | 400 |
| 沒有 Turnstile token | 400 |
| Turnstile 沒通過 | 403 |
| 同一攤商、同一網址 24 小時內送過（不分 IP） | 409 |
| 同一 IP 一小時內已送 10 筆 | 429 |
| 沒設 `TURNSTILE_SECRET` | 503（防止沒有防機器人就上線） |
| 資料庫出錯 | 500，訊息不帶錯誤細節 |

成功回 `201 { ok: true }`，失敗回 `{ ok: false, error }`，`error` 是給使用者看的中文。

**不覆蓋已確認資料**：API 只新增紀錄，不改公開資料，也不改已經有的紀錄。人工確認後照 PLAN §5 寫進 `data/review-decisions.csv`、重新匯入，公開狀態才會變。

## 3. 網頁這邊

- 正式環境的補交頁直接送到 API，送出前要通過 Turnstile。網站金鑰在 `web/js/env.js` 的 `TURNSTILE_PROD_KEY`。
- Turnstile 小工具（2026-11-01 建立）：名稱「台灣攤商地圖 補交頁」、模式 Managed、網域只有 `googlemap-store.pages.dev`。在其他網域打開補交頁，驗證會失敗、送不出去。
- 後端沒設秘密金鑰時一律回 503，所以就算網頁先上線，也不會在沒有防機器人的情況下收資料。
- 開發環境照開發開關：模擬送出（預設）、正式 API、關閉。選正式 API 時用 Cloudflare 公開的測試金鑰（一定通過）。

## 4. 匯出 CSV

```bash
python scripts/export_submissions.py --pending
```

- 預設讀正式 D1，輸出 `data/submissions-YYYYMMDD.csv`。這個檔案有 IP，`data/*.csv` 不進 git。
- `--pending` 只匯出還沒人工處理的；`--local` 讀本機 D1；`--out` 指定檔名。
- 欄位、順序和網頁「下載 CSV」相同；UTF-8 加 BOM，Excel 直接開不會亂碼。只讀資料庫。

## 5. 本機測試

```bash
copy .dev.vars.example .dev.vars
npx wrangler d1 migrations apply googlemap-store --local
npx wrangler pages dev --port 8788
```

打開 <http://127.0.0.1:8788/submit.html>，在左下角「開發」把補交改成「正式 API」，就會送到本機的 API 和本機 D1。自動測試見 [TESTING.md](TESTING.md)。

## 6. 上線步驟（每一步都要先取得同意）

| # | 步驟 | 誰做 |
|---|---|---|
| 1 | 建立 D1：`npx wrangler d1 create googlemap-store`（APAC），id 已填進 `wrangler.toml` | Claude ✅ 2026-11-01 |
| 2 | 建立表格：`npx wrangler d1 migrations apply googlemap-store --remote` | Claude ✅ 2026-11-01 |
| 3 | 建立 Pages 專案：`npx wrangler pages project create googlemap-store --production-branch main`，網址是 `googlemap-store.pages.dev`，和 Turnstile 的網域一致 | Claude ✅ 2026-11-01 |
| 4 | 建立 Turnstile 小工具（用 wrangler 登入的 Cloudflare API） | Claude ✅ 2026-11-01 |
| 5 | 設定**秘密金鑰**：Cloudflare 後台 → Turnstile →「台灣攤商地圖 補交頁」複製秘密金鑰，執行 `npx wrangler pages secret put TURNSTILE_SECRET --project-name googlemap-store` 貼上。寫入秘密金鑰 Claude 沒有權限，秘密金鑰也不要貼到對話裡 | 你 |
| 6 | 網站金鑰填進 `web/js/env.js` 的 `TURNSTILE_PROD_KEY`，跑測試 | Claude ✅ 2026-11-01 |
| 7 | 部署：`npx wrangler pages deploy`，然後在正式網址送一筆測試、匯出確認，再把那筆標成測試 | Claude |

D1、Pages、Turnstile 都在免費額度內（D1 每天 10 萬次寫入、Pages 每月 500 次部署）。
