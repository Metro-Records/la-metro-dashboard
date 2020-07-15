#!/bin/sh
set -e

pupa update --datadir=/cache/$TARGET/_data/ lametro --scrape $TARGET window=$WINDOW --rpm=$RPM
DATABASE_URL=$LA_METRO_DATABASE_URL pupa update --datadir=/cache/$TARGET/_data/ lametro --import
