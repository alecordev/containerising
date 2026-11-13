# Mockoon

[Mockoon](https://mockoon.com/) runs mock REST APIs described by a single JSON "environment" file. Design the mock in the free Mockoon desktop app (or edit the JSON by hand), then serve it in Docker with the CLI. Supports templating (Faker, request data), rules per response, latency, CORS, proxy/record mode and OpenAPI import.

Compare with [`wiremock/`](../wiremock): Mockoon is quicker to author visually; WireMock is stronger for test suites (verification, scenarios, programmatic admin API).

## Run

```bash
cd mockoon
# Optional: copy .env.example to .env to override defaults
docker compose up -d --wait
curl http://localhost:3001/hello
curl http://localhost:3001/api/users/7
```

## Environment variables

| Variable | Default | Meaning |
|---|---|---|
| `MOCKOON_VERSION` | `9.10.0` | `mockoon/cli` image tag |
| `MOCKOON_PORT` | `3001` | Host port (the mock listens on 3000 inside the container) |

## The environment file

`mockoon-env.json` is mounted read-only at `/data/mockoon-env.json`. It defines:

| Route | Response |
|---|---|
| `GET /hello` | Static JSON |
| `GET /api/users/:id` | Templated JSON: `{{urlParam 'id'}}` and `{{faker 'person.fullName'}}` |

CORS is enabled (`"cors": true`): Mockoon answers browser preflight (`OPTIONS`) requests with the `Access-Control-*` headers; plain `GET` responses carry no CORS headers by themselves.

To change the mock: edit the file and `docker compose restart mockoon`. To author visually, open the Mockoon desktop app, build the API, **File > Export** the environment as JSON and drop it over `mockoon-env.json`. The CLI migrates older file formats automatically.

## Other ways to run it

```bash
# straight from an OpenAPI spec, no environment file needed
# use an absolute path to your spec on the host (Windows: C:\path\to\openapi.yaml)
docker run --rm -p 3001:3000 -v /abs/path/to/openapi.yaml:/data/openapi.yaml:ro mockoon/cli:9.10.0 --data /data/openapi.yaml --port 3000
```

## Resources

- https://mockoon.com/cli/
- https://mockoon.com/docs/latest/templating/overview/
