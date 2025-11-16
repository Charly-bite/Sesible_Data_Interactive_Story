#!/usr/bin/env bash
# Helper to start the local Flask app and ngrok tunnel
# Usage:
#   ./scripts/ngrok.sh    # serve on 5000 and open ngrok
# Optional args: PORT (defaults to 5000) and NGROK_BIN (path to ngrok)
set -euo pipefail

PORT=${1:-5000}
NGROK_BIN=${NGROK_BIN:-$(command -v ngrok || echo "")}
# Fallback: look for a bin/ngrok that our installer created
if [ -z "$NGROK_BIN" ]; then
  if [ -x "$(pwd)/bin/ngrok" ]; then
    NGROK_BIN="$(pwd)/bin/ngrok"
  elif [ -x "./bin/ngrok" ]; then
    NGROK_BIN="./bin/ngrok"
  fi
fi

if [ -z "$NGROK_BIN" ]; then
  echo "ngrok not found on PATH. Try ./scripts/install_ngrok.sh or set NGROK_BIN to the path of an ngrok binary." >&2
  exit 2
fi

# Prefer the project virtualenv Python if it exists
PYTHON_CMD="$(command -v python3 || echo "python3")"
if [ -x ".venv/bin/python" ]; then
  PYTHON_CMD=".venv/bin/python"
fi

echo "Starting local server on port $PORT ($PYTHON_CMD api.py)"
# Start the Flask dev server in background to make it easy to tear down
$PYTHON_CMD api.py &
APP_PID=$!

echo "Server started (pid=$APP_PID); starting ngrok..."
nohup "$NGROK_BIN" http "$PORT" --log=stdout > /tmp/ngrok.log 2>&1 &
NGROK_PID=$!

trap 'echo "Stopping ngrok and server..."; kill $NGROK_PID || true; kill $APP_PID || true; exit' INT TERM EXIT

echo "Waiting for ngrok to initialize (this may take a few seconds)"
sleep 2

# Query the local ngrok API to get the public URL
if command -v curl >/dev/null 2>&1; then
  TUNNELS_JSON=$(curl -s http://127.0.0.1:4040/api/tunnels || true)
else
  TUNNELS_JSON=""
fi

if [ -n "$TUNNELS_JSON" ]; then
  # parse with python to avoid jq dependency
  PUB=$(python3 - <<PY
import sys, json
try:
    j = json.loads(sys.stdin.read())
    tunnels = j.get('tunnels') or []
    if not tunnels:
        sys.exit(2)
    print(tunnels[0].get('public_url', ''))
except Exception:
    sys.exit(2)
PY
  ) <<< "$TUNNELS_JSON"
  echo "Public URL: ${PUB:-(not available yet)}"
else
  echo "ngrok running but could not query http://127.0.0.1:4040. Check /tmp/ngrok.log for details" >&2
fi

echo "Open the public URL in your browser and log in (use auth.json.example or set env variables for creds)."

# Keep script running to preserve processes
wait
