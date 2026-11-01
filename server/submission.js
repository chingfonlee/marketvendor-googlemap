// 補交紀錄的後端檢查和寫入（docs/PLAN.md §5、任務 12）。functions/api/submissions.js 呼叫這裡；
// 不碰 Cloudflare 的全域物件，測試時可以直接傳入假的 D1 和 Turnstile。
//
// 原則：
// - 只相信攤商代號、操作、網址三個欄位；縣市、市場、店名、送出前狀態一律由伺服器從公開資料填。
// - 只新增待處理紀錄，不改公開資料；人工處理欄（review_result 等）送出時一律空白。

import { checkUrl } from "../web/js/urlcheck.js";
import { DEDUPE_MS, HOURLY_LIMIT, buildRecord } from "../web/js/record.js";

export const MAX_BODY = 8 * 1024;
const ACTIONS = ["confirm", "update"];

const fail = (status, error) => ({ status, body: { ok: false, error } });

// D1 的 SQL：防重複和每小時上限都用 submitted_ms 查，送出時間的文字（台北時間）只給人看和匯出用
const SQL = {
  dupe: "SELECT 1 FROM submissions WHERE vendor_id = ? AND url = ? AND submitted_ms > ? LIMIT 1",
  hourly: "SELECT COUNT(*) AS n FROM submissions WHERE ip = ? AND submitted_ms > ?",
  insert: `INSERT INTO submissions (submitted_at, submitted_ms, ip, county, market_id, market_name, vendor_id,
    vendor_name, action, url, place_key, status_before) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
};

// 回傳 { status, body }，body 是 { ok, error? }
export async function handleSubmission({ text, ip, token, now = new Date(), db, vendors, markets, verifyTurnstile }) {
  if (text.length > MAX_BODY) return fail(413, "送出的資料太大。");
  let input;
  try {
    input = JSON.parse(text);
  } catch {
    return fail(400, "送出的資料格式不對，請重新整理頁面再試。");
  }
  if (!input || typeof input !== "object") return fail(400, "送出的資料格式不對，請重新整理頁面再試。");

  const vendor = vendors.find((v) => v.id === input.vendor_id);
  const market = vendor && markets.find((m) => m.id === vendor.market_id);
  if (!vendor || !market) return fail(400, "找不到這家攤商，請重新整理頁面再選一次。");
  if (!ACTIONS.includes(input.action)) return fail(400, "請選一個操作：「這是我的店」或貼上正確的網址。");

  let url, placeKey;
  if (input.action === "confirm") {
    if (!vendor.url) return fail(400, "這家店目前沒有連結，不能確認，請改貼正確的網址。");
    if (vendor.status === "verified") return fail(400, "這家店已經確認完成，不用再確認。");
    url = vendor.url;
    placeKey = checkUrl(vendor.url).placeKey || "";
  } else {
    const check = checkUrl(typeof input.url === "string" ? input.url : "");
    if (!check.ok) return fail(400, check.error);
    const current = vendor.url ? checkUrl(vendor.url) : null;
    if (current?.ok && check.placeKey && current.placeKey === check.placeKey) {
      return fail(400, vendor.status === "verified" ? "和目前已確認的連結是同一家店，不用補交。" : "和目前的連結是同一家店，請改選「這是我的店」。");
    }
    url = check.url;
    placeKey = check.placeKey;
  }

  if (!token) return fail(400, "請先完成「確認你不是機器人」的驗證。");
  if (!(await verifyTurnstile(token, ip))) return fail(403, "驗證沒有通過，請重新驗證後再送出。");

  const ms = now.getTime();
  if (await db.prepare(SQL.dupe).bind(vendor.id, url, ms - DEDUPE_MS).first()) {
    return fail(409, "這家店的這個網址 24 小時內已經送過了，不用再送。");
  }
  const { n } = await db.prepare(SQL.hourly).bind(ip, ms - 3600 * 1000).first();
  if (n >= HOURLY_LIMIT) return fail(429, "送出次數太多，請一小時後再試。");

  const r = buildRecord({ vendor, market, action: input.action, url, placeKey, ip, now });
  await db.prepare(SQL.insert).bind(r.submitted_at, ms, r.ip, r.county, r.market_id, r.market_name, r.vendor_id,
    r.vendor_name, r.action, r.url, r.place_key, r.status_before).run();
  return { status: 201, body: { ok: true } };
}

// Cloudflare Turnstile 的伺服器端驗證
export async function siteverify(secret, token, ip, fetchImpl = fetch) {
  const form = new FormData();
  form.append("secret", secret);
  form.append("response", token);
  if (ip) form.append("remoteip", ip);
  try {
    const res = await fetchImpl("https://challenges.cloudflare.com/turnstile/v0/siteverify", { method: "POST", body: form });
    return (await res.json()).success === true;
  } catch {
    return false;
  }
}
