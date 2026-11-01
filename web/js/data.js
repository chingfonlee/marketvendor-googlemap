// 讀取匯入程式產生的 JSON（任務 6），算各範圍的統計。網頁只讀，不改資料。

import { STATUSES } from "./state.js";

export const data = {
  meta: null,
  labels: null,      // county-labels.json
  manifest: null,    // assets/manifest.json
  markets: [],
  vendors: [],
  counties: [],      // 照 labels.json 的順序（北到南）
  marketById: new Map(),
  marketsByCounty: new Map(),
  vendorsByMarket: new Map(),
};

async function getJSON(path) {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`${path}: ${res.status}`);
  return res.json();
}

export async function loadData() {
  const [markets, vendors, meta, labels, manifest] = await Promise.all([
    getJSON("data/markets.json"),
    getJSON("data/vendors.json"),
    getJSON("data/meta.json"),
    getJSON("data/county-labels.json"),
    getJSON("assets/manifest.json"),
  ]);
  Object.assign(data, { markets, vendors, meta, labels, manifest });
  data.counties = labels.labels.map((l) => l.county);
  for (const c of data.counties) data.marketsByCounty.set(c, []);
  for (const m of markets) {
    data.marketById.set(m.id, m);
    data.marketsByCounty.get(m.county)?.push(m);
    data.vendorsByMarket.set(m.id, []);
  }
  for (const v of vendors) data.vendorsByMarket.get(v.market_id)?.push(v);

  // 底圖換了但座標沒跟著更新時提醒（LAYER_ARCHITECTURE §4；開發開關面板讀這個標記顯示警告）
  if (manifest.basemap_source_sha256 !== labels.basemap_sha256) {
    console.warn("county-labels.json 的 basemap_sha256 和網頁使用的底圖不一致，標籤位置可能對不上");
    document.documentElement.dataset.basemapMismatch = "";
  }
  return data;
}

function emptyCounts() {
  return Object.fromEntries(STATUSES.map((s) => [s, 0]));
}

// 縣市（null＝全台）的市場數、攤商數、各狀態數量。不受狀態篩選和搜尋影響。
export function countyStats(county) {
  const markets = county ? data.marketsByCounty.get(county) || [] : data.markets;
  const counts = emptyCounts();
  let vendors = 0;
  for (const m of markets) {
    vendors += m.vendor_count;
    for (const s of STATUSES) counts[s] += m.counts[s];
  }
  return { markets: markets.length, vendors, counts };
}

export function marketsIn(county) {
  return county ? data.marketsByCounty.get(county) || [] : data.markets;
}

// 攤商清單的範圍：有市場用市場，只有縣市用縣市，都沒有是全台；再套用搜尋，不套用狀態
export function vendorsInScope({ county, marketId, keyword }) {
  let list;
  if (marketId) list = data.vendorsByMarket.get(marketId) || [];
  else if (county) list = marketsIn(county).flatMap((m) => data.vendorsByMarket.get(m.id));
  else list = data.vendors;
  const k = keyword.toLowerCase();
  return k ? list.filter((v) => v.name.toLowerCase().includes(k)) : list;
}

export function countByStatus(list) {
  const counts = emptyCounts();
  for (const v of list) counts[v.status] += 1;
  return counts;
}

// 「臺北」＋「永春市場」＝「臺北永春市場」；名稱已經帶縣市的不重複（臺東市觀光夜市）
export function marketFullName(m) {
  const short = m.county.replace(/[市縣]$/, "");
  return m.name.startsWith(short) ? m.name : short + m.name;
}

export function scopeName({ county, marketId }) {
  if (marketId) return marketFullName(data.marketById.get(marketId));
  return county || "全台";
}
