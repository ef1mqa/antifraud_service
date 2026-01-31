from typing import AsyncIterator
import os

import redis.asyncio as redis
from redis.asyncio import Redis

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_URL = f"redis://{REDIS_HOST}:6379/0"


async def get_redis() -> AsyncIterator[Redis]:
    client = redis.from_url(REDIS_URL, decode_responses=True)
    try:
        yield client
    finally:
        await client.close()
