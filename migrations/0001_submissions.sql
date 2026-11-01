-- 補交紀錄（docs/PLAN.md §5）。只由 /api/submissions 新增；人工處理後填 review_result、reviewed_at、note。
CREATE TABLE submissions (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  submitted_at  TEXT    NOT NULL,              -- 台北時間，2026-11-01T09:00:00+08:00
  submitted_ms  INTEGER NOT NULL,              -- 同一時間的毫秒數，查 24 小時、1 小時用
  ip            TEXT    NOT NULL,
  county        TEXT    NOT NULL,
  market_id     TEXT    NOT NULL,
  market_name   TEXT    NOT NULL,
  vendor_id     TEXT    NOT NULL,
  vendor_name   TEXT    NOT NULL,
  action        TEXT    NOT NULL CHECK (action IN ('confirm', 'update')),
  url           TEXT    NOT NULL,
  place_key     TEXT    NOT NULL DEFAULT '',
  status_before TEXT    NOT NULL,
  review_result TEXT    NOT NULL DEFAULT '',
  reviewed_at   TEXT    NOT NULL DEFAULT '',
  note          TEXT    NOT NULL DEFAULT ''
);
CREATE INDEX submissions_vendor_url ON submissions (vendor_id, url, submitted_ms);
CREATE INDEX submissions_ip ON submissions (ip, submitted_ms);
