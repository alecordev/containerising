# OpenSearch

OpenSearch 3.x single node plus OpenSearch Dashboards. An Apache-2.0 alternative to the [`elasticsearch/`](../elasticsearch) template. **Local development only: the security plugin is disabled.**

## Run

```bash
cd opensearch
# optional: copy .env.example to .env to override defaults
docker compose up -d --wait
docker compose down    # add -v to delete the data volume
```

### Linux hosts: `vm.max_map_count`

OpenSearch needs a larger memory-map limit than most Linux distros set by default (Docker Desktop on macOS/Windows handles this for you):

```bash
sudo sysctl -w vm.max_map_count=262144      # Linux host
wsl -d docker-desktop sysctl -w vm.max_map_count=262144   # Windows + Docker Desktop (WSL2), if the container exits
```

To persist it on Linux, put `vm.max_map_count=262144` in a file under `/etc/sysctl.d/`.

## Ports and URLs

| Service | URL | Env override |
|---|---|---|
| OpenSearch REST | http://localhost:9200 | `OPENSEARCH_PORT` |
| Performance analyzer | http://localhost:9600 | `OPENSEARCH_PERF_PORT` |
| Dashboards | http://localhost:5602 | `DASHBOARDS_PORT` |

Dashboards uses host port **5602** by default so it can run next to Kibana (5601).

## Environment variables

| Variable | Default | Notes |
|---|---|---|
| `OPENSEARCH_VERSION` | `3.9.0` | Used for both OpenSearch and Dashboards (versions must match) |
| `OPENSEARCH_HEAP` | `1g` | JVM min/max heap |
| `OPENSEARCH_INITIAL_ADMIN_PASSWORD` | `Dev-Opensearch-9!` | Required by the image even with security off; must be a strong password |
| `OPENSEARCH_DISABLE_SECURITY` | `true` | `false` enables HTTPS + basic auth (`admin` / the password above); Dashboards then needs HTTPS settings |

## Try it

```python
import json, urllib.request

def call(method, url, body=None):
    req = urllib.request.Request(url, method=method,
                                 data=None if body is None else json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        return json.load(r)

BASE = "http://localhost:9200"
call("PUT", f"{BASE}/books", {})
call("POST", f"{BASE}/books/_doc/1?refresh=true", {"title": "Dune", "author": "Frank Herbert"})
print(call("GET", f"{BASE}/books/_search?q=title:dune"))
call("DELETE", f"{BASE}/books")
```

OpenSearch also ships k-NN vector search; see the docs below.

## Resources

- https://opensearch.org/docs/latest/
- https://opensearch.org/docs/latest/install-and-configure/install-opensearch/docker/

## Smoke test

`python scripts/smoke.py opensearch` starts this stack, waits for the healthchecks, runs [`smoke.py`](smoke.py) (a real round trip against the service) and tears everything down again. `smoke.py` is also a runnable example: with the stack already up, `python smoke.py` (or `uv run smoke.py`) runs just the check (from another directory give the path, e.g. `uv run opensearch/smoke.py`); it needs only the Python standard library.
