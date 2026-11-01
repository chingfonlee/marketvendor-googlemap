// 縣市 → 市場 → 攤商連動（PLAN §2 互動規則、LAYER_ARCHITECTURE §3）。
// 測 state.js 的 6 個動作和網址 hash，以及 data.js 依狀態算出的範圍。畫面上的連動另見 tests/browser/。

import { test, beforeEach } from "node:test";
import assert from "node:assert/strict";
import { boot, openHash } from "./helpers.mjs";

const app = await boot();
const { data, state } = app;
const events = [];
app.subscribe((s, prev, cause) => events.push({ cause, county: s.county, marketId: s.marketId }));

beforeEach(() => {
  openHash(app, "");
  events.length = 0;
});

const marketOf = (county) => data.marketsByCounty.get(county)[0];
const twoMarketCounty = () => data.counties.find((c) => data.marketsByCounty.get(c).length >= 2);
const otherCounty = (c) => data.counties.find((x) => x !== c);

test("縣市順序照標籤檔，8 個縣市都有市場", () => {
  assert.equal(data.counties.length, 8);
  for (const c of data.counties) assert.ok(data.marketsByCounty.get(c).length > 0, c);
});

test("選縣市：市場清單換成該縣市，攤商清單是整個縣市", () => {
  const c = twoMarketCounty();
  app.selectCounty(c);
  assert.equal(state.county, c);
  assert.equal(state.marketId, null);
  const markets = app.marketsIn(c);
  assert.ok(markets.every((m) => m.county === c));
  const scoped = app.vendorsInScope(state);
  assert.equal(scoped.length, markets.reduce((n, m) => n + m.vendor_count, 0));
  assert.ok(scoped.every((v) => data.marketById.get(v.market_id).county === c));
  assert.equal(app.scopeName(state), c);
});

test("選市場：縣市跟著設成市場所在的縣市，攤商清單只剩該市場", () => {
  const c = twoMarketCounty();
  const m = data.marketsByCounty.get(c)[1];
  app.selectMarket(m.id);            // 沒先選縣市也可以（例如從全台市場清單點）
  assert.equal(state.county, c);
  assert.equal(state.marketId, m.id);
  const scoped = app.vendorsInScope(state);
  assert.equal(scoped.length, m.vendor_count);
  assert.ok(scoped.every((v) => v.market_id === m.id));
  assert.equal(app.scopeName(state), app.marketFullName(m));
});

test("切換縣市：原本選的市場清掉，換成新縣市的內容", () => {
  const c = twoMarketCounty();
  app.selectMarket(marketOf(c).id);
  const c2 = otherCounty(c);
  app.selectCounty(c2);
  assert.equal(state.county, c2);
  assert.equal(state.marketId, null);
  assert.ok(app.vendorsInScope(state).every((v) => data.marketById.get(v.market_id).county === c2));
});

test("同縣市換市場：縣市不變，攤商換成新市場的", () => {
  const c = twoMarketCounty();
  const [m1, m2] = data.marketsByCounty.get(c);
  app.selectMarket(m1.id);
  app.selectMarket(m2.id);
  assert.equal(state.county, c);
  assert.ok(app.vendorsInScope(state).every((v) => v.market_id === m2.id));
});

test("點已選的縣市不變，也不觸發重畫", () => {
  const c = twoMarketCounty();
  app.selectMarket(marketOf(c).id);
  events.length = 0;
  app.selectCounty(c);
  assert.equal(state.marketId, marketOf(c).id, "市場不該被清掉");
  assert.equal(events.length, 0);
});

test("清除市場回到縣市範圍；清除縣市回到全台", () => {
  const c = twoMarketCounty();
  app.selectMarket(marketOf(c).id);
  app.clearMarket();
  assert.deepEqual([state.county, state.marketId], [c, null]);
  app.selectMarket(marketOf(c).id);
  app.clearCounty();
  assert.deepEqual([state.county, state.marketId], [null, null]);
  assert.equal(app.vendorsInScope(state).length, data.vendors.length);
  assert.equal(app.scopeName(state), "全台");
});

