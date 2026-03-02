#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Add project root to Python path
export PYTHONPATH="${SCRIPT_DIR}/..:$PYTHONPATH"

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
RELOAD="${RELOAD:-true}"
TIMEOUT_GRACEFUL_SHUTDOWN="${TIMEOUT_GRACEFUL_SHUTDOWN:-1}"
LOG_CONFIG="${LOG_CONFIG:-${SCRIPT_DIR}/logging.conf}"
APP_MODULE="${APP_MODULE:-app.api:app}"

echo "🚀 Starting server on ${HOST}:${PORT}..."
echo "   App: ${APP_MODULE}"
echo "   Reload: ${RELOAD}"
echo "   Graceful shutdown timeout: ${TIMEOUT_GRACEFUL_SHUTDOWN}s"
echo "   Log config: ${LOG_CONFIG}"

source "${SCRIPT_DIR}/.venv/bin/activate"

CMD=(
  uvicorn "${APP_MODULE}"
  --host "${HOST}"
  --port "${PORT}"
  --timeout-graceful-shutdown "${TIMEOUT_GRACEFUL_SHUTDOWN}"
  --log-config "${LOG_CONFIG}"
)

if [[ "${RELOAD}" == "true" ]]; then
  CMD+=(--reload)
fi

exec "${CMD[@]}"