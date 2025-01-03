#!/bin/bash

export DOCKER_BUILDKIT=1
export ENVIRONMENT=${1:-development}
export BACKEND_BASE_URL="http://host.docker.internal:8010"

git clone https://github.com/ministryofjustice/cla_backend ../cla_backend


echo "Running environment: $ENVIRONMENT"

docker compose down --remove-orphans

echo "Starting multi-container app"
docker compose -f compose.yml up --build -d

echo "Waiting for backend container to be ready..."
until docker exec cla_backend bash -c "echo 'Backend is ready'"; do
  echo "Waiting for backend container to be fully up..."
  sleep 5
done

echo "Running database creation script"
docker exec cla_backend bin/create_db.sh