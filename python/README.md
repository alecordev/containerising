# Python Dockerfiles

## Run Jupyter from container

- Locally, no install step: `uv run --with jupyterlab jupyter lab`
- In a container: see [`../jupyterlab`](../jupyterlab) (pinned libraries) or [`multi_stage`](multi_stage)`

## Templates

| Dir | Pattern | Run |
|---|---|---|
| `multi_stage` | wheelhouse build -> slim runtime, JupyterLab + pandas | `docker build -t nb . && docker run --rm -p 8888:8888 -e JUPYTER_TOKEN=secret nb` |
| `multi_stage_gcc` | compile C extensions (gcc) in builder only | `docker build -t gcc-demo . && docker run --rm gcc-demo` |
| `multi_stage_streamlit` | FastAPI API + Streamlit dashboard, two images | `docker compose up --build` |
| `plain_django` | Django 5.2 LTS + gunicorn + WhiteNoise | `docker compose up --build` |
| `plain_flask_gunicorn` | Flask + gunicorn | `docker compose up --build` |
| `plain_multi_stage` | `pip install --prefix` multi-stage | `docker build -t pms . && docker run --rm -p 8000:8000 pms` |

All images use `python:3.14-slim-trixie`, run as a non-root user and define a `HEALTHCHECK` where a server runs.

## References

- https://testdriven.io/blog/docker-best-practices/