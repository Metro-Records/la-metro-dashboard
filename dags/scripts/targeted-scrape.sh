#!/bin/bash
set -e

conditionally_import_to_staging() {
    if [[ -n "$LA_METRO_STAGING_DATABASE_URL" ]]; then
        echo "Importing into staging database ${LA_METRO_STAGING_DATABASE_URL}"
        SHARED_DB=True LA_METRO_DATABASE_URL=$LA_METRO_STAGING_DATABASE_URL pupa update lametro --import || echo "${LA_METRO_STAGING_DATABASE_URL} does not exist"
    fi
}

if [[ -n "$WINDOW" ]]; then
    SHARED_DB=True \
        pupa update --datadir=/cache/$TARGET/_data/ lametro $TARGET \
        window=$WINDOW --rpm=$RPM
else
    SHARED_DB=True \
        pupa update --datadir=/cache/$TARGET/_data/ lametro $TARGET \
        --rpm=$RPM
fi

conditionally_import_to_staging
