# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Real inference round trip: Ollama directly, then through the LiteLLM gateway, then Open WebUI health.

Runs after `docker compose up -d --wait`. The GPU override (docker-compose.override.gpu.yml) is not
smoke-tested: it needs NVIDIA hardware.
"""
import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import env, exec_, expect, http, port, run  # noqa: E402

MODEL = env("OLLAMA_MODEL", "qwen2.5:0.5b")


def main() -> None:
    expect(MODEL in exec_("ollama", "ollama", "list").stdout, f"model {MODEL} was not pulled")

    r = http(
        f"http://localhost:{port('OLLAMA_PORT', 11434)}/api/generate",
        "POST",
        json_body={"model": MODEL, "prompt": "Say hi", "stream": False, "options": {"num_predict": 8}},
        timeout=120,
    )
    expect("response" in r.json(), "Ollama /api/generate returned no 'response'")

    key = env("LITELLM_MASTER_KEY", "sk-dev-litellm-key")
    r = http(
        f"http://localhost:{port('LITELLM_PORT', 4000)}/v1/chat/completions",
        "POST",
        json_body={"model": "qwen2.5-0.5b", "messages": [{"role": "user", "content": "Say hi"}], "max_tokens": 8},
        headers={"Authorization": f"Bearer {key}"},
        timeout=120,
    )
    expect("choices" in r.json(), "LiteLLM chat completion returned no 'choices'")

    http(f"http://localhost:{port('OPEN_WEBUI_PORT', 3000)}/health")


run(main)
