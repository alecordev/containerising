# Spark 4.3 standalone cluster

Official `apache/spark:4.3.0-scala2.13-java21-python3-ubuntu` image: one master and two workers. Replaces the stale `bde2020/*` images (Spark 3.2 / Hadoop 3.2).

## Run

Optional: copy `.env.example` to `.env` to override defaults (every variable has a default, so this is not required).

```bash
docker compose up -d
docker compose down
```

- Master UI: http://localhost:8080 — workers: http://localhost:8081, http://localhost:8082
- Master URL: `spark://localhost:7077` (inside docker: `spark://spark-master:7077`)
- Worker size: `SPARK_WORKER_CORES` (2) and `SPARK_WORKER_MEMORY` (1g) per worker.
- Mount: `./examples` -> `/opt/spark/examples-py` (read-only).

## Submit jobs

Inside the cluster (no local Java needed):

```bash
docker compose exec spark-master /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 /opt/spark/examples-py/example_estimate_pi.py
docker compose exec spark-master /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 /opt/spark/examples-py/example_param.py /opt/spark/README.md
```

From the host with PySpark (needs Java 17+; uv installs PySpark from the script header). Client mode only works from a machine the workers can reach; on Docker Desktop prefer the in-cluster submit above:

```bash
# set SPARK_MASTER=spark://localhost:7077 in your environment first
uv run examples/using_cluster.py
uv run examples/cores.py        # local[*], no cluster required
```

Examples read `SPARK_MASTER` (default `local[*]`).

## Resources

- https://spark.apache.org/docs/latest/spark-standalone.html
- https://hub.docker.com/r/apache/spark
