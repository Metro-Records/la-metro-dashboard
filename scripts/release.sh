#!/bin/bash

set -euo pipefail

# Run migrations.
airflow initdb

# Check if initial data exists, and if not, run initial imports.
if [ `psql ${DATABASE_URL} -tAX -c "SELECT COUNT(*) FROM users"` -eq "0" ]; then
    python scripts/init_db.py
fi
