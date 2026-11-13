# Object storage (S3-compatible)

Local S3-compatible object stores for development: upload/download with the AWS CLI, boto3, `rclone`, Spark/Trino/Airflow S3 connectors, etc., without an AWS account. Each option is a self-contained compose project in its own subdirectory.

| Option | Directory | S3 port | Licence | Footprint | Notes |
|---|---|---|---|---|---|
| **SeaweedFS** | [`seaweedfs/`](seaweedfs) | 8333 | Apache-2.0 | one container | Closest drop-in for what MinIO used to be: single process (master + volume + filer + S3), filer UI, versioning/IAM, scales to clusters. **Recommended default.** |
| **Garage** | [`garage/`](garage) | 3900 | AGPL-3.0 | one small container + one-shot init | Very light, Rust, designed for geo-distributed clusters. No object lock/versioning. Needs a layout bootstrap (automated by `garage-init`). |
| MinIO | not shipped | 9000 | AGPL-3.0 | n/a | See "What happened to MinIO" below. |

For AWS service mocks beyond S3 (SQS, SNS, DynamoDB, ...) see [`../localstack/`](../localstack).

## Quick start

```bash
cd object-storage/seaweedfs          # or: garage
docker compose up -d --wait
docker compose run --rm aws s3 mb s3://demo
echo hi | docker compose run --rm -T aws s3 cp - s3://demo/hi.txt
docker compose run --rm aws s3 ls s3://demo
```

The `aws` helper service (profile `tools`) is the AWS CLI already pointed at the local endpoint with the right credentials, on the compose network. From the host, use any S3 client with the endpoint and credentials listed in each README (use **path-style** addressing).

Both options run side by side: their S3 ports (8333 and 3900) and container names do not collide.

## Pointing clients at it

```python
import boto3
s3 = boto3.client(
    "s3",
    endpoint_url="http://localhost:8333",          # garage: http://localhost:3900
    aws_access_key_id="devaccesskey",              # see each README
    aws_secret_access_key="devsecretkey",
    region_name="us-east-1",                       # garage: "garage"
)
s3.create_bucket(Bucket="demo")
```

With the AWS CLI, set these environment variables (SeaweedFS shown; see each README for Garage) and run `aws s3 ls`:

- `AWS_ENDPOINT_URL=http://localhost:8333`
- `AWS_ACCESS_KEY_ID=devaccesskey`, `AWS_SECRET_ACCESS_KEY=devsecretkey`, `AWS_DEFAULT_REGION=us-east-1`

## What happened to MinIO

MinIO was the default local object store for years. In 2025-2026 upstream stopped publishing free container images, moved the community edition to source-only/maintenance mode and eventually removed its Docker Hub repositories; the GitHub repository was archived. Existing images keep working but receive no feature or guaranteed security updates, and `minio/minio` no longer resolves on Docker Hub. Because this repo pins images that can be pulled today, MinIO is not included. If you need it anyway: build from source, or use a maintained image such as Chainguard's `cgr.dev/chainguard/minio` or the `pgsty/silo` fork (both resolve today; not tested here).

## Credentials

All defaults are dev-only and live in each service's `.env.example`.

| Option | Access key | Secret key |
|---|---|---|
| SeaweedFS | `devaccesskey` | `devsecretkey` |
| Garage | `GK31c2f218a2e44f485b94239e` | `b892c0665f0ada8a4755dae98baa3b133590e11dae3bcc1f9d769d67f16c3835` |

Garage's key must be `GK` + 24 hex characters and its secret 64 hex characters, which is why its defaults look different.

## Resources

- https://github.com/seaweedfs/seaweedfs/wiki/Amazon-S3-API
- https://garagehq.deuxfleurs.fr/documentation/
