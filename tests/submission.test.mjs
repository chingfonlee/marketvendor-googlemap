// 補交後端（PLAN §5、§6 任務 12）：server/submission.js 的檢查和寫入、functions/api/submissions.js 的接線。
// D1 用 Node 內建的 SQLite 代替，表格直接跑 migrations/ 的 SQL，所以 SQL 寫錯也測得出來。

import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { DatabaseSync } from "node:sqlite";
import { ROOT } from "./helpers.mjs";

const { handleSubmission, siteverify, MAX_BODY } = await import(pathToFileURL(path.join(ROOT, "server", "submission.js")));
const { CSV_COLUMNS, HOURLY_LIMIT } = await import(pathToFileURL(path.join(ROOT, "web", "js", "record.js")));
const { onRequestPost } = await import(pathToFileURL(path.join(ROOT, "functions", "api", "submissions.js")));

const MIGRATION = readFileSync(path.join(ROOT, "migrations", "0001_submissions.sql"), "utf8");

// 和 D1 一樣的 prepare().bind().first()/run()/all()
function fakeD1() {
  const sqlite = new DatabaseSync(":memory:");
  sqlite.exec(MIGRATION);
  return {
    sqlite,
    prepare(sql) {
      const st = sqlite.prepare(sql);
      let args = [];
      const q = {
        bind: (...a) => { args = a; return q; },
        first: async () => st.get(...args) ?? null,
        run: async () => { st.run(...args); return { success: true }; },
        all: async () => ({ results: st.all(...args) }),
      };
      return q;
    },
    rows: () => sqlite.prepare("SELECT * FROM submissions ORDER BY id").all(),
  };
}

const MARKETS = [{ id: "m01", name: "測試市場", county: "臺北市" }];
const VENDORS = [
  { id: "m01-v001", market_id: "m01", name: "待確認的店", status: "submitted", url: "https://maps.google.com/?cid=1001" },
  { id: "m01-v002", market_id: "m01", name: "沒有連結的店", status: "not_submitted", url: null },
  { id: "m01-v003", market_id: "m01", name: "已完成的店", status: "verified", url: "https://maps.google.com/?cid=1003" },
];
const NOW = new Date("2026-11-01T01:00:00Z");
const HOUR = 3600 * 1000;

function setup() {
  const db = fakeD1();
  const calls = [];
  let pass = true;
  const send = (input, { ip = "203.0.113.5", token = "tok", now = NOW, text } = {}) =>
    handleSubmission({
      text: text ?? JSON.stringify(input), ip, token, now, db, vendors: VENDORS, markets: MARKETS,
      verifyTurnstile: async (t, i) => { calls.push([t, i]); return pass; },
    });
  return { db, send, calls, setPass: (v) => { pass = v; } };
}

test("確認現有連結：存一筆，縣市、市場、店名、送出前狀態都由伺服器填", async () => {
  const { db, send, calls } = setup();
  const r = await send({ vendor_id: "m01-v001", action: "confirm" });
  assert.deepEqual(r, { status: 201, body: { ok: true } });
  const [row] = db.rows();
  assert.equal(row.submitted_at, "2026-11-01T09:00:00+08:00", "台北時間");
  assert.equal(row.submitted_ms, NOW.getTime());
  assert.equal(row.ip, "203.0.113.5");
  assert.deepEqual([row.county, row.market_id, row.market_name], ["臺北市", "m01", "測試市場"]);
  assert.deepEqual([row.vendor_id, row.vendor_name, row.status_before], ["m01-v001", "待確認的店", "submitted"]);
  assert.deepEqual([row.action, row.url, row.place_key], ["confirm", "https://maps.google.com/?cid=1001", "cid:1001"]);
  assert.deepEqual([row.review_result, row.reviewed_at, row.note], ["", "", ""]);
  assert.deepEqual(calls, [["tok", "203.0.113.5"]], "Turnstile 收到 token 和 IP");
});

test("瀏覽器送來的其他欄位一律不採用：店名、狀態、IP、人工處理結果都改不了", async () => {
  const { db, send } = setup();
  await send({
    vendor_id: "m01-v001", action: "confirm", url: "https://maps.google.com/?cid=9999",
    vendor_name: "假店名", status_before: "verified", ip: "1.1.1.1", county: "高雄市",
    review_result: "approved", reviewed_at: "2026-01-01", note: "已確認",
  });
  const [row] = db.rows();
  assert.equal(row.vendor_name, "待確認的店");
  assert.equal(row.status_before, "submitted");
  assert.equal(row.ip, "203.0.113.5");
  assert.equal(row.county, "臺北市");
  assert.equal(row.url, "https://maps.google.com/?cid=1001", "確認時用公開資料的網址，不用送來的");
  assert.deepEqual([row.review_result, row.reviewed_at, row.note], ["", "", ""]);
});

