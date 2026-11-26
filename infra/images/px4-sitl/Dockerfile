# syntax=docker/dockerfile:1.7
# PX4 SITL with headless Gazebo Harmonic, one instance per container.

ARG PX4_VERSION=v1.16.0

FROM px4io/px4-dev-simulation-jammy:2024-05-18 AS builder

ARG PX4_VERSION

WORKDIR /src

RUN git clone --branch "${PX4_VERSION}" --depth 1 --recurse-submodules --shallow-submodules \
    https://github.com/PX4/PX4-Autopilot.git PX4-Autopilot

WORKDIR /src/PX4-Autopilot

RUN HEADLESS=1 make px4_sitl_default

FROM ubuntu:22.04 AS runtime

ENV DEBIAN_FRONTEND=noninteractive \
    HEADLESS=1 \
    PX4_SIM_MODEL=gz_x500 \
    PX4_HOME=/opt/px4

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl gnupg lsb-release \
    && curl -fsSL https://packages.osrfoundation.org/gazebo.gpg -o /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" \
        > /etc/apt/sources.list.d/gazebo-stable.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends gz-harmonic libgl1 libglu1-mesa xvfb \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /src/PX4-Autopilot/build/px4_sitl_default /opt/px4/build/px4_sitl_default
COPY --from=builder /src/PX4-Autopilot/Tools/simulation/gz /opt/px4/Tools/simulation/gz
COPY infra/images/px4-sitl/entrypoint.sh /usr/local/bin/entrypoint.sh

RUN groupadd --system --gid 10001 px4 \
    && useradd --system --uid 10001 --gid px4 --home-dir /home/px4 --create-home --shell /usr/sbin/nologin px4 \
    && chmod 0755 /usr/local/bin/entrypoint.sh \
    && chown -R px4:px4 /opt/px4

WORKDIR /opt/px4
USER 10001:10001

EXPOSE 18570/udp

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
