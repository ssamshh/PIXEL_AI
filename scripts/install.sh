#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
command -v python3 >/dev/null || { echo "Install Python 3 first."; exit 1; }
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
[[ -f .env ]] || cp .env.example .env
echo
echo "PIXEL 3.0 installed."
echo "Start with: source .venv/bin/activate && uvicorn pixel.api:app --host 127.0.0.1 --port 8000"
echo "Open: http://127.0.0.1:8000/app"
