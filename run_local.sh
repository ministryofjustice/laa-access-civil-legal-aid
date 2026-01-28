#!/usr/bin/env bash
set -euo pipefail

export DOCKER_BUILDKIT=1
export ENVIRONMENT="${1:-development}"

BACKEND_REPO_URL="https://github.com/ministryofjustice/cla_backend"
BACKEND_DIR="${BACKEND_DIR:-../cla_backend}"
CACHE_DIR=".tmp/cla_backend"

# Use local backend if present, otherwise use cached backend, otherwise clone into cache
if [ -f "$BACKEND_DIR/docker-compose.yaml" ]; then
  echo "Using local backend at: $BACKEND_DIR"
elif [ -f "$CACHE_DIR/docker-compose.yaml" ]; then
  echo "Using cached backend at: $CACHE_DIR"
  BACKEND_DIR="$CACHE_DIR"
else
  echo "Backend not found at $BACKEND_DIR — cloning into $CACHE_DIR..."
  mkdir -p "$(dirname "$CACHE_DIR")"
  git clone --depth 1 "$BACKEND_REPO_URL" "$CACHE_DIR"
  BACKEND_DIR="$CACHE_DIR"
fi

if [ "${UPDATE_BACKEND:-0}" = "1" ] && [ "$BACKEND_DIR" = "$CACHE_DIR" ]; then
  echo "Refreshing cached backend in $CACHE_DIR..."
  (cd "$CACHE_DIR" && git fetch --depth 1 origin && git reset --hard origin/main)
fi

export CLA_BACKEND_DIR="$(cd "$BACKEND_DIR" && pwd)"
BACKEND_COMPOSE_FILE="$CLA_BACKEND_DIR/docker-compose.yaml"

# Helper function to run docker compose with multiple files
compose() {
  docker compose \
    -f compose-standalone.yml \
    -f "$BACKEND_COMPOSE_FILE" \
    -f compose-backend-path.override.yml \
    "$@"
}

compose down --remove-orphans
compose up -d --build
compose run --rm start_applications

docker exec cla_backend bash -lc "bin/create_db.sh"

echo "Done. Web should be on http://localhost:8020"
