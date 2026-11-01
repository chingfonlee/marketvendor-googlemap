# 統計報表頁：進度紀錄

- 更新日期：2026-11-01（PLAN 已更新）
- 用途：記錄「統計報表」頁做到哪裡、下一步是什麼。斷線或換新對話時，**先讀這份**，再讀下面列的文件，不要靠對話記憶。
- 流程：照 skill `image-svg-web-pipeline` 的階段表，每一階段做完都停下來，等使用者驗收。
- 分工（照 `docs/PLAN.md` 和專案記憶）：
  - **Codex**：只出圖，存到 `design/`。
  - **Claude Code**：規格、SVG、網頁、測試、驗收。
  - **使用者**：做決定、驗收。

---

## 1. 現在在哪裡

> **第 0 階段（設計基準）的示意圖已完成，第 2 階段（元件盤點）和第 3 階段（素材需求）的規格草稿已完成。§4 的 D1～D7 和 §4.1 入口（A＋B）都已決定（2026-11-01）。設計基準已 commit（分支 `claude/stats-page`，`e8254d6`）。第 1 階段 PLAN 已更新並 commit（`d2e9752`），`SVG_COMPONENTS.md` 的分頁和進度卡規則也改了。素材 S01～S03、S05 已生成並驗收（`design/assets/review/stats/ACCEPTANCE.md`，4 張都可用），使用者確認（2026-11-01），已存到 `design/assets/final/stats/`，commit `b624506`。SVG 組件和響應式規格（PLAN 任務 15）已完成，使用者驗收通過（2026-11-01），commit `7011cc7`：`design/tools/build_stats_svg.py` 產生 9 個 SVG，截圖在 `design/assets/review/stats/svg/`。網頁（PLAN 任務 16）已完成，使用者驗收通過（2026-11-01），commit `911ab65`。測試（PLAN 任務 17）已完成；驗收時使用者把 ④ 改成「最強友善力市集」（§4.2），已改完、測試全過，使用者驗收通過（2026-11-01），commit `4b57617`。整體驗收（PLAN 任務 18）已完成，使用者驗收通過（2026-11-01），已 commit（`docs/ACCEPTANCE.md` §5）。下一步：§5 第 11 項 README 和部署（PLAN 任務 19，部署前先問）。**
> 之後的任務編號以 PLAN §6 為準（任務 13～19），本文件 §5 的對照見該表最後一欄。

---

## 2. 已完成的東西

| 項目 | 檔案 | 狀態 |
|---|---|---|
| 統計方向討論 | （對話）建議先做市場和縣市的比例統計 | 使用者選了比例類圖表 |
| 示意圖提示詞 | `design/asset-briefs/stats-mockup-prompt.md` | ✅ |
| 示意圖 v1（桌機） | `design/reference/stats-mockup-v1.png`，提示詞紀錄 `design/asset-briefs/stats-mockup-v1-generation.txt` | 縣市長條多一段灰色，不採用 |
| 示意圖 v2（桌機＋手機） | `design/reference/stats-mockup-v2.png`、`stats-mockup-v2-mobile.png`，提示詞紀錄 `stats-mockup-v2-generation.txt` | ✅ 使用者確認是想要的方向（2026-11-01） |
| 拆分與素材清單 | `design/asset-briefs/stats-page-assets.md` | 草稿，等驗收 |
| ├ §一 整頁拆解 | 每個元素標明：已有／手寫 SVG／要補圖／動態 | |
| ├ §二 SVG 組件樹 | 4 張卡片、atoms（`crown`、`pie`、`ratio-bar`、`cloud`）、桌機和手機兩頁 | 還沒畫 SVG |
| ├ §三 補圖提示詞 | S01～S03 類型圖示（必要）、S04 頁首街景、S05 角落樹叢（選用） | 還沒生圖 |
| └ §五 資料綁定 | 名詞定義、各圖表算法、排序和挑選規則、捨入、特殊狀況、7 項測試 | ✅ 使用者要求確認「圖表會跟著資料變」，已補上 |

**已 commit：`e8254d6`（分支 `claude/stats-page`）。**

---

## 3. 階段對照（skill 階段表）