test("狀態按鈕只篩清單，不影響圓環（縣市統計）和範圍", () => {
  const c = twoMarketCounty();
  app.selectCounty(c);
  const before = app.countyStats(c);
  const scopedBefore = app.vendorsInScope(state).length;
  app.setStatus("not_submitted");
  assert.deepEqual(app.countyStats(state.county), before);
  assert.equal(app.vendorsInScope(state).length, scopedBefore, "vendorsInScope 不套用狀態");
  assert.equal(state.county, c, "狀態不清掉縣市");
});

test("搜尋套在目前範圍內，不分大小寫", () => {
  const m = data.markets.find((x) => data.vendorsByMarket.get(x.id).some((v) => /[A-Za-z]/.test(v.name)));
  const v = data.vendorsByMarket.get(m.id).find((x) => /[A-Za-z]/.test(x.name));
  const word = v.name.match(/[A-Za-z]+/)[0];
  app.selectMarket(m.id);
  app.setKeyword(`  ${word.toLowerCase()} `);
  assert.equal(state.keyword, word.toLowerCase(), "前後空白去掉");
  const found = app.vendorsInScope(state);
  assert.ok(found.some((x) => x.id === v.id));
  assert.ok(found.every((x) => x.market_id === m.id));
  // 換到別的縣市，同一個關鍵字只在新範圍找
  app.selectCounty(otherCounty(m.county));
  assert.ok(app.vendorsInScope(state).every((x) => data.marketById.get(x.market_id).county === state.county));
});

test("每次改變都通知，cause 標明來源", () => {
  const c = twoMarketCounty();
  app.selectCounty(c);
  app.selectMarket(data.marketsByCounty.get(c)[1].id);
  app.setStatus("submitted");
  app.setKeyword("x");
  app.clearMarket();
  assert.deepEqual(events.map((e) => e.cause), ["county", "market", "status", "keyword", "market"]);
});

// ---------- 網址 hash ----------
test("狀態寫進 hash，重新讀回來一樣", () => {
  const m = marketOf(twoMarketCounty());
  app.selectMarket(m.id);
  app.setStatus("submitted");
  app.setKeyword("麵");
  const hash = location.hash;
  const p = new URLSearchParams(hash.slice(1));
  assert.equal(p.get("market"), m.id);
  assert.equal(p.get("county"), m.county);
  assert.equal(p.get("status"), "submitted");
  assert.equal(p.get("q"), "麵");

  openHash(app, "");
  assert.deepEqual([state.county, state.marketId, state.status, state.keyword], [null, null, "all", ""]);
  assert.equal(location.hash, "", "全台、全部時 hash 清空");
  openHash(app, hash.slice(1));
  assert.deepEqual([state.county, state.marketId, state.status, state.keyword], [m.county, m.id, "submitted", "麵"]);
});

test("hash 的市場和縣市對不上時，以市場為準", () => {
  const m = marketOf(data.counties[0]);
  openHash(app, `county=${encodeURIComponent(data.counties[1])}&market=${m.id}`);
  assert.deepEqual([state.county, state.marketId], [m.county, m.id]);
});

test("hash 裡不存在的市場、未參與的縣市、錯的狀態都忽略", () => {
  openHash(app, "market=m99");
  assert.deepEqual([state.county, state.marketId], [null, null]);
  openHash(app, `county=${encodeURIComponent("嘉義縣")}`);
  assert.equal(state.county, null, "未參與的縣市不能選");
  openHash(app, "status=pending");
  assert.equal(state.status, "all");
  openHash(app, `market=m99&county=${encodeURIComponent(data.counties[2])}`);
  assert.deepEqual([state.county, state.marketId], [data.counties[2], null], "市場不存在時退回縣市");
});

// ---------- 補交頁的三層選單用的是同一份索引 ----------
test("三層選單的資料：縣市→市場→攤商，每家攤商剛好出現在一個市場", () => {
  const seen = new Set();
  for (const c of data.counties) {
    for (const m of data.marketsByCounty.get(c)) {
      assert.equal(m.county, c);
      for (const v of data.vendorsByMarket.get(m.id)) {
        assert.equal(v.market_id, m.id);
        assert.ok(!seen.has(v.id), `${v.id} 重複`);
        seen.add(v.id);
      }
    }
  }
  assert.equal(seen.size, data.vendors.length);
});
