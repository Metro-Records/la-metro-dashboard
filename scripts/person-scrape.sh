#!/bin/sh
set -e

exec 2>&1

update --datadir=/cache/people/_data/ /scrapers-us-municipal/lametro --scrape people
SHARED_DB=True update --datadir=/cache/people/_data/ /scrapers-us-municipal/lametro people
update --datadir=/cache/people/_data/ /scrapers-us-municipal/lametro people
