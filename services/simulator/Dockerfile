# syntax=docker/dockerfile:1.7
# Build context: the repository root, because the shared lock file is there.

FROM rust:1.91.1-slim-bookworm AS rust

WORKDIR /workspace/rust

COPY rust /workspace/rust

RUN cargo build --release --locked -p swarm-synthetic-drones

FROM python:3.12.16-slim-bookworm AS python

COPY --from=ghcr.io/astral-sh/uv:0.12.21 /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/opt/venv

WORKDIR /workspace

COPY pyproject.toml uv.lock README.md ./
COPY packages/python packages/python
COPY backend/libs backend/libs
COPY services/simulator services/simulator

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable --package swarm-simulator

FROM python:3.12.16-slim-bookworm AS runtime

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

RUN groupadd --system --gid 10001 swarm \
    && useradd --system --uid 10001 --gid swarm --home-dir /app --shell /usr/sbin/nologin swarm \
    && mkdir -p /app/services/simulator \
    && chown -R swarm:swarm /app

COPY --from=python /opt/venv /opt/venv
COPY --from=rust /workspace/rust/target/release/swarm-synthetic-drones /usr/local/bin/swarm-synthetic-drones
COPY services/simulator/conf/ /app/services/simulator/conf/

WORKDIR /app/services/simulator
USER 10001:10001

ENTRYPOINT ["swarm-simulator"]
CMD ["serve"]
