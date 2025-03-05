#!/bin/bash
set -e

: "${FLASK_RUN_PORT:=8000}"
: "${GUNICORN_WORKERS:=4}"

exec gunicorn --bind "0.0.0.0:$FLASK_RUN_PORT" --workers "$GUNICORN_WORKERS" "app:create_app()"
