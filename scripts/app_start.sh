#!/bin/bash
set -euo pipefail

# Make sure the deployment group specific variables are available to this
# script.
source ${BASH_SOURCE%/*}/../configs/$DEPLOYMENT_GROUP_NAME-config.conf

# Re-read supervisor config, and add new processes
echo "Reloading supervisor"
supervisorctl update $APP_NAME $APP_NAME-scheduler

echo "Reloading nginx"
nginx -t
service nginx reload || service nginx start
