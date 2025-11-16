#!/usr/bin/env bash
# Small helper to download a private data.db from AWS S3 into $DATA_DIRECTORY
# Usage: DATA_DIRECTORY=/opt/render/project/data ./scripts/fetch_db_from_s3.sh s3://mybucket/path/to/data.db

set -euo pipefail

if [ $# -ne 1 ]; then
  echo "Usage: $0 s3://bucket/key/to/data.db"
  exit 2
fi

S3_PATH="$1"

: ${DATA_DIRECTORY:=./Data}
mkdir -p "$DATA_DIRECTORY"

echo "Downloading $S3_PATH into $DATA_DIRECTORY/data.db..."

# Use aws cli (recommended) — make sure AWS_ACCESS_KEY_ID & AWS_SECRET_ACCESS_KEY are set in the environment
if command -v aws >/dev/null 2>&1; then
  echo "Using aws s3 cp..."
  aws s3 cp "$S3_PATH" "$DATA_DIRECTORY/data.db"
  echo "Downloaded to $DATA_DIRECTORY/data.db"
  exit 0
fi

# Fallback: try curl with a pre-signed URL if provided
if echo "$S3_PATH" | grep -q "https://"; then
  echo "Detected https URL — using curl"
  curl -fSL "$S3_PATH" -o "$DATA_DIRECTORY/data.db"
  echo "Downloaded to $DATA_DIRECTORY/data.db"
  exit 0
fi

echo "No aws cli found and no https url provided; please install aws-cli or provide a presigned url"
exit 1
