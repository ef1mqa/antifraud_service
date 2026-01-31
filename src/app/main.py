import logging

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator  # NEW

from app.api import healthz, antifroud_service

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(healthz.router)
app.include_router(antifroud_service.router)


@app.on_event("startup")
async def _startup() -> None:
    Instrumentator(
        should_group_status_codes=False,
    ).instrument(app).expose(
        app,
        endpoint="/metrics",
        include_in_schema=False,
    )
