FROM python:3.12-slim-trixie

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

COPY pyproject.toml uv.lock ./

ENV UV_NO_DEV=1

RUN uv sync --locked

COPY ./src ./src

CMD ["uv", "run", "src/run.py"]