| # | 階段 | 統計頁的狀態 | 說明 |
|---|---|---|---|
| 0 | 設計基準 | ✅ 示意圖已定，已 commit `e8254d6` | v2 是設計基準。SVG 產生器還沒做，放在第 2 階段一起做 |
| 1 | 計畫 | ✅ 已 commit `d2e9752` | PLAN §1、§2、§2.1、§3（已提交比例的定義）、§6 任務 13～19、§7 |
| 2 | SVG 審查與元件盤點 | ✅ 完成 | `docs/SVG_COMPONENTS.md` §7；`design/tools/build_stats_svg.py` 產生 `design/svg/{pages,components,atoms}/stats-*.svg` |
| 3 | 底圖與素材 | ✅ 定稿，存在 `design/assets/final/stats/` | S01～S03、S05 在 `design/assets/generated/`，驗收見 `design/assets/review/stats/ACCEPTANCE.md`；S04 不做（D4） |
| 4 | 圖層架構與共用狀態 | ✅ 已決定 | 獨立頁、不跟縣市篩選連動（D1、D3），沒有共用狀態，不用另寫文件 |
| 5 | 疊圖座標 | — 不需要 | 統計頁沒有疊在底圖上的元素 |
| 6 | 響應式版面 | ✅ 完成 | 手機版照 v2 手機示意圖，單欄，順序 ①②③④。要寫進 `docs/RESPONSIVE_LAYOUT.md`。舊規則「手機不顯示分頁」已在 `SVG_COMPONENTS.md` 標成作廢，RESPONSIVE_LAYOUT 在 PLAN 任務 15 改 |
| 7 | 資料匯入 | ✅ 不用改 | `web/data/markets.json` 已有 `county`、`type`、`counts`，足夠算出所有圖表。`web/js/data.js` 已有 `countyStats`、`countByStatus` 可以重用 |
| 8 | 網頁組成 | ✅ | 照 `stats-page-assets.md` §二、§五 |
| 9 | 表單 | — 不需要 | |
| 10 | 開發開關 | — 不需要 | D7：不加 |
| 11 | 測試 | ⬜ | 照 `stats-page-assets.md` §五.6 的 7 項，加進 `tests/` |
| 12 | 整體驗收 | ⬜ | 在 `docs/ACCEPTANCE.md` 加一節 |
| 13 | 後端與上線 | — 不用新後端 | 純靜態頁。部署前要先取得同意。注意 PLAN §6 第 12 項（補交後端）還在「等驗收」 |
| 14 | 收尾 | ⬜ | README 加上統計頁的說明 |

圖例：✅ 完成　🟡 進行中　⬜ 還沒開始　— 不需要

---

## 4. 等使用者決定的事

| # | 問題 | 建議 | 決定 |
|---|---|---|---|
| D1 | 統計頁要做成**獨立頁** `web/stats.html`，還是 `index.html` 裡的分頁？ | 獨立頁。和補交頁一樣，網址可以直接分享，也不會影響地圖頁現有的程式 | ✅ 獨立頁 `web/stats.html`（2026-11-01，使用者同意照建議） |
| D2 | 手機版要不要顯示「地圖總覽／統計報表」分頁？`SVG_COMPONENTS.md` 現在寫「手機和平板直向不顯示分頁」 | 要顯示。有兩頁之後，手機沒有分頁就切換不了。改成精簡版分頁，並更新舊文件 | ✅ 手機版顯示精簡版分頁，更新 `SVG_COMPONENTS.md` 的舊規則（入口方式另見 §4.1）（2026-11-01，使用者同意照建議） |
| D3 | 統計頁要不要跟地圖頁的縣市篩選連動？ | 第一版不連動，只看全台。連動之後再做 | ✅ 第一版不連動，只看全台（2026-11-01，使用者同意照建議） |
| D4 | S04 頁首街景、S05 角落樹叢要不要做？ | S05 做（成本低、畫面比較完整），S04 先不做（頁首會太擠） | ✅ S05 做，S04 不做（2026-11-01，使用者同意照建議） |
| D5 | 「待加強市場」列幾個？ | 3 個，做成設定值 | ✅ 3 個，做成設定值（2026-11-01，使用者同意照建議）。**同日改版**：卡片改成「最強友善力市集」，列比例最高的 3 個（0% 不列），見 §4.2 |
| D6 | 「已提交」包含已完成嗎？（`stats-page-assets.md` §五.1） | 包含 | ✅ 包含（2026-11-01，使用者同意照建議） |
| D7 | 開發開關要不要加「統計頁」？ | 不加。現有的「統計」開關只控制地圖頁的進度卡，統計頁用測試頁驗收就好 | ✅ 不加（2026-11-01，使用者同意照建議） |

決定後，把結果和日期填進「決定」欄，再寫進 PLAN。

