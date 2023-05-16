#!/bin/bash
set -euo pipefail

# Make sure the deployment group specific variables are available to this
# script.
source ${BASH_SOURCE%/*}/../configs/$DEPLOYMENT_GROUP_NAME/deployment.cfg

echo "Stopping supervisor process"
supervisorctl stop $APP_NAME $APP_NAME-scheduler
