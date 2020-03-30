#!/bin/sh
set -e

if [ "$AIRFLOW_MIGRATE" = 'on' ]; then
    airflow initdb
fi

exec "$@"