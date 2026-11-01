// 統計頁的計算（web/js/stats-calc.js，任務 17）：design/asset-briefs/stats-page-assets.md §五.6 的 7 項。
// 除了第 1 項用正式資料，其他都用假資料，確認圖表跟著資料變，不是寫死的。

import { test } from "node:test";
import assert from "node:assert/strict";
import path from "node:path";
import { readJSON, WEB } from "./helpers.mjs";
import {
  KEYS, TOP_N, MIN_DONUT_SEG, total, done, ratio, pctText, overall,
  countyRows, typeRows, topRows, barWidths, donutSegments, typeOf,
} from "../web/js/stats-calc.js";

const markets = readJSON(path.join(WEB, "data", "markets.json"));
const mk = (id, county, type, verified, submitted, not_submitted) =>
  ({ id, name: `市場${id}`, county, type, counts: { verified, submitted, not_submitted } });
const clone = (x) => structuredClone(x);
const pcts = (rows) => rows.map((r) => [r.county, pctText(r.counts)]);
const sum = (a) => a.reduce((s, v) => s + v, 0);
const close = (a, b, what) => assert.ok(Math.abs(a - b) < 1e-9, `${what}：${a} ≠ ${b}`);

test("1. 正式資料：62.5%、各縣市百分比和排序、最強友善力市集 3 個市場", () => {
  const all = overall(markets);
  assert.deepEqual(all, { verified: 0, submitted: 217, not_submitted: 130 });
  assert.equal(pctText(all, 1), "62.5%");
  const rows = countyRows(markets);
  assert.deepEqual(pcts(rows), [
    ["高雄市", "85%"], ["新北市", "78%"], ["新竹市", "76%"], ["臺北市", "74%"],
    ["臺南市", "60%"], ["臺中市", "55%"], ["臺東縣", "43%"], ["桃園市", "29%"],
  ]);
  assert.deepEqual(rows.filter((r) => r.crown).map((r) => r.county), ["高雄市"]);
  assert.deepEqual(typeRows(markets).map((r) => [r.type, pctText(r.counts)]),
    [["night_market", "61%"], ["traditional_market", "58%"], ["other", "80%"]]);
  // 3 個 100% 的市場：21 家的在前，20 家的兩個照 ID
  assert.deepEqual(topRows(markets).map((m) => [m.id, `${done(m.counts)}/${total(m.counts)}`]),
    [["m03", "21/21"], ["m02", "20/20"], ["m13", "20/20"]]);
  assert.equal(TOP_N, 3);
});

test("2. verified > 0：綠色段出現，已提交比例包含已完成", () => {
  const data = clone(markets);
  const m = data.find((x) => x.id === "m15");  // 臺東 21/49
  m.counts = { verified: 10, submitted: 11, not_submitted: 28 };
  assert.equal(pctText(overall(data), 1), "62.5%", "已完成從待確認移過去，已提交總數不變");
  m.counts = { verified: 20, submitted: 11, not_submitted: 18 };  // 再多 10 家從未提交變已完成
  const all = overall(data);
  assert.equal(all.verified, 20);
  assert.equal(done(all), 227);
  assert.equal(pctText(all, 1), "65.4%");
  const taitung = countyRows(data).find((r) => r.county === "臺東縣");
  assert.equal(pctText(taitung.counts), "63%");
  assert.ok(barWidths(taitung.counts)[0] > 0, "縣市長條有綠色段");
  assert.equal(donutSegments(all, 100)[0].key, "verified", "甜甜圈第一段是綠色");
  assert.ok(!donutSegments(overall(markets), 100).some((s) => s.key === "verified"), "已完成 0 時不畫綠色段");
});

test("3. 縣市 0% 和 100%：長條全紅、沒有紅色，排序跟著變", () => {
  const data = [
    mk("a1", "甲市", "night_market", 0, 0, 10),
    mk("b1", "乙市", "night_market", 3, 7, 0),
    mk("c1", "丙市", "night_market", 0, 5, 5),
  ];
  const rows = countyRows(data);
  assert.deepEqual(pcts(rows), [["乙市", "100%"], ["丙市", "50%"], ["甲市", "0%"]]);
  assert.deepEqual(barWidths(rows[2].counts), [0, 0, 100], "0%：只有紅色");
  assert.equal(barWidths(rows[0].counts)[2], 0, "100%：沒有紅色");
  // 最強友善力市集：比例高到低，0% 的不列
  assert.deepEqual(topRows(data).map((m) => m.id), ["b1", "c1"]);
  // 甲市改成 100%（12 家）：比乙市多，排到最前面
  data[0].counts = { verified: 0, submitted: 12, not_submitted: 0 };
  assert.deepEqual(countyRows(data).map((r) => r.county), ["甲市", "乙市", "丙市"]);
  assert.deepEqual(countyRows(data).filter((r) => r.crown).map((r) => r.county), ["甲市", "乙市"]);
});

