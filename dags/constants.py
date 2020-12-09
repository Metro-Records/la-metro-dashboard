from datetime import datetime
import os


START_DATE = datetime(2020, 7, 15)

# Configure DAG container to connect to specific Docker network, useful for
# local development (not necessary in production)
DOCKER_NETWORK = os.getenv('DOCKER_NETWORK', None)

# Configure the location of the GPG keyring to mount into the container for
# decrypting secrets
GPG_KEYRING_PATH = os.getenv('GPG_KEYRING_PATH', '/home/datamade/.gnupg')

# Configure the Airflow directory path. For local development, this should
# be the root directory of your Airflow project. This has to be configured
# because the Docker daemon creates containers from the host, not from within
# the application container.
AIRFLOW_DIR_PATH = os.getenv(
    'AIRFLOW_DIR_PATH',
    os.path.join(os.path.abspath(os.path.dirname(__file__)), '..')
)

# Configure connection strings for the Metro database and Solr index
LA_METRO_DATABASE_URL = os.getenv('LA_METRO_DATABASE_URL', 'postgres://postgres:postgres@postgres:5432/lametro')
LA_METRO_STAGING_DATABASE_URL = os.getenv('LA_METRO_STAGING_DATABASE_URL', '')
LA_METRO_SOLR_URL = os.getenv('LA_METRO_SOLR_URL', 'http://solr:8983/solr/lametro')

# Grab the correct image tag ('staging' on staging, 'production' on production)
LA_METRO_DOCKER_IMAGE_TAG = os.getenv('LA_METRO_DOCKER_IMAGE_TAG', 'staging')
