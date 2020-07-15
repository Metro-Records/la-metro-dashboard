#!/bin/sh
#
# Try to decrypt application secrets using the local GPG keychain. If
# decryption fails, fall back to using the example settings file (for Metro)
# or the existing settings file (for the scrapers).
set -e

(
    echo "Attempting to decrypt application secrets"
    blackbox_postdeploy

    if [ "$DECRYPTED_SETTINGS" != "$DESTINATION_SETTINGS" ]; then
        cp $DECRYPTED_SETTINGS $DESTINATION_SETTINGS
    fi
) || (
    echo "Falling back to example settings file"
    test $DESTINATION_SETTINGS || cp $DESTINATION_SETTINGS.example $DESTINATION_SETTINGS
)

cat airflow_configs/connection_settings.py >> $DESTINATION_SETTINGS
