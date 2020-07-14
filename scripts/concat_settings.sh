#!/bin/sh
set -e

echo $DECRYPTED_SETTINGS
echo $DESTINATION_SETTINGS

blackbox_postdeploy

if [ "$DECRYPTED_SETTINGS" != "$DESTINATION_SETTINGS" ]; then
    cp $DECRYPTED_SETTINGS $DESTINATION_SETTINGS
fi

cat airflow_configs/connection_settings.py >> $DESTINATION_SETTINGS

cat $DESTINATION_SETTINGS
