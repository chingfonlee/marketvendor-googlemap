// 補交／確認頁（docs/PLAN.md §5）：縣市 → 市場 → 攤商三層選單，確認現有連結或貼新網址。
// 後端（任務 12）還沒建立：開發環境依開發開關模擬送出或打正式 API；正式環境暫時不能送出。

import { data, loadData, marketFullName } from "./data.js";
import { checkUrl } from "./urlcheck.js";
import { IS_DEV, loadDevtools, submitMode } from "./env.js";

const $ = (sel) => document.querySelector(sel);
const LABEL = { verified: "已完成", submitted: "待確認", not_submitted: "未提交" };

const MODE = submitMode();   // "mock" | "api" | "off"
const API = "/api/submissions";
const MODE_TEXT = {
  mock: "開發模式：模擬送出，紀錄只存在這個瀏覽器，不會送到伺服器。",
  api: `開發模式：送到正式 API（${API}）。後端在任務 12 才建立，在那之前會送出失敗。`,
  off: IS_DEV ? "開發模式：送出已關閉，畫面和目前的正式環境一樣。" : "補交功能還在準備中，暫時無法送出。",
};

const MOCK_KEY = "gm-submit-mock";
const DEDUPE_MS = 24 * 3600 * 1000;   // 同一攤商、同一網址 24 小時內只收一次
const HOURLY_LIMIT = 10;              // 同一 IP 每小時上限（模擬時以這個瀏覽器代替 IP）
export const CSV_COLUMNS = [
  "submitted_at", "ip", "county", "market_id", "market_name", "vendor_id", "vendor_name",
  "action", "url", "place_key", "status_before", "review_result", "reviewed_at", "note",
];

const sel = { county: null, marketId: null, vendorId: null };
let urlTouched = false;

// ---------- 紀錄 ----------
export function taipeiTime(date = new Date()) {
  return new Date(date.getTime() + 8 * 3600 * 1000).toISOString().slice(0, 19) + "+08:00";
}

export function buildRecord({ vendor, market, action, url, placeKey, ip = "", now = new Date() }) {
  return {
    submitted_at: taipeiTime(now),
    ip,
    county: market.county,
    market_id: market.id,
    market_name: market.name,
    vendor_id: vendor.id,
    vendor_name: vendor.name,
    action,
    url,
    place_key: placeKey,
    status_before: vendor.status,
    review_result: "",
    reviewed_at: "",
    note: "",
  };
}

