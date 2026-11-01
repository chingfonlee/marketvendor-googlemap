"""瀏覽器測試：python tests/serve_tests.py [port]，預設 8766，打開 http://localhost:8766/ 會自動跑。

  /            測試頁（tests/browser/）
  /web/…       正式網頁和正式資料（web/）
  /fx/<名稱>/…  同一份網頁，但 data/*.json 換成 tests/fixtures/<名稱>/（邊界案例用）

只在本機用，不部署。不讓瀏覽器快取，改了 JS 重新整理就會重跑。
"""
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "web"
BROWSER = ROOT / "tests" / "browser"
FIXTURES = ROOT / "tests" / "fixtures"


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

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8766
    server = ThreadingHTTPServer(("127.0.0.1", port), partial(TestHandler, directory=str(BROWSER)))
    print(f"http://localhost:{port}/")
    server.serve_forever()
