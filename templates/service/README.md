# myservice

One-line description of the service and what this template provides.

## Run

```bash
# optional: copy .env.example to .env to override defaults
docker compose up -d --wait
docker compose logs -f
docker compose down      # add -v to delete the data volume
```

## Ports and URLs

| Port | Purpose |
|---|---|
| `8080` (`MYSERVICE_PORT`) | Web endpoint: http://localhost:8080 |

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `NGINX_VERSION` | `1.31-alpine-slim` | Image tag |
| `MYSERVICE_PORT` | `8080` | Host port |

## Credentials (dev only)

None / `user` / `password`.

## Usage examples

```bash
curl http://localhost:8080/
```

## Notes

- Caveats, resource needs (RAM), host requirements (Linux sysctls, GPU), licensing.

## Resources

- Official docs: https://example.com
