# n8n

n8n `2.48.2` (workflow automation, `n8nio/n8n`) on PostgreSQL 18. Local development only.

## Run

```bash
# Optional: copy .env.example to .env to override defaults (set N8N_ENCRYPTION_KEY to something of your own)
docker compose up -d --wait
docker compose down    # add -v to delete workflows, credentials and executions
```

- Editor/UI: http://localhost:5678 (`N8N_PORT`). The first visit asks you to create the **owner account**.
- Webhooks: `http://localhost:5678/webhook/<path>` (production) and `/webhook-test/<path>` (while testing in the editor).

## Environment

| Variable | Default |
|---|---|
| `N8N_VERSION` | `2.48.2` |
| `N8N_PORT` | `5678` |
| `N8N_ENCRYPTION_KEY` | `dev-only-change-me-n8n-encryption-key` |
| `N8N_DB_NAME` / `N8N_DB_USER` / `N8N_DB_PASSWORD` | `n8n` |
| `TZ` | `UTC` (also used as `GENERIC_TIMEZONE` for Cron/Schedule nodes) |

> **Encryption key:** n8n encrypts stored credentials with `N8N_ENCRYPTION_KEY`. Set your own value **before** the first start and never change it, or existing credentials become unreadable.

## Notes

- `N8N_SECURE_COOKIE=false` lets the editor work over plain `http://localhost`. Remove it when serving over HTTPS.
- Telemetry, version notifications and the personalization survey are disabled.
- To receive webhooks from the internet, expose the port with a tunnel and set `WEBHOOK_URL` to the public URL (edit the compose file).
- CLI examples: `docker compose exec n8n n8n list:workflow`, `docker compose exec n8n n8n export:workflow --all --output=/home/node/.n8n/workflows.json`.
- Data lives in the `n8n-data` (files) and `postgres-data` (workflows, credentials, executions) volumes.
- The n8n image ships `wget` (used by the healthcheck) but no `curl`.

## Resources

- https://docs.n8n.io/hosting/installation/docker/
- https://docs.n8n.io/hosting/configuration/environment-variables/
