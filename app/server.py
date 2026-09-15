from __future__ import annotations

import argparse
import json
import mimetypes
import secrets
import socket
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from recovered.main import run

WEB_ROOT = Path(__file__).with_name("web")


def _lan_ip() -> str:
    """Return the LAN address used to reach this laptop from a phone."""
    probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        probe.connect(("8.8.8.8", 80))
        return str(probe.getsockname()[0])
    except OSError:
        return socket.gethostbyname(socket.gethostname())
    finally:
        probe.close()


class NovaixHandler(BaseHTTPRequestHandler):
    server_version = "NOVAIX/1.2"

    def _authorized(self) -> bool:
        query = parse_qs(urlparse(self.path).query)
        token = self.headers.get("X-NOVAIX-Token") or query.get("token", [""])[0]
        return secrets.compare_digest(token, self.server.access_token)  # type: ignore[attr-defined]

    def _json(self, value: object, status: int = 200) -> None:
        body = json.dumps(value, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            self._json({"status": "ok", "name": "NOVAIX AI App Builder", "version": "1.2.0"})
            return
        if parsed.path.startswith("/download/"):
            if not self._authorized():
                self._json({"error": "Unauthorized"}, HTTPStatus.UNAUTHORIZED)
                return
            name = Path(parsed.path.removeprefix("/download/")).name
            target = (Path("generated_apps") / name).resolve()
            allowed = Path("generated_apps").resolve()
            if allowed not in target.parents or not target.is_file() or target.suffix != ".zip":
                self._json({"error": "File not found"}, HTTPStatus.NOT_FOUND)
                return
            body = target.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "application/zip")
            self.send_header("Content-Disposition", f'attachment; filename="{target.name}"')
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        relative = "index.html" if parsed.path == "/" else parsed.path.lstrip("/")
        target = (WEB_ROOT / relative).resolve()
        if WEB_ROOT.resolve() not in target.parents or not target.is_file():
            self.send_error(404)
            return
        body = target.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", mimetypes.guess_type(target.name)[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:  # noqa: N802
        if urlparse(self.path).path != "/api/build":
            self.send_error(404)
            return
        if not self._authorized():
            self._json({"error": "Unauthorized"}, HTTPStatus.UNAUTHORIZED)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 100_000:
                raise ValueError("Request must be between 1 and 100000 bytes")
            payload = json.loads(self.rfile.read(length).decode())
            name = str(payload.get("name", "")).strip()
            instruction = str(payload.get("instruction", "")).strip()
            result = run(name, instruction)
            release = result["stages"][-1]["output"]
            archive = Path(release["artifacts"][1])
            result["download_url"] = f"/download/{archive.name}"
            self._json(result)
        except (ValueError, KeyError, json.JSONDecodeError) as exc:
            self._json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
        except Exception as exc:
            self._json({"error": f"Build failed: {exc}"}, HTTPStatus.INTERNAL_SERVER_ERROR)

    def log_message(self, format: str, *args: object) -> None:
        print(f"NOVAIX: {format % args}")


def serve(host: str = "127.0.0.1", port: int = 8765, token: str | None = None) -> None:
    server = ThreadingHTTPServer((host, port), NovaixHandler)
    server.access_token = token or secrets.token_urlsafe(18)  # type: ignore[attr-defined]
    shown_host = "localhost" if host == "127.0.0.1" else _lan_ip()
    url = f"http://{shown_host}:{port}/?token={server.access_token}"  # type: ignore[attr-defined]
    print(f"NOVAIX ready: {url}")
    if host == "127.0.0.1":
        webbrowser.open(url)
    server.serve_forever()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the NOVAIX App Builder dashboard")
    parser.add_argument("--host", default="127.0.0.1", help="Use 0.0.0.0 for phone access on the same Wi-Fi")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--token")
    args = parser.parse_args()
    serve(args.host, args.port, args.token)


if __name__ == "__main__":
    main()
