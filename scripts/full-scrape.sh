#!/bin/sh
set -e

exec 2>&1

# Bills are windowed to 3 days by default. Scrape all people, all events, and
# windowed bills.
pupa update /scrapers-us-municipal/lametro --scrape
SHARED_DB=True pupa update /scrapers-us-municipal/lametro
pupa update /scrapers-us-municipal/lametro

# Scrape all bills.
pupa update /scrapers-us-municipal/lametro --scrape bills window=0
SHARED_DB=True pupa update /scrapers-us-municipal/lametro
pupa update /scrapers-us-municipal/lametro
