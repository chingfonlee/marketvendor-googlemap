// 網址檢查（PLAN §4、§5）：web/js/urlcheck.js，以及它和 scripts/import_excel.py 的 check_url 規則一致。

import { test } from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { readFileSync } from "node:fs";
import path from "node:path";
import { ROOT, WEB, readJSON, jsUrl } from "./helpers.mjs";

const { checkUrl, extractUrl, MAX_URL_LENGTH } = await import(jsUrl("urlcheck"));

const CID = "7600088901324819454";
// 0x…:0x698ae1bcd0bbd0fe 的後半段 = 7605139121840574718
const LONG = "https://www.google.com/maps/place/%E6%98%A5%E5%92%8C/@25.04,121.57,17z/data=!3m1!4b1!4m6!3m5!1s0x3442ab:0x698ae1bcd0bbd0fe!8m2!3d25.04!4d121.57";

const ACCEPT = [
  [`https://maps.google.com/?cid=${CID}`, `cid:${CID}`],
  [`http://maps.google.com/?cid=${CID}`, `cid:${CID}`],
  [`https://www.google.com/maps?cid=${CID}`, `cid:${CID}`],
  [`https://google.com/maps?cid=${CID}`, `cid:${CID}`],
  [`https://www.google.com.tw/maps?cid=${CID}`, `cid:${CID}`],
  [`https://maps.google.com.tw/?cid=${CID}`, `cid:${CID}`],
  [`https://MAPS.Google.com/?cid=${CID}`, `cid:${CID}`],
  ["https://www.google.com/maps/search/?api=1&query=x&query_place_id=ChIJ123abc", "place_id:ChIJ123abc"],
  ["https://www.google.com/maps/place/?q=place_id:ChIJ&place_id=ChIJxyz", "place_id:ChIJxyz"],
  [LONG, "cid:7605139121840574718"],
];

const SHORT = ["https://maps.app.goo.gl/AbCdEf123", "https://goo.gl/maps/AbCdEf123"];

const REJECT = [
  ["", "請貼上"],
  ["   ", "請貼上"],
  ["春和油飯", "不是有效的網址"],
  ["ftp://maps.google.com/?cid=1", "不是有效的網址"],
  ["https://www.google.com/search?q=春和油飯", "不是 Google 地圖"],
  ["https://www.google.com/?cid=1", "不是 Google 地圖"],
  ["https://goo.gl/abc", "不是 Google 地圖"],
  ["https://maps.google.com.evil.com/?cid=1", "不是 Google 地圖"],
  ["https://evil.com/maps.google.com/?cid=1", "不是 Google 地圖"],
  ["https://www.facebook.com/maps", "不是 Google 地圖"],
  ["https://maps.app.goo.gl/", "短網址不完整"],
  ["https://goo.gl/maps/", "短網址不完整"],
  ["https://maps.google.com/", "找不到店家"],
  ["https://maps.google.com/?cid=abc", "找不到店家"],
  ["https://www.google.com/maps/@25.04,121.57,15z", "找不到店家"],
  [`https://maps.google.com/?cid=1&x=${"a".repeat(MAX_URL_LENGTH)}`, "太長"],
];

test("接受的 Google 地圖網址，解析出 cid 或 place_id", () => {
  for (const [url, key] of ACCEPT) {
    const r = checkUrl(url);
    assert.equal(r.ok, true, `${url}：${r.error}`);
    assert.equal(r.placeKey, key, url);
    assert.ok(!r.short);
  }
});

test("短網址接受，但解析不出地點（留給人工展開）", () => {
  for (const url of SHORT) {
    const r = checkUrl(url);
    assert.equal(r.ok, true, url);
    assert.equal(r.short, true);
    assert.equal(r.placeKey, "");
  }
});

test("不接受的網址，錯誤訊息說明原因", () => {
  for (const [url, msg] of REJECT) {
    const r = checkUrl(url);
    assert.equal(r.ok, false, `應該拒絕：${url.slice(0, 80)}`);
    assert.ok(r.error.includes(msg), `${url.slice(0, 60)} → ${r.error}`);
  }
});

test("長度上限剛好 2048 字還能過，多一個字就拒絕", () => {
  const base = `https://maps.google.com/?cid=${CID}&x=`;
  assert.equal(checkUrl(base + "a".repeat(MAX_URL_LENGTH - base.length)).ok, true);
  assert.equal(checkUrl(base + "a".repeat(MAX_URL_LENGTH - base.length + 1)).ok, false);
});

