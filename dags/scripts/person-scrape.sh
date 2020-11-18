#!/bin/bash
set -e

conditionally_import_to_staging() {
    if [[ -n "$LA_METRO_STAGING_DATABASE_URL" ]]; then
        echo "Importing into staging database ${LA_METRO_STAGING_DATABASE_URL}"
        SHARED_DB=True DATABASE_URL=$LA_METRO_STAGING_DATABASE_URL pupa update lametro --import || echo "${LA_METRO_STAGING_DATABASE_URL} does not exist"
    fi
}

# Scrape people
pupa update lametro --scrape people
SHARED_DB=True DATABASE_URL=$LA_METRO_DATABASE_URL pupa update lametro --import
conditionally_import_to_staging