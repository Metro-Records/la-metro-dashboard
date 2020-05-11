#!/bin/sh
set -e

exec 2>&1

(cd /scrapers-us-municipal/ &&
pupa update --datadir=/cache/events/_data/ lametro --scrape events --rpm=0 &&
SHARED_DB=True pupa update --datadir=/cache/events/_data/ lametro &&
pupa update --datadir=/cache/events/_data/ lametro)