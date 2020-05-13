#!/bin/sh
set -e

WINDOW={{params.window}}
TARGET={{params.target}}
RPM={{params.rpm}}

(cd /scrapers-us-municipal/ &&
pupa update --datadir=/cache/events/_data/ lametro --scrape $TARGET window=$WINDOW --rpm=$RPM &&
pupa update lametro --import)