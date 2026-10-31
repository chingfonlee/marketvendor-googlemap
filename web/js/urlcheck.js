// Google 地圖網址的格式檢查，規則和 scripts/import_excel.py 的 check_url 相同，
// 另外接受 google.com.tw 和短網址（短網址離線解析不出地點，留給人工確認時展開）。

export const MAX_URL_LENGTH = 2048;

// 從貼上的文字取出第一個網址（手機「分享」常會帶店名：「春和油飯 https://maps.app.goo.gl/…」）
export function extractUrl(text) {
  const m = String(text || "").match(/https?:\/\/[^\s<>"'，。、）)]+/i);
  return m ? m[0] : String(text || "").trim();
}

const SHORT_HOSTS = ["maps.app.goo.gl", "goo.gl"];
const GOOGLE_HOSTS = ["www.google.com", "google.com", "www.google.com.tw", "google.com.tw"];

function isMapsHost(host, path) {
  if (host === "maps.google.com" || host === "maps.google.com.tw" || host === "maps.app.goo.gl") return true;
  if (GOOGLE_HOSTS.includes(host)) return path.startsWith("/maps");
  if (host === "goo.gl") return path.startsWith("/maps");
  return false;
}

// 回傳 { ok, url, placeKey, short, error }。placeKey 是「cid:…」或「place_id:…」，短網址是空字串。
export function checkUrl(input) {
  const url = extractUrl(input);
  if (!url) return { ok: false, url, error: "請貼上 Google 地圖網址" };
  if (url.length > MAX_URL_LENGTH) return { ok: false, url, error: "網址太長，請改用 Google 地圖「分享」產生的連結" };
  let u;
  try {
    u = new URL(url);
  } catch {
    return { ok: false, url, error: "這不是有效的網址" };
  }
  if (u.protocol !== "http:" && u.protocol !== "https:") return { ok: false, url, error: "這不是有效的網址" };
  const host = u.hostname.toLowerCase();
  if (!isMapsHost(host, u.pathname)) return { ok: false, url, error: "網址不是 Google 地圖的連結" };
  if (SHORT_HOSTS.includes(host)) {
    if (u.pathname.length <= 1 || u.pathname === "/maps" || u.pathname === "/maps/") {
      return { ok: false, url, error: "短網址不完整，請重新複製" };
    }
    return { ok: true, url, placeKey: "", short: true };
  }
  const cid = u.searchParams.get("cid");
  if (cid && /^\d+$/.test(cid)) return { ok: true, url, placeKey: `cid:${cid}` };
  for (const k of ["place_id", "query_place_id"]) {
    const v = u.searchParams.get(k);
    if (v) return { ok: true, url, placeKey: `place_id:${v}` };
  }
  // 長網址裡的 !1s0x…:0x…，後半段就是 cid
  const m = url.match(/!1s0x[0-9a-f]+:0x([0-9a-f]+)/i);
  if (m) return { ok: true, url, placeKey: `cid:${BigInt("0x" + m[1]).toString()}` };
  return { ok: false, url, error: "這個網址找不到店家。請在 Google 地圖點開你的店，按「分享」再複製連結" };
}
