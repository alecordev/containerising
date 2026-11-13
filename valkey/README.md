# Valkey

`valkey/valkey:9.1.3-alpine`: the Linux Foundation's BSD-licensed, Redis-compatible fork. Works with every Redis client; compare with [`../redis`](../redis).

```bash
# optional: copy .env.example to .env to override defaults
docker compose up -d --wait
docker compose down      # add -v to delete data
```

## Access

| What | Where |
|---|---|
| Server | `localhost:6379` |
| Password | `password` |

```bash
docker compose exec valkey valkey-cli                   # then type: AUTH <password>  (default: password)
redis-cli -a password -h localhost        # redis-cli works too
```

Python (`uv run --with redis python`, or `--with valkey`): `redis.Redis(host="localhost", password="password")`.

## Environment variables

| Variable | Default |
|---|---|
| `VALKEY_VERSION` | `9.1.3-alpine` |
| `VALKEY_PASSWORD` | `password` |
| `VALKEY_MAXMEMORY` / `VALKEY_MAXMEMORY_POLICY` | `256mb` / `allkeys-lru` |
| `VALKEY_PORT` | `6379` |

## Notes

- Append-only persistence is on; data lives in the named volume `valkey-data`.
- Host port 6379 clashes with `redis/` and `all/`; override `VALKEY_PORT`.

## Resources

- https://valkey.io/documentation/
- https://hub.docker.com/r/valkey/valkey

## Smoke test

`python scripts/smoke.py valkey` starts this stack, waits for the healthchecks, runs [`smoke.py`](smoke.py) (a real round trip against the service) and tears everything down again. `smoke.py` is also a runnable example: with the stack already up, `python smoke.py` (or `uv run smoke.py`) runs just the check (from another directory give the path, e.g. `uv run valkey/smoke.py`); it needs only the Python standard library.
