#!/usr/bin/env bash
# Start PX4 SITL instance 0 with headless Gazebo.
# PX4 v1.16 binds its GCS MAVLink link on UDP 18570 + instance and answers the address it receives from.
set -euo pipefail

PX4_ROOT="${PX4_HOME:-/opt/px4}"
PX4_BUILD="${PX4_ROOT}/build/px4_sitl_default"
ROOTFS="${PX4_BUILD}/rootfs"

export HEADLESS="${HEADLESS:-1}"
export PX4_SIM_MODEL="${PX4_SIM_MODEL:-gz_x500}"
export PX4_GZ_MODELS="${PX4_ROOT}/Tools/simulation/gz/models"
export PX4_GZ_WORLDS="${PX4_ROOT}/Tools/simulation/gz/worlds"
export PX4_GZ_SERVER_CONFIG="${PX4_ROOT}/Tools/simulation/gz/server.config"

mkdir -p "${ROOTFS}/0"
cd "${ROOTFS}/0"

exec "${PX4_BUILD}/bin/px4" -i 0 -d "${PX4_BUILD}/etc" "$@"
