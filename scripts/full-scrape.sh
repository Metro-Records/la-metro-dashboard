#!/bin/sh
set -e

exec 2>&1

# Bills are windowed to 3 days by default. Scrape all people, all events, and
# windowed bills.
pupa update lametro --scrape
SHARED_DB=True pupa update lametro
pupa update lametro

# Scrape all bills.
pupa update lametro --scrape bills window=0
SHARED_DB=True pupa update lametro
pupa update lametro