test("貼新網址：照網頁的格式檢查，解析出 place_key；手機分享帶的店名會去掉", async () => {
  const { db, send } = setup();
  assert.equal((await send({ vendor_id: "m01-v002", action: "update", url: "沒有連結的店 https://maps.google.com/?cid=2002" })).status, 201);
  assert.equal((await send({ vendor_id: "m01-v001", action: "update", url: "https://maps.app.goo.gl/AbC123" })).status, 201);
  const rows = db.rows();
  assert.deepEqual([rows[0].url, rows[0].place_key, rows[0].status_before], ["https://maps.google.com/?cid=2002", "cid:2002", "not_submitted"]);
  assert.deepEqual([rows[1].url, rows[1].place_key], ["https://maps.app.goo.gl/AbC123", ""], "短網址留給人工展開");
});

test("已完成的店可以貼新網址（人工決定要不要換），但不能再確認", async () => {
  const { db, send } = setup();
  const confirm = await send({ vendor_id: "m01-v003", action: "confirm" });
  assert.equal(confirm.status, 400);
  assert.match(confirm.body.error, /已經確認完成/);
  const same = await send({ vendor_id: "m01-v003", action: "update", url: "https://www.google.com/maps?cid=1003" });
  assert.equal(same.status, 400);
  assert.match(same.body.error, /已確認的連結是同一家店/);
  assert.equal((await send({ vendor_id: "m01-v003", action: "update", url: "https://maps.google.com/?cid=3333" })).status, 201);
  assert.equal(db.rows()[0].status_before, "verified");
});

test("送錯的資料：一律 400 或 413、不存、也不用 Turnstile", async () => {
  const { db, send, calls } = setup();
  const cases = [
    [{ text: "{" }, 400, /格式不對/],
    [{ text: "null" }, 400, /格式不對/],
    [{ text: "x".repeat(MAX_BODY + 1) }, 413, /太大/],
    [{ input: { vendor_id: "m99-v001", action: "confirm" } }, 400, /找不到這家攤商/],
    [{ input: { action: "confirm" } }, 400, /找不到這家攤商/],
    [{ input: { vendor_id: "m01-v001", action: "delete" } }, 400, /請選一個操作/],
    [{ input: { vendor_id: "m01-v002", action: "confirm" } }, 400, /沒有連結，不能確認/],
    [{ input: { vendor_id: "m01-v002", action: "update" } }, 400, /請貼上 Google 地圖網址/],
    [{ input: { vendor_id: "m01-v002", action: "update", url: 12345 } }, 400, /請貼上 Google 地圖網址/],
    [{ input: { vendor_id: "m01-v002", action: "update", url: "https://example.com/?cid=1" } }, 400, /不是 Google 地圖/],
    [{ input: { vendor_id: "m01-v002", action: "update", url: "https://maps.google.com/?cid=1&x=" + "a".repeat(2100) } }, 400, /太長/],
    [{ input: { vendor_id: "m01-v001", action: "update", url: "https://maps.google.com/?cid=1001" } }, 400, /請改選「這是我的店」/],
  ];
  for (const [{ input, text }, status, error] of cases) {
    const r = await send(input, { text });
    assert.equal(r.status, status, JSON.stringify(input ?? text.slice(0, 20)));
    assert.equal(r.body.ok, false);
    assert.match(r.body.error, error);
  }
  assert.equal(db.rows().length, 0);
  assert.equal(calls.length, 0);
});

test("Turnstile：沒有 token 是 400、沒通過是 403，都不存", async () => {
  const { db, send, setPass } = setup();
  const none = await send({ vendor_id: "m01-v001", action: "confirm" }, { token: "" });
  assert.equal(none.status, 400);
  assert.match(none.body.error, /不是機器人/);
  setPass(false);
  const bad = await send({ vendor_id: "m01-v001", action: "confirm" });
  assert.equal(bad.status, 403);
  assert.equal(db.rows().length, 0);
});

test("防重複：同一攤商、同一網址 24 小時內只收一次；換網址、換店、過 24 小時都可以", async () => {
  const { db, send } = setup();
  const url = "https://maps.google.com/?cid=2002";
  assert.equal((await send({ vendor_id: "m01-v002", action: "update", url })).status, 201);
  const again = await send({ vendor_id: "m01-v002", action: "update", url }, { ip: "198.51.100.9", now: new Date(NOW.getTime() + 23 * HOUR) });
  assert.equal(again.status, 409, "換 IP 也一樣擋");
  assert.match(again.body.error, /24 小時內已經送過/);
  assert.equal((await send({ vendor_id: "m01-v002", action: "update", url: "https://maps.google.com/?cid=2003" })).status, 201);
  assert.equal((await send({ vendor_id: "m01-v001", action: "update", url })).status, 201);
  assert.equal((await send({ vendor_id: "m01-v002", action: "update", url }, { now: new Date(NOW.getTime() + 24 * HOUR + 1) })).status, 201);
  assert.equal(db.rows().length, 4);
});

