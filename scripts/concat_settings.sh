#!/bin/sh
set -e

blackbox_postdeploy

if [ "$DECRYPTED_SETTINGS" != "$DESTINATION_SETTINGS" ]; then
    cp $DECRYPTED_SETTINGS $DESTINATION_SETTINGS
fi

cat airflow_configs/connection_settings.py >> $DESTINATION_SETTINGS
