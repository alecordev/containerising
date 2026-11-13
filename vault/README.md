# Vault

HashiCorp Vault `2.2.2` (`hashicorp/vault`) for local secrets management experiments. Two modes:

| Service | Mode | Storage | Port | When |
|---|---|---|---|---|
| `vault` | **dev** (default) | in-memory, auto-unsealed | `8200` | quick tests; data is lost on restart |
| `vault-persistent` | **non-dev** (profile `persistent`) | file storage in a named volume | `8201` | learn init/unseal, keep data across restarts |

> **Dev mode is insecure by design**: fixed root token, no TLS, nothing persisted. Local use only.

## Dev mode

```bash
# Optional: copy .env.example to .env to override defaults
docker compose up -d --wait
```

- UI/API: http://localhost:8200 — token: `root` (`VAULT_DEV_ROOT_TOKEN`)
- A KV v2 engine is mounted at `secret/`.

```bash
docker compose exec vault vault kv put -mount=secret myapp user=alice
docker compose exec vault vault kv get -mount=secret myapp
curl -s -H "X-Vault-Token: root" http://localhost:8200/v1/secret/data/myapp
```

From your host (optional): set the environment variables `VAULT_ADDR=http://localhost:8200` and `VAULT_TOKEN=root` in your shell.

## Persistent (non-dev) mode

Config: `config/vault.hcl` (file storage, plain HTTP listener, UI). The image entrypoint loads every file in `/vault/config`.

```bash
docker compose --profile persistent up -d --wait vault-persistent
docker compose exec vault-persistent vault operator init -key-shares=1 -key-threshold=1
# Save the printed "Unseal Key 1" and "Initial Root Token"
docker compose exec vault-persistent vault operator unseal <unseal-key>
docker compose exec -e VAULT_TOKEN=<root-token> vault-persistent vault secrets enable -path=secret kv-v2
docker compose exec -e VAULT_TOKEN=<root-token> vault-persistent vault kv put -mount=secret demo a=b
```

After a container restart Vault comes back **sealed**: run `operator unseal` again. Data lives in the `vault-file` volume (`docker compose down -v` deletes it). The healthcheck treats uninitialised/sealed as healthy so you can run `operator init`. Use 1 key share only for local convenience (production uses 5/3 or auto-unseal).

## Environment

| Variable | Default |
|---|---|
| `VAULT_VERSION` | `2.2.2` |
| `VAULT_PORT` | `8200` |
| `VAULT_DEV_ROOT_TOKEN` | `root` |
| `VAULT_PERSISTENT_PORT` | `8201` |

## Licence note and OpenBao

Vault has been under the Business Source License (BSL 1.1) since 2023: fine for local development, but not open source. For a fully open-source, API-compatible drop-in use [OpenBao](https://openbao.org/): change the image to `openbao/openbao:2.7.2` (tag verified on Docker Hub), keep the same commands but use the `bao` binary instead of `vault` (`docker compose exec vault bao status`), and the `BAO_*` environment variable names (`BAO_DEV_ROOT_TOKEN_ID`, `BAO_DEV_LISTEN_ADDRESS`, `BAO_ADDR`, `BAO_TOKEN`).

## Resources

- https://developer.hashicorp.com/vault/docs
- https://hub.docker.com/r/hashicorp/vault
- https://openbao.org/docs/