test("4. 兩個縣市比例一樣：總數多的在前，再照名稱；並列第一的都有皇冠", () => {
  const data = [
    mk("a1", "乙市", "night_market", 0, 4, 4),     // 50%，8 家
    mk("b1", "甲市", "night_market", 0, 10, 10),   // 50%，20 家
    mk("c1", "丁市", "night_market", 0, 9, 1),     // 90%
    mk("d1", "丙市", "night_market", 0, 18, 2),    // 90%，20 家
  ];
  const rows = countyRows(data);
  assert.deepEqual(rows.map((r) => r.county), ["丙市", "丁市", "甲市", "乙市"]);
  assert.deepEqual(rows.filter((r) => r.crown).map((r) => r.county), ["丙市", "丁市"]);
  // 總數也一樣：照名稱字碼（和 build_stats_svg.py 的 sorted 一樣）
  const same = countyRows([mk("x", "臺南市", "other", 0, 1, 1), mk("y", "臺中市", "other", 0, 1, 1)]);
  assert.deepEqual(same.map((r) => r.county), ["臺中市", "臺南市"].sort());
  assert.ok(same.every((r) => r.crown));
  // 最強友善力市集：同比例總數多的在前，再照 ID；只列 3 個
  const top = topRows([mk("w1", "甲市", "other", 0, 1, 1), mk("w2", "甲市", "other", 0, 5, 5),
    mk("w4", "甲市", "other", 0, 3, 3), mk("w3", "甲市", "other", 0, 3, 3)]);
  assert.deepEqual(top.map((m) => m.id), ["w2", "w3", "w4"]);
});

test("5. 沒有市場提交：最強友善力市集是空的（畫面顯示「還沒有市場提交」）；全部 100%：照總數列 3 個", () => {
  const none = clone(markets).map((m) => ({ ...m, counts: { verified: 0, submitted: 0, not_submitted: total(m.counts) } }));
  assert.deepEqual(topRows(none), []);
  assert.equal(pctText(overall(none), 1), "0.0%");
  const all = clone(markets).map((m) => ({ ...m, counts: { verified: total(m.counts), submitted: 0, not_submitted: 0 } }));
  assert.equal(pctText(overall(all), 1), "100.0%");
  assert.ok(countyRows(all).every((r) => r.crown), "全部並列第一");
  assert.deepEqual(topRows(all).map((m) => total(m.counts)), [49, 31, 25], "同 100% 時總數多的在前");
});

test("6. 新縣市、新類型：縣市多一列，新類型歸到「其他」；總數 0 的不列", () => {
  const data = clone(markets);
  data.push(mk("m16", "花蓮縣", "street_food", 0, 3, 7));
  data.push(mk("m17", "嘉義市", "night_market", 0, 0, 0));
  const rows = countyRows(data);
  assert.equal(rows.length, 9, "花蓮多一列，嘉義總數 0 不列");
  assert.deepEqual(rows.slice(-2).map((r) => [r.county, pctText(r.counts)]), [["花蓮縣", "30%"], ["桃園市", "29%"]]);
  const types = typeRows(data);
  assert.deepEqual(types.map((r) => r.type), ["night_market", "traditional_market", "other"], "沒有多出新類型");
  const other = types.find((r) => r.type === "other").counts;
  const before = typeRows(markets).find((r) => r.type === "other").counts;
  assert.equal(total(other), total(before) + 10, "新類型的 10 家算進「其他」");
  // 某類型沒有市場：不列
  assert.deepEqual(typeRows(markets.filter((m) => m.type !== "other")).map((r) => r.type), ["night_market", "traditional_market"]);
});

test("7. 每一條長條、每一個甜甜圈，三段加起來都等於 100%", () => {
  const cases = [
    ...markets.map((m) => m.counts),
    ...countyRows(markets).map((r) => r.counts),
    ...typeRows(markets).map((r) => r.counts),
    overall(markets),
    { verified: 1, submitted: 0, not_submitted: 999 },
    { verified: 1, submitted: 1, not_submitted: 998 },
    { verified: 0, submitted: 0, not_submitted: 5 },
    { verified: 7, submitted: 0, not_submitted: 0 },
  ];
  const C = 2 * Math.PI * 48;
  for (const c of cases) {
    const what = JSON.stringify(c);
    close(sum(barWidths(c)), 100, `長條 ${what}`);
    close(sum(barWidths(c, 5)), 100, `長條（最小 5%）${what}`);
    const segs = donutSegments(c, C);
    close(sum(segs.map((s) => s.len)), C, `甜甜圈 ${what}`);
    for (const s of segs) assert.ok(s.len >= MIN_DONUT_SEG - 1e-9, `甜甜圈每段至少 ${MIN_DONUT_SEG}px ${what}`);
    segs.forEach((s, i) => close(s.offset, sum(segs.slice(0, i).map((x) => x.len)), `甜甜圈接續 ${what}`));
    KEYS.forEach((k, i) => assert.equal(barWidths(c, 5)[i] > 0, c[k] > 0, `家數 0 的段不畫、> 0 的段看得見 ${what}`));
  }
  assert.deepEqual(barWidths({ verified: 0, submitted: 0, not_submitted: 0 }), [0, 0, 0]);
  assert.deepEqual(donutSegments({ verified: 0, submitted: 0, not_submitted: 0 }, C), []);
});

test("其他：ratio、新類型、空資料", () => {
  assert.equal(ratio({ verified: 0, submitted: 0, not_submitted: 0 }), 0);
  assert.equal(typeOf({ type: "street_food" }), "other");
  assert.equal(typeOf({ type: "night_market" }), "night_market");
  assert.equal(total(overall([])), 0);
  assert.deepEqual(countyRows([]), []);
});
