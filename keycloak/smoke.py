# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""The demo realm was imported: discovery document, real password-grant and client-credentials tokens, health."""
import urllib.parse

import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import expect, http, port, run, step  # noqa: E402


def main() -> None:
    base = f"http://localhost:{port('KEYCLOAK_PORT', 8080)}"
    token_url = f"{base}/realms/demo/protocol/openid-connect/token"
    form = {"Content-Type": "application/x-www-form-urlencoded"}

    step("discovery document")
    expect("issuer" in http(f"{base}/realms/demo/.well-known/openid-configuration").json(), "no issuer in discovery document")

    step("password grant (public client demo-app)")
    body = urllib.parse.urlencode({"grant_type": "password", "client_id": "demo-app", "username": "demo", "password": "demo"})
    expect("access_token" in http(token_url, "POST", data=body, headers=form).json(), "no access_token (password grant)")

    step("client-credentials grant (confidential client demo-backend)")
    body = urllib.parse.urlencode({"grant_type": "client_credentials", "client_id": "demo-backend",
                                   "client_secret": "demo-backend-secret"})
    expect("access_token" in http(token_url, "POST", data=body, headers=form).json(), "no access_token (client credentials)")

    step("management health")
    http(f"http://localhost:{port('KEYCLOAK_MANAGEMENT_PORT', 9000)}/health/ready")


run(main)
