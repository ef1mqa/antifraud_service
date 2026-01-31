import pytest_asyncio
from httpx import AsyncClient, ASGITransport
import fakeredis.aioredis as fakeredis

from app.main import app
from app.db.redis_client import get_redis


@pytest_asyncio.fixture
async def fake_redis():
    r = fakeredis.FakeRedis(decode_responses=True)
    await r.flushdb()
    return r


@pytest_asyncio.fixture
async def client(fake_redis) -> AsyncClient:
    async def _override_get_redis():
        return fake_redis

    app.dependency_overrides[get_redis] = _override_get_redis

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac

    app.dependency_overrides.clear()
