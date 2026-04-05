import os
import requests
from http.server import BaseHTTPRequestHandler

API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")


class handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"ok":true}')

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)

        if not API_KEY:
            self._respond(500, b'{"error":{"message":"API key not configured on server."}}')
            return

        try:
            resp = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": API_KEY,
                    "anthropic-version": "2023-06-01",
                },
                data=body,
                timeout=30,
            )
            self._respond(resp.status_code, resp.content)
        except Exception as e:
            self._respond(500, f'{{"error":{{"message":"Proxy error: {e}"}}}}'.encode())

    def _respond(self, status, body):
        self.send_response(status)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
