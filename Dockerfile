FROM python:3.7

LABEL maintainer "DataMade <info@datamade.us>"

# Install Docker
RUN apt-get update && \
    apt-get install -y \
      apt-transport-https \
      ca-certificates \
      curl \
      gnupg-agent \
      software-properties-common \
      postgresql-client && \
    rm -rf /var/lib/apt/lists/* && \
    curl -fsSL https://get.docker.com -o get-docker.sh && \
    sh get-docker.sh

RUN mkdir /app
WORKDIR /app

ARG AIRFLOW_VERSION=2.6.0
ARG PYTHON_VERSION=3.7
ARG CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"

COPY ./requirements.txt /app/requirements.txt

RUN pip install "apache-airflow[s3,docker]==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}" && \
  pip install --no-cache-dir -r requirements.txt

COPY . /app
