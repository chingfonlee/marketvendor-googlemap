// 在真的瀏覽器裡開網頁（iframe），照使用者的操作點選，檢查畫面。由 tests/serve_tests.py 提供。
// 結果顯示在頁面上，也放在 window.testResults（給自動化工具讀）。
// 從 localhost 打開時跑開發環境的測試，最後再到 127.0.0.2（正式環境）跑 prodTest 的項目，結果合在一起。

const { IS_DEV, DEV_KEY } = await import("/web/js/env.js");
const EMBEDDED = new URLSearchParams(location.search).has("embedded");
const stage = document.getElementById("stage");
const results = [];
const tests = [];
const test = (name, fn) => { if (IS_DEV) tests.push({ name, fn }); };
const prodTest = (name, fn) => { if (!IS_DEV) tests.push({ name: `正式環境：${name}`, fn }); };

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function until(fn, what, ms = 3000) {
  const end = Date.now() + ms;
  for (;;) {
    try { if (fn()) return; } catch { /* 還沒好 */ }
    if (Date.now() > end) throw new Error(`等不到：${what}`);
    await sleep(20);
  }
}

function eq(a, b, what) {
  if (JSON.stringify(a) !== JSON.stringify(b)) throw new Error(`${what}：得到 ${JSON.stringify(a)}，應該是 ${JSON.stringify(b)}`);
}
function ok(v, what) {
  if (!v) throw new Error(what);
}

// 開發開關的設定和網頁同源，存在同一個 localStorage；每頁開之前先設好（預設是清掉）
function setDev(settings) {
  try {
    if (settings) localStorage.setItem(DEV_KEY, JSON.stringify(settings));
    else localStorage.removeItem(DEV_KEY);
  } catch { /* 無痕視窗 */ }
}

// 開一頁：寬高決定 D／L 版（iframe 的 media query 看的是 iframe 自己的大小）
async function open(url, { width = 1280, height = 800, beforeLoad, dev = null } = {}) {
  stage.replaceChildren();
  const frame = document.createElement("iframe");
  frame.width = width;
  frame.height = height;
  stage.append(frame);
  if (dev !== "keep") setDev(dev);
  if (beforeLoad) beforeLoad();
  const loaded = nextLoad(frame);
  frame.src = url;
  await loaded;
  return wrap(frame);
}

async function nextLoad(frame) {
  await new Promise((r) => frame.addEventListener("load", r, { once: true }));
  const doc = frame.contentDocument;
  await until(() => !doc.body.hasAttribute("data-loading"), "頁面載入完成");
  // 開發開關的 devtools.css 是載入後才加進來的，等它套上，關掉的元件才會真的消失
  if (doc.querySelector(".dev-fab")) {
    await until(() => [...doc.styleSheets].some((s) => s.href?.includes("devtools.css")), "devtools.css 載入");
  }
  await sleep(50);
}

function wrap(frame) {
  const win = frame.contentWindow;
  const doc = frame.contentDocument;
  // 頁面自己重新載入（補交頁換送出方式）：等載入完，拿新的 document
  const reloaded = async (trigger) => {
    const loaded = nextLoad(frame);
    await trigger();
    await loaded;
    return wrap(frame);
  };
  const $ = (s) => doc.querySelector(s);
  const $$ = (s) => [...doc.querySelectorAll(s)];
  const text = (s) => $(s)?.textContent.replace(/\s+/g, " ").trim();
  const choose = async (sel, value) => {
    const el = $(sel);
    el.value = value;
    el.dispatchEvent(new win.Event("change", { bubbles: true }));
    await sleep(30);
  };
  const click = async (el) => {
    (typeof el === "string" ? $(el) : el).click();
    await sleep(30);
  };
  const type = async (sel, value) => {
    const el = $(sel);
    el.value = value;
    el.dispatchEvent(new win.Event("input", { bubbles: true }));
    el.dispatchEvent(new win.Event("blur"));
    await sleep(30);
  };
  const css = (s, prop) => win.getComputedStyle($(s))[prop];
  return { win, doc, $, $$, text, choose, click, type, reloaded, css };
}

const getJSON = (p) => fetch(p).then((r) => r.json());
const markets = await getJSON("web/data/markets.json");
const vendors = await getJSON("web/data/vendors.json");
const labels = await getJSON("web/data/county-labels.json");
const counties = labels.labels.map((l) => l.county);
const byCounty = (c) => markets.filter((m) => m.county === c);
const countyVendors = (c) => byCounty(c).reduce((n, m) => n + m.vendor_count, 0);
const fullName = (m) => { const s = m.county.replace(/[市縣]$/, ""); return m.name.startsWith(s) ? m.name : s + m.name; };
const total = vendors.length;

// ================= 總覽頁 D 版（三欄） =================
test("D 版初始：8 個縣市標籤、15 個市場分 8 組、攤商清單是全台", async () => {
  const p = await open("web/index.html");
  eq(p.doc.body.dataset.layout, "d", "版面");
  eq(p.$$(".county-label").map((b) => b.querySelector(".label-head").textContent.trim()), counties, "標籤（只有參與的縣市）");
  eq(p.$$(".market-group").length, 8, "市場清單分組");
  eq(p.$$(".market-row").length, markets.length, "市場列");
  eq(p.text(".donut-value"), String(total), "圓環中間的總數");
  eq(p.text("#vendor-title"), `全台・攤商清單 (${total})`, "攤商清單標題");
  eq(p.$$(".vendor-row").length, total, "攤商列（不分頁）");
  eq(p.$$(".county-label.dim").length, 0, "沒選縣市時標籤都不淡");
});

