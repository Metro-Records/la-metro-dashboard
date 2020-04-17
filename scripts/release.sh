#!/bin/bash
airflow initdb
airflow webserver --port \$PORT