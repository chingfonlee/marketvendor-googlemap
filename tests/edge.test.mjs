// 邊界案例（PLAN §6 任務 10）：空市場、全部完成、沒有市場的縣市。
// 用 tests/fixtures/edge 的小資料：臺北市＝全完成市場（3 家）＋空市場（0 家），臺東縣＝三種狀態各 1 家，
// 其他 6 個縣市有標籤但沒有市場。另外補交頁的紀錄格式（§5）也在這裡測。

import { test, beforeEach } from "node:test";
import assert from "node:assert/strict";
import path from "node:path";
import { FIXTURES, WEB, readJSON, boot, openHash, installBrowser, jsUrl } from "./helpers.mjs";

const app = await boot({ dataDir: path.join(FIXTURES, "edge") });
const { data, state } = app;
beforeEach(() => openHash(app, ""));

const rate = (st) => (st.vendors ? st.counts.verified / st.vendors : 0);

test("fixture 本身前後一致（markets 的數字和 vendors 逐筆相符）", () => {
  for (const m of data.markets) {
    const list = data.vendorsByMarket.get(m.id);
    assert.equal(list.length, m.vendor_count, m.id);
    assert.deepEqual(app.countByStatus(list), m.counts, m.id);
  }
});

test("空市場：攤商清單是空的，各狀態都是 0，不會出現 NaN", () => {
  app.selectMarket("m02");
  assert.deepEqual([state.county, state.marketId], ["臺北市", "m02"]);
  const list = app.vendorsInScope(state);
  assert.deepEqual(list, []);
  assert.deepEqual(app.countByStatus(list), { verified: 0, submitted: 0, not_submitted: 0 });
  for (const s of ["verified", "submitted", "not_submitted"]) {
    app.setStatus(s);
    assert.deepEqual(app.vendorsInScope(state).filter((v) => v.status === s), []);
  }
  assert.equal(app.scopeName(state), "臺北空市場");
});

test("空市場不影響所屬縣市的統計：臺北市仍是 2 個市場、3 家", () => {
  const st = app.countyStats("臺北市");
  assert.equal(st.markets, 2);
  assert.equal(st.vendors, 3);
});

test("全部完成：完成率 100%，待確認和未提交都是 0", () => {
  const st = app.countyStats("臺北市");
  assert.deepEqual(st.counts, { verified: 3, submitted: 0, not_submitted: 0 });
  assert.equal(rate(st), 1);
  app.selectMarket("m01");
  app.setStatus("not_submitted");
  const scoped = app.vendorsInScope(state);
  assert.equal(scoped.length, 3, "範圍不受狀態影響");
  assert.equal(scoped.filter((v) => v.status === "not_submitted").length, 0, "篩未提交時是空清單");
});

test("全台的完成率：4 / 6", () => {
  const st = app.countyStats(null);
  assert.equal(st.vendors, 6);
  assert.equal(st.markets, 3);
  assert.equal(st.counts.verified, 4);
  assert.equal(rate(st), 4 / 6);
});

test("有標籤但沒有市場的縣市：0 個市場、0 家，不會出錯", () => {
  const empty = data.counties.filter((c) => !["臺北市", "臺東縣"].includes(c));
  assert.equal(empty.length, 6);
  for (const c of empty) {
    app.selectCounty(c);
    assert.deepEqual(app.marketsIn(c), []);
    assert.deepEqual(app.vendorsInScope(state), []);
    const st = app.countyStats(c);
    assert.deepEqual([st.markets, st.vendors], [0, 0]);
    assert.equal(rate(st), 0);
  }
});

test("搜尋找不到時是空清單；在空市場搜尋也一樣", () => {
  app.selectCounty("臺東縣");
  app.setKeyword("不存在的店");
  assert.deepEqual(app.vendorsInScope(state), []);
  app.selectMarket("m02");
  assert.deepEqual(app.vendorsInScope(state), []);
});

