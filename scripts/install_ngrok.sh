#!/usr/bin/env bash
# Small helper to download the latest ngrok for Linux x86_64 and install it under ./bin
# Usage: ./scripts/install_ngrok.sh
set -euo pipefail
OUT_DIR="$(pwd)/bin"
mkdir -p "$OUT_DIR"

if command -v ngrok >/dev/null 2>&1; then
  echo "ngrok already installed on PATH. Aborting." 
  exit 0
fi

echo "Downloading ngrok (linux/amd64)..."
TMPFILE=$(mktemp)
trap 'rm -f "$TMPFILE"' EXIT

URL="https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip"
curl -fsSL "$URL" -o "$TMPFILE"
unzip -q "$TMPFILE" -d "$OUT_DIR"
chmod +x "$OUT_DIR/ngrok"

cat <<EOF
ngrok downloaded to $OUT_DIR/ngrok.
Add $OUT_DIR to your PATH if you want to run it system-wide (for example: export PATH=\"$OUT_DIR:\$PATH\")
To use ngrok, sign up for an account at https://ngrok.com and run:

  $OUT_DIR/ngrok authtoken <your-token>

Then start a tunnel to your local server:

  $OUT_DIR/ngrok http 5000

EOF

exit 0
