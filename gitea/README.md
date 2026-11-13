# Gitea

Gitea `28.3` (self-hosted Git service with Gitea Actions CI) on PostgreSQL 18. Local development only.

## Run

```bash
# Optional: copy .env.example to .env to override defaults
docker compose up -d --wait
```

- Web UI: http://localhost:3001 (`GITEA_HTTP_PORT`; 3001 because 3000 is taken by `grafana/`, `dagster/`, `observability/`)
- Git over SSH: `ssh://git@localhost:2222/<user>/<repo>.git` (`GITEA_SSH_PORT`)
- The installer is skipped (`INSTALL_LOCK`), and self-registration is disabled, so create the first admin with the CLI:

```bash
docker compose exec -u git gitea gitea admin user create --admin --username admin --password "Change-me-123!" --email admin@example.com --must-change-password=false
```

Then log in, create a repository and push:

```bash
git clone http://localhost:3001/admin/myrepo.git
```

Use `GITEA_DISABLE_REGISTRATION=false` to allow sign-ups in the UI.

## Actions runner (profile `runner`)

Gitea Actions is enabled. To run workflows (`.gitea/workflows/*.yaml`, GitHub Actions-compatible) start a runner:

```bash
# 1. get a registration token (instance-level)
docker compose exec -u git gitea gitea actions generate-runner-token
# 2. put it in .env
#    GITEA_RUNNER_REGISTRATION_TOKEN=<token>
# 3. start the runner
docker compose --profile runner up -d runner
```

The runner mounts the host Docker socket (`/var/run/docker.sock`) to start job containers. That gives it control of your Docker daemon: use on a local dev machine only. Labels default to `ubuntu-latest:docker://gitea/runner-images:ubuntu-latest`; change with `GITEA_RUNNER_LABELS`.

## Environment

| Variable | Default |
|---|---|
| `GITEA_VERSION` | `28.3` |
| `GITEA_HTTP_PORT` / `GITEA_SSH_PORT` | `3001` / `2222` |
| `GITEA_DB_NAME` / `GITEA_DB_USER` / `GITEA_DB_PASSWORD` | `gitea` |
| `GITEA_DISABLE_REGISTRATION` | `true` |
| `ACT_RUNNER_VERSION` | `0.6.1` |
| `GITEA_RUNNER_REGISTRATION_TOKEN` / `GITEA_RUNNER_NAME` / `GITEA_RUNNER_LABELS` | empty / `local-runner` / see above |

Any Gitea setting can be passed as `GITEA__<section>__<KEY>` (see the compose file for examples).

## Notes

- Data: `gitea-data` (repositories, config in `/data/gitea/conf/app.ini`), `postgres-data`, `runner-data`. `docker compose down -v` deletes everything.
- If you change `GITEA_HTTP_PORT`, `ROOT_URL` follows automatically (clone URLs shown in the UI use it).

## Resources

- https://docs.gitea.com/installation/install-with-docker
- https://docs.gitea.com/usage/actions/overview
- https://gitea.com/gitea/act_runner
