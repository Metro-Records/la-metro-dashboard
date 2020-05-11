#!/bin/sh
set -e

exec 2>&1

(cd /scrapers-us-municipal/ &&
pupa update lametro bills window=1 --rpm=0)