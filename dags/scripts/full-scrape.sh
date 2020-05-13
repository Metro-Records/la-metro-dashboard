#!/bin/sh
set -e

(cd /scrapers-us-municipal/ &&
# Bills are windowed to 3 days by default. Scrape all people, all events, and
# windowed bills.
pupa update lametro --scrape &&
pupa update lametro --import &&

# Scrape all bills.
pupa update lametro --scrape bills window=0 &&
pupa update lametro --import)