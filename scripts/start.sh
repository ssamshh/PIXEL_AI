#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
source .venv/bin/activate
exec uvicorn pixel.api:app --host "${PIXEL_HOST:-127.0.0.1}" --port "${PIXEL_PORT:-8000}"
