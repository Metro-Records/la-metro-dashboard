#!/bin/bash
set -e

conditionally_import_to_staging() {
    if [[ -n "$LA_METRO_STAGING_DATABASE_URL" ]]; then
        echo "Importing into staging database ${LA_METRO_STAGING_DATABASE_URL}"
        SHARED_DB=True DATABASE_URL=$LA_METRO_STAGING_DATABASE_URL pupa update lametro --import || echo "${LA_METRO_STAGING_DATABASE_URL} does not exist"
    fi
}

# Bills are windowed to 3 days by default. Scrape all people and all events.
pupa update lametro --scrape people events
SHARED_DB=True DATABASE_URL=$LA_METRO_DATABASE_URL pupa update lametro --import
conditionally_import_to_staging

# Scrape all bills.
pupa update lametro --scrape bills window=0
SHARED_DB=True DATABASE_URL=$LA_METRO_DATABASE_URL pupa update lametro --import
conditionally_import_to_staging
