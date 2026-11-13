# Grafana + InfluxDB 2 + Telegraf + Prometheus + Alertmanager

| Service | Image | URL |
|---|---|---|
| Grafana | `grafana/grafana:13.2.6` | http://localhost:3000 (admin / admin) |
| InfluxDB 2 | `influxdb:2.9` | http://localhost:8086 (admin / adminadmin, org `monitoring`, bucket `telegraf`) |
| Telegraf | `telegraf:1.40-alpine` | writes system metrics to InfluxDB |
| Prometheus | `prom/prometheus:v3.16.0` | http://localhost:9090 |
| Alertmanager | `prom/alertmanager:v0.35.0` | http://localhost:9093 |
| cAdvisor (profile) | `ghcr.io/google/cadvisor:v0.60.6` | http://localhost:8088 |

InfluxDB is the 2.x line on purpose: Telegraf's `influxdb_v2` output and Grafana's Flux datasource need it (InfluxDB 3 is a different product).

## Run

Optional: copy `.env.example` to `.env` to override defaults (every variable has a default, so this is not required).

```bash
docker compose up -d
docker compose --profile host-metrics up -d   # + cAdvisor and host-level Telegraf (Linux only)
docker compose down      # add -v to delete all data
```

Grafana comes with both datasources provisioned (`provisioning/datasources/datasources.yml`): Prometheus (default) and InfluxDB (Flux). Import dashboards from https://grafana.com/grafana/dashboards/ (e.g. Telegraf system, cAdvisor).

## Configuration files

- `telegraf.conf`: inputs (cpu, disk, mem, ping, ...) and the `influxdb_v2` output; URL/org/bucket/token come from environment variables.
- `prometheus/prometheus.yml`: scrape jobs (`cadvisor` is DOWN unless the `host-metrics` profile is on) and Alertmanager target.
- `alertmanager/config.yml`: minimal routing to a no-op receiver; add webhook/email/Slack receivers.

## Security note

The `host-metrics` profile mounts the host `/`, `/sys`, `/proc`, `/etc`, `/var/lib/docker` and the Docker socket (root-equivalent) into containers. Default stack mounts none of these. All passwords/tokens are dev defaults: change them in `.env`.

## Environment

`GRAFANA_PORT`, `GRAFANA_ADMIN_USER/PASSWORD`, `INFLUXDB_PORT`, `INFLUXDB_USER/PASSWORD/ORG/BUCKET/ADMIN_TOKEN`, `PROMETHEUS_PORT`, `ALERTMANAGER_PORT`, `CADVISOR_PORT` (8088), plus `*_VERSION` overrides. See `.env.example`.

Data lives in named volumes (`grafana-data`, `influxdb-data`, `influxdb-config`, `prometheus-data`, `alertmanager-data`).
