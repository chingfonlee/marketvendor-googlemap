---
name: image-svg-web-pipeline
description: 以一張設計圖（完成圖、mockup、手繪稿、AI 生圖）為起點，經過「底圖／素材生圖 → SVG 拆分 → 元件盤點 → 圖層與狀態規格 → 響應式版面 → 資料匯入 → 靜態網頁組成 → 開發開關 → 測試 → 整體驗收 → 後端（Cloudflare Pages＋D1＋Turnstile）→ 部署上線」，由人、生圖 Agent、Claude Code 分工、每一階段停下來讓人驗收的完整協作流程。SVG 是人和 Agent 之間溝通設計的共同語言，文件是合約。只要使用者拿一張畫面圖或設計稿說「照這個做成網站」「把這張圖拆成元件／SVG」「做一個像這樣的地圖／儀表板／成果展示頁」「從設計稿做到上線」「再做一個跟攤商地圖一樣的專案」，或想沿用「先出圖、再拆 SVG、再組網頁、最後接後端」這套做法，就使用這個 skill；即使使用者只提到其中一段（例如只要拆 SVG、只要寫生圖提示詞、只要規劃任務清單），也要用它來決定那一段的做法和交付物。
---

# 以圖片為起點的網站協作流程

這套流程從「國際友善力提升輔導・臺灣攤商地圖」整理而來（2026-10-31～11-01，從一張完成圖到正式上線）。核心想法：

1. **圖片是起點，不是規格。** 設計圖讓人一眼看懂想要什麼，但 Agent 沒辦法從像素可靠地讀出尺寸、狀態、互動。所以第一件事是把圖轉成可以討論、可以版本控制的東西。
2. **SVG 是人和 Agent 的共同語言。** SVG 是文字（Agent 能讀能改、git 能 diff），打開又是圖（人能看能指）。拆成 atoms／components／pages 之後，雙方可以用「`progress-card.svg` 的圓環改成 3 段」這種精確的句子溝通，而不是「左上那塊改一下」。
3. **文件是合約。** 每一階段的結論寫進 `docs/` 的一份 Markdown，附日期和「誰決定的」。之後的階段只讀文件，不靠對話記憶。文件寫錯就改文件，不在程式裡偷偷偏離。
4. **每一階段停下來等人驗收。** 人看得懂的交付物（截圖、疊圖、表格、測試結果）+ 明確的驗收標準，人說「過」才進下一階段。這是讓人保有控制權、也讓 Agent 不會在錯的方向上跑很遠的關鍵。

## 角色

| 角色 | 負責 |
|---|---|
| **人（使用者）** | 提供設計圖和資料、做所有取捨決定、驗收每一階段、做 Agent 不該做的動作（設定秘密金鑰、付費、帳號權限） |
| **生圖 Agent**（例如 Codex 或其他有生圖能力的工具） | 只負責出圖：底圖、插畫、縮圖、放大。照 Claude 寫的需求包做，不改程式 |
| **Claude Code** | 規格、SVG 拆分與整合、網頁和匯入程式、測試、驗收報告、後端、部署 |

多個 Agent 共用一個資料夾時，先講好誰改哪個資料夾（例如生圖 Agent 只寫 `design/assets/`），避免同時改同一個檔案。把分工記進記憶或 `docs/PLAN.md`。

## 階段總覽

每一階段的詳細做法、交付物範本、驗收清單在 `references/` 裡，做到那一段再讀。

| # | 階段 | 主要交付物 | 詳細 |
|---|---|---|---|
| 0 | 設計基準：設計圖 → SVG 產生器 → atoms/components/pages | `design/`、git 基準 commit | [svg-pipeline.md](references/svg-pipeline.md) §1 |
| 1 | 計畫：範圍、狀態定義、任務清單（每項有驗收標準） | `docs/PLAN.md` | [planning.md](references/planning.md) |
| 2 | SVG 審查與元件盤點：每個元件標「固定／調整／新增」和實作形式 | `design/REVIEW.md`、`docs/SVG_COMPONENTS.md` | [svg-pipeline.md](references/svg-pipeline.md) §2–3 |
| 3 | 底圖與素材：檢討 → 生圖需求包 → 驗收 → 放大 → 鎖 SHA-256 | `docs/BASEMAP_REVIEW.md`、`design/asset-briefs/` | [assets-and-basemap.md](references/assets-and-basemap.md) |
| 4 | 圖層架構與共用狀態 | `docs/LAYER_ARCHITECTURE.md` | [web-build.md](references/web-build.md) §1 |
| 5 | 疊在圖上的元素位置（標籤、熱點）＋疊圖預覽 | `*.labels.json`、疊圖 PNG | [assets-and-basemap.md](references/assets-and-basemap.md) §5 |
| 6 | 響應式版面（附線框圖和驗收清單） | `docs/RESPONSIVE_LAYOUT.md` | [web-build.md](references/web-build.md) §2 |
| 7 | 資料匯入：原始資料 → 公開 JSON＋匯入報告，固定 ID、可重跑 | `scripts/import_*.py`、`reports/` | [web-build.md](references/web-build.md) §3 |
| 8 | 網頁組成（純 HTML/CSS/ES modules，無建置） | `web/` | [web-build.md](references/web-build.md) §4 |
| 9 | 表單／補交頁（前端，先模擬送出） | `web/submit.html` 等 | [web-build.md](references/web-build.md) §5 |
| 10 | 開發開關（只在本機出現，正式環境打不開） | `web/js/env.js`、`devtools.js` | [web-build.md](references/web-build.md) §6 |
| 11 | 測試：Node 規則測試＋瀏覽器測試頁 | `tests/`、`docs/TESTING.md` | [testing-and-acceptance.md](references/testing-and-acceptance.md) §1 |
| 12 | 整體驗收：逐條核對前面每一項 | `docs/ACCEPTANCE.md` | [testing-and-acceptance.md](references/testing-and-acceptance.md) §2 |
| 13 | 後端與上線（人確認網頁後才開始） | `functions/`、`migrations/`、`docs/BACKEND.md` | [backend-cloudflare.md](references/backend-cloudflare.md) |
| 14 | 收尾：README（技術、使用方式、交給別人要改哪裡） | `README.md` | [testing-and-acceptance.md](references/testing-and-acceptance.md) §3 |

