#!/bin/sh
set -e

WINDOW={{params.window}}
TARGET={{params.target}}
RPM={{params.rpm}}
SCRAPERS_DIR_PATH={{params.scrapers_dir_path}}

cd $SCRAPERS_DIR_PATH
pupa update --datadir=$SCRAPERS_DIR_PATH/cache/events/_data/ lametro --scrape $TARGET window=$WINDOW --rpm=$RPM
pupa update lametro --import
