# RabbitMQ

`rabbitmq:4.3-management-alpine`.

```bash
docker compose up -d
```

- AMQP: `amqp://admin:admin@localhost:5672/`
- Management UI: http://localhost:15672 (`admin` / `admin`)

| Variable | Default |
|---|---|
| `RABBITMQ_DEFAULT_USER` / `RABBITMQ_DEFAULT_PASS` | `admin` / `admin` |
| `RABBITMQ_PORT` | `5672` |
| `RABBITMQ_MANAGEMENT_PORT` | `15672` |

Data lives in the named volume `rabbitmq-data`. Reset with `docker compose down -v`.
Note: the default `guest` user can only connect from localhost inside the container, which is why the
default user is `admin` here.
