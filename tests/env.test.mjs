// 開發開關（PLAN §6 任務 9）：哪些網址算開發環境、設定怎麼讀、補交頁的送出方式。
// 重點是「正式環境無法開啟」：不管瀏覽器裡存了什麼設定，正式網址一律用預設值、不能送出。
// 畫面上每個開關關掉的效果另見 tests/browser/。

import { test } from "node:test";
import assert from "node:assert/strict";
import { installBrowser, jsUrl } from "./helpers.mjs";

// env.js 在匯入時就決定 IS_DEV，所以每個網址都要重新匯入一份
let seq = 0;
async function envAt(hostname, stored) {
  installBrowser({ hostname });
  const store = new Map(stored === undefined ? [] : [["gm-dev", typeof stored === "string" ? stored : JSON.stringify(stored)]]);
  globalThis.localStorage = {
    getItem: (k) => (store.has(k) ? store.get(k) : null),
    setItem: (k, v) => store.set(k, String(v)),
  };
  const env = await import(jsUrl("env", `?h=${++seq}`));
  return { env, store };
}

const DEV_HOSTS = ["localhost", "127.0.0.1", "[::1]", "app.localhost", "gm.test", "a.b.test"];
const PROD_HOSTS = [
  "example.org", "marketvendor.pages.dev", "localhost.example.com", "mylocalhost", "notlocalhost",
  "127.0.0.2", "10.0.0.1", "192.168.1.10", "test", "gm.test.example.com", "gmtest", "localhost.",
];

test("開發環境只有 localhost、127.0.0.1、[::1]、*.localhost、*.test", async () => {
  for (const h of DEV_HOSTS) assert.equal((await envAt(h)).env.IS_DEV, true, h);
  for (const h of PROD_HOSTS) assert.equal((await envAt(h)).env.IS_DEV, false, h);
});

test("正式環境：就算瀏覽器存了設定，也讀不到（開關不生效）", async () => {
  const { env } = await envAt("example.org", { base: false, labels: false, interact: false, stats: false, list: false, submit: "mock" });
  assert.equal(env.readDev(), null);
});

test("正式環境：補交頁一律送到 API（用正式 Turnstile 金鑰），存了 mock 或 off 也一樣", async () => {
  for (const submit of ["mock", "api", "off"]) {
    const { env } = await envAt("googlemap-store.pages.dev", { submit });
    assert.equal(env.submitMode(), "api", submit);
    assert.equal(env.TURNSTILE_SITE_KEY, env.TURNSTILE_PROD_KEY);
  }
  assert.match((await envAt("example.org")).env.TURNSTILE_PROD_KEY, /^0x4/, "正式金鑰（不是 1x 開頭的測試金鑰）");
});

test("開發環境：Turnstile 一律用測試金鑰", async () => {
  const { env } = await envAt("localhost", { submit: "api" });
  assert.equal(env.TURNSTILE_SITE_KEY, "1x00000000000000000000AA");
});

test("正式環境：devtools.js 就算被手動載入也不會建立開關", async () => {
  installBrowser({ hostname: "example.org" });
  let appended = 0;
  globalThis.document.body.append = () => { appended += 1; };
  globalThis.document.head = { append: () => { appended += 1; } };
  const { initDevtools } = await import(jsUrl("devtools", `?h=${++seq}`));
  initDevtools("overview");
  assert.equal(appended, 0);
});

test("開發環境沒存過設定：全部打開，補交是模擬送出", async () => {
  const { env } = await envAt("localhost");
  assert.deepEqual(env.readDev(), env.DEV_DEFAULTS);
  assert.deepEqual(env.DEV_DEFAULTS, { base: true, labels: true, interact: true, stats: true, list: true, submit: "mock" });
  assert.equal(env.submitMode(), "mock");
});

test("開發環境：存過的設定蓋過預設，沒存的項目用預設", async () => {
  const { env } = await envAt("localhost", { stats: false, submit: "api" });
  assert.deepEqual(env.readDev(), { ...env.DEV_DEFAULTS, stats: false, submit: "api" });
  assert.equal(env.submitMode(), "api");
});

test("開發環境：存的設定壞掉或送出方式不認得時，退回預設", async () => {
  assert.deepEqual((await envAt("localhost", "{壞掉的 JSON")).env.readDev().submit, "mock");
  assert.equal((await envAt("localhost", { submit: "post" })).env.submitMode(), "mock");
  assert.equal((await envAt("localhost", "null")).env.submitMode(), "mock");
});

test("開發環境：讀 localStorage 出錯（無痕視窗）也不會中斷", async () => {
  const { env } = await envAt("localhost");
  globalThis.localStorage = { getItem() { throw new Error("blocked"); }, setItem() { throw new Error("blocked"); } };
  assert.deepEqual(env.readDev(), env.DEV_DEFAULTS);
  assert.doesNotThrow(() => env.writeDev({ ...env.DEV_DEFAULTS, base: false }));
});

test("writeDev 存的格式 readDev 讀得回來", async () => {
  const { env, store } = await envAt("localhost");
  env.writeDev({ ...env.DEV_DEFAULTS, labels: false, submit: "off" });
  assert.equal(JSON.parse(store.get(env.DEV_KEY)).labels, false);
  assert.equal(env.readDev().labels, false);
  assert.equal(env.submitMode(), "off");
});
