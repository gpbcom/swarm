# syntax=docker/dockerfile:1.7
# Build context: the repository root, because the shared uv.lock is there.

FROM rust:1.91.1-slim-bookworm AS rust

WORKDIR /workspace/rust

COPY rust /workspace/rust

RUN cargo build --release --locked -p swarm-synthetic-drones

FROM python:3.12.16-slim-bookworm AS build

COPY --from=ghcr.io/astral-sh/uv:0.12.21 /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/opt/venv

WORKDIR /workspace

COPY pyproject.toml uv.lock ./
COPY backend/apps/simulator/pyproject.toml backend/apps/simulator/pyproject.toml
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
    uv sync --frozen --no-dev --no-editable --no-install-workspace --package swarm-simulator --package swarm-scripts

COPY README.md README.md
COPY backend backend
COPY scripts scripts

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable --package swarm-simulator --package swarm-scripts

FROM python:3.12.16-slim-bookworm AS runtime

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    SWARM_APP=simulator \
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
COPY --from=rust /workspace/rust/target/release/swarm-synthetic-drones /usr/local/bin/swarm-synthetic-drones
COPY --from=build --chown=swarm:swarm /workspace/backend/apps/simulator/conf /app/conf

WORKDIR /app
USER 10001:10001

# The image serves POST /v1/simulations and answers the Commands of the bus: it reads /app/conf/app.yaml, whose
# Operator, credentials and subject the deployment gives, and refuses to start without simulated credentials.
ENTRYPOINT ["swarm-simulator-serve"]
