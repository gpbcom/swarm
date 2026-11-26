# syntax=docker/dockerfile:1.7
# Build context: the repository root, because the shared uv.lock is there.

FROM python:3.12.16-slim-bookworm AS wheel

COPY --from=ghcr.io/astral-sh/uv:0.12.21 /uv /usr/local/bin/uv

ENV RUSTUP_HOME=/opt/rustup \
    CARGO_HOME=/opt/cargo \
    PATH="/opt/cargo/bin:$PATH" \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential ca-certificates curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --profile minimal --default-toolchain none

WORKDIR /workspace/rust

COPY rust /workspace/rust

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=cache,target=/opt/cargo/registry \
    rustup show active-toolchain || rustup toolchain install \
    && uv tool install maturin \
    && /root/.local/bin/maturin build --release --locked \
        --manifest-path swarm-core/python/Cargo.toml --out /wheels

FROM python:3.12.16-slim-bookworm AS build

COPY --from=ghcr.io/astral-sh/uv:0.12.21 /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/opt/venv

WORKDIR /workspace

COPY pyproject.toml uv.lock ./
COPY backend/apps/flight-engine/pyproject.toml backend/apps/flight-engine/pyproject.toml
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
    uv sync --frozen --no-dev --no-editable --no-install-workspace --package swarm-flight-engine --package swarm-scripts

COPY README.md README.md
COPY backend backend
COPY scripts scripts

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable --package swarm-flight-engine --package swarm-scripts

COPY --from=wheel /wheels /wheels

RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --python /opt/venv/bin/python --no-deps /wheels/*.whl

FROM python:3.12.16-slim-bookworm AS runtime

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    SWARM_APP=flight-engine \
    SWARM_APP_ROOT=/app

RUN groupadd --system --gid 10001 swarm \
    && useradd --system --uid 10001 --gid swarm --home-dir /app --shell /usr/sbin/nologin swarm \
    && mkdir -p /app \
    && chown swarm:swarm /app

COPY --from=build /opt/venv /opt/venv
COPY --from=build --chown=swarm:swarm /workspace/backend/apps/flight-engine/conf /app/conf

WORKDIR /app
USER 10001:10001

# The image flies the Missions of its edge and serves their live socket: it reads /app/conf/app.yaml.
ENTRYPOINT ["swarm-flight-engine-serve"]
