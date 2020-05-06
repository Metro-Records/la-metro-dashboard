#!/bin/sh
set -e

exec 2>&1

pupa update --datadir=/cache/events/_data/ /scrapers-us-municipal/lametro --scrape events --rpm=0
SHARED_DB=True pupa update --datadir=/cache/events/_data/ /scrapers-us-municipal/lametro
pupa update --datadir=/cache/events/_data/ /scrapers-us-municipal/lametro