### 4.2 ④ 卡片改成「最強友善力市集」（2026-11-01，任務 17 驗收時使用者提出）

- 使用者要把「待加強市集」改成「最強友善力市集」。問過之後，選了「改列比例最高的 3 個」（不是只改標題）。
- 規則：已提交比例高到低；同比例總數多的在前，再照市場 ID；0% 的不列；全部 0% 時顯示「還沒有市場提交，一起加油！」。標題圖示改成皇冠，大聲公貓保留。
- 目前資料：南機場夜市 21/21、華西街觀光夜市 20/20、龍華市場 20/20。
- 改到的地方：`stats-calc.js`（`topRows`、`TOP_N`）、`stats.js`、`stats.html`、`stats.css`（class 從 `st-weak` 改成 `st-top`）、`build_stats_svg.py`（元件檔改名 `stats-top-card.svg`）、測試和假資料（`stats-done` 改成 `stats-none`）、規格文件。

### 4.1 統計頁的入口（2026-11-01 已決定：A＋B）

使用者問「除了分頁，還有什麼方式可以呈現統計頁」。可選的方式：

| 方式 | 說明 |
|---|---|
| A. 頁首分頁 | 目前的決定（D2）。桌機、手機都在頁首放「地圖總覽／統計報表」 |
| B. 進度卡加連結 | 地圖頁左上的進度卡加一個「看完整統計 →」按鈕。不用改頁首 |
| C. 放在地圖頁下方 | 不另開一頁，地圖頁往下捲就看到 4 張統計卡片。D1 要改成「同一頁」 |
| D. 地圖頁的側邊抽屜 | 按按鈕從右邊滑出統計面板，關掉就回到地圖。D1 要改 |
| E. 手機底部導覽列 | 手機畫面最下面固定一排「地圖／統計」按鈕，像 App |

建議：**A＋B**，頁首分頁加進度卡連結。

**決定（2026-11-01，使用者同意照建議）：A＋B。**
- A：頁首分頁「地圖總覽／統計報表」，桌機和手機都有（手機用精簡版，見 D2）。地圖頁、統計頁、補交頁的頁首共用。
- B：地圖頁左上進度卡加「看完整統計 →」連結到 `stats.html`。這會改到地圖頁現有的進度卡，要更新 `docs/SVG_COMPONENTS.md` 的進度卡那一列。
- C、D、E 不做。

---

## 5. 接下來的任務（照順序，每項做完都停下來驗收）

| # | 任務 | 誰做 | 驗收標準 |
|---|---|---|---|
| 1 | 回答 §4 的 D1～D7、§4.1 入口 | 使用者 | ✅ 2026-11-01 全部照建議，入口 A＋B |
| 2 | commit 設計基準 | Claude（先問過再 commit） | ✅ 2026-11-01 `e8254d6`，分支 `claude/stats-page` |
| 3 | 更新 PLAN | Claude | ✅ 2026-11-01 PLAN 和 SVG_COMPONENTS 已改，commit `d2e9752`（對應 PLAN 任務 13） |
| 4 | 生成 S01～S03（＋D4 決定要做的） | Codex | ✅ 2026-11-01 S01～S03、S05 已生成，S04 跳過 |
| 5 | 素材驗收 | Claude → 使用者 | ✅ 2026-11-01 使用者確認，定稿存到 `design/assets/final/stats/`（驗收 `design/assets/review/stats/ACCEPTANCE.md`）。S03 偏小，轉 WebP 時統一裁邊處理 |
| 6 | SVG 組件 | Claude | ✅ 2026-11-01：`build_stats_svg.py`、9 個 SVG、`SVG_COMPONENTS.md` §7 |
| 7 | 響應式規格 | Claude | ✅ 2026-11-01：`RESPONSIVE_LAYOUT.md` 決定 J、§13 |
| 8 | 網頁實作 | Claude | ✅ 2026-11-01 完成，使用者驗收通過，commit `911ab65`。`web/stats.html`，只讀 `markets.json`，不寫死數字；素材由 `scripts/build_web_assets.py` 轉成 WebP；三頁頁首都有「地圖總覽／統計報表」分頁；地圖頁進度卡加「看完整統計 →」連結 |
| 9 | 測試 | Claude | ✅ 2026-11-01 完成，使用者驗收通過，commit `4b57617`。Node `tests/stats.test.mjs`、瀏覽器 5 項（假資料 `tests/fixtures/stats-*`）；Node 74、瀏覽器 36 項全部通過 |
| 10 | 整體驗收 | Claude → 使用者 | ✅ 2026-11-01 完成，使用者驗收通過。`docs/ACCEPTANCE.md` §5；截圖和對照圖在 `design/assets/review/stats/web/`（不進 git）；修了 3 個 CSS 小問題 |
| 11 | README、部署 | Claude（部署前先問） | README 加統計頁；部署指令要加 `--branch main` |

