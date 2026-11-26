# syntax=docker/dockerfile:1.7
# Build context: the repository root, because the shared uv.lock is there.

FROM python:3.12.16-slim-bookworm AS build

COPY --from=ghcr.io/astral-sh/uv:0.12.21 /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/opt/venv

WORKDIR /workspace

COPY pyproject.toml uv.lock ./
COPY services/gateway/pyproject.toml services/gateway/pyproject.toml
COPY backend/libs/swarm-catalog/pyproject.toml backend/libs/swarm-catalog/pyproject.toml
COPY backend/libs/swarm-lifecycle/pyproject.toml backend/libs/swarm-lifecycle/pyproject.toml
COPY backend/libs/swarm-logging/pyproject.toml backend/libs/swarm-logging/pyproject.toml
COPY backend/swarm-models/pyproject.toml backend/swarm-models/pyproject.toml
COPY backend/libs/swarm-nats/pyproject.toml backend/libs/swarm-nats/pyproject.toml
COPY backend/libs/swarm-web/pyproject.toml backend/libs/swarm-web/pyproject.toml
COPY backend/swarm-storage/pyproject.toml backend/swarm-storage/pyproject.toml
COPY backend/swarm-service/pyproject.toml backend/swarm-service/pyproject.toml
COPY backend/swarm-api/pyproject.toml backend/swarm-api/pyproject.toml
COPY packages/python/swarm-rest/pyproject.toml packages/python/swarm-rest/pyproject.toml

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable --no-install-workspace --package swarm-gateway

COPY README.md README.md
COPY services/gateway services/gateway
COPY packages/python packages/python
COPY backend backend

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable --package swarm-gateway

FROM python:3.12.16-slim-bookworm AS runtime

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    SWARM_GATEWAY_HOME=/app

RUN groupadd --system --gid 10001 swarm \
    && useradd --system --uid 10001 --gid swarm --home-dir /app --shell /usr/sbin/nologin swarm \
    && mkdir -p /app \
    && chown swarm:swarm /app

COPY --from=build /opt/venv /opt/venv
COPY --from=build --chown=swarm:swarm /workspace/services/gateway/conf /app/conf
COPY --from=build --chown=swarm:swarm /workspace/services/gateway/migrations /app/migrations

WORKDIR /app
USER 10001:10001

ENTRYPOINT ["swarm-gateway-serve"]
