#!/bin/sh
set -e

if [ "$AIRFLOW_MIGRATE" = 'on' ]; then
    airflow initdb
    if [ `psql ${DATABASE_URL} -tAX -c "SELECT COUNT(*) FROM users"` -eq "0" ]; then
        python scripts/init_db.py
    fi
fi


exec "$@"