和 PLAN §6 的編號對照：本表 1～3 → 任務 13；4～5 → 任務 14；6～7 → 任務 15；8 → 任務 16；9 → 任務 17；10 → 任務 18；11 → 任務 19。

---

### 5.1 做 SVG 時發現的事（2026-11-01）

- **示意圖的待加強市場第三名是錯的**：示意圖寫臺東市觀光夜市（43%），照規則算應該是鄭仔寮花園夜市（7/20，35%）。網頁照規則算。（④ 後來改成「最強友善力市集」，這條已無關，見 §4.2）
- **長條上很小的段會被圓角切掉**：最小寬度改成「長條高度的一半＋2px」，已寫進 `stats-page-assets.md` §五.4。
- **手機圖例放不下百分比**：「審核中」會和數字重疊，手機版圖例只顯示家數。

### 5.2 做網頁時發現的事（2026-11-01）

- **1024～1279 寬的 2×2**：卡片只有約 430 寬，① 的貓會擋到圖例。加了一組縮小尺寸，寫進 RESPONSIVE_LAYOUT §13.2。
- **手機頁首**：分頁列放到第二列後，「確認連結」按鈕會被擠下去。標題改成先縮小、先換行。
- **手機甜甜圈中間**：「已提交 217／347 家」放不下，分成兩行。
- **補交頁頁首**：原本的「回地圖總覽」換成「地圖總覽」「統計報表」兩個分頁（手機只顯示圖示）。
- **`web/assets/bg-form.webp` 沒有動**：重跑 `build_web_assets.py` 會產生和 git 裡不同的檔案（之前的 commit `859701b` 是另外做的），這次還原了，沒有放進變更。之後重跑素材腳本要注意。

### 5.3 寫測試時發現的事（2026-11-01）

- **甜甜圈的最小段沒有扣回**：規格說補出來的長度從最長的段扣回，但 `stats-calc.js` 和 `build_stats_svg.py` 都只補不扣，三段加起來會超過一圈。兩邊都改了；目前的資料沒有太小的段，SVG 重新產生後沒有變化。
- **1024 寬的縮小尺寸在某些螢幕沒套上**：螢幕縮放不是整數時寬度是 1023.x，`min-width: 1024px` 和 `max-width: 1023px` 都不符合。改成 `max-width: 1279px`，見 RESPONSIVE_LAYOUT §13.2。地圖頁的 `layout.css`（767／768）也是同樣寫法，正式頁還沒碰到問題，先記下不改。
- **1280 寬時貓壓到圖例**：貓在 1280～1439 縮到 180 寬。

## 6. 檔案位置（重要）

- 這次的工作在 **worktree**：`C:\Users\user\claudecode\googlemap-store\.claude\worktrees\vendor-confirm-screen-visual-388349\`
- 為了讓其他工具找得到，下面兩個檔案**另外複製了一份到主資料夾**（`C:\Users\user\claudecode\googlemap-store\`），內容和 worktree 相同：
  - `design/asset-briefs/stats-mockup-prompt.md`
  - `design/asset-briefs/stats-page-assets.md`
  - 本文件 `docs/STATS_PAGE_PROGRESS.md`
- ⚠️ 主資料夾的這些副本**都還沒進 git**。之後把 worktree 的分支合併回 main 之前，要先刪掉主資料夾的副本，不然 Git 會因為「未追蹤的檔案會被覆蓋」而拒絕合併。
- 改文件時以 **worktree 版本為準**，改完再複製到主資料夾。

---

## 7. 斷線後怎麼接

1. 讀本文件，看 §1 現在在哪、§4 還有哪些沒決定、§5 下一項是什麼。
2. 讀 `design/asset-briefs/stats-page-assets.md`（拆分、素材、資料規則）。
3. 看示意圖 `design/reference/stats-mockup-v2.png`、`stats-mockup-v2-mobile.png`。
4. 用 `git status` 確認哪些檔案還沒 commit。
5. 從 §5 第一個還沒完成的任務繼續；每完成一項，就更新本文件的 §1、§3、§5，並寫上日期。
