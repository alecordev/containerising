# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "redis>=8.1,<9",
#     "python-dotenv>=1.2",
# ]
# ///

import asyncio
import json
import os

import redis.asyncio as redis
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

REDIS_HOSTNAME = os.getenv("REDIS_HOSTNAME", "localhost")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "password")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))


def client() -> redis.Redis:
    return redis.Redis(
        host=REDIS_HOSTNAME,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        decode_responses=True,
    )


async def get(key):
    async with client() as conn:
        return await conn.get(key)


async def get_json(key):
    return json.loads(await get(key))


async def set(key, value):
    async with client() as conn:
        await conn.set(key, value)
        return await conn.get(key)


if __name__ == "__main__":
    print(asyncio.run(set("value", 2)))