test("正式資料全部改成已完成時，每個縣市和全台都是 100%", async () => {
  // 不改檔案：把正式資料讀進來、在記憶體裡改狀態，再交給 data.js
  const markets = readJSON(path.join(WEB, "data", "markets.json")).map((m) => ({
    ...m, counts: { verified: m.vendor_count, submitted: 0, not_submitted: 0 },
  }));
  const vendors = readJSON(path.join(WEB, "data", "vendors.json")).map((v) => ({
    ...v, status: "verified", url: v.url || "https://maps.google.com/?cid=1",
  }));
  const real = await boot();
  real.data.markets.length = 0;
  real.data.markets.push(...markets);
  real.data.marketsByCounty.forEach((list, c) => list.splice(0, list.length, ...markets.filter((m) => m.county === c)));
  real.data.vendorsByMarket.forEach((list, id) => list.splice(0, list.length, ...vendors.filter((v) => v.market_id === id)));
  real.data.vendors.splice(0, real.data.vendors.length, ...vendors);

  assert.equal(rate(real.countyStats(null)), 1);
  for (const c of real.data.counties) assert.equal(rate(real.countyStats(c)), 1, c);

  // boot() 把 state 接到正式資料了，接回 fixture，後面的測試才不受影響
  app.configure({ countyOf: (id) => data.marketById.get(id)?.county ?? null, isCounty: (c) => data.counties.includes(c) });
});

// ---------- 補交頁的紀錄（PLAN §5） ----------
installBrowser({ dataDir: path.join(FIXTURES, "edge"), hostname: "example.org" });
const submit = await import(jsUrl("submit"));

test("紀錄欄位和 §5 的表格一模一樣，順序也一樣", () => {
  assert.deepEqual(submit.CSV_COLUMNS, [
    "submitted_at", "ip", "county", "market_id", "market_name", "vendor_id", "vendor_name",
    "action", "url", "place_key", "status_before", "review_result", "reviewed_at", "note",
  ]);
});

test("確認現有連結的紀錄：status_before 是送出時的狀態，人工欄位留空", () => {
  const vendor = data.vendorsByMarket.get("m03")[1];   // 待確認
  const market = data.marketById.get("m03");
  const r = submit.buildRecord({
    vendor, market, action: "confirm", url: vendor.url, placeKey: "cid:3002", now: new Date("2026-11-01T01:02:03Z"),
  });
  assert.deepEqual(Object.keys(r), submit.CSV_COLUMNS);
  assert.equal(r.submitted_at, "2026-11-01T09:02:03+08:00", "台北時間");
  assert.equal(r.county, "臺東縣");
  assert.equal(r.market_id, "m03");
  assert.equal(r.market_name, "臺東混合市場");
  assert.equal(r.vendor_id, "m03-v002");
  assert.equal(r.status_before, "submitted");
  assert.equal(r.action, "confirm");
  assert.deepEqual([r.review_result, r.reviewed_at, r.note], ["", "", ""]);
});

test("台北時間跨日：UTC 16:00 是隔天 00:00", () => {
  assert.equal(submit.taipeiTime(new Date("2026-12-31T16:00:00Z")), "2027-01-01T00:00:00+08:00");
});

test("CSV：有逗號、引號的店名正確跳脫，用 CRLF 換行", () => {
  const vendor = data.vendorsByMarket.get("m01")[2];   // Done "丙", 逗號
  const market = data.marketById.get("m01");
  const r = submit.buildRecord({ vendor, market, action: "update", url: "https://maps.app.goo.gl/AbC", placeKey: "", ip: "127.0.0.1" });
  const csv = submit.toCSV([r]);
  const lines = csv.split("\r\n");
  assert.equal(lines.length, 3, "表頭、一筆、結尾空行");
  assert.equal(lines[0], submit.CSV_COLUMNS.join(","));
  assert.ok(lines[1].includes(`"Done ""丙"", 逗號"`), lines[1]);
  assert.equal(lines[2], "");
  assert.equal(submit.toCSV([]), submit.CSV_COLUMNS.join(",") + "\r\n", "沒有紀錄時只有表頭");
});
