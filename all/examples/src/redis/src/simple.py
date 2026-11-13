# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "redis>=8.1,<9",
#     "python-dotenv>=1.2",
# ]
# ///

import os

import redis
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

r = redis.Redis(
    host=os.getenv("REDIS_HOSTNAME", "localhost"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    password=os.getenv("REDIS_PASSWORD", "password"),
    decode_responses=True,
)
r.set("key", 2)

resp = int(r.get("key"))
print(resp)

assert resp == 2

r.mset({"Croatia": "Zagreb", "Bahamas": "Nassau"})
print(r.get("Bahamas"))
