#!/usr/bin/env bash
# Request (up) or close (down) the ephemeral dev cell of a branch.
#
# Usage: dev-cell.sh [--dry-run] up|down <branch>
#
# Environment:
#   DEV_CELL_BACKEND_CONFIG  Path of the Terraform backend configuration file (required, kept outside the repository).
#   DEV_CELL_VAR_FILE        Path of the dev-branch variables file (required, kept outside the repository).
#   DEV_CELL_TIMEOUT         Wait timeout for Argo CD (default 15m).
#   DEV_CELL_UNSIGNED_IMAGE  Image the cell must refuse, as it is not signed (default under ghcr.io/gpbcom/swarm/, never signed).
#   KUBECONFIG               Used by kubectl.
#
# Terraform is made non-interactive and reconfiguring through TF_INPUT and TF_CLI_ARGS_init, so that the printed
# commands stay short and the backend key of each branch is always taken into account.
set -euo pipefail

readonly CELL_DIR="infra/terraform/cells/dev-branch"
readonly SLUG_MAX=30
readonly HASH_LENGTH=8
readonly BAD_USAGE=2
readonly NAMESPACE="argocd"
readonly SYNC_PATH="{.status.sync.status}=Synced"
readonly HEALTH_PATH="{.status.health.status}=Healthy"
readonly DEFAULT_UNSIGNED_IMAGE="ghcr.io/gpbcom/swarm/unsigned-probe:never-signed"
readonly PROBE_NAME="swarm-unsigned-probe"

usage() {
  printf 'Usage: %s [--dry-run] up|down <branch>\n' "$(basename "$0")" >&2
}

fail() {
  printf '%s\n' "$1" >&2
  usage
  exit "${BAD_USAGE}"
}

sha256_of() {
  if command -v sha256sum >/dev/null 2>&1; then
    printf '%s' "$1" | sha256sum | cut -c1-"${HASH_LENGTH}"
  else
    printf '%s' "$1" | shasum -a 256 | cut -c1-"${HASH_LENGTH}"
  fi
}

cell_name_of() {
  local branch="$1" slug digest
  slug="$(printf '%s' "${branch}" | tr '[:upper:]' '[:lower:]' | LC_ALL=C sed -E 's/[^a-z0-9]+/-/g')"
  slug="${slug:0:${SLUG_MAX}}"
  while [[ "${slug}" == -* ]]; do slug="${slug#-}"; done
  while [[ "${slug}" == *- ]]; do slug="${slug%-}"; done
  digest="$(sha256_of "${branch}")"
  printf 'cell-%s-%s' "${slug}" "${digest}"
}

DRY_RUN=0

run() {
  if [[ "${DRY_RUN}" -eq 1 ]]; then
    local IFS=' '
    printf '+ %s\n' "$*"
  else
    "$@"
  fi
}

if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=1
  shift
fi

[[ $# -eq 2 ]] || fail "Expected an action and a branch."
ACTION="$1"
BRANCH="$2"
case "${ACTION}" in
  up | down) ;;
  *) fail "Unknown action: ${ACTION}." ;;
esac
[[ -n "${BRANCH}" ]] || fail "The branch is empty."
[[ -n "${DEV_CELL_BACKEND_CONFIG:-}" ]] || fail "DEV_CELL_BACKEND_CONFIG is not set."
[[ -n "${DEV_CELL_VAR_FILE:-}" ]] || fail "DEV_CELL_VAR_FILE is not set."
TIMEOUT="${DEV_CELL_TIMEOUT:-15m}"

cd "$(dirname "${BASH_SOURCE[0]}")/../.."

CELL="$(cell_name_of "${BRANCH}")"
STATE_KEY="dev-branch/${CELL}.tfstate"
export TF_INPUT=0
export TF_CLI_ARGS_init="-reconfigure"

terraform_run() {
  run terraform "-chdir=${CELL_DIR}" "$@"
}

terraform_init() {
  terraform_run init "-backend-config=${DEV_CELL_BACKEND_CONFIG}" "-backend-config=key=${STATE_KEY}"
}

terraform_verb() {
  terraform_run "$1" -auto-approve "-var-file=${DEV_CELL_VAR_FILE}" "-var=branch=${BRANCH}" "-var=cell_name=${CELL}"
}

wait_for() {
  run kubectl wait --namespace "${NAMESPACE}" "--for=jsonpath=$1" "application/${CELL}" "--timeout=${TIMEOUT}"
}

check_unsigned_image_refused() {
  local image="${DEV_CELL_UNSIGNED_IMAGE:-${DEFAULT_UNSIGNED_IMAGE}}"
  if [[ "${DRY_RUN}" -eq 1 ]]; then
    run kubectl run "${PROBE_NAME}" --namespace "${CELL}" "--image=${image}" --restart=Never --dry-run=server
  elif kubectl run "${PROBE_NAME}" --namespace "${CELL}" "--image=${image}" --restart=Never --dry-run=server; then
    printf 'Cell %s accepted an unsigned image: %s.\n' "${CELL}" "${image}" >&2
    exit 1
  else
    printf 'Cell %s refused the unsigned image %s.\n' "${CELL}" "${image}"
  fi
}

case "${ACTION}" in
  up)
    START="${SECONDS}"
    terraform_init
    terraform_verb apply
    wait_for "${SYNC_PATH}"
    wait_for "${HEALTH_PATH}"
    check_unsigned_image_refused
    printf 'Cell %s is ready after %d seconds.\n' "${CELL}" "$((SECONDS - START))"
    ;;
  down)
    terraform_init
    terraform_verb destroy
    ;;
esac
