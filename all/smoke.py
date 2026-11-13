# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Smoke test for the combined stack: Redis, Postgres, Mongo, Elasticsearch and RabbitMQ all respond."""
import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import env, exec_, expect, http, port, retry, run  # noqa: E402


def main() -> None:
    pong = exec_("redis", "redis-cli", "-a", env("REDIS_PASSWORD", "password"), "--no-auth-warning", "ping").stdout
    expect("PONG" in pong, f"redis: {pong!r}")
    pg = exec_("postgres", "sh", "-c", 'psql -qtA -U "$POSTGRES_USER"', input="select 1;").stdout
    expect(pg.strip() == "1", f"postgres: {pg!r}")
    mongo = exec_(
        "mongo", "mongosh", "--quiet", "-u", env("MONGO_USER", "admin"), "-p", env("MONGO_PASSWORD", "admin"),
        "--authenticationDatabase", "admin", "--eval", "db.runCommand({ping: 1}).ok",
    ).stdout
    expect(mongo.strip().endswith("1"), f"mongo: {mongo!r}")
    retry(lambda: http(f"http://localhost:{port('ES_PORT', 9200)}/_cluster/health"), desc="Elasticsearch health")
    exec_("rabbitmq", "rabbitmq-diagnostics", "-q", "check_running")


run(main)
