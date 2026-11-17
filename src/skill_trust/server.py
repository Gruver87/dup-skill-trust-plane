"""Minimal self-host HTTP API (stdlib) — local trust plane."""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from skill_trust import __version__
from skill_trust.pipeline import verify_pack, write_cards


def serve(host: str | None = None, port: int | None = None) -> None:
    host = host or os.environ.get("TRUST_BIND") or "127.0.0.1"
    port = int(port or os.environ.get("TRUST_PORT") or 8788)
    cards_dir = Path(os.environ.get("TRUST_CARDS_DIR") or "cards")

    class Handler(BaseHTTPRequestHandler):
        def _json(self, code: int, body: dict) -> None:
            raw = json.dumps(body, ensure_ascii=False, default=str).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def do_GET(self) -> None:  # noqa: N802
            path = urlparse(self.path).path
            if path in {"/", "/v1/health", "/health"}:
                self._json(
                    200,
                    {
                        "ok": True,
                        "product": "dup-skill-trust-plane",
                        "version": __version__,
                        "note": "trust plane — not a marketplace",
                    },
                )
                return
            self._json(404, {"ok": False, "error": "not found"})

        def do_POST(self) -> None:  # noqa: N802
            path = urlparse(self.path).path
            length = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(length) if length else b"{}"
            try:
                data = json.loads(raw.decode("utf-8") or "{}")
            except json.JSONDecodeError:
                self._json(400, {"ok": False, "error": "invalid json"})
                return
            if path != "/v1/verify":
                self._json(404, {"ok": False, "error": "not found"})
                return
            pack = data.get("pack_root")
            if not pack:
                self._json(400, {"ok": False, "error": "pack_root required"})
                return
            source = data.get("source") or "Gruver87/dup-agent-skills"
            report = verify_pack(Path(pack), source=source)
            if data.get("write_cards"):
                write_cards(report, cards_dir)
            self._json(200 if report.ok else 422, report.to_dict())

        def log_message(self, fmt: str, *args) -> None:
            sys_stderr = __import__("sys").stderr
            sys_stderr.write("trust_api: " + (fmt % args) + "\n")

    httpd = ThreadingHTTPServer((host, port), Handler)
    print(f"dup-skill-trust serve http://{host}:{port}  (POST /v1/verify)")
    httpd.serve_forever()
