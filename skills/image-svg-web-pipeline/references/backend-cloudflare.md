# 後端與上線（Cloudflare Pages＋Functions＋D1＋Turnstile）

**網頁全部驗收後才開始。** 開始前用選項問人三件事：存在哪裡（D1／KV／試算表…）、怎麼部署（wrangler 上傳／連 GitHub）、資料怎麼取出（本機指令匯出／管理頁）。下面是攤商地圖選的組合：D1、wrangler 上傳、本機指令匯出 CSV（網路上沒有讀紀錄的網址）。

## 1. 檔案

| 檔案 | 內容 |
|---|---|
| `wrangler.toml` | `name`、`pages_build_output_dir = "web"`、`compatibility_date`、`[[d1_databases]]` 綁定 `DB` 和 `database_id`、`migrations_dir` |
| `migrations/0001_*.sql` | 表格：PLAN 的紀錄欄位＋流水號＋查詢用的毫秒時間；`CHECK` 限制列舉值；防重複和頻率限制用的索引 |
| `functions/api/<name>.js` | `onRequestPost` 處理；`onRequestGet` 回 405（紀錄不能從網路讀） |
| `server/<name>.js` | 純規則函式 `handle({ text, ip, token, now, db, … verifyTurnstile })` → `{ status, body }`，可以單獨測試 |
| `web/js/record.js` | 紀錄格式、時區、CSV 欄位，前後端共用 |
| `scripts/export_*.py` | `npx wrangler d1 execute <db> --json` 匯出 CSV（UTF-8 BOM、CRLF，Excel 直接開）；`--local`、`--pending`、`--out` |
| `.dev.vars.example` | 本機用的 Turnstile 測試秘密金鑰（`1x0000000000000000000000000000000AA`），複製成 `.dev.vars` |

`.gitignore`：`.dev.vars`、`.wrangler/`、匯出的 CSV。

## 2. 規則（依序檢查，任一不過就不存）

| 檢查 | 回應 |
|---|---|
| 內容太大（例如 > 8 KB） | 413 |
| 不是 JSON、找不到對象、操作不合法 | 400 |
| 業務規則（例如已完成的不能再確認、新網址和現有的是同一個地點） | 400 |
| 沒有 Turnstile token | 400 |
| Turnstile 沒通過 | 403 |
| 同一對象＋同一內容 24 小時內送過（不分 IP） | 409 |
| 同一 IP 一小時超過上限 | 429 |
| 沒設秘密金鑰 | 503（防止沒有防機器人就上線） |
| 資料庫出錯 | 500，不帶錯誤細節 |

- **只採用瀏覽器送來的最少欄位**（例如對象 id、操作、網址）。名稱、分組、送出前狀態由伺服器從公開 JSON 填（`env.ASSETS.fetch` 讀，每個 isolate 快取）；IP 取 `CF-Connecting-IP`；token 從 `X-Turnstile-Token` 標頭。
- **只新增，不改公開資料**。人工審核後寫進 `review-decisions.csv` 再重新匯入。
- 便宜的檢查放前面，Turnstile（要打外部 API）放在格式檢查之後。
- 成功 `201 { ok: true }`，失敗 `{ ok: false, error: "<給使用者看的中文>" }`。

## 3. 前端

- `env.js`：`TURNSTILE_SITE_KEY = IS_DEV ? 測試金鑰 "1x00000000000000000000AA" : 正式網站金鑰`；正式環境的送出方式固定是 API。
- Turnstile 用 explicit render，每次送出後 reset。
- 本機測試：`npx wrangler d1 migrations apply <db> --local`、`npx wrangler pages dev --port 8788`，在開發面板切「正式 API」。

## 4. 上線步驟（每一步都先取得同意，記在 BACKEND.md 的表格，做完打 ✅ 和日期）

| # | 步驟 | 誰做 |
|---|---|---|
| 1 | `npx wrangler d1 create <db>`（選區域），id 寫進 `wrangler.toml` | Claude |
| 2 | `npx wrangler d1 migrations apply <db> --remote` | Claude |
| 3 | `npx wrangler pages project create <name> --production-branch main`，確認網址 `<name>.pages.dev` | Claude |
| 4 | 建立 Turnstile 小工具（Managed，網域只填正式網域），透過 Cloudflare API | Claude |
| 5 | 秘密金鑰：`npx wrangler pages secret put TURNSTILE_SECRET --project-name <name>`，到後台複製貼上 | **人** |
| 6 | 網站金鑰填進 `env.js`，跑全部測試 | Claude |
| 7 | 部署（下面），人在正式網址送一筆測試 → Claude 從 D1 查到 → 標成測試（`review_result='test'` 和備註） | Claude＋人 |

部署指令：

```bash
npx --no-install wrangler pages deploy --branch main --commit-hash <sha> --commit-message "<ascii 說明>"
```

- 少了 `--branch main` 會變成預覽部署，正式網址不變。
- 部署後用正式網址讀頁面內容，確認是新版再回報。
- 順序：commit → 合進 main → 確認遠端沒有別人的新 commit（有就先合併）→ push → 部署 → 驗證。

## 5. Windows 注意

- 主控台 cp950：命令列參數裡的中文會變亂碼（例如小工具名稱、部署訊息）。送 API 用 ASCII 跳脫（`\uXXXX`）的 JSON 檔 `--data-binary @file`；讀 wrangler 輸出時用 UTF-8 解碼。
- 用管線把秘密值餵給 `wrangler secret put` 可能被權限規則擋下，這本來就該由人做。

## 6. 費用

D1、Pages、Turnstile 在這種規模都在免費額度內（D1 每天 10 萬次寫入、Pages 每月 500 次部署）。寫進文件，讓人放心。
