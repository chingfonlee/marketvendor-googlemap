// 在真的瀏覽器裡開網頁（iframe），照使用者的操作點選，檢查畫面。由 tests/serve_tests.py 提供。
// 結果顯示在頁面上，也放在 window.testResults（給自動化工具讀）。

const stage = document.getElementById("stage");
const results = [];
const tests = [];
const test = (name, fn) => tests.push({ name, fn });

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

// 開一頁：寬高決定 D／L 版（iframe 的 media query 看的是 iframe 自己的大小）
async function open(url, { width = 1280, height = 800, beforeLoad } = {}) {
  stage.replaceChildren();
  const frame = document.createElement("iframe");
  frame.width = width;
  frame.height = height;
  stage.append(frame);
  if (beforeLoad) beforeLoad();
  frame.src = url;
  await new Promise((r) => frame.addEventListener("load", r, { once: true }));
  const win = frame.contentWindow;
  const doc = frame.contentDocument;
  await until(() => !doc.body.hasAttribute("data-loading"), "頁面載入完成");
  await sleep(50);
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
  return { win, doc, $, $$, text, choose, click, type };
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
    eq(shown.map((s) => s.textContent), ["我是攤商，補交 Google 地圖連結"], `${w} 寬的按鈕文字`);
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
  ok(p.text(".progress-legend .total").includes("100%"), `完成率：${p.text(".progress-legend .total")}`);
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
  ok(p.text(".progress-legend .total").includes("0%"), `完成率：${p.text(".progress-legend .total")}`);
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

// ================= 執行 =================
const list = document.getElementById("results");
for (const t of tests) {
  const li = document.createElement("li");
  li.textContent = t.name;
  list.append(li);
  const t0 = performance.now();
  try {
    await t.fn();
    li.className = "pass";
    results.push({ name: t.name, ok: true });
  } catch (err) {
    li.className = "fail";
    const pre = document.createElement("pre");
    pre.textContent = err.message;
    li.append(pre);
    results.push({ name: t.name, ok: false, error: err.message });
  }
  li.insertAdjacentHTML("beforeend", ` <small>${Math.round(performance.now() - t0)}ms</small>`);
}
stage.replaceChildren();
const failed = results.filter((r) => !r.ok).length;
const summary = document.getElementById("summary");
summary.textContent = failed ? `${failed} / ${results.length} 項失敗` : `${results.length} 項全部通過`;
summary.className = failed ? "bad" : "ok";
window.testResults = { done: true, passed: results.length - failed, failed, results };
