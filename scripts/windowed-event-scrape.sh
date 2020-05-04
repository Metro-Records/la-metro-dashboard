#!/bin/sh
set -e

exec 2>&1

pupa update --datadir=/cache/events/_data/ lametro --scrape events window=$WINDOW
SHARED_DB=True pupa update --datadir=/cache/events/_data/ lametro
pupa update --datadir=/cache/events/_data/ lametro
