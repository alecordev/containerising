# FastAPI + Streamlit (multi-stage)

Two images built from one context (`Dockerfile` for the API, `Dockerfile-dashboard` for Streamlit),
each with its own BuildKit ignore file (`Dockerfile.dockerignore`, `Dockerfile-dashboard.dockerignore`).

Optional: copy `.env.example` to `.env` to set `API_KEY` and ports.

```bash
docker compose up --build
```

- API: http://localhost:8081/docs (send header `X-API-Key: <API_KEY>` to `/data`)
- Dashboard: http://localhost:8501 (reaches the API at `http://api:8081` via `API_URL`)
