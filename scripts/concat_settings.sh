#!/bin/sh
set -e

blackbox_postdeploy
cp configs/settings_deployment.staging.py councilmatic/settings_deployment.py
cat airflow_configs/connection_settings.py >> councilmatic/settings_deployment.py

cat councilmatic/settings_deployment.py
