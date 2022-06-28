#!/bin/sh
set -e

if [ "$AIRFLOW_MIGRATE" = 'on' ]; then
    airflow db init
    if [ `psql ${AIRFLOW__CORE__SQL_ALCHEMY_CONN} -tAX -c "SELECT COUNT(*) FROM ab_user"` -eq "0" ]; then
        airflow create_user -r Admin -u ${AIRFLOW_USERNAME} -p ${AIRFLOW_PASSWORD} -e team@datamade.us -f Airflow -l Admin
    fi
fi

exec "$@"
