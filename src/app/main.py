import logging

from fastapi import FastAPI

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
