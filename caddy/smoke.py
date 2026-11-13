# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Automatic local HTTPS: proxy + static + health over TLS (SNI without DNS), local-CA issuer, HTTP->HTTPS redirect.

Connects to 127.0.0.1 but sends the site name as TLS SNI / Host header, so it does not depend on the OS
resolving *.localhost (Windows may not)."""
import http.client
import socket
import ssl

import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import env, expect, port, retry, run, step  # noqa: E402

HOST = env("CADDY_SITE", "app.localhost")
HTTPS = port("CADDY_HTTPS_PORT", 8443)
HTTP = port("CADDY_HTTP_PORT", 8080)


class SniConnection(http.client.HTTPSConnection):
    """HTTPS to 127.0.0.1:<port> with ``HOST`` as the SNI name; certificate is NOT verified (Caddy's local CA)."""

    def __init__(self, port: int) -> None:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        super().__init__("127.0.0.1", port, context=ctx, timeout=15)

    def connect(self) -> None:
        sock = socket.create_connection(("127.0.0.1", self.port), timeout=15)
        self.sock = self._context.wrap_socket(sock, server_hostname=HOST)


def https_get(path: str) -> tuple[int, str, bytes]:
    c = SniConnection(HTTPS)
    try:
        c.request("GET", path, headers={"Host": f"{HOST}:{HTTPS}"})
        r = c.getresponse()
        body = r.read().decode("utf-8", "replace")
        cert = c.sock.getpeercert(binary_form=True) or b""
        return r.status, body, cert
    finally:
        c.close()


def main() -> None:
    step("health over HTTPS")
    status, body, cert = retry(lambda: https_get("/healthz"), timeout=60, interval=2, desc="Caddy HTTPS")
    expect(status == 200 and body.startswith("ok"), f"/healthz -> {status} {body!r}")

    step("static files + reverse proxy")
    status, body, _ = https_get("/static/")
    expect(status == 200 and "Served by Caddy" in body, f"/static/ -> {status}")
    status, body, _ = https_get("/")
    expect(status == 200 and "Hostname:" in body, f"/ (proxy) -> {status}")

    step("certificate issued by Caddy's local CA")
    expect(b"Caddy Local Authority" in cert, "issuer is not 'Caddy Local Authority'")

    step("HTTP redirects to HTTPS")
    c = http.client.HTTPConnection("127.0.0.1", HTTP, timeout=15)
    c.request("GET", "/", headers={"Host": f"{HOST}:{HTTP}"})
    r = c.getresponse()
    r.read()
    loc = r.getheader("Location", "")
    expect(r.status in (301, 302, 307, 308) and loc.lower().startswith("https://"), f"no redirect: {r.status} {loc!r}")


run(main)
