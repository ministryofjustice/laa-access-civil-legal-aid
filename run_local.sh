#!/bin/bash

export DOCKER_BUILDKIT=1
export ENVIRONMENT=${1:-development}
export BACKEND_BASE_URL="http://host.docker.internal:8010"

git clone https://github.com/ministryofjustice/cla_backend ../cla_backend


echo "Running environment: $ENVIRONMENT"

docker compose down --remove-orphans

if ! docker images -q govuk-frontend-standalone; then
  echo "The 'govuk-frontend-standalone' image is not found locally. Building it now..."
  docker compose -f compose.yml -f compose-standalone.yml up --build -d
else
  echo "'govuk-frontend-standalone' image already exists. Starting containers without rebuilding."
  docker compose -f compose.yml -f compose-standalone.yml up -d
fi

echo "Waiting for backend container to be ready..."
until docker exec cla_backend bash -c "echo 'Backend is ready'"; do
  echo "Waiting for backend container to be fully up..."
  sleep 5
done

echo "Running database creation script"
docker exec cla_backend bin/create_db.sh