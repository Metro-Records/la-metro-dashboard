#!/bin/bash

# Cause the entire deployment to fail if something in this script exits with
# a non-zero exit code. This will make debugging your deployment much simpler.
# Read more about this here: http://redsymbol.net/articles/unofficial-bash-strict-mode/

set -euo pipefail

# Make directory for project
mkdir -p /home/datamade/la-metro-dashboard
