// 開發開關（任務 9，docs/SVG_COMPONENTS.md §6）。只在開發環境由 main.js／submit.js 載入，
// 正式環境不會下載這個檔案。設定存在這個瀏覽器，總覽頁和補交頁共用。

import { DEV_DEFAULTS, IS_DEV, readDev, writeDev } from "./env.js";

const SWITCHES = [
  { key: "base", name: "底圖", hint: "底圖、地圖標語、地圖上的貓" },
  { key: "labels", name: "縣市標籤", hint: "地圖標籤、圖例、清單版的縣市卡片" },
  { key: "interact", name: "互動", hint: "地圖點選和縮放、縣市卡片、選單、搜尋、狀態按鈕、市場清單" },
  { key: "stats", name: "統計", hint: "進度卡" },
  { key: "list", name: "清單", hint: "篩選面板、市場清單卡、攤商清單、空狀態" },
];
const SUBMIT = [
  { value: "mock", name: "模擬送出", hint: "紀錄存在這個瀏覽器" },
  { value: "api", name: "正式 API", hint: "送到 /api/submissions（任務 12 才建立）" },
  { value: "off", name: "關閉", hint: "和目前正式環境一樣，不能送出" },
];
// 互動關閉時整塊不能操作，畫面停在目前的篩選（inert 同時擋掉滑鼠、觸控和鍵盤）
const INTERACTIVE = "main.map, .county-cards, .filter-search, .filter-selects, .filter-status, .market-card";

let settings;
let page;

export function initDevtools(which) {
  if (!IS_DEV) return;   // 就算有人手動載入這個檔案，正式環境也不會出現開關
  page = which;
  settings = readDev();
  const css = document.createElement("link");
  css.rel = "stylesheet";
  css.href = "css/devtools.css";
  document.head.append(css);
  build();
  apply();
}

function apply() {
  const root = document.documentElement;
  const off = SWITCHES.filter((s) => !settings[s.key]).map((s) => s.key);
  if (off.length) root.dataset.devOff = off.join(" ");
  else delete root.dataset.devOff;
  for (const el of document.querySelectorAll(INTERACTIVE)) el.inert = !settings.interact;
  document.querySelector(".dev-fab").classList.toggle("is-changed", off.length > 0 || settings.submit !== DEV_DEFAULTS.submit);
}

function save() {
  writeDev(settings);
  apply();
}

function build() {
  const mismatch = "basemapMismatch" in document.documentElement.dataset;
  const fab = document.createElement("button");
  fab.type = "button";
  fab.className = "dev-fab";
  fab.setAttribute("aria-expanded", "false");
  fab.setAttribute("aria-controls", "dev-panel");
  fab.innerHTML = `開發${mismatch ? `<span class="dev-alert" aria-label="有警告">!</span>` : ""}`;

  const panel = document.createElement("section");
  panel.id = "dev-panel";
  panel.className = "dev-panel";
  panel.setAttribute("aria-label", "開發開關");
  panel.hidden = true;
  panel.innerHTML = `
    <header class="dev-head">
      <b>開發開關</b>
      <span>只在本機出現，正式環境沒有</span>
    </header>
    ${mismatch ? `<p class="dev-warn" role="alert">底圖和 county-labels.json 的 SHA-256 不一致，標籤位置可能對不上。請重跑 scripts/build_web_assets.py。</p>` : ""}
    <fieldset class="dev-group">
      <legend>總覽頁</legend>
      ${SWITCHES.map((s) => `
        <label class="dev-row">
          <input type="checkbox" name="${s.key}" ${settings[s.key] ? "checked" : ""}>
          <span><b>${s.name}</b><small>${s.hint}</small></span>
        </label>`).join("")}
    </fieldset>
    <fieldset class="dev-group">
      <legend>補交頁的送出方式</legend>
      ${SUBMIT.map((m) => `
        <label class="dev-row">
          <input type="radio" name="submit" value="${m.value}" ${settings.submit === m.value ? "checked" : ""}>
          <span><b>${m.name}</b><small>${m.hint}</small></span>
        </label>`).join("")}
    </fieldset>
    <button class="dev-reset" type="button">全部恢復預設</button>`;

  fab.addEventListener("click", () => {
    panel.hidden = !panel.hidden;
    fab.setAttribute("aria-expanded", String(!panel.hidden));
  });
  panel.addEventListener("change", (e) => {
    const input = e.target;
    if (input.type === "checkbox") settings[input.name] = input.checked;
    else if (input.name === "submit") settings.submit = input.value;
    save();
    // 補交頁在啟動時決定送出方式，換了就重新載入
    if (input.name === "submit" && page === "submit") location.reload();
  });
  panel.querySelector(".dev-reset").addEventListener("click", () => {
    const reload = page === "submit" && settings.submit !== DEV_DEFAULTS.submit;
    settings = { ...DEV_DEFAULTS };
    for (const input of panel.querySelectorAll("input")) {
      input.checked = input.type === "checkbox" ? settings[input.name] : input.value === settings.submit;
    }
    save();
    if (reload) location.reload();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !panel.hidden) {
      panel.hidden = true;
      fab.setAttribute("aria-expanded", "false");
      fab.focus();
    }
  });
  document.body.append(panel, fab);
}