不是每個專案都要全部做。開始時先跟人確認範圍，把不做的階段寫進 PLAN 的「未來擴充」，不要默默略過。

## 開始一個新專案時

1. 請人提供：設計圖（越完整越好，桌機和手機都有更好）、真實資料（Excel／CSV）、網站的用途（展示？管理？收集回報？）。
2. 讀圖，用自己的話描述畫面上有哪些區塊、哪些是會變動的資料、哪些是裝飾。讓人確認理解正確——這一步很便宜，卻能擋掉最貴的誤會。
3. 問清楚會影響架構的決定（例如：手機要不要放地圖、狀態有幾種、要不要後端、資料有沒有個資），用 AskUserQuestion 給選項和建議，不要自己猜。
4. 寫 `docs/PLAN.md` 草稿（範本見 [planning.md](references/planning.md)），停下來等確認。
5. 確認後照階段表往下做，一次一個階段，每做完一個停下來。

## 每一階段的固定做法

- **先寫規格再動手。** 規格文件說清楚「做什麼、不做什麼、怎麼驗收」，人確認後才寫程式。小改動可以直接做，但要更新對應文件。
- **交付物要人看得懂。** 給截圖、疊圖、表格、前後對照，不要只說「已完成」。在瀏覽器實際打開看過，量過尺寸，才說通過。
- **決定要落地。** 人在對話裡做的每個決定，寫進對應文件，標日期。文件之間有衝突時，以最新決定為準並回頭改舊文件。
- **產生器優先於手改。** SVG、裁切的素材、網頁用的圖片、JSON 都由腳本產生（`design/tools/`、`scripts/`）。要改就改產生器再重跑，這樣結果可重現，下次換圖也能一鍵重做。
- **把圖和座標綁在一起。** 底圖換了，疊在上面的座標就可能錯。座標檔記錄底圖的 SHA-256，網頁在開發模式檢查是否一致，不一致就警告。
- **commit 前先問。** 每個階段一個 commit（或一個分支），訊息寫清楚做了什麼。推上 GitHub、部署、建立雲端資源前都先取得同意。
- **停下來。** 階段完成後用 wrap_up 給一個明確的驗收問題，不要自動進下一階段。

## 不能做、要交給人的事

- 秘密金鑰（Turnstile secret、API token）：Agent 不寫入、不印出，也請人不要貼進對話。給人完整指令讓他自己執行。
- 含個資的檔案（原始 Excel、匯出的 CSV、`.dev.vars`、`.env`）不進 git，第一天就寫進 `.gitignore`。
- 付費方案、帳號權限、網域：人自己做。

## 踩過的坑（快速清單）

- 從設計圖拆出來的 SVG 通常**不能直接當網頁元件**：沒有 `class`／`data-*`、範例資料寫死、同形狀重複畫、多檔放一起 id 衝突、底圖裡畫了圖釘。把它當規格和視覺參考，網頁用 HTML＋CSS 重做，SVG 只留圖示 sprite 和 `<symbol>` 模板。詳見 [svg-pipeline.md](references/svg-pipeline.md) §2。
- 底圖上**不要畫文字、標籤、圖釘**，這些會隨資料變，交給網頁的 HTML 層。
- 疊在地圖上的標籤用「量到的地圖寬度」切換大小，不要用螢幕寬度判斷。
- 瀏覽器測試時**視窗要看得到**，被藏起來的分頁不重繪，ResizeObserver 不觸發，尺寸相關測試會假失敗。
- Windows 主控台是 cp950，命令列參數裡的中文會變亂碼。要送中文給 API 時，寫成 `\u` 跳脫的 JSON 檔再用 `--data-binary @file`。
- Cloudflare Pages 部署要加 `--branch main`，否則變成預覽部署，正式網址不會更新。
- 手機版頁首在系統字體放大時會被切掉：頁首用 `min-height` 不用固定 `height`，長標題分行用 `inline-block` 片段，按鈕文字準備短版。
