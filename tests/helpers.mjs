// 測試共用：在 Node 裡模擬瀏覽器的 location／history／document／fetch，讓 web/js 的模組可以直接匯入。
// 不裝任何套件，只用 Node 內建的 node:test。

import { readFileSync } from "node:fs";
import { fileURLToPath, pathToFileURL } from "node:url";
import path from "node:path";

export const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
export const WEB = path.join(ROOT, "web");
export const FIXTURES = path.join(ROOT, "tests", "fixtures");

export function readJSON(file) {
  return JSON.parse(readFileSync(file, "utf8"));
}

// 假的 DOM 元素：querySelector 拿到的東西可以任意設屬性、呼叫方法（el.closest(…).classList.toggle(…)），
// 都不會出錯。只為了讓頁面模組在 Node 裡匯入時不中斷，畫面本身另外在瀏覽器測。
function fakeElement() {
  const store = { dataset: {}, style: {} };
  const self = new Proxy(function () {}, {
    get: (_t, k) => (k in store ? store[k] : k === Symbol.iterator ? [][Symbol.iterator] : fakeElement()),
    set: (_t, k, v) => { store[k] = v; return true; },
    apply: () => fakeElement(),
  });
  return self;
}

// 一次設好全域；dataDir 是 data/*.json 的來源（正式資料或 fixture）
export function installBrowser({ dataDir = path.join(WEB, "data"), hostname = "example.org" } = {}) {
  const loc = { hash: "", pathname: "/", search: "", hostname };
  globalThis.location = loc;
  globalThis.history = {
    replaceState(_s, _t, url) {
      const i = String(url).indexOf("#");
      loc.hash = i >= 0 ? String(url).slice(i) : "";
    },
  };
  globalThis.document = {
    documentElement: { dataset: {} },
    body: { dataset: {} },
    querySelector: () => fakeElement(),
    querySelectorAll: () => [],
  };
  globalThis.window = { addEventListener() {}, scrollTo() {} };
  globalThis.localStorage = { getItem: () => null, setItem() {} };
  globalThis.Option = class { constructor(text, value) { Object.assign(this, { text, value }); } };
  globalThis.fetch = async (p) => {
    const file = p.startsWith("data/") ? path.join(dataDir, p.slice(5)) : path.join(WEB, p);
    try {
      const body = readFileSync(file, "utf8");
      return { ok: true, status: 200, json: async () => JSON.parse(body) };
    } catch {
      return { ok: false, status: 404, json: async () => null };
    }
  };
  return loc;
}

export const jsUrl = (name, tag = "") => pathToFileURL(path.join(WEB, "js", `${name}.js`)).href + tag;

// 照 main.js 的啟動順序：載入資料、把 data 接到 state。
// data.js 每次帶不同 query 匯入，拿到全新的一份（它是單例，不同資料要互不影響）；
// state.js 是 data.js 用相對路徑匯入的，同一個測試檔裡只有一份，靠 readHash() 歸零。
let seq = 0;
export async function boot(opts = {}) {
  installBrowser(opts);
  const dataMod = await import(jsUrl("data", `?t=${++seq}`));
  const stateMod = await import(jsUrl("state"));
  await dataMod.loadData();
  stateMod.configure({
    countyOf: (id) => dataMod.data.marketById.get(id)?.county ?? null,
    isCounty: (c) => dataMod.data.counties.includes(c),
  });
  return { ...dataMod, ...stateMod };
}

// 設定網址 hash 再讀進 state（模擬使用者打開分享連結）
export function openHash(app, hash) {
  globalThis.location.hash = hash ? `#${hash}` : "";
  app.readHash();
}
