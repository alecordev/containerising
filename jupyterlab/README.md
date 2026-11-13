# JupyterLab in Docker

JupyterLab 4.6 on `python:3.14-slim`, running as a non-root user, with pinned scientific libraries (`requirements.txt`).

## Run

Optional: copy `.env.example` to `.env` to override defaults (every variable has a default, so this is not required).

```bash
docker compose up --build -d
docker compose down
```

- URL: http://localhost:8888/lab
- Notebooks are stored in `./notebooks` (bind mount to `/home/jupyter/notebooks`).
- Auth: `JUPYTER_TOKEN` is empty by default (no token) and the port is only published on `127.0.0.1`. Set `JUPYTER_TOKEN=secret` in `.env` and open `http://localhost:8888/lab?token=secret` to require a token, and remove the `127.0.0.1:` prefix from the port mapping only if you add a token.
- Linux: if `./notebooks` isn't writable, set `HOST_UID`/`HOST_GID` in `.env` to your user (`id -u`, `id -g`) and rebuild.
- Add libraries: edit `requirements.txt`, then `docker compose up --build -d`. `torch` is commented out (large).

Rebuild from scratch: `docker compose up --build --force-recreate`
