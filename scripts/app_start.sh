#!/bin/bash
set -euo pipefail

# Make sure the deployment group specific variables are available to this
# script.
source ${BASH_SOURCE%/*}/../configs/$DEPLOYMENT_GROUP_NAME-config.conf

# Re-read supervisor config, and add new processes
echo "Reloading supervisor"
supervisorctl reread $APP_NAME $APP_NAME-scheduler

# Add or start the dashboard process groups. Add does not throw a non-zero exit
# code if the process group exists, so grep the add output for the message
# indicating the groups have already been added and conditionally start them.
# (Adding a new process group starts it, so it is redundant to call start in
# that case.)
supervisorctl add $APP_NAME $APP_NAME-scheduler | grep 'process group already active' && supervisorctl start $APP_NAME $APP_NAME-scheduler

echo "Reloading nginx"
nginx -t
service nginx reload || service nginx start
