#!/usr/bin/env python3
"""Download a file from S3 into DATA_DIRECTORY using boto3.

Usage:
  python scripts/fetch_db_from_s3.py s3://mybucket/path/to/data.db

This script expects environment AWS creds or an IAM role provided by Render.
"""
import os
import sys
import urllib.parse
import boto3
from botocore.exceptions import ClientError


def parse_s3_url(s3_url: str):
    if not s3_url.startswith("s3://"):
        raise ValueError("s3_url must start with 's3://'")
    path = s3_url[len("s3://"):]
    parts = path.split('/', 1)
    bucket = parts[0]
    key = parts[1] if len(parts) == 2 else ''
    return bucket, key


def main(argv):
    if len(argv) != 2:
        print("Usage: python scripts/fetch_db_from_s3.py s3://bucket/key")
        return 2

    s3_url = argv[1]
    bucket, key = parse_s3_url(s3_url)
    data_dir = os.environ.get('DATA_DIRECTORY', './Data')
    os.makedirs(data_dir, exist_ok=True)

    local_path = os.path.join(data_dir, 'data.db')
    s3 = boto3.client('s3')

    print(f"Downloading s3://{bucket}/{key} to {local_path} ...")
    try:
        s3.download_file(bucket, key, local_path)
    except ClientError as e:
        print("Failed to download from S3:", e)
        return 1

    print("Downloaded to", local_path)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
