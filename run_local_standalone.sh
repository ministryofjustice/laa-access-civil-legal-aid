#!/bin/bash
export DOCKER_BUILDKIT=1
docker compose -f compose-standalone.yml up --build