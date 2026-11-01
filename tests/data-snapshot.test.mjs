// 正式資料快照（PLAN §6 任務 10）：總數、各市場、各狀態加總。
// 數字以匯入報告（和總表比對過）為準；Excel 有個資不進 git，這裡比對的是它產生的報告和 JSON。

import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import { ROOT, WEB, readJSON, boot } from "./helpers.mjs";

const STATUSES = ["verified", "submitted", "not_submitted"];
const markets = readJSON(path.join(WEB, "data", "markets.json"));
const vendors = readJSON(path.join(WEB, "data", "vendors.json"));
const meta = readJSON(path.join(WEB, "data", "meta.json"));
const labels = readJSON(path.join(WEB, "data", "county-labels.json"));
const idMap = readJSON(path.join(ROOT, "data", "id-map.json"));

// 上線時的數字（PLAN §3）。資料重新匯入後數字會變，到時候連同 PLAN 一起改。
const SNAPSHOT = { total: 347, markets: 15, counties: 8, verified: 0, submitted: 217, not_submitted: 130 };

// 匯入報告 §2 的表格：| ID | 縣市 | 市場 | 類型 | 總表攤數 | 匯入 | 已完成 | 待確認 | 未提交 |
function reportRows() {
  const md = readFileSync(path.join(ROOT, "reports", "import-report.md"), "utf8");
  const section = md.split(/^## /m).find((s) => s.startsWith("2."));
  return section.split("\n")
    .filter((l) => /^\| m\d\d \|/.test(l))
    .map((l) => {
      const c = l.split("|").slice(1, -1).map((s) => s.trim());
      return { id: c[0], county: c[1], name: c[2], type: c[3], sheet: +c[4], imported: +c[5], verified: +c[6], submitted: +c[7], not_submitted: +c[8] };
    });
}

test("總數、市場數、縣市數和上線快照一致", () => {
  assert.equal(vendors.length, SNAPSHOT.total);
  assert.equal(markets.length, SNAPSHOT.markets);
  assert.equal(new Set(markets.map((m) => m.county)).size, SNAPSHOT.counties);
  assert.equal(meta.total, SNAPSHOT.total);
  assert.equal(meta.markets, SNAPSHOT.markets);
  assert.equal(meta.counties, SNAPSHOT.counties);
  for (const s of STATUSES) {
    assert.equal(vendors.filter((v) => v.status === s).length, SNAPSHOT[s], s);
    assert.equal(meta.counts[s], SNAPSHOT[s], `meta.counts.${s}`);
  }
});

test("每個攤商只有三種狀態之一，三種加總等於總數", () => {
  for (const v of vendors) assert.ok(STATUSES.includes(v.status), `${v.id} 狀態 ${v.status}`);
  const sum = STATUSES.reduce((n, s) => n + meta.counts[s], 0);
  assert.equal(sum, meta.total);
});

test("各市場：vendor_count、各狀態數量和 vendors.json 逐筆算的一致", () => {
  for (const m of markets) {
    const list = vendors.filter((v) => v.market_id === m.id);
    assert.equal(m.vendor_count, list.length, `${m.id} vendor_count`);
    for (const s of STATUSES) {
      assert.equal(m.counts[s], list.filter((v) => v.status === s).length, `${m.id} ${s}`);
    }
    assert.equal(STATUSES.reduce((n, s) => n + m.counts[s], 0), m.vendor_count, `${m.id} 三種加總`);
  }
});

test("各市場和匯入報告（與總表比對過的攤數）一致", () => {
  const rows = reportRows();
  assert.equal(rows.length, markets.length, "報告的市場列數");
  for (const r of rows) {
    const m = markets.find((x) => x.id === r.id);
    assert.ok(m, `報告有 ${r.id}，JSON 沒有`);
    assert.equal(m.name, r.name);
    assert.equal(m.county, r.county);
    assert.equal(m.type, r.type);
    assert.equal(r.imported, r.sheet, `${r.id} 匯入數和總表攤數不同`);
    assert.equal(m.vendor_count, r.imported, `${r.id} 攤商數`);
    for (const s of STATUSES) assert.equal(m.counts[s], r[s], `${r.id} ${s}`);
  }
  assert.equal(rows.reduce((n, r) => n + r.sheet, 0), SNAPSHOT.total, "總表攤數合計");
});

test("市場和攤商 ID 格式固定、不重複，和 id-map.json 一致", () => {
  const mIds = markets.map((m) => m.id);
  assert.equal(new Set(mIds).size, mIds.length);
  for (const id of mIds) assert.match(id, /^m\d{2}$/);
  for (const m of markets) assert.equal(idMap.markets[m.name], m.id, `${m.name} 在 id-map 的 ID`);

  const vIds = vendors.map((v) => v.id);
  assert.equal(new Set(vIds).size, vIds.length);
  const mapped = new Map();
  for (const [mid, names] of Object.entries(idMap.vendors)) for (const id of Object.values(names)) mapped.set(id, mid);
  for (const v of vendors) {
    assert.match(v.id, /^m\d{2}-v\d{3}$/);
    assert.ok(mIds.includes(v.market_id), `${v.id} 的 market_id ${v.market_id} 不存在`);
    assert.equal(mapped.get(v.id), v.market_id, `${v.id} 在 id-map 屬於別的市場`);
  }
});

test("有連結 ⇔ 不是未提交；已完成一定有連結", () => {
  for (const v of vendors) {
    if (v.status === "not_submitted") assert.equal(v.url, null, `${v.id} 未提交卻有連結`);
    else assert.ok(typeof v.url === "string" && v.url.length > 0, `${v.id} ${v.status} 沒有連結`);
  }
});

test("公開 JSON 沒有個資欄位", () => {
  assert.deepEqual([...new Set(vendors.flatMap(Object.keys))].sort(), ["id", "market_id", "name", "status", "url"]);
  assert.deepEqual([...new Set(markets.flatMap(Object.keys))].sort(), ["counts", "county", "id", "name", "type", "vendor_count"]);
  // 店名裡不應該出現電話號碼（手機 09xx、市話 0x-xxxx）
  const phone = /09\d{2}[-\s]?\d{3}[-\s]?\d{3}|0\d{1,2}-\d{6,8}/;
  for (const v of vendors) assert.doesNotMatch(v.name, phone, v.id);
});

test("每個市場的縣市都有標籤，標籤只有參與的 8 個縣市", () => {
  const labelCounties = labels.labels.map((l) => l.county);
  assert.equal(labelCounties.length, SNAPSHOT.counties);
  assert.deepEqual([...labelCounties].sort(), [...new Set(markets.map((m) => m.county))].sort());
});

test("網頁載入後（data.js）算出的統計和快照一致", async () => {
  const app = await boot();
  assert.equal(app.data.markets.length, SNAPSHOT.markets);
  assert.equal(app.data.vendors.length, SNAPSHOT.total);
  const all = app.countyStats(null);
  assert.equal(all.vendors, SNAPSHOT.total);
  assert.equal(all.markets, SNAPSHOT.markets);
  for (const s of STATUSES) assert.equal(all.counts[s], SNAPSHOT[s]);

  // 縣市加總回全台，每個市場都分到某個縣市
  let vendorSum = 0, marketSum = 0;
  for (const c of app.data.counties) {
    const st = app.countyStats(c);
    vendorSum += st.vendors;
    marketSum += st.markets;
    assert.equal(STATUSES.reduce((n, s) => n + st.counts[s], 0), st.vendors, `${c} 三種加總`);
  }
  assert.equal(vendorSum, SNAPSHOT.total);
  assert.equal(marketSum, SNAPSHOT.markets);
  // 每個市場的攤商清單長度等於 vendor_count（沒有攤商掉到不存在的市場）
  for (const m of app.data.markets) assert.equal(app.data.vendorsByMarket.get(m.id).length, m.vendor_count, m.id);
});
