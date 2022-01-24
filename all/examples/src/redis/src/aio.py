import os
import json
import asyncio

import aioredis

from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())


REDIS_HOSTNAME = os.getenv("REDIS_HOSTNAME", "localhost")
# REDIS_USERNAME = os.getenv("REDIS_USERNAME", "admin")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "password")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))


async def f1(value):
    conn = aioredis.from_url(
        f"redis://{REDIS_HOSTNAME}",
        password=REDIS_PASSWORD,
        port=REDIS_PORT,
        encoding="utf-8",
        decode_responses=True,
    )
    async with conn.client() as conn:
        result = await conn.get(value)
        payload = json.loads(result)
    return dict(
        status=payload,
    )


async def get(key):
    conn = aioredis.from_url(
        f"redis://{REDIS_HOSTNAME}",
        password=REDIS_PASSWORD,
        port=REDIS_PORT,
        encoding="utf-8",
        decode_responses=True,
    )
    async with conn.client() as conn:
        val = await conn.get(key)
    return val


async def set(key, value):
    conn = aioredis.from_url(
        "redis://localhost",
        password=REDIS_PASSWORD,
        encoding="utf-8",
        decode_responses=True,
    )
    async with conn.client() as conn:
        await conn.set(key, value)
        val = await conn.get(key)
    return val


if __name__ == '__main__':
    asyncio.run(set("value", 2))
    print(asyncio.run(get("value")))
    assert int(asyncio.run(get("value"))) == 2
