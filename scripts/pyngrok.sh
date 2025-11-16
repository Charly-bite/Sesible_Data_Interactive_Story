#!/usr/bin/env bash
# Small wrapper to start the Flask server and create an ngrok tunnel using pyngrok.
set -euo pipefail
PORT=${1:-5000}
: ${NGROK_AUTH_TOKEN:=}

if [ -x ".venv/bin/python" ]; then
  PY=.venv/bin/python
else
  PY=python3
fi

echo "Using python: $PY"
echo "Ensure your venv is activated if you want environment isolation."

export NGROK_AUTH_TOKEN=${NGROK_AUTH_TOKEN}

"$PY" scripts/pyngrok_start.py "$PORT"