test("點地圖上的縣市標籤：左側選單、市場清單、圓環、其他標籤變淡一起動", async () => {
  const p = await open("web/index.html");
  const c = counties[0];
  await p.click(p.$$(".county-label")[0]);
  eq(p.$("#county-select").value, c, "左側縣市選單同步");
  eq(p.$("#market-select").value, "", "市場未選");
  eq(p.$$(".market-row").map((r) => r.dataset.market), byCounty(c).map((m) => m.id), "市場清單只剩該縣市");
  eq(p.text(".donut-value"), String(countyVendors(c)), "圓環改算該縣市");
  eq(p.text("#progress-title"), `${c}完成進度`, "進度卡標題");
  eq(p.$$(".county-label.dim").length, 7, "其他 7 個標籤變淡");
  eq(p.$$(".county-label")[0].getAttribute("aria-pressed"), "true", "選到的標籤");
  eq(p.$$(".vendor-row").length, countyVendors(c), "攤商清單是整個縣市");
});

test("點市場：右下顯示該市場的攤商，市場選單同步", async () => {
  const p = await open("web/index.html");
  const m = markets.find((x) => byCounty(x.county).length >= 2 && x !== byCounty(x.county)[0]);
  await p.click(p.$(`.market-row[data-market="${m.id}"]`));   // 從全台的市場清單直接點
  eq(p.$("#county-select").value, m.county, "縣市跟著設好");
  eq(p.$("#market-select").value, m.id, "市場選單");
  eq(p.text("#vendor-title"), `${fullName(m)}・攤商清單 (${m.vendor_count})`, "攤商清單標題");
  eq(p.$$(".vendor-row").length, m.vendor_count, "攤商列");
  eq(p.$(`.market-row[data-market="${m.id}"]`).getAttribute("aria-current"), "true", "市場列標示目前選取");
});

test("用左側選單切換縣市：原本的市場清掉，換成新縣市", async () => {
  const p = await open("web/index.html");
  const m = markets[0];
  await p.choose("#county-select", m.county);
  await p.choose("#market-select", m.id);
  const c2 = counties[counties.length - 1];
  await p.choose("#county-select", c2);
  eq(p.$("#market-select").value, "", "市場被清掉");
  eq([...p.$("#market-select").options].slice(1).map((o) => o.value), byCounty(c2).map((x) => x.id), "市場選單只剩新縣市的市場");
  eq(p.$$(".vendor-row").length, countyVendors(c2), "攤商清單");
  ok(!p.$$(".county-label")[counties.length - 1].classList.contains("dim"), "新縣市的標籤不淡");
});

test("狀態按鈕只篩清單，圓環和進度不變", async () => {
  const p = await open("web/index.html");
  const c = counties[counties.length - 1];
  await p.choose("#county-select", c);
  const donut = p.text(".donut-value");
  const legend = p.text(".progress-legend");
  const notSubmitted = byCounty(c).reduce((n, m) => n + m.counts.not_submitted, 0);
  await p.click('.status-btn[data-status="not_submitted"]');
  eq(p.$$(".vendor-row").length, notSubmitted, "清單只剩未提交");
  ok(p.$$(".vendor-row .badge").every((b) => b.dataset.status === "not_submitted"), "每列都是未提交");
  eq(p.text(".donut-value"), donut, "圓環不變");
  eq(p.text(".progress-legend"), legend, "圖例不變");
  eq(p.text('.status-btn[data-status="all"] b'), String(countyVendors(c)), "「全部」按鈕的數字");
});

