# Garage (S3)

[Garage](https://garagehq.deuxfleurs.fr/) is a lightweight, self-hosted S3-compatible object store written in Rust (AGPL-3.0), built for small, geo-distributed clusters. This template runs one node and bootstraps it automatically. See [`../README.md`](../README.md) for the comparison with SeaweedFS.

## Run

```bash
cd object-storage/garage
# Optional: copy .env.example to .env to override defaults
docker compose up -d --wait
docker compose run --rm aws s3 ls
docker compose run --rm aws s3 ls s3://dev
```

| Endpoint | URL |
|---|---|
| S3 API | http://localhost:3900 |
| Static websites | http://localhost:3902 |
| Admin API / metrics | http://localhost:3903 |

Credentials: access key `GK31c2f218a2e44f485b94239e`, secret `b892c0665f0ada8a4755dae98baa3b133590e11dae3bcc1f9d769d67f16c3835`, region `garage`, **path-style** addressing. A bucket named `dev` exists and the key can read/write/own it.

## What the bootstrap does

Garage refuses to store data until it has a **cluster layout**, and S3 keys/buckets are created through its CLI, not through environment variables. The `garage-init` one-shot service (script: `init.py`, Python standard library only) therefore runs after the server starts and, idempotently:

1. assigns this node to zone `dc1` with `GARAGE_CAPACITY` and applies layout version 1,
2. imports the fixed dev key (`dev-key`) and lets it create buckets over S3,
3. creates the bucket `GARAGE_BUCKET` and grants the key read/write/owner.

The `garage` service only becomes healthy once the layout is applied (the admin `/health` endpoint returns 503 before that), so `docker compose up --wait` returns when the store is usable. The image is built locally from the official static binary plus a shell (`Dockerfile`), because the official image is `scratch` and has no `sh`.

## Environment variables

| Variable | Default | Meaning |
|---|---|---|
| `GARAGE_VERSION` | `v2.5.0` | Garage release (build arg and image tag) |
| `AWS_CLI_VERSION` | `2.40.1` | Tag of the `aws` helper image |
| `GARAGE_RPC_SECRET` | dev value | 64 hex chars shared by cluster nodes |
| `GARAGE_ADMIN_TOKEN` / `GARAGE_METRICS_TOKEN` | dev values | Bearer tokens for the admin API |
| `GARAGE_ACCESS_KEY` | `GK31c2f218a2e44f485b94239e` | `GK` + 24 hex |
| `GARAGE_SECRET_KEY` | 64 hex dev value | 64 hex |
| `GARAGE_BUCKET` | `dev` | Bucket created at start-up |
| `GARAGE_CAPACITY` | `1G` | Capacity advertised for this node |
| `GARAGE_S3_PORT` / `GARAGE_WEB_PORT` / `GARAGE_ADMIN_PORT` | `3900` / `3902` / `3903` | Host ports |

Generate your own values with Python: `python -c "import secrets; print(secrets.token_hex(32)); print('GK' + secrets.token_hex(12))"` (a 64-hex secret, and a `GK` + 24-hex key id).

## Usage

```bash
docker compose exec garage garage status          # node + layout
docker compose exec garage garage bucket list
docker compose exec garage garage key list
docker compose exec garage garage bucket create reports
docker compose exec garage garage bucket allow --read --write --owner reports --key dev-key
```

## Notes

- Metadata and data live in the `garage-meta` and `garage-data` volumes. Removing only the metadata volume loses the layout and all bucket definitions.
- `replication_factor = 1` in `garage.toml` means no redundancy: this is a single-node dev setup. A production cluster uses 3 nodes and a factor of 3.
- Garage intentionally has no object versioning or object lock.

## Resources

- https://garagehq.deuxfleurs.fr/documentation/quick-start/
- https://garagehq.deuxfleurs.fr/documentation/reference-manual/configuration/
