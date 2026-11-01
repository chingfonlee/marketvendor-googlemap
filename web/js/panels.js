// 地圖以外的區塊：進度卡、縣市卡片（L 版）、篩選、市場清單卡、攤商清單。
// 每個 render 只看 state 算畫面（docs/LAYER_ARCHITECTURE.md §3「各區塊怎麼算」）。

import {
  state, STATUSES, selectCounty, clearCounty, selectMarket, clearMarket, setStatus, setKeyword,
} from "./state.js";
import {
  data, countyStats, marketsIn, vendorsInScope, countByStatus, marketFullName, scopeName,
} from "./data.js";

const ICONS = "assets/icons.svg";
const LABEL = { all: "全部", verified: "已完成", submitted: "待確認", not_submitted: "未提交" };
const COLOR = { verified: "var(--verified)", submitted: "var(--submitted)", not_submitted: "var(--not-submitted)" };
const $ = (sel) => document.querySelector(sel);
const reduceMotion = matchMedia("(prefers-reduced-motion: reduce)");

let marketsExpanded = false;   // L 版全台時市場清單的展開，只是畫面開關，不進狀態
let layout = "d";

const esc = (s) => String(s).replace(/[&<>"']/g, (c) => `&#${c.charCodeAt(0)};`);
const icon = (name) => `<svg class="icon" aria-hidden="true"><use href="${ICONS}#${name}"/></svg>`;
const pct = (n, total) => (total ? Math.round((n / total) * 1000) / 10 : 0);

export function setLayout(l) {
  layout = l;
  if (l === "l") marketsExpanded = false;
}

// ---------- 初始化：只綁一次事件 ----------
export function initPanels() {
  // 搜尋：輸入停 250ms 才觸發
  const search = $("#search");
  let timer;
  search.value = state.keyword;
  search.addEventListener("input", () => {
    clearTimeout(timer);
    timer = setTimeout(() => setKeyword(search.value), 250);
  });
  search.addEventListener("search", () => { clearTimeout(timer); setKeyword(search.value); });

  $("#county-select").addEventListener("change", (e) => {
    e.target.value ? selectCounty(e.target.value) : clearCounty();
  });
  $("#market-select").addEventListener("change", (e) => {
    e.target.value ? selectMarket(e.target.value) : clearMarket();
  });

  initStatusButtons();
  initCountySwitch();
  initCountyTiles();

  $(".status-note-toggle").addEventListener("click", (e) => {
    const note = $(".status-note");
    const open = !note.hasAttribute("data-open");
    note.toggleAttribute("data-open", open);
    e.currentTarget.setAttribute("aria-expanded", String(open));
  });

  $(".market-toggle").addEventListener("click", () => {
    marketsExpanded = !marketsExpanded;
    renderMarketCard(state);
  });

  $(".market-list").addEventListener("click", (e) => {
    const row = e.target.closest(".market-row");
    if (!row) return;
    if (row.dataset.market) {
      selectMarket(row.dataset.market);
      if (layout === "l") scrollToVendorTitle();
    } else {
      clearMarket();
    }
  });

  $(".empty-action").addEventListener("click", () => {
    if (state.keyword) {
      $("#search").value = "";
      setKeyword("");
    } else {
      setStatus("all");
    }
  });

  initToTop();
}

function initStatusButtons() {
  const group = $(".status-buttons");
  group.innerHTML = ["all", ...STATUSES].map((s) => `
    <button class="status-btn" type="button" role="radio" data-status="${s}" aria-checked="false" tabindex="-1">
      <span>${LABEL[s]}</span><b>0</b>
    </button>`).join("");
  group.addEventListener("click", (e) => {
    const btn = e.target.closest(".status-btn");
    if (btn) setStatus(btn.dataset.status);
  });
  // radiogroup：一個 Tab 停點，左右鍵切換
  group.addEventListener("keydown", (e) => {
    const keys = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 };
    if (!(e.key in keys)) return;
    e.preventDefault();
    const order = ["all", ...STATUSES];
    const i = (order.indexOf(state.status) + keys[e.key] + order.length) % order.length;
    setStatus(order[i]);
    group.querySelector(`[data-status="${order[i]}"]`).focus();
  });
}

// 市場清單卡標頭的「切換縣市 ⌄」（RESPONSIVE_LAYOUT §2.4）
function initCountySwitch() {
  const btn = $(".county-switch");
  const list = $("#county-switch-list");
  const options = [null, ...data.counties];
  let active = 0;

  const paint = () => {
    list.innerHTML = options.map((c, i) => {
      const label = c ?? `全部縣市 (${data.counties.length})`;
      return `<li role="option" id="cs-${i}" data-i="${i}" aria-selected="${state.county === c}"
        class="${i === active ? "active" : ""}">${esc(label)}</li>`;
    }).join("");
    list.setAttribute("aria-activedescendant", `cs-${active}`);
  };
  const open = () => {
    active = Math.max(0, options.indexOf(state.county));
    paint();
    list.hidden = false;
    btn.setAttribute("aria-expanded", "true");
    list.focus();
  };
  const close = (refocus) => {
    list.hidden = true;
    btn.setAttribute("aria-expanded", "false");
    if (refocus) btn.focus();
  };
  const choose = (i) => {
    close(true);
    options[i] ? selectCounty(options[i]) : clearCounty();
  };

  btn.addEventListener("click", () => (list.hidden ? open() : close(true)));
  btn.addEventListener("keydown", (e) => {
    if (e.key === "ArrowDown" || e.key === "ArrowUp") { e.preventDefault(); open(); }
  });
  list.addEventListener("click", (e) => {
    const li = e.target.closest("li");
    if (li) choose(Number(li.dataset.i));
  });
  list.addEventListener("keydown", (e) => {
    if (e.key === "ArrowDown") active = Math.min(options.length - 1, active + 1);
    else if (e.key === "ArrowUp") active = Math.max(0, active - 1);
    else if (e.key === "Home") active = 0;
    else if (e.key === "End") active = options.length - 1;
    else if (e.key === "Enter" || e.key === " ") { e.preventDefault(); choose(active); return; }
    else if (e.key === "Escape") { e.preventDefault(); close(true); return; }
    else if (e.key === "Tab") { close(false); return; }
    else return;
    e.preventDefault();
    paint();
    list.querySelector(".active")?.scrollIntoView({ block: "nearest" });
  });
  document.addEventListener("pointerdown", (e) => {
    if (!list.hidden && !e.target.closest(".market-head")) close(false);
  });
}

function initCountyTiles() {
  const grid = $(".county-grid");
  grid.innerHTML = [null, ...data.counties].map((c) => {
    const st = countyStats(c);
    const name = c ?? "全台";
    return `
      <button class="county-tile" type="button" data-county="${esc(c ?? "")}" aria-pressed="false"
        aria-label="${esc(name)}，${st.markets} 個市場，${st.vendors} 家攤商">
        <span class="tile-head">${esc(name)}</span>
        <span class="tile-body" aria-hidden="true"><span>${st.markets} 個市場</span><span>${st.vendors} 家攤商</span></span>
      </button>`;
  }).join("");
  grid.addEventListener("click", (e) => {
    const tile = e.target.closest(".county-tile");
    if (!tile) return;
    tile.dataset.county ? selectCounty(tile.dataset.county) : clearCounty();
  });
}

function initToTop() {
  const btn = $(".to-top");
  const title = $("#vendor-title");
  new IntersectionObserver(([entry]) => {
    // 捲過攤商清單標題（標題跑到畫面上方）才出現
    btn.hidden = layout !== "l" || entry.isIntersecting || entry.boundingClientRect.top > 0;
  }).observe(title);
  btn.addEventListener("click", () => {
    const target = $("#county-cards-title");
    target.scrollIntoView({ behavior: reduceMotion.matches ? "auto" : "smooth", block: "start" });
    target.focus({ preventScroll: true });
  });
}

function scrollToVendorTitle() {
  const title = $("#vendor-title");
  title.scrollIntoView({ behavior: reduceMotion.matches ? "auto" : "smooth", block: "start" });
  title.focus({ preventScroll: true });
}

// ---------- 畫面 ----------
export function renderPanels(s, prev, cause) {
  if (prev?.county && !s.county) marketsExpanded = false;  // 回到全台恢復收起
  renderProgress(s);
  renderCountyTiles(s);
  renderSelects(s);
  renderMarketCard(s);
  const list = vendorsInScope(s);
  renderStatusButtons(s, list);
  renderVendors(s, list, prev);
  if (cause && cause !== "hash") announce(s, list);
}

function renderProgress(s) {
  const st = countyStats(s.county);
  const total = st.vendors;
  const name = s.county ?? "全台";
  const updated = formatTime(data.meta.updated);
  if (layout === "l") {
    $("#progress-title").textContent = `${name} ${st.markets} 個市場・${total} 家攤商`;
    $(".progress-updated").textContent = `Google 地圖登錄進度・最後更新 ${updated}`;
    $(".donut-value").textContent = `${pct(st.counts.verified, total)}%`;
    $(".donut-unit").textContent = "完成率";
  } else {
    $("#progress-title").textContent = s.county ? `${s.county}完成進度` : "整體完成進度";
    $(".progress-updated").textContent = `最後更新：${updated}`;
    $(".donut-value").textContent = total;
    $(".donut-unit").textContent = "家攤商";
  }

  // 圓環：3 段，從 12 點鐘方向順時針
  const r = 52;
  const C = 2 * Math.PI * r;
  let offset = 0;
  $(".donut-segments").innerHTML = `<circle cx="60" cy="60" r="${r}" stroke="var(--field)"/>` +
    STATUSES.map((k) => {
      const len = total ? (st.counts[k] / total) * C : 0;
      const seg = len > 0
        ? `<circle cx="60" cy="60" r="${r}" stroke="${COLOR[k]}" stroke-dasharray="${len} ${C - len}" stroke-dashoffset="${-offset}"/>`
        : "";
      offset += len;
      return seg;
    }).join("");

  $(".progress-legend").innerHTML = STATUSES.map((k) => `
    <li><span class="dot" style="background:${COLOR[k]}"></span><span>${LABEL[k]}</span>
      <b>${st.counts[k]} <small>(${pct(st.counts[k], total)}%)</small></b></li>`).join("");
}

function renderCountyTiles(s) {
  for (const tile of document.querySelectorAll(".county-tile")) {
    tile.setAttribute("aria-pressed", String((tile.dataset.county || null) === s.county));
  }
}

function renderSelects(s) {
  $("#county-select").innerHTML =
    `<option value="">全部縣市 (${data.counties.length})</option>` +
    data.counties.map((c) => `<option value="${esc(c)}"${c === s.county ? " selected" : ""}>${esc(c)}</option>`).join("");
  const markets = marketsIn(s.county);
  $("#market-select").innerHTML =
    `<option value="">全部市場 (${markets.length})</option>` +
    markets.map((m) => `<option value="${m.id}"${m.id === s.marketId ? " selected" : ""}>${esc(m.name)}</option>`).join("");
}

function marketRow(m, s) {
  const thumb = data.manifest.market_types[m.type];
  const current = m.id === s.marketId;
  return `
    <button class="market-row" type="button" data-market="${m.id}" aria-current="${current}">
      ${thumb ? `<img class="market-thumb" src="assets/${thumb}" alt="" loading="lazy">` : `<span class="market-thumb"></span>`}
      <span class="market-info">
        <span class="market-name">${esc(marketFullName(m))}</span>
        <span class="market-meta">${m.vendor_count} 家攤商</span>
        <span class="market-meta">完成 ${m.counts.verified}<span class="sep">|</span>待確認 ${m.counts.submitted}<span class="sep">|</span>未提交 ${m.counts.not_submitted}</span>
      </span>
      ${current && layout === "l" ? `<span class="check" aria-hidden="true">✓</span>` : icon("chevron-right")}
    </button>`;
}

function renderMarketCard(s) {
  const st = countyStats(s.county);
  const name = s.county ?? "全台";
  const markets = marketsIn(s.county);
  $(".market-head-name").textContent = name;
  $(".market-head-sub").textContent = `共 ${st.markets} 個市場｜${st.vendors} 家攤商`;
  $(".county-switch").setAttribute("aria-label", `切換縣市，目前${name}`);
  $(".market-title-l").textContent = `${name}・市場 (${markets.length})`;

  // L 版：全台時收起（決定 F）
  const toggle = $(".market-toggle");
  const collapsible = layout === "l" && !s.county;
  toggle.hidden = !collapsible;
  toggle.setAttribute("aria-expanded", String(marketsExpanded));
  toggle.innerHTML = marketsExpanded
    ? `<span class="hint"><b>收起 ${markets.length} 個市場</b></span><span aria-hidden="true">⌃</span>`
    : `<b>${markets.length} 個市場</b><span class="hint">▸ 點縣市卡片查看，或展開全部</span><span aria-hidden="true">展開 ⌄</span>`;

  const list = $(".market-list");
  list.hidden = collapsible && !marketsExpanded;
  let html = "";
  if (s.county) {
    if (layout === "l") {
      html += `
        <button class="market-row market-row-all" type="button" aria-current="${!s.marketId}">
          <span class="market-info"><span class="market-name">全部市場（${st.vendors} 家）</span></span>
          ${!s.marketId ? `<span class="check" aria-hidden="true">✓</span>` : icon("chevron-right")}
        </button>`;
    }
    html += markets.map((m) => marketRow(m, s)).join("");
  } else {
    for (const c of data.counties) {
      html += `<p class="market-group">${esc(c)}</p>` + data.marketsByCounty.get(c).map((m) => marketRow(m, s)).join("");
    }
  }
  list.innerHTML = html;
}

function renderStatusButtons(s, list) {
  const counts = countByStatus(list);
  for (const btn of document.querySelectorAll(".status-btn")) {
    const k = btn.dataset.status;
    const checked = k === s.status;
    btn.setAttribute("aria-checked", String(checked));
    btn.tabIndex = checked ? 0 : -1;
    btn.querySelector("b").textContent = k === "all" ? list.length : counts[k];
  }
}

function renderVendors(s, scoped, prev) {
  const list = s.status === "all" ? scoped : scoped.filter((v) => v.status === s.status);
  $("#vendor-title").textContent = `${scopeName(s)}・攤商清單 (${list.length})`;
  $(".vendor-list").innerHTML = list.map((v) => {
    const action = v.url
      ? `<a class="vendor-action" href="${esc(v.url)}" target="_blank" rel="noopener" aria-label="開啟 ${esc(v.name)} 的 Google 地圖">${icon("external")}</a>`
      : `<a class="vendor-action" href="submit.html#vendor=${v.id}" aria-label="補交 ${esc(v.name)} 的 Google 地圖連結">${icon("edit")}</a>`;
    return `<li class="vendor-row"><span class="vendor-name">${esc(v.name)}</span>
      <span><span class="badge" data-status="${v.status}">${LABEL[v.status]}</span></span>${action}</li>`;
  }).join("");

  const empty = list.length === 0;
  $(".vendor-card").classList.toggle("is-empty", empty);
  $(".empty-state").hidden = !empty;
  if (empty) {
    const byKeyword = s.keyword && scoped.length === 0;
    // 範圍本身沒有攤商（例如攤商全部被排除的市場）：已經是「全部」，沒有按鈕可以按
    const noVendors = !byKeyword && s.status === "all";
    $(".empty-text").textContent = byKeyword
      ? `找不到符合「${s.keyword}」的攤商`
      : noVendors
        ? `${s.marketId ? "這個市場" : s.county ? "這個縣市" : "目前"}還沒有攤商`
        : `這個範圍還沒有${LABEL[s.status]}的攤商`;
    $(".empty-action").textContent = byKeyword ? "清除搜尋" : "顯示全部狀態";
    $(".empty-action").hidden = noVendors;
  }

  // 範圍或篩選改變時，D 版清單捲回最上面
  const changed = !prev || prev.county !== s.county || prev.marketId !== s.marketId ||
    prev.status !== s.status || prev.keyword !== s.keyword;
  if (changed && layout === "d") $(".vendor-scroll").scrollTop = 0;
  if ($("#search").value.trim() !== s.keyword) $("#search").value = s.keyword;
}

function announce(s, scoped) {
  const n = s.status === "all" ? scoped.length : scoped.filter((v) => v.status === s.status).length;
  $("#live").textContent = n ? `${scopeName(s)}，${n} 家攤商` : "找不到符合的攤商";
}

function formatTime(iso) {
  const d = new Date(iso);
  const p = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}/${p(d.getMonth() + 1)}/${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`;
}
