// 判斷開發環境，讀開發開關的設定（任務 9）。正式環境一律回傳預設值，開發開關不會生效。
// 開關的畫面在 devtools.js，只在開發環境載入。

export const IS_DEV = /^(localhost|127\.0\.0\.1|\[::1\])$|\.localhost$|\.test$/.test(location.hostname);

export const DEV_KEY = "gm-dev";
export const SUBMIT_MODES = ["mock", "api", "off"];
export const DEV_DEFAULTS = {
  base: true, labels: true, interact: true, stats: true, list: true,
  submit: "mock",
};

export function readDev() {
  if (!IS_DEV) return null;
  try {
    return { ...DEV_DEFAULTS, ...JSON.parse(localStorage.getItem(DEV_KEY)) };
  } catch {
    return { ...DEV_DEFAULTS };
  }
}

export function writeDev(settings) {
  try {
    localStorage.setItem(DEV_KEY, JSON.stringify(settings));
  } catch { /* 無痕視窗等情況存不了，只影響這次 */ }
}

// 只在開發環境呼叫；開關載入失敗不影響頁面本身
export async function loadDevtools(page) {
  try {
    const { initDevtools } = await import("./devtools.js");
    initDevtools(page);
  } catch (err) {
    console.error("開發開關載入失敗", err);
  }
}

// Turnstile（防機器人）的網站金鑰，公開的、不是秘密。開發環境用 Cloudflare 的測試金鑰（永遠通過）；
// 正式金鑰是 Cloudflare 的「台灣攤商地圖 補交頁」小工具，只接受 googlemap-store.pages.dev（docs/BACKEND.md）。
export const TURNSTILE_TEST_KEY = "1x00000000000000000000AA";
export const TURNSTILE_PROD_KEY = "0x4AAAAAAFuufVJfrbnLdIh_";
export const TURNSTILE_SITE_KEY = IS_DEV ? TURNSTILE_TEST_KEY : TURNSTILE_PROD_KEY;

// 補交頁的送出方式：開發環境照開關（預設模擬）；正式環境一律送到 API（任務 12），沒有 Turnstile 金鑰時關閉
export function submitMode() {
  const dev = readDev();
  if (!dev) return TURNSTILE_SITE_KEY ? "api" : "off";
  return SUBMIT_MODES.includes(dev.submit) ? dev.submit : "mock";
}