test(`頻率限制：同一 IP 每小時 ${HOURLY_LIMIT} 筆，第 ${HOURLY_LIMIT + 1} 筆 429；別的 IP、一小時後不受影響`, async () => {
  const { db, send } = setup();
  const post = (i, opts) => send({ vendor_id: "m01-v002", action: "update", url: `https://maps.google.com/?cid=${5000 + i}` }, opts);
  for (let i = 0; i < HOURLY_LIMIT; i++) assert.equal((await post(i, { now: new Date(NOW.getTime() + i * 60000) })).status, 201, `第 ${i + 1} 筆`);
  const over = await post(99, { now: new Date(NOW.getTime() + 30 * 60000) });
  assert.equal(over.status, 429);
  assert.match(over.body.error, /一小時後再試/);
  assert.equal((await post(98, { ip: "198.51.100.9" })).status, 201, "別的 IP");
  assert.equal((await post(97, { now: new Date(NOW.getTime() + HOUR + 1) })).status, 201, "第一筆過了一小時");
  assert.equal(db.rows().length, HOURLY_LIMIT + 2);
});

test("D1 表格：欄位涵蓋 §5 的紀錄，action 只能是 confirm 或 update", () => {
  const db = fakeD1();
  const cols = db.sqlite.prepare("PRAGMA table_info(submissions)").all().map((c) => c.name);
  for (const c of CSV_COLUMNS) assert.ok(cols.includes(c), c);
  assert.throws(() => db.sqlite.exec(`INSERT INTO submissions (submitted_at, submitted_ms, ip, county, market_id, market_name,
    vendor_id, vendor_name, action, url, status_before) VALUES ('', 0, '', '', '', '', '', '', 'delete', '', '')`), /CHECK/);
});

test("siteverify：把金鑰、token、IP 送給 Cloudflare；沒有 success 或連不上都算沒通過", async () => {
  let sent;
  const ok = await siteverify("secret", "tok", "203.0.113.5", async (url, init) => {
    sent = { url, form: Object.fromEntries(init.body) };
    return { json: async () => ({ success: true }) };
  });
  assert.equal(ok, true);
  assert.equal(sent.url, "https://challenges.cloudflare.com/turnstile/v0/siteverify");
  assert.deepEqual(sent.form, { secret: "secret", response: "tok", remoteip: "203.0.113.5" });
  assert.equal(await siteverify("s", "t", "", async () => ({ json: async () => ({ success: false }) })), false);
  assert.equal(await siteverify("s", "t", "", async () => { throw new Error("offline"); }), false);
});

// ---------- functions/api/submissions.js ----------
function fakeEnv(db, secret = "1x0000000000000000000000000000000AA") {
  const files = { vendors: VENDORS, markets: MARKETS };
  return {
    DB: db,
    TURNSTILE_SECRET: secret,
    ASSETS: { fetch: async (u) => ({ json: async () => files[new URL(u).pathname.match(/\/data\/(\w+)\.json/)[1]] }) },
  };
}
const request = (body, headers = {}) =>
  new Request("https://example.org/api/submissions", { method: "POST", body: JSON.stringify(body), headers });

test("API：IP 取 CF-Connecting-IP、token 取 X-Turnstile-Token，回 JSON", async (t) => {
  const realFetch = globalThis.fetch;
  globalThis.fetch = async () => ({ json: async () => ({ success: true }) });
  t.after(() => { globalThis.fetch = realFetch; });
  const db = fakeD1();
  const res = await onRequestPost({
    request: request({ vendor_id: "m01-v001", action: "confirm" }, { "CF-Connecting-IP": "203.0.113.7", "X-Turnstile-Token": "tok" }),
    env: fakeEnv(db),
  });
  assert.equal(res.status, 201);
  assert.match(res.headers.get("Content-Type"), /application\/json/);
  assert.deepEqual(await res.json(), { ok: true });
  assert.equal(db.rows()[0].ip, "203.0.113.7");

  const noToken = await onRequestPost({ request: request({ vendor_id: "m01-v001", action: "confirm" }), env: fakeEnv(db) });
  assert.equal(noToken.status, 400);
});

test("API：沒設 Turnstile 金鑰時一律 503，不存（避免沒有防機器人就上線）", async () => {
  const db = fakeD1();
  const res = await onRequestPost({ request: request({ vendor_id: "m01-v001", action: "confirm" }, { "X-Turnstile-Token": "tok" }), env: fakeEnv(db, "") });
  assert.equal(res.status, 503);
  assert.equal((await res.json()).ok, false);
  assert.equal(db.rows().length, 0);
});

test("API：資料庫出錯時回 500 和中文訊息，不把錯誤細節給瀏覽器", async (t) => {
  const realFetch = globalThis.fetch;
  globalThis.fetch = async () => ({ json: async () => ({ success: true }) });
  const realError = console.error;
  console.error = () => {};
  t.after(() => { globalThis.fetch = realFetch; console.error = realError; });
  const broken = { prepare: () => { throw new Error("D1_ERROR: no such table"); } };
  const res = await onRequestPost({ request: request({ vendor_id: "m01-v001", action: "confirm" }, { "X-Turnstile-Token": "tok" }), env: fakeEnv(broken) });
  assert.equal(res.status, 500);
  const body = await res.json();
  assert.equal(body.ok, false);
  assert.ok(!body.error.includes("D1_ERROR"), body.error);
});
