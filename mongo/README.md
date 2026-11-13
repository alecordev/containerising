# Mongo

`mongo:8.0` + Mongo Express (`1.0.2-20-alpine3.19`).

## Run

```bash
docker compose up -d
uv run src/mongo.py          # installs pymongo from the script header on first run
```

- MongoDB: `mongodb://admin:admin@localhost:27017/?authSource=admin`
- Mongo Express UI: http://localhost:8081 (basic auth `admin` / `admin`)

## Configuration

| Variable | Default |
|---|---|
| `MONGO_USER` / `MONGO_PASSWORD` | `admin` / `admin` |
| `MONGO_DB` | `auth` |
| `MONGO_PORT` | `27017` |
| `MONGO_EXPRESS_USER` / `MONGO_EXPRESS_PASSWORD` | `admin` / `admin` |
| `MONGO_EXPRESS_PORT` | `8081` |

Data lives in the named volumes `mongo-data` / `mongo-config`. Reset with `docker compose down -v`.

## Resources

- https://www.mongodb.com/languages/python/pymongo-tutorial
