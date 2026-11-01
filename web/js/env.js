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

// 補交頁的送出方式：開發環境照開關（預設模擬）；正式環境在任務 12 建好後端前一律關閉
export function submitMode() {
  const dev = readDev();
  if (!dev) return "off";
  return SUBMIT_MODES.includes(dev.submit) ? dev.submit : "mock";
}
