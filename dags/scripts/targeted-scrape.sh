#!/bin/bash
set -e

SHARED_DB=True DATABASE_URL=$LA_METRO_DATABASE_URL pupa update --datadir=/cache/$TARGET/_data/ lametro $TARGET window=$WINDOW --rpm=$RPM
