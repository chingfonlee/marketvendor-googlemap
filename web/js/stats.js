// 統計報表頁（PLAN §2.1）：只讀 markets.json 和 meta.json，所有數字、列數、排序都由 stats-calc.js 算。
// 頁首照 --layout 切換 D／L 樣式（和總覽頁共用 layout.css），內容的 2×2／單欄由 stats.css 的寬度決定。

import {
  KEYS, TYPES, total, done, pctText, overall, countyRows, typeRows, topRows, barWidths, donutSegments, typeOf,
} from "./stats-calc.js";

const $ = (sel) => document.querySelector(sel);
const LABEL = { verified: "已完成", submitted: "待確認", not_submitted: "未提交" };
const TYPE_NAME = { night_market: "夜市", traditional_market: "傳統市場", other: "美食廣場" };
const typeIcon = (t) => `assets/stats/type-${TYPES.includes(t) ? t : "other"}.webp`;
const esc = (s) => String(s).replace(/[&<>"]/g, (ch) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[ch]);

function applyLayout() {
  const next = getComputedStyle(document.documentElement).getPropertyValue("--layout").trim() || "d";
  if (document.body.dataset.layout !== next) document.body.dataset.layout = next;
}

const detail = (c) => KEYS.map((k) => `${LABEL[k]} ${c[k]}`).join("、");

// 甜甜圈：viewBox 120，半徑 48，環寬由 CSS 決定
function donut(c, center) {
  const C = 2 * Math.PI * 48;
  const segs = donutSegments(c, C).map((s) =>
    `<circle class="seg-${s.key}" cx="60" cy="60" r="48" stroke-dasharray="${s.len} ${C}" stroke-dashoffset="${-s.offset}"/>`);
  return `<svg viewBox="0 0 120 120" aria-hidden="true"><g transform="rotate(-90 60 60)">` +
    `<circle class="seg-bg" cx="60" cy="60" r="48"/>${segs.join("")}</g></svg>` +
    `<div class="st-donut-center">${center}</div>`;
}

// 100% 堆疊長條；太窄的段由 CSS 的 min-width 補到看得見
function bar(c) {
  const w = barWidths(c);
  return `<span class="st-bar" aria-hidden="true">${KEYS.map((k, i) =>
    w[i] ? `<i class="seg-${k}" style="--w:${w[i]}%"></i>` : "").join("")}</span>`;
}

function renderOverview(c, updated) {
  const n = total(c);
  const d = new Date(updated);
  const p = (v) => String(v).padStart(2, "0");
  $(".st-updated").textContent = `資料更新：${d.getFullYear()}/${p(d.getMonth() + 1)}/${p(d.getDate())}`;
  const box = $(".st-donut-lg");
  box.setAttribute("aria-label", `已提交 ${pctText(c, 1)}，${done(c)}／${n} 家；${detail(c)}`);
  box.innerHTML = donut(c, `<b class="st-big">${pctText(c, 1)}</b><span class="st-sub"><span>已提交</span> <span>${done(c)}／${n} 家</span></span>`);
  $(".st-legend").innerHTML = KEYS.map((k) => `
    <li><span class="dot seg-${k}"></span><span class="st-legend-name">${LABEL[k]}${
      k === "verified" && c[k] === 0 ? '<span class="st-reviewing">審核中</span>' : ""}</span>
      <b>${c[k]}</b><small>${n ? Math.round((c[k] / n) * 100) : 0}%</small></li>`).join("");
}

function renderCounties(rows) {
  $(".st-county-list").innerHTML = rows.map((r) => `
    <li>
      <span class="st-crown">${r.crown ? '<svg class="icon" aria-label="第一名" role="img"><use href="assets/icons.svg#crown"/></svg>' : ""}</span>
      <span class="st-name">${esc(r.county)}</span>
      ${bar(r.counts)}
      <b class="st-pct">${pctText(r.counts)}</b>
      <span class="sr-only">（${detail(r.counts)}）</span>
    </li>`).join("");
}

function renderTypes(rows) {
  const list = $(".st-type-list");
  list.style.setProperty("--n", rows.length);
  list.innerHTML = rows.map((r) => `
    <li>
      <img src="${typeIcon(r.type)}" alt="" width="80" height="80">
      <span class="st-type-name">${TYPE_NAME[r.type]}</span>
      <div class="st-donut st-donut-sm" role="img" aria-label="${TYPE_NAME[r.type]}已提交 ${pctText(r.counts)}；${detail(r.counts)}">
        ${donut(r.counts, `<b>${pctText(r.counts)}</b>`)}
      </div>
    </li>`).join("");
}

function renderTop(rows) {
  $(".st-top-empty").hidden = rows.length > 0;
  $(".st-top-list").innerHTML = rows.map((m) => `
    <li>
      <img src="${typeIcon(typeOf(m))}" alt="" width="40" height="40">
      <span class="st-top-name">${esc(m.name)}</span>
      ${bar(m.counts)}
      <b class="st-frac">${done(m.counts)}/${total(m.counts)}</b>
      <span class="sr-only">（已提交 ${pctText(m.counts)}；${detail(m.counts)}）</span>
    </li>`).join("");
}

async function getJSON(path) {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`${path}: ${res.status}`);
  return res.json();
}

async function start() {
  applyLayout();
  window.addEventListener("resize", applyLayout);
  let markets, meta;
  try {
    [markets, meta] = await Promise.all([getJSON("data/markets.json"), getJSON("data/meta.json")]);
  } catch (err) {
    console.error(err);
    $(".load-error").hidden = false;
    return;
  }
  const all = overall(markets);
  if (!total(all)) {  // 資料是空的：不畫圖表，顯示空狀態（stats-page-assets §五.5）
    $(".stats-main").innerHTML = `<section class="card st-empty"><img src="assets/empty-state.webp" alt="" width="160">
      <p>目前沒有統計資料。</p></section>`;
    delete document.body.dataset.loading;
    return;
  }
  renderOverview(all, meta.updated);
  renderCounties(countyRows(markets));
  renderTypes(typeRows(markets));
  renderTop(topRows(markets));
  delete document.body.dataset.loading;
}

start();
