# Ollama + Open WebUI + LiteLLM

A local LLM stack:

| Service | Image | Purpose | Port |
|---|---|---|---|
| `ollama` | `ollama/ollama:0.40.16` | model runtime / API | 11434 |
| `model-pull` | same | one-shot: pulls `OLLAMA_MODEL`, then exits | - |
| `open-webui` | `ghcr.io/open-webui/open-webui:0.13.3` | chat UI | 3000 |
| `litellm` | `ghcr.io/berriai/litellm:v1.109.1` | OpenAI-compatible gateway in front of Ollama | 4000 |

The default model is `qwen2.5:0.5b` (about 400 MB) so the first start is quick. Pick a bigger one with `OLLAMA_MODEL`.

## Run

```bash
# optional: copy .env.example to .env to override defaults
docker compose up -d --wait
docker compose down      # add -v to also delete downloaded models
```

- Open WebUI: http://localhost:3000 (login disabled by default, set `WEBUI_AUTH=True` to enable)
- Ollama API: http://localhost:11434
- LiteLLM: http://localhost:4000 (`Authorization: Bearer sk-dev-litellm-key`)

### GPU (NVIDIA)

```bash
docker compose -f docker-compose.yml -f docker-compose.override.gpu.yml up -d
```

Needs the NVIDIA Container Toolkit (Linux) or Docker Desktop with WSL2 GPU support. `OLLAMA_GPU_COUNT` limits the number of GPUs (default `all`). The override is not smoke-tested (it needs NVIDIA hardware).

## Try it

```bash
# chat from the terminal
docker compose exec ollama ollama run qwen2.5:0.5b "Why is the sky blue?"

# pull / list models
docker compose exec ollama ollama pull llama3.2:3b
docker compose exec ollama ollama list
```

HTTP APIs from Python (standard library only, same on every OS):

```python
import json, urllib.request

def post(url, body, headers=None):
    req = urllib.request.Request(url, json.dumps(body).encode(),
                                 {"Content-Type": "application/json", **(headers or {})})
    return json.load(urllib.request.urlopen(req, timeout=120))

# Ollama native API
print(post("http://localhost:11434/api/generate",
           {"model": "qwen2.5:0.5b", "prompt": "Why is the sky blue?", "stream": False})["response"])

# OpenAI-compatible API through LiteLLM
print(post("http://localhost:4000/v1/chat/completions",
           {"model": "qwen2.5-0.5b", "messages": [{"role": "user", "content": "Hello"}]},
           {"Authorization": "Bearer sk-dev-litellm-key"})["choices"][0]["message"]["content"])
```

Any OpenAI SDK also works: `base_url="http://localhost:4000/v1"`, `api_key="sk-dev-litellm-key"`.

To expose another model through LiteLLM, add an entry to `litellm_config.yaml` and `docker compose restart litellm`. If you change `OLLAMA_MODEL`, update the `model:` line in that file too.

## Environment

| Variable | Default |
|---|---|
| `OLLAMA_VERSION` / `OPEN_WEBUI_VERSION` / `LITELLM_VERSION` | see table above |
| `OLLAMA_MODEL` | `qwen2.5:0.5b` |
| `OLLAMA_PORT` / `OPEN_WEBUI_PORT` / `LITELLM_PORT` | `11434` / `3000` / `4000` |
| `WEBUI_AUTH` / `WEBUI_SECRET_KEY` | `False` / dev-only value |
| `LITELLM_MASTER_KEY` | `sk-dev-litellm-key` |
| `OLLAMA_GPU_COUNT` | `all` (GPU override only) |

## Notes

- Models live in the `ollama-data` volume and survive `down`.
- Open WebUI is ~4 GB and needs ~2 GB RAM; bigger models need more.
- Change all default keys before exposing any port beyond localhost.
- **Behind a TLS-inspecting corporate proxy** the `model-pull` step fails with `x509: certificate signed by unknown authority`, because the container does not trust your CA. Pull the model on a network without inspection (or a machine with the CA installed) and copy it into the `ollama-data` volume, or run Ollama natively on the host and point LiteLLM/Open WebUI at it. The rest of the stack is unaffected.

## Verify

`python ../scripts/smoke.py ollama` brings the stack up, runs `smoke.py` (a real generation through Ollama and through LiteLLM, plus the Open WebUI health endpoint) and tears it down. With the stack already running, `python smoke.py` (or `uv run smoke.py`) runs just the check (from another directory give the path, e.g. `uv run ollama/smoke.py`).

## Resources

- https://ollama.com/library · https://docs.openwebui.com · https://docs.litellm.ai
