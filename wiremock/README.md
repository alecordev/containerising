# WireMock

[WireMock](https://wiremock.org/) is an HTTP mock server: define stub responses as JSON files (or through its admin API) and point your app or tests at it instead of a real third-party API. Supports response templating, delays, faults, request verification and stateful scenarios.

Compare with [`mockoon/`](../mockoon): WireMock is code/JSON-mapping driven and very strong for test suites; Mockoon is GUI-authored and quick for ad-hoc API mocks.

## Run

```bash
cd wiremock
# Optional: copy .env.example to .env to override defaults
docker compose up -d --wait
curl http://localhost:8089/hello
curl http://localhost:8089/api/users/42
curl http://localhost:8089/report
curl http://localhost:8089/__admin/mappings        # list loaded stubs
```

## Layout

| Path | Mounted at | Purpose |
|---|---|---|
| `mappings/*.json` | `/home/wiremock/mappings` | Stubs, loaded at start-up |
| `__files/` | `/home/wiremock/__files` | Response bodies referenced by `bodyFileName` |

Included stubs: `/hello` (static JSON), `/api/users/{id}` (response templating), `/report` (body from file), `/slow` (1.5 s delay).

## Environment variables

| Variable | Default | Meaning |
|---|---|---|
| `WIREMOCK_VERSION` | `3.13.2` | Image tag (the 4.x line is still beta) |
| `WIREMOCK_PORT` | `8089` | Host port (container listens on 8080) |

## Admin API

```python
import json, urllib.request


def admin(path, body=None):
    req = urllib.request.Request(f"http://localhost:8089/__admin/{path}", data=None if body is None else json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    return urllib.request.urlopen(req).read().decode()


# add a stub at runtime
admin("mappings", {"request": {"method": "GET", "url": "/ping"}, "response": {"status": 200, "body": "pong"}})
# verify what was called
print(admin("requests/count", {"method": "GET", "url": "/ping"}))
# reload mappings from disk after editing files
admin("mappings/reset", {})
# unmatched requests (great for debugging)
print(admin("requests/unmatched"))
```

Stubs added through the API are not written to `mappings/` unless you call `POST /__admin/mappings/save`.

## Calling it from other containers

Attach the other service to this compose network (or use `host.docker.internal:8089` from a container, `localhost:8089` from the host) and use `http://wiremock:8080`.

## Resources

- https://wiremock.org/docs/
- https://wiremock.org/docs/response-templating/
