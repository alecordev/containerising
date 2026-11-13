# Traefik

Traefik v3 reverse proxy that discovers containers through the Docker provider and routes them by hostname. Lets you run several templates behind names like `http://whoami.localhost` instead of juggling host ports (and colliding on 8080/8081/5432...). Chromium and Firefox resolve `*.localhost` to 127.0.0.1 without any `/etc/hosts` edits.

## Run

```bash
cd traefik
# Optional: copy .env.example to .env to override defaults
docker compose up -d --wait
curl -H "Host: whoami.localhost" http://localhost/      # or open http://whoami.localhost
```

| URL | What |
|---|---|
| http://whoami.localhost | Demo upstream (`traefik/whoami`) |
| https://whoami.localhost | Same, over TLS using Traefik's built-in self-signed cert (browser warning) |
| http://localhost:8088/dashboard/ | Dashboard (no auth: dev only) |

## Environment variables

| Variable | Default | Meaning |
|---|---|---|
| `TRAEFIK_VERSION` | `v3.7.18` | Traefik image tag |
| `WHOAMI_VERSION` | `v1.12.0` | Demo service tag |
| `TRAEFIK_HTTP_PORT` | `80` | Host HTTP port |
| `TRAEFIK_HTTPS_PORT` | `443` | Host HTTPS port |
| `TRAEFIK_DASHBOARD_PORT` | `8088` | Host dashboard/API port |
| `TRAEFIK_LOG_LEVEL` | `INFO` | `DEBUG`, `INFO`, `WARN`, `ERROR` |
| `TRAEFIK_NETWORK` | `proxy` | Docker network used to reach upstreams |

If port 80 is taken, e.g. `TRAEFIK_HTTP_PORT=8000`, browse to `http://whoami.localhost:8000`.

## Route another stack through Traefik

Join the shared network and add labels. Example for any web container:

```yaml
services:
    app:
        image: my-app
        labels:
            - traefik.enable=true
            - traefik.http.routers.app.rule=Host(`app.localhost`)
            - traefik.http.routers.app.entrypoints=web
            - traefik.http.services.app.loadbalancer.server.port=8000   # container port
        networks: [proxy]

networks:
    proxy:
        external: true
        name: proxy      # TRAEFIK_NETWORK
```

Containers are only exposed when `traefik.enable=true` (`exposedbydefault=false`).

## Local HTTPS with mkcert

```bash
mkcert -install
mkcert -cert-file certs/local.pem -key-file certs/local-key.pem "*.localhost" localhost 127.0.0.1 ::1
cp dynamic/tls.yml.example dynamic/tls.yml
```

Traefik reloads the file automatically; `https://whoami.localhost` is then trusted by your browser. `certs/*.pem` are git-ignored.

## Security notes

- The Docker socket is mounted read-only, but it still exposes metadata for every container on the host and is effectively root-equivalent if Traefik is compromised. For anything shared, front it with a `docker-socket-proxy`.
- `--api.insecure=true` publishes the dashboard without authentication; the compose file binds it to the host port you choose. Remove it (and `ports` for 8080) outside local use.

## Resources

- https://doc.traefik.io/traefik/
- https://github.com/FiloSottile/mkcert
