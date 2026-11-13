# SeaweedFS (S3)

[SeaweedFS](https://github.com/seaweedfs/seaweedfs) (Apache-2.0) in one container: master + volume server + filer + S3 gateway. A good local stand-in for AWS S3 and a maintained successor to the old MinIO-in-Docker workflow. See [`../README.md`](../README.md) for the comparison with Garage.

## Run

```bash
cd object-storage/seaweedfs
# Optional: copy .env.example to .env to override defaults
docker compose up -d --wait
docker compose run --rm aws s3 mb s3://demo
docker compose run --rm aws s3 ls
```

| Endpoint | URL |
|---|---|
| S3 API | http://localhost:8333 |
| Master UI | http://localhost:9333 |
| Filer UI / HTTP API | http://localhost:8888 |

Credentials: access key `devaccesskey`, secret `devsecretkey`, region `us-east-1`, **path-style** addressing.

## Environment variables

| Variable | Default | Meaning |
|---|---|---|
| `SEAWEEDFS_VERSION` | `4.53` | Image tag |
| `AWS_CLI_VERSION` | `2.40.1` | Tag of the `aws` helper image |
| `S3_ACCESS_KEY` / `S3_SECRET_KEY` | `devaccesskey` / `devsecretkey` | S3 credentials (server and helper) |
| `SEAWEEDFS_S3_PORT` | `8333` | Host S3 port |
| `SEAWEEDFS_MASTER_PORT` | `9333` | Host master UI port |
| `SEAWEEDFS_FILER_PORT` | `8888` | Host filer port |
| `SEAWEEDFS_VOLUME_SIZE_LIMIT_MB` | `512` | Size of one volume file; lower it to fit many buckets on a small disk |

Data lives in the `seaweedfs-data` volume (`docker compose down -v` deletes it).

## Usage

```bash
# upload / download with the bundled CLI helper (profile "tools")
echo hello | docker compose run --rm -T aws s3 cp - s3://demo/hello.txt
docker compose run --rm -T aws s3 cp s3://demo/hello.txt -

# from the host: set AWS_ENDPOINT_URL=http://localhost:8333, AWS_ACCESS_KEY_ID=devaccesskey,
# AWS_SECRET_ACCESS_KEY=devsecretkey, AWS_DEFAULT_REGION=us-east-1 in your shell, then: aws s3 ls

# browse the same objects through the filer
curl http://localhost:8888/buckets/demo/hello.txt
```

Buckets are directories under `/buckets/` in the filer, so they are also visible in the filer UI.

## Notes

- The S3 identity file is generated at start-up from `S3_ACCESS_KEY`/`S3_SECRET_KEY`; one identity with full rights. For multiple users, mount your own `s3.json` (see the wiki link below) and change the `-s3.config` flag.
- `-volume.max=0` lets SeaweedFS size the number of volumes from free disk space; with the default 30 GB volume size a small laptop disk would otherwise fit very few buckets, hence the 512 MB default limit.
- Everything is plain HTTP and unauthenticated on the master/filer ports: keep it on localhost.

## Resources

- https://github.com/seaweedfs/seaweedfs/wiki/Amazon-S3-API
- https://github.com/seaweedfs/seaweedfs/wiki/Docker
