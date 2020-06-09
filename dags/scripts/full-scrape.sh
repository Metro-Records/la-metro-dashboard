#!/bin/sh
set -e

SCRAPERS_DIR_PATH={{params.scrapers_dir_path}}
LA_METRO_DATABASE_URL={{params.la_metro_database_url}}

cd $SCRAPERS_DIR_PATH
# Bills are windowed to 3 days by default. Scrape all people, all events, and
# windowed bills.
pupa update lametro --scrape
DATABASE_URL=$LA_METRO_DATABASE_URL pupa update lametro --import

# Scrape all bills.
pupa update lametro --scrape bills window=0
DATABASE_URL=$LA_METRO_DATABASE_URL pupa update lametro --import
