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
COPY backend/apps/missions/pyproject.toml backend/apps/missions/pyproject.toml
COPY scripts/pyproject.toml scripts/pyproject.toml
COPY backend/libs/swarm-catalog/pyproject.toml backend/libs/swarm-catalog/pyproject.toml
COPY backend/libs/swarm-lifecycle/pyproject.toml backend/libs/swarm-lifecycle/pyproject.toml
COPY backend/libs/swarm-logging/pyproject.toml backend/libs/swarm-logging/pyproject.toml
COPY backend/libs/swarm-nats/pyproject.toml backend/libs/swarm-nats/pyproject.toml
COPY backend/libs/swarm-web/pyproject.toml backend/libs/swarm-web/pyproject.toml
COPY backend/swarm-models/pyproject.toml backend/swarm-models/pyproject.toml
COPY backend/swarm-storage/pyproject.toml backend/swarm-storage/pyproject.toml
COPY backend/swarm-clients/pyproject.toml backend/swarm-clients/pyproject.toml
COPY backend/swarm-service/pyproject.toml backend/swarm-service/pyproject.toml
COPY backend/swarm-api/pyproject.toml backend/swarm-api/pyproject.toml

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable --no-install-workspace --package swarm-missions --package swarm-scripts

COPY README.md README.md
COPY backend backend
COPY scripts scripts

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable --package swarm-missions --package swarm-scripts

FROM python:3.12.16-slim-bookworm AS runtime

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    SWARM_APP=missions \
    SWARM_APP_ROOT=/app

# Security fixes the base image does not carry yet (CVE-2025-6020 in libpam, found by Trivy): the runtime
# stage takes every Debian update, then drops the package lists.
RUN apt-get update \
    && apt-get upgrade -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --system --gid 10001 swarm \
    && useradd --system --uid 10001 --gid swarm --home-dir /app --shell /usr/sbin/nologin swarm \
    && mkdir -p /app \
    && chown swarm:swarm /app

COPY --from=build /opt/venv /opt/venv
COPY --from=build --chown=swarm:swarm /workspace/backend/apps/missions/conf /app/conf
COPY --from=build --chown=swarm:swarm /workspace/backend/apps/missions/migrations /app/migrations

WORKDIR /app
USER 10001:10001

# The image serves the app. Its schema is migrated by the same image, run as a job with the entrypoint
# swarm-migrations-migrate: SWARM_APP and SWARM_APP_ROOT already name this app and its folder.
ENTRYPOINT ["swarm-missions-serve"]
