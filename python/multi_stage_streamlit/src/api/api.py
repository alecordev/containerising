"""Tiny FastAPI service protected by an API key (header ``X-API-Key``)."""

import os
import secrets

import pandas as pd
from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security import APIKeyHeader

API_KEY = os.environ.get("API_KEY", "change-me")

app = FastAPI(title="Example API")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def require_api_key(key: str | None = Security(api_key_header)) -> None:
    if key is None or not secrets.compare_digest(key, API_KEY):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/data", dependencies=[Depends(require_api_key)])
def data(rows: int = 20) -> list[dict]:
    """Return a small synthetic dataset."""
    rows = max(1, min(rows, 1000))
    df = pd.DataFrame({"x": range(rows), "y": [(i * i) % 97 for i in range(rows)]})
    return df.to_dict(orient="records")
