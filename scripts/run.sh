#!/usr/bin/env bash
# Build the Docker image and run it locally.
# Usage: ./scripts/run.sh [--no-build]
#
# Prerequisites:
#   - .env file with API keys and AWS credentials (see .env.example)
#   - config.py edited with the symbols you want to analyse

set -uo pipefail

IMAGE_NAME="jyjulianwong-tradingagents-funds-runner"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

if [[ ! -f "$PROJECT_DIR/.env" ]]; then
  echo "ERROR: .env not found — copy .env.example to .env and fill in your keys"
  exit 1
fi

if [[ ! -f "$PROJECT_DIR/config.py" ]]; then
  echo "ERROR: config.py not found in project root"
  exit 1
fi

if [[ "${1:-}" != "--no-build" ]]; then
  echo "Building $IMAGE_NAME..."
  docker build -t "$IMAGE_NAME" "$PROJECT_DIR"
fi

REPORTS_DIR="$PROJECT_DIR/reports"
mkdir -p "$REPORTS_DIR"

echo "Starting run..."
docker run --rm \
  --env-file "$PROJECT_DIR/.env" \
  -v "$PROJECT_DIR/config.py:/app/config.py:ro" \
  -v "$REPORTS_DIR:/app/reports" \
  "$IMAGE_NAME"
