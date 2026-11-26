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

WORKDIR /workspace/packages/rust

COPY packages/rust /workspace/packages/rust

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

COPY pyproject.toml uv.lock README.md ./
COPY packages/python packages/python
COPY services/flight-engine services/flight-engine

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-editable --package swarm-flight-engine

COPY --from=wheel /wheels /wheels

RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --python /opt/venv/bin/python --no-deps /wheels/*.whl

FROM python:3.12.16-slim-bookworm AS runtime

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    SWARM_FLIGHT_ENGINE_HOME=/app

RUN groupadd --system --gid 10001 swarm \
    && useradd --system --uid 10001 --gid swarm --home-dir /app --shell /usr/sbin/nologin swarm \
    && mkdir -p /app \
    && chown swarm:swarm /app

COPY --from=build /opt/venv /opt/venv
COPY --from=build --chown=swarm:swarm /workspace/services/flight-engine/conf /app/conf

WORKDIR /app
USER 10001:10001

ENTRYPOINT ["swarm-flight-engine", "--config", "conf/app.yaml"]
