# Redis

`redis:8.8-alpine` with password auth, AOF persistence and a mounted `redis.conf`.

## Run

```bash
docker compose up -d
redis-cli -a password ping        # or: docker compose exec redis redis-cli ping
```

## Configuration

| Variable | Default |
|---|---|
| `REDIS_PASSWORD` | `password` |
| `REDIS_PORT` | `6379` |

## Notes

- The password is passed with `--requirepass` (not stored in `redis.conf`).
- Data lives in the named volume `redis-data` (`/data`). Reset with `docker compose down -v`.
- No static IP / custom subnet: it joins the default compose network.