export function toCSV(records) {
  const cell = (v) => (/[",\n]/.test(String(v)) ? `"${String(v).replace(/"/g, '""')}"` : String(v));
  return [CSV_COLUMNS.join(","), ...records.map((r) => CSV_COLUMNS.map((c) => cell(r[c] ?? "")).join(","))].join("\r\n") + "\r\n";
}

function readMock() {
  try {
    return JSON.parse(localStorage.getItem(MOCK_KEY)) || [];
  } catch {
    return [];
  }
}
function writeMock(list) {
  try {
    localStorage.setItem(MOCK_KEY, JSON.stringify(list));
  } catch { /* 無痕視窗等情況存不了，畫面照常 */ }
}
const recordTime = (r) => Date.parse(r.submitted_at);

// 模擬伺服器會做的檢查（任務 12 由後端負責）
function mockSubmit(record) {
  const list = readMock();
  const now = Date.now();
  if (list.some((r) => r.vendor_id === record.vendor_id && r.url === record.url && now - recordTime(r) < DEDUPE_MS)) {
    return { ok: false, error: "這家店的這個網址 24 小時內已經送過了，不用再送。" };
  }
  if (list.filter((r) => now - recordTime(r) < 3600 * 1000).length >= HOURLY_LIMIT) {
    return { ok: false, error: "送出次數太多，請一小時後再試。" };
  }
  list.push({ ...record, ip: "127.0.0.1" });
  writeMock(list);
  return { ok: true };
}

// 正式 API：IP 由伺服器填；回應格式 { ok, error? } 在任務 12 定案
async function apiSubmit(record) {
  try {
    const res = await fetch(API, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(record),
    });
    const body = await res.json().catch(() => ({}));
    if (res.ok && body.ok !== false) return { ok: true };
    return { ok: false, error: body.error || `送出失敗（伺服器回應 ${res.status}），請稍後再試。` };
  } catch {
    return { ok: false, error: "無法連線到伺服器，請稍後再試。" };
  }
}

// ---------- 選單 ----------
const option = (value, text, selected) => new Option(text, value, false, selected);

function fillSelect(el, placeholder, items, selected) {
  el.replaceChildren(option("", placeholder, !selected), ...items.map(([v, t]) => option(v, t, v === selected)));
}

function renderSelects() {
  fillSelect($("#sp-county"), "請選擇縣市", data.counties.map((c) => [c, c]), sel.county);

  const markets = sel.county ? data.marketsByCounty.get(sel.county) : [];
  fillSelect($("#sp-market"), sel.county ? "請選擇市場" : "請先選縣市", markets.map((m) => [m.id, m.name]), sel.marketId);
  $("#sp-market").disabled = !sel.county;

  const vendors = sel.marketId ? data.vendorsByMarket.get(sel.marketId) : [];
  fillSelect($("#sp-vendor"), sel.marketId ? "請選擇攤商" : "請先選市場",
    vendors.map((v) => [v.id, `${v.name}（${LABEL[v.status]}）`]), sel.vendorId);
  $("#sp-vendor").disabled = !sel.marketId;
}

function currentVendor() {
  return sel.vendorId ? data.vendors.find((v) => v.id === sel.vendorId) : null;
}

function writeHash() {
  const p = new URLSearchParams();
  if (sel.vendorId) p.set("vendor", sel.vendorId);
  else if (sel.marketId) p.set("market", sel.marketId);
  else if (sel.county) p.set("county", sel.county);
  const hash = p.toString();
  history.replaceState(null, "", hash ? `#${hash}` : location.pathname + location.search);
}

// #vendor=m01-v002（總覽頁的「補交」圖示）、#market=m01、#county=臺北市
function readHash() {
  const p = new URLSearchParams(location.hash.slice(1));
  const vendor = data.vendors.find((v) => v.id === p.get("vendor"));
  const market = data.marketById.get(vendor ? vendor.market_id : p.get("market"));
  sel.vendorId = vendor ? vendor.id : null;
  sel.marketId = market ? market.id : null;
  sel.county = market ? market.county : data.counties.includes(p.get("county")) ? p.get("county") : null;
}

// ---------- 目前連結和操作 ----------
function renderVendor() {
  const v = currentVendor();
  $(".sp-current").hidden = !v;
  $(".sp-actions").hidden = !v;
  $(".sp-form-error").textContent = "";
  if (!v) return;

  const badge = $(".sp-current .badge");
  badge.dataset.status = v.status;
  badge.textContent = LABEL[v.status];
  const text = $(".sp-current-text");
  if (v.url) {
    const a = document.createElement("a");
    a.href = v.url;
    a.target = "_blank";
    a.rel = "noopener";
    a.innerHTML = `開啟 Google 地圖，看看是不是你的店<svg class="icon" aria-hidden="true"><use href="assets/icons.svg#external"/></svg>`;
    text.replaceChildren(a);
  } else {
    text.textContent = "目前沒有連結。";
  }

  const confirm = document.querySelector('input[value="confirm"]');
  const update = document.querySelector('input[value="update"]');
  const canConfirm = Boolean(v.url) && v.status !== "verified";
  confirm.disabled = !canConfirm;
  confirm.closest(".sp-choice").classList.toggle("is-disabled", !canConfirm);
  $('.sp-choice-hint[data-for="confirm"]').textContent =
    !v.url ? "目前沒有連結，不能確認" : v.status === "verified" ? "這家店已經確認完成，不用再確認" : "上面的連結就是我的店";
  $('.sp-choice-hint[data-for="update"]').textContent =
    v.status === "verified" ? "已完成的店貼新網址，會由人工決定要不要更換" : "連結不對，或是還沒有連結";

  confirm.checked = false;
  update.checked = !canConfirm;   // 只剩一個選項時直接選好
  $("#sp-url").value = "";
  urlTouched = false;
  renderAction();
}

function selectedAction() {
  return document.querySelector('input[name="action"]:checked')?.value || null;
}

function renderAction() {
  const update = selectedAction() === "update";
  $(".sp-url").hidden = !update;
  renderUrlState();
}

// 回傳 { ok, error, check }
function validateUrl() {
  const v = currentVendor();
  const check = checkUrl($("#sp-url").value);
  if (!check.ok) return { ok: false, error: check.error, check };
  const current = v.url ? checkUrl(v.url) : null;
  if (current?.ok && check.placeKey && current.placeKey === check.placeKey) {
    return {
      ok: false, check,
      error: v.status === "verified" ? "和目前已確認的連結是同一家店，不用補交。" : "和目前的連結是同一家店，請改選「這是我的店」。",
    };
  }
  return { ok: true, check };
}

function renderUrlState() {
  const field = $("#sp-url");
  const msg = $("#sp-url-error");
  if ($(".sp-url").hidden || !urlTouched) {
    field.removeAttribute("aria-invalid");
    msg.textContent = "";
    msg.className = "sp-url-error";
    return;
  }
  const r = validateUrl();
  field.setAttribute("aria-invalid", String(!r.ok));
  msg.className = r.ok ? "sp-url-error is-ok" : "sp-url-error";
  msg.textContent = r.ok
    ? r.check.short ? "格式正確。短網址會在人工確認時展開。" : "格式正確。"
    : r.error;
}

// ---------- 送出 ----------
async function onSubmit(e) {
  e.preventDefault();
  const err = $(".sp-form-error");
  err.textContent = "";
  if (MODE === "off") return;

  const v = currentVendor();
  if (!v) {
    err.textContent = !sel.county ? "請先選擇縣市。" : !sel.marketId ? "請先選擇市場。" : "請先選擇攤商。";
    (!sel.county ? $("#sp-county") : !sel.marketId ? $("#sp-market") : $("#sp-vendor")).focus();
    return;
  }
  const action = selectedAction();
  if (!action) {
    err.textContent = "請選一個操作：「這是我的店」或貼上正確的網址。";
    document.querySelector('input[name="action"]:not(:disabled)').focus();
    return;
  }
  let url, placeKey;
  if (action === "confirm") {
    url = v.url;
    placeKey = checkUrl(v.url).placeKey || "";
  } else {
    urlTouched = true;
    renderUrlState();
    const r = validateUrl();
    if (!r.ok) {
      $("#sp-url").focus();
      return;
    }
    url = r.check.url;
    placeKey = r.check.placeKey;
  }

  const market = data.marketById.get(v.market_id);
  const record = buildRecord({ vendor: v, market, action, url, placeKey });
  const btn = $(".sp-submit");
  btn.disabled = true;
  btn.textContent = "送出中…";
  let res;
  if (MODE === "mock") {
    await new Promise((r) => setTimeout(r, 400));
    res = mockSubmit(record);
  } else {
    res = await apiSubmit(record);
  }
  btn.disabled = false;
  btn.textContent = "送出";
  if (!res.ok) {
    err.textContent = res.error;
    return;
  }
  renderMock();
  showDone(v, market, action);
}

function showDone(v, market, action) {
  $(".sp-done-text").textContent = `${v.name}（${marketFullName(market)}）：${action === "confirm" ? "已確認現有連結" : "已收到新的網址"}。`;
  $(".sp-form-view").hidden = true;
  $(".sp-done").hidden = false;
  $(".sp-done").focus();
  window.scrollTo({ top: 0 });
}

function again() {
  sel.vendorId = null;
  writeHash();
  renderSelects();
  renderVendor();
  $(".sp-done").hidden = true;
  $(".sp-form-view").hidden = false;
  $("#sp-vendor").focus();
}

// ---------- 模擬紀錄面板 ----------
function renderMock() {
  if (MODE !== "mock") return;
  const list = readMock();
  $(".sp-mock").hidden = false;
  $(".sp-mock-count").textContent = list.length;
  $(".sp-mock-json").textContent = list.length ? JSON.stringify(list.slice().reverse(), null, 2) : "還沒有紀錄。";
}

function downloadCSV() {
  const blob = new Blob(["﻿" + toCSV(readMock())], { type: "text/csv;charset=utf-8" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = `submissions-mock-${taipeiTime().slice(0, 10)}.csv`;
  a.click();
  URL.revokeObjectURL(a.href);
}

// ---------- 啟動 ----------
function bind() {
  $("#sp-county").addEventListener("change", (e) => {
    sel.county = e.target.value || null;
    sel.marketId = null;
    sel.vendorId = null;
    writeHash();
    renderSelects();
    renderVendor();
  });
  $("#sp-market").addEventListener("change", (e) => {
    sel.marketId = e.target.value || null;
    sel.vendorId = null;
    writeHash();
    renderSelects();
    renderVendor();
  });
  $("#sp-vendor").addEventListener("change", (e) => {
    sel.vendorId = e.target.value || null;
    writeHash();
    renderVendor();
  });
  for (const r of document.querySelectorAll('input[name="action"]')) {
    r.addEventListener("change", () => {
      $(".sp-form-error").textContent = "";
      renderAction();
      if (selectedAction() === "update") $("#sp-url").focus();
    });
  }
  $("#sp-url").addEventListener("input", () => { if (urlTouched) renderUrlState(); });
  $("#sp-url").addEventListener("blur", () => {
    if ($("#sp-url").value.trim()) urlTouched = true;
    renderUrlState();
  });
  $("#sp-form").addEventListener("submit", onSubmit);
  $(".sp-again").addEventListener("click", again);
  $(".sp-mock-csv").addEventListener("click", downloadCSV);
  $(".sp-mock-clear").addEventListener("click", () => {
    writeMock([]);
    renderMock();
  });
}

async function start() {
  try {
    await loadData();
  } catch (err) {
    console.error(err);
    $(".sp-load-error").hidden = false;
    return;
  }
  const mode = $(".sp-mode");
  mode.hidden = false;
  mode.dataset.mode = MODE;
  mode.textContent = MODE_TEXT[MODE];
  $(".sp-submit").disabled = MODE === "off";
  if (IS_DEV) await loadDevtools("submit");

  readHash();
  bind();
  renderSelects();
  renderVendor();
  renderMock();
  // 已經在這頁時再點總覽頁的「補交」連結，只有 hash 改變、不會重新載入
  window.addEventListener("hashchange", () => {
    readHash();
    renderSelects();
    renderVendor();
    $(".sp-done").hidden = true;
    $(".sp-form-view").hidden = false;
  });
  delete document.body.dataset.loading;
}

start();
