// 進入點：載入資料、還原網址狀態、依 --layout 切換 D／L 版（docs/RESPONSIVE_LAYOUT.md §4.7）。

import { state, configure, subscribe, readHash } from "./state.js";
import { data, loadData } from "./data.js";
import { ensureMap, renderMap } from "./map.js";
import { initPanels, renderPanels, setLayout } from "./panels.js";

const $ = (sel) => document.querySelector(sel);
let layout = null;

// L 版的畫面順序和 D 版不同：搬節點，不用 CSS order，也不複製（DOM 裡永遠只有一個搜尋框）
function moveNodes(l) {
  const keep = document.activeElement;
  const search = $(".filter-search");
  const status = $(".filter-status");
  const cat = $(".megaphone-cat");
  if (l === "l") {
    $(".vendor-filters").append(search, status);
    $(".site-footer").append(cat);
  } else {
    const panel = $(".filter-panel");
    panel.prepend(search);
    $(".filter-selects").after(status);
    panel.append(cat);
  }
  $(".county-cards").hidden = l !== "l";
  if (keep && keep !== document.activeElement && document.contains(keep)) keep.focus({ preventScroll: true });
}

function applyLayout() {
  const next = getComputedStyle(document.documentElement).getPropertyValue("--layout").trim() || "d";
  if (next === layout) return;
  layout = next;
  document.body.dataset.layout = layout;
  setLayout(layout);
  moveNodes(layout);
  $("main.map").hidden = layout !== "d";
  if (layout === "d") ensureMap($("main.map"));   // 清單版不建立地圖、不下載底圖
  render(state);
}

function render(s, prev, cause) {
  renderMap(s);
  renderPanels(s, prev, cause);
}

async function start() {
  try {
    await loadData();
  } catch (err) {
    console.error(err);
    $(".load-error").hidden = false;
    return;
  }
  configure({
    countyOf: (id) => data.marketById.get(id)?.county ?? null,
    isCounty: (c) => data.counties.includes(c),
  });
  initPanels();
  subscribe(render);
  delete document.body.dataset.loading;
  applyLayout();
  readHash();
  window.addEventListener("resize", applyLayout);
  window.addEventListener("hashchange", readHash);
}

start();
