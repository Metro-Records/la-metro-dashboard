#!/bin/bash
set -e

import_to_staging() {
    # If the database URL does not contain "staging", it's the production
    # database. Append "_staging" and import. Assumes that the staging and
    # production databases live on the same server, and follow the naming
    # convention "${DATABASE_NAME}" and "${DATABASE_NAME}_staging".
    if [[ "$DATABASE_URL" != *"staging"* ]]; then
        STAGING_DATABASE_URL="${LA_METRO_DATABASE_URL}_staging"
        echo "Importing into staging database ${STAGING_DATABASE_URL}"
        SHARED_DB=True DATABASE_URL=$STAGING_DATABASE_URL pupa update lametro --import || echo "${STAGING_DATABASE_URL} does not exist"
    fi
}

# Bills are windowed to 3 days by default. Scrape all people, all events, and
# windowed bills.
pupa update lametro --scrape
SHARED_DB=True DATABASE_URL=$LA_METRO_DATABASE_URL pupa update lametro --import
import_to_staging

# Scrape all bills.
pupa update lametro --scrape bills window=0
DATABASE_URL=$LA_METRO_DATABASE_URL pupa update lametro --import
import_to_staging
