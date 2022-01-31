# Airflow docker-compose

Make sure you have an updated docker-compose version. Docker.

- `echo -e "AIRFLOW_UID=$(id -u)\nAIRFLOW_GID=0" > .env`
- `mkdir ./dags ./logs ./plugins`
1. `docker-compose up airflow-init`
2. `docker-compose up`
3. `docker-compose down`

# Environment

```
AIRFLOW_UID=1000
AIRFLOW_GID=0
```

# Dependencies

docker
docker-compose

- https://github.com/docker/compose/releases

# Resources

- https://faun.pub/apache-airflow-2-0-complete-installation-with-docker-explained-f07aa1049f1e