// 統計頁的計算（PLAN §2.1；規則見 design/asset-briefs/stats-page-assets.md §五）。
// 只有純函式，不碰 DOM，Node 測試可以直接 import。和 design/tools/build_stats_svg.py 的算法相同。

export const KEYS = ["verified", "submitted", "not_submitted"];
export const TYPES = ["night_market", "traditional_market", "other"];
export const TOP_N = 3;           // 最強友善力市集列幾個（D5）
export const MIN_DONUT_SEG = 2;   // 甜甜圈：家數 > 0 的段至少幾 px

export const zero = () => ({ verified: 0, submitted: 0, not_submitted: 0 });

export function add(a, b) {
  const out = zero();
  for (const k of KEYS) out[k] = (a[k] || 0) + (b[k] || 0);
  return out;
}

export const total = (c) => KEYS.reduce((n, k) => n + c[k], 0);
// 已提交 = 已完成 + 待確認（PLAN §3）
export const done = (c) => c.verified + c.submitted;
export const ratio = (c) => (total(c) ? done(c) / total(c) : 0);

// 中間的大字顯示到小數一位，其他四捨五入到整數
export const pctText = (c, digits = 0) => `${(ratio(c) * 100).toFixed(digits)}%`;

export function overall(markets) {
  return markets.reduce((acc, m) => add(acc, m.counts), zero());
}

// 新的市場類型歸到「其他」
export const typeOf = (m) => (TYPES.includes(m.type) ? m.type : "other");

function group(markets, keyOf) {
  const out = new Map();
  for (const m of markets) {
    const k = keyOf(m);
    out.set(k, add(out.get(k) || zero(), m.counts));
  }
  for (const [k, c] of out) if (!total(c)) out.delete(k);
  return out;
}

// 已提交比例高到低；同比例總數多的在前；再同照縣市名稱。並列第一的都有皇冠。
export function countyRows(markets) {
  const rows = [...group(markets, (m) => m.county)]
    .map(([county, counts]) => ({ county, counts }))
    .sort((a, b) => ratio(b.counts) - ratio(a.counts) || total(b.counts) - total(a.counts) ||
      (a.county < b.county ? -1 : a.county > b.county ? 1 : 0));  // 和 build_stats_svg.py 一樣照字碼排
  const top = rows.length ? ratio(rows[0].counts) : 0;
  return rows.map((r) => ({ ...r, crown: ratio(r.counts) === top }));
}

// 照 TYPES 的順序，沒有市場的類型不列
export function typeRows(markets) {
  const g = group(markets, typeOf);
  return TYPES.filter((t) => g.has(t)).map((type) => ({ type, counts: g.get(type) }));
}

// 最強友善力市集：已提交比例最高的 n 個，不含 0%；同比例總數多的在前，再照 ID
export function topRows(markets, n = TOP_N) {
  return markets
    .filter((m) => done(m.counts) > 0)
    .sort((a, b) => ratio(b.counts) - ratio(a.counts) ||
      total(b.counts) - total(a.counts) || a.id.localeCompare(b.id))
    .slice(0, n);
}

// 100% 堆疊長條三段的寬度（百分比）。家數 > 0 的段至少 minPct，補出來的從最寬的段扣回，加起來剛好 100。
export function barWidths(c, minPct = 0) {
  const n = total(c);
  if (!n) return KEYS.map(() => 0);
  const w = KEYS.map((k) => (c[k] ? Math.max((c[k] / n) * 100, minPct) : 0));
  const over = w.reduce((s, v) => s + v, 0) - 100;
  if (over > 0) {
    const big = w.indexOf(Math.max(...w));
    w[big] -= over;
  }
  return w;
}

// 甜甜圈三段：[{ key, len, offset }]，len、offset 是圓周上的長度。
// 家數 > 0 的段至少 MIN_DONUT_SEG，補出來的從最長的段扣回，加起來剛好一圈。
export function donutSegments(c, circumference) {
  const n = total(c);
  if (!n) return [];
  const out = KEYS.filter((k) => c[k]).map((key) => ({ key, len: Math.max((c[key] / n) * circumference, MIN_DONUT_SEG) }));
  const over = out.reduce((s, x) => s + x.len, 0) - circumference;
  if (over > 0) out.reduce((a, b) => (b.len > a.len ? b : a)).len -= over;
  let acc = 0;
  for (const x of out) { x.offset = acc; acc += x.len; }
  return out;
}