test("未提交的攤商連到補交頁，其他的連到 Google 地圖", async () => {
  const p = await open("web/index.html");
  for (const row of p.$$(".vendor-row")) {
    const status = row.querySelector(".badge").dataset.status;
    const href = row.querySelector(".vendor-action").getAttribute("href");
    if (status === "not_submitted") ok(/^submit\.html#vendor=m\d\d-v\d{3}$/.test(href), `補交連結 ${href}`);
    else ok(/^https:\/\/(maps\.google\.com|www\.google\.com\/maps)/.test(href), `地圖連結 ${href}`);
  }
});

test("分享連結（hash）打開就是同一個畫面", async () => {
  const m = markets.find((x) => x.counts.submitted > 0 && x.counts.not_submitted > 0);
  const p = await open(`web/index.html#market=${m.id}&status=submitted`);
  eq(p.$("#county-select").value, m.county, "縣市");
  eq(p.$("#market-select").value, m.id, "市場");
  eq(p.$('.status-btn[aria-checked="true"]').dataset.status, "submitted", "狀態按鈕");
  eq(p.$$(".vendor-row").length, m.counts.submitted, "攤商列");
});

test("搜尋找不到：顯示空清單和「清除搜尋」，按了回到原本的清單", async () => {
  const p = await open("web/index.html");
  p.$("#search").value = "不存在的店名xyz";
  p.$("#search").dispatchEvent(new p.win.Event("search"));
  await sleep(30);
  ok(!p.$(".empty-state").hidden, "空清單提示出現");
  ok(p.text(".empty-text").includes("不存在的店名xyz"), `提示文字：${p.text(".empty-text")}`);
  eq(p.text(".empty-action"), "清除搜尋", "按鈕");
  await p.click(".empty-action");
  eq(p.$$(".vendor-row").length, total, "清除後回到全台");
});

test("頁首補交按鈕：桌機（含 1024 寬）用完整文字，不和分頁、標題擠在一起", async () => {
  for (const [w, h] of [[1024, 768], [1280, 800]]) {
    const p = await open("web/index.html", { width: w, height: h });
    const shown = p.$$(".submit-link span").filter((s) => p.win.getComputedStyle(s).display !== "none");
    eq(shown.map((s) => s.textContent), ["我是攤商，確認或補交 Google 地圖連結"], `${w} 寬的按鈕文字`);
    eq(p.$$(".tab").map((t) => t.textContent.trim()), ["地圖總覽", "統計報表"], "分頁：地圖總覽、統計報表（資料管理先不顯示）");
    const btn = p.$(".submit-link").getBoundingClientRect();
    const tabs = p.$(".tabs").getBoundingClientRect();
    ok(btn.left - tabs.right >= 8 && btn.right <= w, `${w} 寬：按鈕和分頁間距 ${Math.round(btn.left - tabs.right)}px`);
    ok(p.$(".brand").getBoundingClientRect().right < tabs.left, `${w} 寬：標題和分頁重疊`);
  }
});

// ================= 總覽頁 L 版（手機） =================
test("L 版（375 寬）：不放地圖，9 張縣市卡片", async () => {
  const p = await open("web/index.html", { width: 375, height: 812 });
  eq(p.doc.body.dataset.layout, "l", "版面");
  ok(p.$("main.map").hidden, "地圖不顯示");
  eq(p.$$(".county-label").length, 0, "不建立地圖標籤");
  eq(p.$$(".county-tile").map((t) => t.querySelector(".tile-head").textContent.trim()), ["全台", ...counties], "縣市卡片");
  const shown = p.$$(".submit-link span").filter((s) => p.win.getComputedStyle(s).display !== "none");
  eq(shown.map((s) => s.textContent), ["確認連結"], "頁首按鈕文字");
  const title = p.$(".brand-title");
  ok(title.scrollWidth <= title.clientWidth + 1, "頁首標題沒有被切掉（放不下時在「・」後面換行）");
  ok(p.$(".brand").getBoundingClientRect().right < p.$(".submit-link").getBoundingClientRect().left, "標題和按鈕不重疊");
  eq(p.$$(".brand-line").map((l) => Math.round(l.getBoundingClientRect().top)).filter((v, i, a) => a.indexOf(v) === i).length, 2, "標題兩行");

  // 手機字體放大（約 1.5 倍）：標題變三行時，頁首跟著長高，第一行不會被切掉
  const big = p.doc.head.appendChild(p.doc.createElement("style"));
  big.textContent = ".brand-title { font-size: 22px !important; }";
  const hdr = p.$(".site-header").getBoundingClientRect();
  const t = title.getBoundingClientRect();
  ok(t.top >= hdr.top && t.bottom <= hdr.bottom, `字體放大時標題在頁首裡：標題 ${Math.round(t.top)}～${Math.round(t.bottom)}，頁首 ${Math.round(hdr.top)}～${Math.round(hdr.bottom)}`);
  big.remove();
});

test("L 版點縣市卡片：市場清單和攤商清單換成該縣市，點「全台」回去", async () => {
  const p = await open("web/index.html", { width: 375, height: 812 });
  const c = counties.find((x) => byCounty(x).length >= 2);
  await p.click(p.$(`.county-tile[data-county="${c}"]`));
  eq(p.$(`.county-tile[data-county="${c}"]`).getAttribute("aria-pressed"), "true", "卡片選取");
  eq(p.$$(".market-row[data-market]").map((r) => r.dataset.market), byCounty(c).map((m) => m.id), "市場清單");
  ok(p.$(".market-row-all"), "有「全部市場」列");
  eq(p.$$(".vendor-row").length, countyVendors(c), "攤商清單");
  await p.click(p.$('.county-tile[data-county=""]'));
  eq(p.$$(".vendor-row").length, total, "回到全台");
});

// ================= 補交頁 =================
const clearMock = () => { try { localStorage.removeItem("gm-submit-mock"); } catch { /* 無痕視窗 */ } };
const readMock = () => JSON.parse(localStorage.getItem("gm-submit-mock") || "[]");

test("補交頁初始：只能選縣市，市場和攤商鎖住；本機是模擬模式", async () => {
  const p = await open("web/submit.html", { beforeLoad: clearMock });
  eq([...p.$("#sp-county").options].map((o) => o.value), ["", ...counties], "縣市選項");
  ok(p.$("#sp-market").disabled && p.$("#sp-vendor").disabled, "市場、攤商鎖住");
  eq(p.$(".sp-mode").dataset.mode, "mock", "模式");
  ok(p.$(".sp-current").hidden && p.$(".sp-actions").hidden, "還沒選店，不顯示連結和操作");
});

test("補交頁三層選單：縣市→市場→攤商，換縣市時市場和攤商歸零", async () => {
  const p = await open("web/submit.html");
  const c = counties.find((x) => byCounty(x).length >= 2);
  await p.choose("#sp-county", c);
  ok(!p.$("#sp-market").disabled, "市場解鎖");
  ok(p.$("#sp-vendor").disabled, "攤商仍鎖住");
  eq([...p.$("#sp-market").options].slice(1).map((o) => o.value), byCounty(c).map((m) => m.id), "市場選項");
  const m = byCounty(c)[1];
  await p.choose("#sp-market", m.id);
  ok(!p.$("#sp-vendor").disabled, "攤商解鎖");
  eq([...p.$("#sp-vendor").options].slice(1).map((o) => o.value), vendors.filter((v) => v.market_id === m.id).map((v) => v.id), "攤商選項");
  await p.choose("#sp-vendor", vendors.find((v) => v.market_id === m.id).id);
  ok(!p.$(".sp-current").hidden, "選了店才顯示目前連結");
  const c2 = counties.find((x) => x !== c);
  await p.choose("#sp-county", c2);
  eq([p.$("#sp-market").value, p.$("#sp-vendor").value], ["", ""], "市場、攤商歸零");
  ok(p.$("#sp-vendor").disabled, "攤商再次鎖住");
  ok(p.$(".sp-current").hidden, "目前連結收起");
  eq(new URLSearchParams(p.win.location.hash.slice(1)).get("county"), c2, "hash 跟著改");
});

test("從總覽頁「補交」連結進來（#vendor=…）：三層選好，未提交的店只能貼網址", async () => {
  const v = vendors.find((x) => x.status === "not_submitted");
  const m = markets.find((x) => x.id === v.market_id);
  const p = await open(`web/submit.html#vendor=${v.id}`);
  eq([p.$("#sp-county").value, p.$("#sp-market").value, p.$("#sp-vendor").value], [m.county, m.id, v.id], "三層選單");
  ok(p.$('input[value="confirm"]').disabled, "沒有連結不能確認");
  ok(p.$('input[value="update"]').checked, "直接選好「貼網址」");
  ok(!p.$(".sp-url").hidden, "網址欄出現");
  eq(p.text(".sp-current-text"), "目前沒有連結。", "目前連結");
});

test("補交頁網址檢查：錯的提示原因，對的顯示格式正確，和現有連結同一家店會提醒", async () => {
  const v = vendors.find((x) => x.status === "submitted" && /cid=\d+/.test(x.url));
  const p = await open(`web/submit.html#vendor=${v.id}`);
  await p.click('input[value="update"]');
  await p.type("#sp-url", "https://www.facebook.com/abc");
  ok(p.text("#sp-url-error").includes("不是 Google 地圖"), `錯誤網域：${p.text("#sp-url-error")}`);
  eq(p.$("#sp-url").getAttribute("aria-invalid"), "true", "aria-invalid");
  await p.type("#sp-url", "店名 https://maps.app.goo.gl/AbCdEf123");
  ok(p.$("#sp-url-error").classList.contains("is-ok"), `短網址：${p.text("#sp-url-error")}`);
  await p.type("#sp-url", v.url);
  ok(p.text("#sp-url-error").includes("同一家店"), `同一家店：${p.text("#sp-url-error")}`);
});

test("模擬送出：確認現有連結產生 §5 格式的紀錄；同一家同網址再送一次會擋下", async () => {
  const v = vendors.find((x) => x.status === "submitted");
  const m = markets.find((x) => x.id === v.market_id);
  const p = await open(`web/submit.html#vendor=${v.id}`, { beforeLoad: clearMock });
  await p.click('input[value="confirm"]');
  p.$("#sp-form").requestSubmit();
  await until(() => !p.$(".sp-done").hidden, "顯示「已收到，待確認」");
  eq(p.text("#sp-done-title"), "已收到，待確認", "完成畫面");
  const list = readMock();
  eq(list.length, 1, "紀錄筆數");
  const r = list[0];
  eq(Object.keys(r), ["submitted_at", "ip", "county", "market_id", "market_name", "vendor_id", "vendor_name",
    "action", "url", "place_key", "status_before", "review_result", "reviewed_at", "note"], "欄位");
  eq([r.county, r.market_id, r.market_name, r.vendor_id, r.vendor_name], [m.county, m.id, m.name, v.id, v.name], "攤商資料");
  eq([r.action, r.url, r.status_before], ["confirm", v.url, "submitted"], "操作");
  ok(/^cid:\d+$|^place_id:/.test(r.place_key), `place_key ${r.place_key}`);
  ok(/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\+08:00$/.test(r.submitted_at), `台北時間 ${r.submitted_at}`);

  await p.click(".sp-again");
  await p.choose("#sp-vendor", v.id);
  await p.click('input[value="confirm"]');
  p.$("#sp-form").requestSubmit();
  await until(() => p.text(".sp-form-error"), "顯示錯誤");
  ok(p.text(".sp-form-error").includes("24 小時內已經送過"), `防重複：${p.text(".sp-form-error")}`);
  eq(readMock().length, 1, "沒有多存一筆");
  clearMock();
});

test("已完成的店不能再「確認」，只能貼新網址（交給人工決定）", async () => {
  const p = await open("fx/edge/submit.html#vendor=m01-v001");
  ok(p.$('input[value="confirm"]').disabled, "確認鎖住");
  ok(p.text('.sp-choice-hint[data-for="update"]').includes("人工"), "貼網址的說明");
});

// ================= 邊界案例（tests/fixtures/edge） =================
test("全部完成的縣市：完成率 100%", async () => {
  const p = await open("fx/edge/index.html#county=" + encodeURIComponent("臺北市"));
  eq(p.text(".donut-value"), "3", "圓環總數");
  eq(p.$$(".progress-legend li").map((li) => li.textContent.replace(/\s+/g, " ").trim()),
    ["已完成 3 (100%)", "待確認 0 (0%)", "未提交 0 (0%)"], "圖例只有三種狀態");
  await p.click('.status-btn[data-status="not_submitted"]');
  ok(!p.$(".empty-state").hidden, "篩未提交時是空清單");
  eq(p.text(".empty-text"), "這個範圍還沒有未提交的攤商", "提示文字");
  eq(p.text(".empty-action"), "顯示全部狀態", "按鈕");
});

test("空市場（0 家）：市場清單顯示 0 家，攤商清單出現空清單提示", async () => {
  const p = await open("fx/edge/index.html#market=m02");
  ok(p.text('.market-row[data-market="m02"]').includes("0 家攤商"), "市場列");
  eq(p.$$(".vendor-row").length, 0, "攤商列");
  ok(!p.$(".empty-state").hidden, "空清單提示出現");
  eq(p.text(".empty-text"), "這個市場還沒有攤商", "提示文字");
  ok(p.$(".empty-action").hidden, "已經是「全部」，不顯示「顯示全部狀態」按鈕");
  // 換到有攤商的市場再篩空，按鈕要回來
  await p.click('.market-row[data-market="m01"]');
  await p.click('.status-btn[data-status="submitted"]');
  ok(!p.$(".empty-action").hidden, "篩狀態造成的空清單仍有按鈕");
  eq(p.text(".empty-text"), "這個範圍還沒有待確認的攤商", "篩狀態的提示");
});

test("有標籤但沒有市場的縣市：點了不出錯，圓環 0、完成率 0%", async () => {
  const p = await open("fx/edge/index.html");
  const c = counties.find((x) => !["臺北市", "臺東縣"].includes(x));
  await p.click(p.$$(".county-label").find((b) => b.textContent.includes(c)));
  eq(p.$("#county-select").value, c, "縣市");
  eq(p.$$(".market-row").length, 0, "市場列");
  eq(p.text(".donut-value"), "0", "圓環");
  eq(p.$$(".progress-legend li").map((li) => li.textContent.replace(/\s+/g, " ").trim()),
    ["已完成 0 (0%)", "待確認 0 (0%)", "未提交 0 (0%)"], "圖例三種狀態都是 0");
  ok(!/NaN|undefined/.test(p.doc.body.textContent), "畫面上沒有 NaN 或 undefined");
});

test("補交頁選到空市場：攤商選單說明這個市場沒有攤商", async () => {
  const p = await open("fx/edge/submit.html#market=m02");
  eq(p.$("#sp-market").value, "m02", "市場");
  eq(p.$("#sp-vendor").options.length, 1, "只有提示選項");
  eq(p.$("#sp-vendor").options[0].text, "這個市場沒有攤商", "攤商選單的提示");
  ok(p.$("#sp-vendor").disabled, "沒有可選的，選單鎖住");
  await p.choose("#sp-market", "m01");
  ok(!p.$("#sp-vendor").disabled, "換到有攤商的市場就解鎖");
  eq(p.$("#sp-vendor").options[0].text, "請選擇攤商", "提示換回來");
});

// ================= 開發開關（任務 9，SVG_COMPONENTS §6） =================
const ALL_ON = { base: true, labels: true, interact: true, stats: true, list: true, submit: "mock" };
const devOff = (p) => (p.doc.documentElement.dataset.devOff || "").split(" ").filter(Boolean);
const toggle = async (p, name) => {
  if (p.$("#dev-panel").hidden) await p.click(".dev-fab");
  await p.click(`#dev-panel input[name="${name}"]`);
};

test("開發開關：本機兩頁左下角都有「開發」按鈕，面板預設收起，Esc 關閉", async () => {
  for (const url of ["web/index.html", "web/submit.html"]) {
    const p = await open(url);
    ok(p.$(".dev-fab"), `${url} 沒有「開發」按鈕`);
    ok(p.$("#dev-panel").hidden, "面板預設收起");
    ok(!p.$(".dev-fab").classList.contains("is-changed"), "預設值時沒有橘點");
    await p.click(".dev-fab");
    ok(!p.$("#dev-panel").hidden, "點了打開");
    eq(p.$$('#dev-panel input[type="checkbox"]').map((i) => [i.name, i.checked]),
      [["base", true], ["labels", true], ["interact", true], ["stats", true], ["list", true]], "五個開關都打開");
    eq(p.$('#dev-panel input[name="submit"]:checked').value, "mock", "送出方式預設模擬");
    p.doc.dispatchEvent(new p.win.KeyboardEvent("keydown", { key: "Escape" }));
    await sleep(30);
    ok(p.$("#dev-panel").hidden, "Esc 關閉");
  }
});

test("開發開關：關掉底圖，底圖、標語、地圖上的貓不顯示，標籤還在", async () => {
  const p = await open("web/index.html");
  await toggle(p, "base");
  eq(devOff(p), ["base"], "data-dev-off");
  for (const s of [".layer-base", ".overlay-headline", ".overlay-cat"]) eq(p.css(s, "visibility"), "hidden", s);
  ok(p.css(".layer-labels", "display") !== "none", "標籤不受影響");
  ok(p.$(".dev-fab").classList.contains("is-changed"), "不是預設值時有橘點");
});

test("開發開關：關掉縣市標籤，地圖標籤、圖例、清單版縣市卡片都不顯示", async () => {
  const p = await open("web/index.html", { dev: { ...ALL_ON, labels: false } });
  for (const s of [".layer-labels", ".legend-toggle", ".legend"]) eq(p.css(s, "display"), "none", s);
  ok(p.css(".layer-base", "visibility") !== "hidden", "底圖不受影響");
  const l = await open("web/index.html", { width: 375, height: 812, dev: { ...ALL_ON, labels: false } });
  eq(l.css(".county-cards", "display"), "none", "清單版的縣市卡片");
});

test("開發開關：關掉統計，進度卡不顯示；關掉清單，篩選、市場清單、攤商清單不顯示", async () => {
  const p = await open("web/index.html", { dev: { ...ALL_ON, stats: false } });
  eq(p.css(".progress-card", "display"), "none", "進度卡");
  ok(p.css(".vendor-card", "display") !== "none", "清單不受影響");
  const q = await open("web/index.html", { dev: { ...ALL_ON, list: false } });
  for (const s of [".filter-panel", ".market-card", ".vendor-card"]) eq(q.css(s, "display"), "none", s);
  ok(q.css(".progress-card", "display") !== "none", "進度卡不受影響");
});

test("開發開關：關掉互動，地圖、選單、搜尋、狀態按鈕、市場清單不能操作，攤商連結照常", async () => {
  const p = await open(`web/index.html#county=${encodeURIComponent(counties[0])}`, { dev: { ...ALL_ON, interact: false } });
  for (const s of ["main.map", ".filter-search", ".filter-selects", ".filter-status", ".market-card"]) ok(p.$(s).inert, `${s} 應該不能操作`);
  ok(!p.$(".vendor-card").inert, "攤商清單（連結）照常可以點");
  eq(p.$("#county-select").value, counties[0], "畫面停在目前的篩選");
  // inert 擋的是使用者的滑鼠、觸控、鍵盤；程式的 .click() 擋不住，所以用「拿不到焦點」來驗證
  for (const s of [".county-label", "#search", "#county-select", ".status-btn", ".market-row"]) {
    const el = p.$(s);
    el.focus();
    ok(p.doc.activeElement !== el, `${s} 不該拿到焦點`);
  }
  const link = p.$(".vendor-action");
  link.focus();
  eq(p.doc.activeElement, link, "攤商的連結可以拿到焦點");
  await toggle(p, "interact");
  ok(!p.$("main.map").inert, "打開互動後恢復");
  p.$(".county-label").focus();
  eq(p.doc.activeElement, p.$(".county-label"), "標籤又拿得到焦點");
  await p.click(p.$$(".county-label")[1]);
  eq(p.$("#county-select").value, counties[1], "點標籤有反應");
});

test("開發開關：設定重新整理後還在，總覽頁和補交頁共用；「全部恢復預設」全部打開", async () => {
  const p = await open("web/index.html");
  await toggle(p, "stats");
  await toggle(p, "list");
  const r = await p.reloaded(() => p.win.location.reload());
  eq(devOff(r).sort(), ["list", "stats"], "重新整理後還在");
  ok(!r.$('#dev-panel input[name="stats"]').checked, "面板也記得");
  const s = await open("web/submit.html", { dev: "keep" });
  ok(s.$(".dev-fab").classList.contains("is-changed"), "補交頁也看到不是預設值（橘點）");
  const q = await open("web/index.html", { dev: "keep" });
  await q.click(".dev-fab");
  await q.click(".dev-reset");
  eq(devOff(q), [], "恢復預設後沒有關掉的元件");
  ok(!q.$(".dev-fab").classList.contains("is-changed"), "橘點消失");
  eq(JSON.parse(localStorage.getItem(DEV_KEY)), ALL_ON, "存的設定也恢復");
});

test("開發開關：補交頁換送出方式會自動重新載入；選「關閉」時不能送出", async () => {
  const p = await open("web/submit.html");
  eq(p.$(".sp-mode").dataset.mode, "mock", "預設模擬");
  await p.click(".dev-fab");
  const r = await p.reloaded(() => p.click('#dev-panel input[name="submit"][value="off"]'));
  eq(r.$(".sp-mode").dataset.mode, "off", "重新載入後是關閉");
  ok(r.text(".sp-mode").includes("送出已關閉"), `說明：${r.text(".sp-mode")}`);
  ok(r.$(".sp-submit").disabled, "送出按鈕停用");
});

test("開發開關：選「正式 API」時先過 Turnstile（測試金鑰），送到 /api/submissions，內容是 §5 的紀錄；伺服器失敗時顯示錯誤", async () => {
  await fetch("/api/_reset", { method: "POST" });
  const v = vendors.find((x) => x.status === "submitted");
  const p = await open(`web/submit.html#vendor=${v.id}`, { dev: { ...ALL_ON, submit: "api" }, beforeLoad: clearMock });
  eq(p.$(".sp-mode").dataset.mode, "api", "模式");
  ok(!p.$(".sp-turnstile").hidden, "顯示 Turnstile");
  await p.click('input[value="confirm"]');
  // 測試金鑰有時一載入就通過，「還沒驗證不能送出」在這裡測不穩，由 tests/submission.test.mjs 的後端測試涵蓋
  const token = () => p.$('.sp-turnstile [name="cf-turnstile-response"]')?.value;
  await until(token, "Turnstile 測試金鑰通過（要能連到 challenges.cloudflare.com）", 15000);
  p.$("#sp-form").requestSubmit();
  await until(() => !p.$(".sp-done").hidden, "顯示「已收到，待確認」");
  const got = await getJSON("/api/_received");
  eq(got.length, 1, "伺服器收到一筆");
  eq(Object.keys(got[0]), ["submitted_at", "ip", "county", "market_id", "market_name", "vendor_id", "vendor_name",
    "action", "url", "place_key", "status_before", "review_result", "reviewed_at", "note"], "欄位");
  eq([got[0].vendor_id, got[0].action, got[0].url], [v.id, "confirm", v.url], "內容");
  eq(readMock().length, 0, "不會另外存模擬紀錄");

  await fetch("/api/_fail", { method: "POST" });
  await p.click(".sp-again");
  await p.choose("#sp-vendor", v.id);
  await p.click('input[value="confirm"]');
  await until(token, "重新驗證", 15000);
  p.$("#sp-form").requestSubmit();
  await until(() => p.text(".sp-form-error"), "顯示錯誤");
  ok(p.text(".sp-form-error").includes("500"), `錯誤訊息：${p.text(".sp-form-error")}`);
  ok(p.$(".sp-done").hidden, "沒有顯示完成");
});

// ================= 統計報表頁（任務 17，stats-page-assets §五.6） =================
const S = await import("/web/js/stats-calc.js");
const fxMarkets = await getJSON("fx/stats-changed/data/markets.json");

// 每條長條：三段加起來等於長條寬，家數 > 0 的段至少「高度一半＋2px」；每個甜甜圈：三段加起來一整圈
function checkCharts(p) {
  for (const bar of p.$$(".st-bar")) {
    const w = bar.getBoundingClientRect().width;
    const segs = [...bar.children].map((i) => i.getBoundingClientRect().width);
    const h = bar.getBoundingClientRect().height;
    ok(Math.abs(segs.reduce((s, v) => s + v, 0) - w) <= 1, `長條三段加起來 ${segs.map(Math.round)}，長條 ${Math.round(w)}px`);
    ok(segs.every((v) => v >= h / 2 + 2 - 0.5), `長條每段至少 ${h / 2 + 2}px：${segs.map((v) => v.toFixed(1))}`);
  }
  const C = 2 * Math.PI * 48;
  for (const svg of p.$$(".st-donut svg")) {
    const lens = [...svg.querySelectorAll("circle:not(.seg-bg)")].map((c) => parseFloat(c.getAttribute("stroke-dasharray")));
    ok(Math.abs(lens.reduce((s, v) => s + v, 0) - C) < 0.01, `甜甜圈三段加起來 ${lens.reduce((s, v) => s + v, 0).toFixed(2)}，一圈 ${C.toFixed(2)}`);
  }
}
const segKeys = (bar) => [...bar.children].map((i) => i.className.replace("seg-", ""));
const countyRowsShown = (p) => p.$$(".st-county-list li").map((li) => [li.querySelector(".st-name").textContent, li.querySelector(".st-pct").textContent]);
const crowns = (p) => p.$$(".st-county-list li").filter((li) => li.querySelector(".st-crown svg")).map((li) => li.querySelector(".st-name").textContent);
const noHScroll = (p, w) => ok(p.doc.documentElement.scrollWidth <= w, `${w} 寬有橫向捲軸（${p.doc.documentElement.scrollWidth}px）`);

test("統計頁（正式資料）：62.5%、審核中、8 個縣市照比例排、皇冠、3 種類型、最強友善力市集 3 個", async () => {
  const p = await open("web/stats.html", { width: 1440, height: 900 });
  eq(p.text(".st-big"), "62.5%", "中間大字");
  eq(p.text(".st-sub"), "已提交 217／347 家", "中間小字");
  eq(p.$$(".st-legend b").map((b) => b.textContent), ["0", "217", "130"], "圖例家數");
  ok(p.$(".st-reviewing"), "已完成 0 時有「審核中」");
  eq(p.text(".st-updated"), "資料更新：2026/10/31", "更新日期");
  eq(countyRowsShown(p), S.countyRows(markets).map((r) => [r.county, S.pctText(r.counts)]), "縣市列");
  eq(countyRowsShown(p)[0], ["高雄市", "85%"], "第一名");
  eq(crowns(p), ["高雄市"], "皇冠");
  eq(p.$$(".st-type-name").map((s) => s.textContent), ["夜市", "傳統市場", "美食商圈"], "類型");
  eq(p.$$(".st-type-list b").map((b) => b.textContent), ["61%", "58%", "80%"], "類型百分比");
  eq(p.text("#st-top-title"), "最強友善力市集", "④ 標題");
  eq(p.$$(".st-top-name").map((s) => s.textContent), S.topRows(markets).map((m) => m.name), "最強友善力市集");
  eq(p.$$(".st-frac").map((s) => s.textContent), ["21/21", "20/20", "20/20"], "最強友善力市集分數");
  ok(p.$(".st-top-empty").hidden, "不顯示「還沒有市場提交」");
  ok(p.$$(".st-bar i.seg-verified").length === 0, "已完成 0 時不畫綠色段");
  checkCharts(p);
  noHScroll(p, 1440);
});

test("統計頁（假資料）：已完成 > 0、0% 和 100% 的縣市、並列第一、新縣市、新類型都跟著變", async () => {
  const p = await open("fx/stats-changed/stats.html", { width: 1440, height: 900 });
  const all = S.overall(fxMarkets);
  eq(p.text(".st-big"), S.pctText(all, 1), "中間大字照已提交（含已完成）算");
  eq(p.text(".st-sub"), `已提交 ${S.done(all)}／${S.total(all)} 家`, "中間小字");
  ok(!p.$(".st-reviewing"), "已完成 > 0 時「審核中」消失");
  ok(p.$(".st-donut-lg circle.seg-verified"), "大甜甜圈有綠色段");
  eq(p.text(".st-updated"), "資料更新：2026/11/15", "更新日期跟著 meta.json");
  eq(countyRowsShown(p), [["新北市", "100%"], ["臺北市", "100%"], ["高雄市", "60%"], ["花蓮縣", "50%"], ["臺南市", "1%"], ["桃園市", "0%"]], "縣市列數和排序");
  eq(crowns(p), ["新北市", "臺北市"], "並列第一都有皇冠");
  const bars = Object.fromEntries(p.$$(".st-county-list li").map((li) => [li.querySelector(".st-name").textContent, segKeys(li.querySelector(".st-bar"))]));
  eq(bars["桃園市"], ["not_submitted"], "0%：全紅");
  eq(bars["新北市"], ["submitted"], "100%：沒有紅色");
  eq(bars["臺北市"], ["verified", "submitted"], "有已完成：綠色段出現");
  eq(bars["臺南市"], ["verified", "not_submitted"], "1 家已完成也看得見");
  eq(p.$$(".st-type-name").map((s) => s.textContent), ["夜市", "傳統市場", "美食商圈"], "新類型歸到「其他」，沒有多一個");
  ok(p.$$(".st-type-list img")[2].getAttribute("src").endsWith("type-other.webp"), "其他的圖示");
  eq(p.$$(".st-top-name").map((s) => s.textContent), ["測試夜市甲", "測試市場乙", "測試夜市己"], "最強友善力市集：同 100% 照 ID，0% 的不列");
  checkCharts(p);
});

test("統計頁：沒有市場提交時顯示「還沒有市場提交」；沒有資料時顯示空狀態", async () => {
  let p = await open("fx/stats-none/stats.html", { width: 1440, height: 900 });
  eq(p.$$(".st-top-list li").length, 0, "最強友善力市集是空的");
  ok(!p.$(".st-top-empty").hidden, "顯示提示");
  eq(p.text(".st-top-empty"), "還沒有市場提交，一起加油！", "提示文字");
  ok(p.css(".st-megaphone", "display") !== "none", "大聲公貓保留");
  eq(p.text(".st-big"), "0.0%", "中間大字");
  checkCharts(p);

  p = await open("fx/stats-empty/stats.html", { width: 1440, height: 900 });
  ok(p.$(".st-empty"), "空狀態");
  eq(p.$$(".st-card").length, 0, "不畫圖表");
  ok(p.$(".st-empty img").getAttribute("src").endsWith("empty-state.webp"), "空狀態插畫");
});

test("統計頁版面：1440、1280、1024 是 2×2，375 是單欄、手機分頁列、沒有橫向捲軸、貓不擋圖例", async () => {
  for (const [w, h, cols] of [[1440, 900, 2], [1280, 800, 2], [1024, 768, 2], [375, 812, 1]]) {
    const p = await open("web/stats.html", { width: w, height: h });
    const lefts = new Set(p.$$(".st-card").map((c) => Math.round(c.getBoundingClientRect().left)));
    eq(lefts.size, cols, `${w} 寬的欄數`);
    noHScroll(p, w);
    checkCharts(p);
    eq(p.$('.tab[aria-current="page"]')?.textContent.trim(), "統計報表", `${w} 寬：目前的分頁`);
    const legend = p.$(".st-legend").getBoundingClientRect();
    const cat = p.$(".st-cat").getBoundingClientRect();
    ok(cat.bottom <= legend.top || cat.right <= legend.left || cat.left >= legend.right, `${w} 寬：貓擋住圖例`);
  }
  const p = await open("web/stats.html", { width: 375, height: 812 });
  eq(p.doc.body.dataset.layout, "l", "手機版頁首");
  const tabs = p.$$(".tab").map((t) => t.getBoundingClientRect());
  ok(tabs[0].top === tabs[1].top && tabs[0].top >= p.$(".brand").getBoundingClientRect().bottom - 1, "分頁在頁首第二列、兩格同一列");
  ok(p.$$(".st-legend small").every((s) => p.win.getComputedStyle(s).display === "none"), "手機圖例不顯示百分比");
});

test("入口：地圖頁進度卡「看完整統計」和兩頁的分頁都連到統計頁", async () => {
  let p = await open("web/index.html");
  eq(p.$(".progress-more").getAttribute("href"), "stats.html", "進度卡連結");
  eq(p.$$(".tab").map((t) => t.getAttribute("href")), ["./", "stats.html"], "總覽頁分頁");
  p = await open("web/submit.html", { width: 375, height: 812 });
  eq(p.$$(".sp-tab").map((t) => t.getAttribute("href")), ["./", "stats.html"], "補交頁分頁");
  p = await open("web/stats.html");
  eq(p.$$(".tab").map((t) => t.getAttribute("href")), ["./", "stats.html"], "統計頁分頁");
});

// ================= 正式環境（127.0.0.2） =================
const EVERYTHING_OFF = { base: false, labels: false, interact: false, stats: false, list: false, submit: "mock" };

prodTest("總覽頁沒有「開發」按鈕，也不下載 devtools.js；存了「全部關掉」也不生效", async () => {
  const p = await open("web/index.html", { dev: EVERYTHING_OFF });
  ok(!p.$(".dev-fab") && !p.$("#dev-panel"), "不應該有開發按鈕或面板");
  const files = p.win.performance.getEntriesByType("resource").map((e) => e.name);
  ok(!files.some((f) => /devtools\.(js|css)/.test(f)), `不應該下載：${files.filter((f) => /devtools/.test(f)).join("、")}`);
  eq(p.doc.documentElement.dataset.devOff, undefined, "data-dev-off");
  ok(p.css(".progress-card", "display") !== "none", "進度卡照常顯示");
  ok(p.css(".layer-labels", "display") !== "none", "標籤照常顯示");
  ok(!p.$("main.map").inert, "地圖照常可以操作");
  await p.click(p.$$(".county-label")[0]);
  eq(p.$("#county-select").value, counties[0], "點標籤有反應");
});

prodTest("補交頁一律送到正式 API、顯示 Turnstile；存了「模擬送出」或「關閉」也一樣", async () => {
  for (const submit of ["mock", "off"]) {
    const p = await open("web/submit.html", { dev: { ...EVERYTHING_OFF, submit } });
    ok(!p.$(".dev-fab"), "沒有開發按鈕");
    eq(p.$(".sp-mode").dataset.mode, "api", `存了 ${submit} 時的模式`);
    ok(p.$(".sp-mode").hidden, "正式環境不顯示模式說明");
    ok(!p.$(".sp-turnstile").hidden, "顯示 Turnstile");
    ok(!p.$(".sp-submit").disabled, "送出按鈕可以按");
    ok(p.$(".sp-mock").hidden, "沒有模擬紀錄面板");
  }
  setDev(null);
});

// ================= 執行 =================
const list = document.getElementById("results");

function show(r) {
  const li = document.createElement("li");
  li.textContent = r.name;
  li.className = r.skip ? "" : r.ok ? "pass" : "fail";
  if (r.error || r.skip) {
    const pre = document.createElement("pre");
    pre.textContent = r.error || `跳過：${r.skip}`;
    li.append(pre);
  }
  if (r.ms !== undefined) li.insertAdjacentHTML("beforeend", ` <small>${r.ms}ms</small>`);
  list.append(li);
}

for (const t of tests) {
  const t0 = performance.now();
  const r = { name: t.name, ok: true };
  try {
    await t.fn();
  } catch (err) {
    Object.assign(r, { ok: false, error: err.message });
  }
  r.ms = Math.round(performance.now() - t0);
  results.push(r);
  show(r);
}
setDev(null);
stage.replaceChildren();

// 開發環境跑完後，到 127.0.0.2（正式環境）跑 prodTest，結果用 postMessage 傳回來
if (IS_DEV && !EMBEDDED) {
  const prodUrl = `http://127.0.0.2:${Number(location.port || 80) + 1}/?embedded`;
  const prod = await new Promise((resolve) => {
    const frame = document.createElement("iframe");
    const timer = setTimeout(() => resolve(null), 30000);
    window.addEventListener("message", (e) => {
      if (e.origin === new URL(prodUrl).origin && e.data?.testResults) {
        clearTimeout(timer);
        resolve(e.data.testResults);
      }
    });
    frame.src = prodUrl;
    stage.append(frame);
  });
  stage.replaceChildren();
  if (prod) for (const r of prod.results) { results.push(r); show(r); }
  else {
    const r = { name: "正式環境（127.0.0.2）的測試", ok: true, skip: `連不到 ${prodUrl}，請用 python tests/serve_tests.py 啟動` };
    results.push(r);
    show(r);
  }
}

const failed = results.filter((r) => !r.ok).length;
const skipped = results.filter((r) => r.skip).length;
const passed = results.length - failed - skipped;
const summary = document.getElementById("summary");
summary.textContent = failed ? `${failed} / ${results.length} 項失敗`
  : `${passed} 項全部通過${skipped ? `（${skipped} 項跳過）` : ""}`;
summary.className = failed ? "bad" : "ok";
window.testResults = { done: true, passed, failed, skipped, results };
if (EMBEDDED) parent.postMessage({ testResults: window.testResults }, "*");
