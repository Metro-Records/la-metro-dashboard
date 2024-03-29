from datetime import datetime
import os


ENVIRONMENT = os.getenv("AIRFLOW__SENTRY__ENVIRONMENT", "dev")

START_DATE = datetime(2020, 7, 15)

# Configure DAG container to connect to specific Docker network, useful for
# local development (not necessary in production)
DOCKER_NETWORK = os.getenv("DOCKER_NETWORK", None)

# Configure the location of the GPG keyring to mount into the container for
# decrypting secrets
GPG_KEYRING_PATH = os.getenv("GPG_KEYRING_PATH", "/home/datamade/.gnupg")

# Configure the Airflow directory path. For local development, this should
# be the root directory of your Airflow project. This has to be configured
# because the Docker daemon creates containers from the host, not from within
# the application container.
AIRFLOW_DIR_PATH = os.getenv(
    "AIRFLOW_DIR_PATH", os.path.join(os.path.abspath(os.path.dirname(__file__)), "..")
)

# Grab the correct image tag ('main' on staging, 'deploy' on production)
LA_METRO_DOCKER_IMAGE_TAG = os.getenv("LA_METRO_DOCKER_IMAGE_TAG", "main")
LA_SCRAPERS_DOCKER_IMAGE_TAG = os.getenv("LA_SCRAPERS_DOCKER_IMAGE_TAG", "main")

# URLs for Docker images
LA_SCRAPERS_IMAGE_URL = (
    f"ghcr.io/metro-records/scrapers-lametro:{LA_SCRAPERS_DOCKER_IMAGE_TAG}"
)
LA_METRO_IMAGE_URL = (
    f"ghcr.io/metro-records/la-metro-councilmatic:{LA_METRO_DOCKER_IMAGE_TAG}"
)

# Configure connection strings for the Metro database and Solr index
LA_METRO_DATABASE_URL = os.getenv(
    "LA_METRO_DATABASE_URL", "postgres://postgres:postgres@postgres:5432/lametro"
)
LA_METRO_STAGING_DATABASE_URL = os.getenv("LA_METRO_STAGING_DATABASE_URL", "")
LA_METRO_SEARCH_URL = os.getenv("LA_METRO_SEARCH_URL", "http://solr:8983/solr/lametro")

# Get AWS credentials
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "")

if LA_METRO_DOCKER_IMAGE_TAG == "main":
    DEPLOYMENT = "staging"
else:
    DEPLOYMENT = "production"

LA_METRO_CONFIGS = {
    "AWS_KEY": os.getenv("AWS_KEY"),
    "AWS_SECRET": os.getenv("AWS_SECRET"),
    "SMART_LOGIC_ENVIRONMENT": os.getenv("SMART_LOGIC_ENVIRONMENT"),
    "SMART_LOGIC_KEY": os.getenv("SMART_LOGIC_KEY"),
    "REFRESH_KEY": os.getenv("REFRESH_KEY"),
    "MERGE_HOST": os.getenv("MERGE_HOST"),
    "MERGE_ENDPOINT": os.getenv("MERGE_ENDPOINT")
}
