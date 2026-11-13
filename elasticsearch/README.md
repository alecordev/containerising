# Elasticsearch + Kibana

Elastic stack `9.5.6` (single node, **security disabled — local development only**).

```bash
docker compose up -d
curl http://localhost:9200
```

- Elasticsearch: http://localhost:9200
- Kibana: http://localhost:5601

| Variable | Default |
|---|---|
| `ELASTIC_VERSION` | `9.5.6` |
| `ES_HEAP` | `1g` (JVM min/max heap) |
| `ES_PORT` / `KIBANA_PORT` | `9200` / `5601` |

## Notes

- Data lives in the named volume `elasticsearch-data` (no host permission fiddling needed). Reset with `docker compose down -v`.
- On a Linux host, if Elasticsearch exits at startup, raise the kernel limit: `sudo sysctl -w vm.max_map_count=262144`
  (Docker Desktop / WSL2: `wsl -d docker-desktop sysctl -w vm.max_map_count=262144`).
- Python client examples: `all/examples/src/elastic`.
