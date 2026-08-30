from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from rackshift.actions import apply_remediation, apply_vendor_revision
from rackshift.remediate import remediations
from rackshift.serialize import report_to_dict
from rackshift.store import repo_root
from rackshift.validate import validate

HOST = "127.0.0.1"
PORT = 8787


def state_payload() -> dict:
    report = validate()
    return report_to_dict(report, remediations(report))


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:
        sys_stderr = __import__("sys").stderr
        sys_stderr.write("%s - %s\n" % (self.address_string(), format % args))

    def _send(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, code: int, payload: dict) -> None:
        self._send(code, json.dumps(payload).encode(), "application/json")

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path in {"/", "/index.html"}:
            ui = repo_root() / "ui" / "index.html"
            self._send(200, ui.read_bytes(), "text/html; charset=utf-8")
            return
        if path == "/api/state":
            self._send_json(200, state_payload())
            return
        self._send_json(404, {"error": "not found"})

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw.decode() or "{}")
        except json.JSONDecodeError:
            self._send_json(400, {"error": "invalid json"})
            return
        try:
            if path == "/api/revise":
                apply_vendor_revision()
                self._send_json(200, state_payload())
                return
            if path == "/api/apply":
                option_id = str(body.get("option_id") or "")
                apply_remediation(option_id)
                self._send_json(200, state_payload())
                return
        except (ValueError, FileNotFoundError, KeyError) as exc:
            self._send_json(400, {"error": str(exc)})
            return
        self._send_json(404, {"error": "not found"})


def serve(host: str = HOST, port: int = PORT) -> None:
    root = repo_root()
    httpd = ThreadingHTTPServer((host, port), Handler)
    print(f"RackShift UI http://{host}:{port}  repo={root}", flush=True)
    httpd.serve_forever()
