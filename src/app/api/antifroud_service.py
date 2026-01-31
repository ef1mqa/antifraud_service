from fastapi import APIRouter, Body, Depends
import asyncio
import json
import redis.asyncio as redis

from app.schemas import UserCheck, AntifroudRepsonse
from app.services.checks import check_user
from app.db.redis_client import get_redis
from app.services.cache_key import make_user_check_key

router = APIRouter(
    prefix="/antifroud_service",
    tags=["system"],
)


@router.post("/check", response_model=AntifroudRepsonse)
async def antifroud_checking(
    data: UserCheck = Body(
        example={
            "birth_date": "30.01.1994",
            "phone_number": "+79876543210",
            "loans_history": [
                {
                    "amount": 10000,
                    "loan_data": "30.01.2010",
                    "is_closed": True,
                },
                {
                    "amount": 15000,
                    "loan_data": "28.02.2011",
                    "is_closed": True,
                },
            ],
        }
    ),
    r: redis.Redis = Depends(get_redis),
) -> AntifroudRepsonse:
    key = make_user_check_key(data)

    # 1. Читаем из Redis асинхронно
    cached = await r.get(key)
    if cached is not None:
        cached_dict = json.loads(cached)
        return AntifroudRepsonse(**cached_dict)

    # 2. Считаем результат (с задержкой 3 сек)
    await asyncio.sleep(3)
    result = check_user(data)

    # 3. Пишем в Redis с TTL (1 час)
    await r.setex(key, 3600, json.dumps(result, ensure_ascii=False))

    return AntifroudRepsonse(**result)
