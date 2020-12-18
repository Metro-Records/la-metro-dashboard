#!/bin/bash
#
# Scrape and import data to the production database and, if a connection string
# is defined, the staging database.
#
# N.b., we append a definition for DATABASE_URL to pupa_settings.py that sources
# the value from the LA_METRO_DATABASE_URL environment variable. This variable
# is set to the production database URI in the Supervisor config, i.e., we do
# not need to pass a value for the production scrape and import. We set it
# equal to the staging database connection string for the staging import.

set -e

conditionally_import_to_staging() {
    if [[ -n "$LA_METRO_STAGING_DATABASE_URL" ]]; then
        SHARED_DB=True LA_METRO_DATABASE_URL=$LA_METRO_STAGING_DATABASE_URL \
            pupa update --datadir=/cache/$TARGET/_data/ lametro --import $TARGET \
            || echo "${LA_METRO_STAGING_DATABASE_URL} does not exist"

        echo "Imported into staging database ${LA_METRO_STAGING_DATABASE_URL}"
    else
        echo 'No value set for $LA_METRO_STAGING_DATABASE_URL'
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

echo "Scraped and imported into production database ${LA_METRO_DATABASE_URL}"

conditionally_import_to_staging
