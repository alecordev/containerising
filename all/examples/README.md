# Examples

Small client scripts for the services in `../docker-compose.yml`. Each folder under `src/` is a [uv](https://docs.astral.sh/uv/) project with its own `requirements.txt` (the source of truth), a generated `pyproject.toml`, and a dependency header in every script:

```bash
cd src/redis
uv run src/simple.py          # first run creates the environment and installs the dependencies
```

From the repo root, `uv run all/examples/src/redis/src/simple.py` works too. Plain pip still works: `pip install -r requirements.txt`, then `python src/simple.py`.

Connection settings come from environment variables (or a `.env` found by python-dotenv; see `../.env.example`)
and default to the compose defaults on `localhost`. MongoDB uses `MONGO_URI`, Elasticsearch `ELASTICSEARCH_URL`,
Postgres `PG_HOST`/`PG_PORT`/`POSTGRES_*`.
