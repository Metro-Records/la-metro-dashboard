#!/bin/sh
set -e

exec 2>&1

(cd /scrapers-us-municipal/ &&
update --datadir=/cache/people/_data/ lametro --scrape people &&
SHARED_DB=True update --datadir=/cache/people/_data/ lametro people &&
update --datadir=/cache/people/_data/ lametro people)