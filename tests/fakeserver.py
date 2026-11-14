"""Servidor HTTP falso para testes: responde em fila com (status, corpo, content-type)."""
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer


class FakeServer:
    def __init__(self, responses):
        self.responses = list(responses)
        self.requests = []  # (path, headers, body_json_or_bytes)
        outer = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def _handle(self):
                n = int(self.headers.get("Content-Length") or 0)
                raw = self.rfile.read(n) if n else b""
                try:
                    body = json.loads(raw) if raw else None
                except ValueError:
                    body = raw
                outer.requests.append((self.path, dict(self.headers), body))
                status, payload, ctype = outer.responses.pop(0)
                data = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
                self.send_response(status)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            do_POST = _handle
            do_GET = _handle

        self.httpd = HTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.httpd.server_port}"
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()

    def close(self):
        self.httpd.shutdown()
        self.httpd.server_close()


def chat_reply(content: str, tin=10, tout=20):
    return (200, {"choices": [{"message": {"content": content}}],
                  "usage": {"prompt_tokens": tin, "completion_tokens": tout}}, "application/json")
