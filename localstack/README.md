# AWS mock: moto (default) and LocalStack

A local AWS endpoint for development and tests: S3, SQS, SNS, DynamoDB, Lambda, IAM, STS and many more, without an AWS account.

> **LocalStack now requires an account.** Since 2026-03-23 the `localstack/localstack` image is a single unified image that needs a (free for non-commercial use) auth token; the old no-token community image is no longer updated. This template therefore ships two options:
>
> | Service | Needs token | Host port | Notes |
> |---|---|---|---|
> | **`moto`** (default) | no | 4566 | [moto](https://github.com/getmoto/moto) server, in-memory, covers the common AWS APIs. Starts instantly. |
> | `localstack` (profile `localstack`) | **yes** | 4567 | Full LocalStack with the broadest service coverage and persistence. |

## Run

```bash
cd localstack
# Optional: copy .env.example to .env to override defaults
docker compose up -d --wait                 # starts moto on :4566

# AWS CLI preconfigured for the mock (profile "tools")
docker compose run --rm aws s3 mb s3://demo
docker compose run --rm aws s3 ls
docker compose run --rm aws sqs create-queue --queue-name jobs
```

From the host use any SDK/CLI with a dummy credential:

Set these environment variables in your shell (or in a `.env` file for your tool), then run `aws s3 ls`:

- `AWS_ENDPOINT_URL=http://localhost:4566`
- `AWS_ACCESS_KEY_ID=test`, `AWS_SECRET_ACCESS_KEY=test`, `AWS_DEFAULT_REGION=us-east-1`

```python
import boto3
sqs = boto3.client("sqs", endpoint_url="http://localhost:4566", region_name="us-east-1",
                   aws_access_key_id="test", aws_secret_access_key="test")
print(sqs.create_queue(QueueName="jobs")["QueueUrl"])
```

## Real LocalStack (opt in)

1. Create a free account at https://app.localstack.cloud and copy your auth token.
2. Put it in `.env` as `LOCALSTACK_AUTH_TOKEN=...` (never commit it) or export it in the shell.
3. Start it (it uses host port 4567 so it can run next to moto):

```bash
docker compose --profile localstack up -d --wait localstack
AWS_ENDPOINT_URL=http://localstack:4566 docker compose run --rm aws s3 ls     # inside the network
curl http://localhost:4567/_localstack/health                                   # from the host
```

Without a valid token the container exits with a licence error. Pin or upgrade the image with `LOCALSTACK_VERSION`.

## Environment variables

| Variable | Default | Meaning |
|---|---|---|
| `MOTO_VERSION` | `5.2.5` | moto image tag |
| `MOTO_PORT` | `4566` | Host port for moto |
| `AWS_CLI_VERSION` | `2.40.1` | Tag of the `aws` helper image |
| `AWS_DEFAULT_REGION` | `us-east-1` | Region for the helper |
| `AWS_ENDPOINT_URL` | `http://moto:4566` | Endpoint the helper talks to (override for LocalStack) |
| `LOCALSTACK_VERSION` | `2026.10.7` | LocalStack image tag |
| `LOCALSTACK_AUTH_TOKEN` | empty | **Required** for the `localstack` profile |
| `LOCALSTACK_PORT` | `4567` | Host port for LocalStack |
| `LOCALSTACK_SERVICES` | empty (all) | e.g. `s3,sqs,dynamodb` to start fewer services |
| `LOCALSTACK_PERSISTENCE` | `0` | `1` keeps state in the `localstack-data` volume |

## Notes

- moto keeps all state in memory: restarting the container resets it. Its dashboard is at http://localhost:4566/moto-api/, and `POST /moto-api/reset` clears state without a restart.
- moto emulates the API surface, not the infrastructure: Lambda execution, ECS tasks and similar compute features are limited compared with real LocalStack.
- For a durable S3 store with a real storage engine, see [`../object-storage/`](../object-storage).

## Resources

- https://docs.getmoto.org/en/latest/docs/server_mode.html
- https://docs.localstack.cloud/getting-started/auth-token/
