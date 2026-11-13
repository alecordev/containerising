# Keycloak

Keycloak `26.8.2` (`start-dev`) on PostgreSQL 18, with a demo realm imported at startup. Local development only: plain HTTP, dev cache, bootstrap admin.

## Run

```bash
# Optional: copy .env.example to .env to override defaults
docker compose up -d --wait   # first start takes ~30-60 s (realm import + DB migration)
docker compose down           # add -v to delete the database
```

| What | Where |
|---|---|
| Admin console | http://localhost:8080/admin (`admin` / `admin`) |
| Demo realm account console | http://localhost:8080/realms/demo/account |
| Health (management port) | http://localhost:9000/health/ready · `/health/live` · `/metrics` |

## Demo realm (`realm/demo-realm.json`)

Imported with `--import-realm` only when the realm does not exist yet. To re-import after editing the JSON: `docker compose down -v && docker compose up -d --wait`.

| Item | Value |
|---|---|
| Realm | `demo` |
| User | `demo` / `demo` (email `demo@example.com`, realm role `app-user`) |
| Public client | `demo-app` — authorization code + PKCE (S256), direct access grants enabled (handy for curl tests) |
| Confidential client | `demo-backend` — secret `demo-backend-secret`, service account (client credentials) |
| Redirect URIs | `http://localhost:8000/*`, `:8080/*`, `:5000/*`, `:3000/*` |

## OIDC endpoints (realm `demo`)

Base: `http://localhost:8080/realms/demo`

| Endpoint | Path |
|---|---|
| Discovery | `/.well-known/openid-configuration` |
| Authorization | `/protocol/openid-connect/auth` |
| Token | `/protocol/openid-connect/token` |
| Userinfo | `/protocol/openid-connect/userinfo` |
| JWKS | `/protocol/openid-connect/certs` |
| End session | `/protocol/openid-connect/logout` |

Get a token:

```python
import json, urllib.parse, urllib.request

body = urllib.parse.urlencode({"grant_type": "password", "client_id": "demo-app",
                               "username": "demo", "password": "demo"}).encode()
url = "http://localhost:8080/realms/demo/protocol/openid-connect/token"
print(json.load(urllib.request.urlopen(urllib.request.Request(url, data=body)))["access_token"][:40], "...")
```

## Use it from the `python/` templates

The issuer is pinned to `KEYCLOAK_HOSTNAME` (`http://localhost:8080`) so browser redirects work, while the back channel is dynamic, so a container can call Keycloak at `http://host.docker.internal:8080` (Docker Desktop; on Linux add `extra_hosts: ["host.docker.internal:host-gateway"]`) or, if joined to the same network, at `http://keycloak:8080`.

**Flask** (`python/plain_flask_gunicorn`; add `Authlib` and `requests` to its `requirements.txt`):

```python
from authlib.integrations.flask_client import OAuth

oauth = OAuth(app)
oauth.register(
    "keycloak",
    client_id="demo-backend",
    client_secret="demo-backend-secret",
    server_metadata_url="http://host.docker.internal:8080/realms/demo/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)
# /login:    return oauth.keycloak.authorize_redirect(url_for("auth", _external=True))
# /auth:     token = oauth.keycloak.authorize_access_token()
```

**Django** (`python/plain_django`; add `mozilla-django-oidc` to its `requirements.txt`), in `settings.py`:

```python
OIDC_RP_CLIENT_ID = "demo-backend"
OIDC_RP_CLIENT_SECRET = "demo-backend-secret"
OIDC_RP_SIGN_ALGO = "RS256"
KC = "http://host.docker.internal:8080/realms/demo/protocol/openid-connect"
OIDC_OP_AUTHORIZATION_ENDPOINT = "http://localhost:8080/realms/demo/protocol/openid-connect/auth"  # browser
OIDC_OP_TOKEN_ENDPOINT = f"{KC}/token"          # server side
OIDC_OP_USER_ENDPOINT = f"{KC}/userinfo"
OIDC_OP_JWKS_ENDPOINT = f"{KC}/certs"
```

## Environment

| Variable | Default |
|---|---|
| `KEYCLOAK_VERSION` | `26.8.2` |
| `KEYCLOAK_PORT` / `KEYCLOAK_MANAGEMENT_PORT` | `8080` / `9000` |
| `KEYCLOAK_HOSTNAME` | `http://localhost:8080` |
| `KEYCLOAK_ADMIN` / `KEYCLOAK_ADMIN_PASSWORD` | `admin` / `admin` |
| `KC_DB_NAME` / `KC_DB_USERNAME` / `KC_DB_PASSWORD` | `keycloak` |

## Notes

- Port 8080 is also used by `airflow/`, `spark/` and others; override `KEYCLOAK_PORT` **and** `KEYCLOAK_HOSTNAME` together.
- The image has neither `curl` nor `wget`; the healthcheck speaks HTTP over bash's `/dev/tcp` against the management port.
- For production use `start` with a real hostname, TLS and `--optimized` builds, not `start-dev`.

## Resources

- https://www.keycloak.org/server/containers
- https://www.keycloak.org/server/importExport
- https://www.keycloak.org/server/hostname
