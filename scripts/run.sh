#!/usr/bin/env bash
# Build the Docker image and run it locally.
# Usage: ./scripts/run.sh [--no-build]
#
# Prerequisites:
#   - .env file with API keys (see .env.example)
#   - an active AWS CLI session for the account to upload to (e.g. `aws sso login`)
#     — its temporary credentials are passed into the container; no access keys
#     live in .env
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

# Short-lived credentials from whatever the AWS CLI is signed in as (SSO,
# profile, ...), handed to the container as env vars for this run only.
AWS_CREDENTIALS_ENV="$(aws configure export-credentials --format env-no-export)" || {
  echo "ERROR: no working AWS credentials — run \`aws sso login\` (or set AWS_PROFILE) first"
  exit 1
}
ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)" || exit 1

# Default the reports bucket to the account's (terraform/main.tf:
# "<account ID>-jyjulianwong-tafr-reports") unless .env sets one.
BUCKET_ARGS=()
if ! grep -qE '^AWS_S3_REPORTS_BUCKET_NAME=.+' "$PROJECT_DIR/.env"; then
  BUCKET_ARGS=(-e "AWS_S3_REPORTS_BUCKET_NAME=${ACCOUNT_ID}-jyjulianwong-tafr-reports")
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
  --env-file <(printf '%s\n' "$AWS_CREDENTIALS_ENV") \
  ${BUCKET_ARGS[@]+"${BUCKET_ARGS[@]}"} \
  -v "$PROJECT_DIR/config.py:/app/config.py:ro" \
  -v "$REPORTS_DIR:/app/reports" \
  "$IMAGE_NAME"
