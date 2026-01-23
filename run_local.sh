#!/usr/bin/env bash
set -e

export DOCKER_BUILDKIT=1
export ENVIRONMENT="${1:-development}"

BACKEND_REPO_URL="https://github.com/ministryofjustice/cla_backend"
BACKEND_DIR="${BACKEND_DIR:-../cla_backend}"

# Use local backend if present, otherwise clone into a temp dir
if [ ! -f "$BACKEND_DIR/docker-compose.yaml" ]; then
  echo "Backend not found at $BACKEND_DIR — cloning..."
  TMP_DIR="$(mktemp -d)"
  git clone --depth 1 "$BACKEND_REPO_URL" "$TMP_DIR/cla_backend"
  BACKEND_DIR="$TMP_DIR/cla_backend"
fi

export CLA_BACKEND_DIR="$(cd "$BACKEND_DIR" && pwd)"
BACKEND_COMPOSE_FILE="$CLA_BACKEND_DIR/docker-compose.yaml"

echo "Running environment: $ENVIRONMENT"
echo "Using backend: $CLA_BACKEND_DIR"

docker compose \
  -f compose-standalone.yml \
  -f "$BACKEND_COMPOSE_FILE" \
  -f compose-backend-path.override.yml \
  down --remove-orphans

docker compose \
  -f compose-standalone.yml \
  -f "$BACKEND_COMPOSE_FILE" \
  -f compose-backend-path.override.yml \
  up -d --build

# Wait like backend repo does
docker compose \
  -f compose-standalone.yml \
  -f "$BACKEND_COMPOSE_FILE" \
  -f compose-backend-path.override.yml \
  run --rm start_applications

docker exec cla_backend bash -lc "bin/create_db.sh"

echo "Done. Web should be on http://localhost:8020"
