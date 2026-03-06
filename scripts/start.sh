#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "${SCRIPT_DIR}")"

cd "${PROJECT_DIR}"

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
TIMEOUT_GRACEFUL_SHUTDOWN="${TIMEOUT_GRACEFUL_SHUTDOWN:-1}"
LOG_CONFIG="${LOG_CONFIG:-${PROJECT_DIR}/logging.conf}"
APP_MODULE="${APP_MODULE:-app.api:app}"

echo "Starting server on ${HOST}:${PORT}"
echo "App: ${APP_MODULE}"
echo "Project dir: ${PROJECT_DIR}"
echo "Graceful shutdown timeout: ${TIMEOUT_GRACEFUL_SHUTDOWN}s"
echo "Log config: ${LOG_CONFIG}"

# Activate virtual environment
if [[ -f "${PROJECT_DIR}/.venv/bin/activate" ]]; then
    # shellcheck disable=SC1091
    source "${PROJECT_DIR}/.venv/bin/activate"
else
    echo "Virtual environment not found at ${PROJECT_DIR}/.venv"
    exit 1
fi

CMD=(
    uvicorn "${APP_MODULE}"
    --host "${HOST}"
    --port "${PORT}"
    --timeout-graceful-shutdown "${TIMEOUT_GRACEFUL_SHUTDOWN}"
    --log-config "${LOG_CONFIG}"
)

exec "${CMD[@]}"