test("從手機分享的文字取出網址（前面帶店名、後面帶標點）", () => {
  assert.equal(extractUrl("春和油飯 https://maps.app.goo.gl/AbC123"), "https://maps.app.goo.gl/AbC123");
  assert.equal(extractUrl("看這裡：https://maps.app.goo.gl/AbC123，謝謝"), "https://maps.app.goo.gl/AbC123");
  assert.equal(extractUrl("（https://maps.google.com/?cid=1）"), "https://maps.google.com/?cid=1");
  assert.equal(extractUrl("春和油飯\nhttps://maps.app.goo.gl/AbC123\n"), "https://maps.app.goo.gl/AbC123");
  assert.equal(checkUrl(`春和油飯 https://maps.google.com/?cid=${CID}`).placeKey, `cid:${CID}`);
  assert.equal(extractUrl(null), "");
});

test("正式資料裡現有的連結全部通過檢查", () => {
  const vendors = readJSON(path.join(WEB, "data", "vendors.json"));
  const withUrl = vendors.filter((v) => v.url);
  assert.ok(withUrl.length > 0);
  for (const v of withUrl) {
    const r = checkUrl(v.url);
    assert.equal(r.ok, true, `${v.id} ${v.url}：${r.error}`);
    assert.ok(r.placeKey, `${v.id} 解析不出地點`);
  }
});

test("不同攤商共用同一個地點，只有 review-decisions.csv 列為例外的那幾家", () => {
  const vendors = readJSON(path.join(WEB, "data", "vendors.json"));
  const csv = readFileSync(path.join(ROOT, "data", "review-decisions.csv"), "utf8").trim().split(/\r?\n/).slice(1);
  const shared = csv.map((l) => l.split(",")).filter((c) => c[1] === "share_place").map((c) => new Set([c[3], c[4]]));
  const byKey = new Map();
  for (const v of vendors.filter((x) => x.url)) {
    const k = checkUrl(v.url).placeKey;
    byKey.set(k, [...(byKey.get(k) || []), v.name]);
  }
  for (const [k, names] of byKey) {
    if (names.length < 2) continue;
    const ok = shared.some((s) => names.every((n) => s.has(n)));
    assert.ok(ok, `${k} 被 ${names.join("、")} 共用，但沒有列在 share_place`);
  }
});

// 抽出 import_excel.py 的 check_url 單獨執行（整支程式會去讀 Excel，不能直接匯入）
function pythonCheck(urls) {
  const code = `
import ast, json, re, sys
from urllib.parse import urlsplit, parse_qs
src = open(sys.argv[1], encoding="utf-8").read()
fn = next(n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef) and n.name == "check_url")
exec(ast.get_source_segment(src, fn))
urls = json.loads(sys.stdin.read())
print(json.dumps([check_url(u) for u in urls]))
`;
  try {
    const out = execFileSync("python", ["-I", "-c", code, path.join(ROOT, "scripts", "import_excel.py")], {
      input: JSON.stringify(urls), encoding: "utf8",
    });
    return JSON.parse(out);
  } catch (err) {
    return { skip: `找不到 Python 或執行失敗：${err.message.split("\n")[0]}` };
  }
}

test("和匯入程式（Python）的 check_url 結果一致", (t) => {
  // 兩邊刻意不同的地方：網頁多接受 google.com.tw 和短網址（PLAN §5）、拒絕過長網址的訊息不同，這些不比
  const shared = [
    ...ACCEPT.filter(([u]) => !/google\.com\.tw/.test(u)),
    ...REJECT.filter(([u]) => u.trim() && /^https?:/.test(u) && !u.includes("goo.gl") && u.length <= MAX_URL_LENGTH),
  ].map(([u]) => u);
  const vendors = readJSON(path.join(WEB, "data", "vendors.json"));
  shared.push(...vendors.filter((v) => v.url).map((v) => v.url));

  const py = pythonCheck(shared);
  if (py.skip) return t.skip(py.skip);
  shared.forEach((u, i) => {
    const [key, problem] = py[i];
    const js = checkUrl(u);
    assert.equal(js.ok, problem === null, `${u.slice(0, 80)}：JS ${js.ok}，Python ${problem}`);
    if (js.ok) assert.equal(js.placeKey, key, u);
  });
});
