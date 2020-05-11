#!/bin/sh
set -e

exec 2>&1

WINDOW={{params.window}}

(cd /scrapers-us-municipal/ &&
pupa update lametro bills window=$WINDOW --rpm=0)