"""Superset configuration, mounted at /app/pythonpath/superset_config.py (loaded automatically)."""
import os

# --- required -------------------------------------------------------------------------------
# Generate your own: python -c "import secrets; print(secrets.token_urlsafe(42))"
SECRET_KEY = os.environ["SUPERSET_SECRET_KEY"]
SQLALCHEMY_DATABASE_URI = os.environ["SUPERSET_DATABASE_URI"]

# --- caching (Redis) ------------------------------------------------------------------------
REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379")


def _cache(db: int, prefix: str, timeout: int = 300) -> dict:
    return {
        "CACHE_TYPE": "RedisCache",
        "CACHE_DEFAULT_TIMEOUT": timeout,
        "CACHE_KEY_PREFIX": prefix,
        "CACHE_REDIS_URL": f"{REDIS_URL}/{db}",
    }


CACHE_CONFIG = _cache(1, "superset_metadata_")
DATA_CACHE_CONFIG = _cache(2, "superset_data_")
FILTER_STATE_CACHE_CONFIG = _cache(3, "superset_filter_", 86400)
EXPLORE_FORM_DATA_CACHE_CONFIG = _cache(4, "superset_explore_", 86400)

# --- local development defaults -------------------------------------------------------------
WTF_CSRF_ENABLED = True
TALISMAN_ENABLED = False  # no TLS in front of this dev stack
