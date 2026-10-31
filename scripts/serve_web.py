"""本機預覽 web/：python scripts/serve_web.py [port]，預設 8765。

和 python -m http.server 一樣，但不讓瀏覽器快取，改了 CSS／JS 重新整理就看得到。
"""
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

WEB = Path(__file__).resolve().parent.parent / "web"


class NoCacheHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    server = ThreadingHTTPServer(("127.0.0.1", port), partial(NoCacheHandler, directory=str(WEB)))
    print(f"http://localhost:{port}/")
    server.serve_forever()
