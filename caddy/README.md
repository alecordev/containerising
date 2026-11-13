# Caddy

Caddy 2 reverse proxy with **automatic local HTTPS**: `tls internal` issues certificates from Caddy's own local certificate authority, so `https://app.localhost` works without writing any TLS config. A tiny demo upstream (`traefik/whoami`) and a static folder are included.

Compare with the [`traefik/`](../traefik) template: Caddy uses a static `Caddyfile` (simplest for a handful of fixed services); Traefik discovers containers from Docker labels (better when stacks come and go).

## Run

```bash
cd caddy
# Optional: copy .env.example to .env to override defaults
docker compose up -d --wait
```

| URL | What |
|---|---|
| https://app.localhost:8443/ | Reverse proxy to the demo upstream |
| https://app.localhost:8443/static/ | Static files from `./site` |
| https://app.localhost:8443/healthz | Plain `ok` |
| http://app.localhost:8080/ | Redirects to HTTPS |

The browser shows a certificate warning until you trust Caddy's root CA (below).

## Environment variables

| Variable | Default | Meaning |
|---|---|---|
| `CADDY_VERSION` | `2.11.9-alpine` | Image tag |
| `WHOAMI_VERSION` | `v1.12.0` | Demo upstream tag |
| `CADDY_SITE` | `app.localhost` | Hostname served (used as the Caddyfile site address) |
| `CADDY_HTTP_PORT` | `8080` | HTTP port, **both** on the host and inside the container |
| `CADDY_HTTPS_PORT` | `8443` | HTTPS port, host and container |

The host and container ports are deliberately identical so Caddy's HTTP to HTTPS redirect points at a reachable port. Set them to `80`/`443` if those are free (then the URLs need no port).

## Trust the local CA (optional)

```bash
docker compose cp caddy:/data/caddy/pki/authorities/local/root.crt ./caddy-root.crt
```

Import `caddy-root.crt` into your OS/browser trust store. `curl` users can just pass `-k` or `--cacert caddy-root.crt`. The CA lives in the `caddy-data` volume, so it survives restarts but not `docker compose down -v`.

## Add your own service

Edit `Caddyfile` (it is mounted read-only; reload with `docker compose exec caddy caddy reload --config /etc/caddy/Caddyfile`):

```caddy
api.localhost {
    tls internal
    reverse_proxy host.docker.internal:8000      # something running on the host
}
```

To proxy a container from another compose project, attach both to a shared Docker network and use its service name in `reverse_proxy`.

## Resources

- https://caddyserver.com/docs/
- https://caddyserver.com/docs/automatic-https#local-https
