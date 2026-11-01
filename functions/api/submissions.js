// POST /api/submissions：補交頁送出的紀錄存進 D1（任務 12）。檢查規則在 server/submission.js。
// 設定：D1 綁定 DB（wrangler.toml）、Turnstile 金鑰 TURNSTILE_SECRET（本機放 .dev.vars，正式用 wrangler pages secret）。

import { handleSubmission, siteverify } from "../../server/submission.js";

// 攤商和市場資料跟著網頁一起部署，同一個版本裡不會變，讀一次就留著
let cache = null;
async function loadData(env, request) {
  if (!cache) {
    const get = async (name) => (await env.ASSETS.fetch(new URL(`/data/${name}.json`, request.url))).json();
    cache = Promise.all([get("vendors"), get("markets")]).catch((err) => {
      cache = null;
      throw err;
    });
  }
  const [vendors, markets] = await cache;
  return { vendors, markets };
}

const json = (status, body) =>
  new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store" } });

// 只收 POST；GET 等其他方法不回網頁，直接 405（紀錄不能從網路上讀）
export const onRequestGet = () => json(405, { ok: false, error: "只接受 POST。" });

export async function onRequestPost({ request, env }) {
  if (!env.TURNSTILE_SECRET) return json(503, { ok: false, error: "補交功能還在準備中，暫時無法送出。" });
  try {
    const { vendors, markets } = await loadData(env, request);
    const { status, body } = await handleSubmission({
      text: await request.text(),
      ip: request.headers.get("CF-Connecting-IP") || "",
      token: request.headers.get("X-Turnstile-Token") || "",
      db: env.DB,
      vendors,
      markets,
      verifyTurnstile: (token, ip) => siteverify(env.TURNSTILE_SECRET, token, ip),
    });
    return json(status, body);
  } catch (err) {
    console.error(err);
    return json(500, { ok: false, error: "伺服器發生錯誤，請稍後再試。" });
  }
}
