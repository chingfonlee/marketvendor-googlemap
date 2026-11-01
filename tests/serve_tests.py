"""瀏覽器測試：python tests/serve_tests.py [port]，預設 8766，打開 http://localhost:8766/ 會自動跑。

  /            測試頁（tests/browser/）
  /web/…       正式網頁和正式資料（web/）
  /fx/<名稱>/…  同一份網頁，但 data/*.json 換成 tests/fixtures/<名稱>/（邊界案例用）
  /api/…       假的補交 API（開發開關選「正式 API」時用），見 FakeApi

另外在 http://127.0.0.2:<port+1>/ 開同一個伺服器：127.0.0.2 不是開發網址（web/js/env.js），
網頁會當成正式環境，用來測「正式環境無法開啟開發開關」。兩個都只聽本機，不對外。
不讓瀏覽器快取，改了 JS 重新整理就會重跑。
"""
import json
import sys
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "web"
BROWSER = ROOT / "tests" / "browser"
FIXTURES = ROOT / "tests" / "fixtures"


class FakeApi:
    """POST /api/submissions 收下紀錄；GET /api/_received 取回收到的；POST /api/_fail 讓下一次送出失敗。"""
    received = []
    fail_next = False


class TestHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        parts = unquote(urlsplit(path).path).lstrip("/").split("/")
        if parts[0] == "web":
            base, rest = WEB, parts[1:]
        elif parts[0] == "fx" and len(parts) >= 3:
            fixture = FIXTURES / parts[1]
            rest = parts[2:]
            base = fixture if rest[0] == "data" and len(rest) == 2 else WEB
            if base is fixture:
                rest = rest[1:]
        else:
            base, rest = BROWSER, parts
        target = base.joinpath(*[p for p in rest if p not in ("", ".", "..")])
        return str(target)

    def send_json(self, status, body):
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if urlsplit(self.path).path == "/api/_received":
            return self.send_json(200, FakeApi.received)
        return super().do_GET()

    def do_POST(self):
        path = urlsplit(self.path).path
        body = self.rfile.read(int(self.headers.get("Content-Length") or 0))
        if path == "/api/_reset":
            FakeApi.received, FakeApi.fail_next = [], False
            return self.send_json(200, {"ok": True})
        if path == "/api/_fail":
            FakeApi.fail_next = True
            return self.send_json(200, {"ok": True})
        if path == "/api/submissions":
            if FakeApi.fail_next:
                FakeApi.fail_next = False
                return self.send_json(500, {"ok": False})
            FakeApi.received.append(json.loads(body or b"{}"))
            return self.send_json(201, {"ok": True})
        self.send_error(404)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *args):
        pass


def serve(host, port):
    server = ThreadingHTTPServer((host, port), partial(TestHandler, directory=str(BROWSER)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8766
    serve("127.0.0.1", port)
    print(f"開發環境：http://localhost:{port}/")
    try:
        serve("127.0.0.2", port + 1)
        print(f"正式環境：http://127.0.0.2:{port + 1}/")
    except OSError as err:
        print(f"127.0.0.2 開不起來，正式環境的瀏覽器測試會跳過：{err}")
    threading.Event().wait()
