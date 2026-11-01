// 補交紀錄的格式（docs/PLAN.md §5）。補交頁（模擬送出）和後端（server/submission.js）共用。

export const DEDUPE_MS = 24 * 3600 * 1000;   // 同一攤商、同一網址 24 小時內只收一次
export const HOURLY_LIMIT = 10;              // 同一 IP 每小時上限
export const CSV_COLUMNS = [
  "submitted_at", "ip", "county", "market_id", "market_name", "vendor_id", "vendor_name",
  "action", "url", "place_key", "status_before", "review_result", "reviewed_at", "note",
];

export function taipeiTime(date = new Date()) {
  return new Date(date.getTime() + 8 * 3600 * 1000).toISOString().slice(0, 19) + "+08:00";
}

export function buildRecord({ vendor, market, action, url, placeKey, ip = "", now = new Date() }) {
  return {
    submitted_at: taipeiTime(now),
    ip,
    county: market.county,
    market_id: market.id,
    market_name: market.name,
    vendor_id: vendor.id,
    vendor_name: vendor.name,
    action,
    url,
    place_key: placeKey,
    status_before: vendor.status,
    review_result: "",
    reviewed_at: "",
    note: "",
  };
}

export function toCSV(records) {
  const cell = (v) => (/[",\n]/.test(String(v)) ? `"${String(v).replace(/"/g, '""')}"` : String(v));
  return [CSV_COLUMNS.join(","), ...records.map((r) => CSV_COLUMNS.map((c) => cell(r[c] ?? "")).join(","))].join("\r\n") + "\r\n";
}
