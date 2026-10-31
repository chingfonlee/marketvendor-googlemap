// 全頁唯一的狀態和 6 個動作（docs/LAYER_ARCHITECTURE.md §3）。
// 每次改變都通知所有區塊依新狀態重畫，區塊之間不互相呼叫。

export const state = {
  county: null,      // 縣市名稱；null 表示全台
  marketId: null,    // 市場 id；null 表示未選
  status: "all",     // "all" | "verified" | "submitted" | "not_submitted"
  keyword: "",
  zoom: { scale: 1, x: 0, y: 0 },  // 由 map.js 直接更新，不觸發重畫
};

export const STATUSES = ["verified", "submitted", "not_submitted"];
const listeners = new Set();
let lookup = { countyOf: () => null, isCounty: () => false };

export function configure(fns) { lookup = fns; }
export function subscribe(fn) { listeners.add(fn); }

function commit(patch, cause) {
  const prev = { ...state };
  Object.assign(state, patch);
  writeHash();
  for (const fn of listeners) fn(state, prev, cause);
}

export function selectCounty(c) {
  if (c === state.county) return;  // 點已選的縣市：不變
  commit({ county: c, marketId: null }, "county");
}
export function clearCounty() {
  if (state.county === null && state.marketId === null) return;
  commit({ county: null, marketId: null }, "county");
}
export function selectMarket(id) {
  if (id === state.marketId) return;
  commit({ marketId: id, county: lookup.countyOf(id) }, "market");
}
export function clearMarket() {
  if (state.marketId === null) return;
  commit({ marketId: null }, "market");
}
export function setStatus(s) {
  if (s === state.status) return;
  commit({ status: s }, "status");
}
export function setKeyword(k) {
  k = k.trim();
  if (k === state.keyword) return;
  commit({ keyword: k }, "keyword");
}

// ---------- 網址 hash：#county=臺北市&market=m01&status=submitted&q=… ----------
function writeHash() {
  const p = new URLSearchParams();
  if (state.county) p.set("county", state.county);
  if (state.marketId) p.set("market", state.marketId);
  if (state.status !== "all") p.set("status", state.status);
  if (state.keyword) p.set("q", state.keyword);
  const hash = p.toString();
  if (hash !== location.hash.slice(1)) {
    history.replaceState(null, "", hash ? `#${hash}` : location.pathname + location.search);
  }
}

export function readHash() {
  const p = new URLSearchParams(location.hash.slice(1));
  const patch = { county: null, marketId: null, status: "all", keyword: "" };
  const market = p.get("market");
  if (market && lookup.countyOf(market)) {
    patch.marketId = market;
    patch.county = lookup.countyOf(market);
  } else if (lookup.isCounty(p.get("county"))) {
    patch.county = p.get("county");
  }
  if (STATUSES.includes(p.get("status"))) patch.status = p.get("status");
  patch.keyword = (p.get("q") || "").trim();
  commit(patch, "hash");
}
