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

DAG_DESCRIPTIONS = {
    'daily_scraping': 'Scrape all people and committees, bills, and events "politely" – that is, with requests throttled to 60 per minute, or 1 per second. This generally takes 6-7 hours.',
    'windowed_bill_scraping': 'Scrape bills with a window of 0.05 at 5, 20, 35, and 50 minutes past the hour. Between 9 p.m. UTC Friday and 6 a.m. UTC Saturday, scrape bills with a window of 1 at 35 and 50 minutes past the hour. Windowed scrapes capture bills with timestamps within a given window or in the future. This generally takes somewhere between a few seconds and a few minutes, depending on the volume of updates.',
    'windowed_event_scraping': 'Scrape events with a window of 0.05 at 0, 15, 30, and 45 minutes past the hour. Between 9 p.m. UTC Friday and 6 a.m. UTC Saturday, scrape events with a window of 1 at 35 and 50 minutes past the hour. Windowed scrapes capture events with timestamps within a given window or in the future. This generally takes somewhere between a few seconds and a few minutes, depending on the volume of updates.',
    'fast_full_scraping': 'Scrape all events quickly on the hour and all bills quickly at 5 past the hour between 9 p.m. UTC Friday and 6 a.m. UTC Saturday. Fast scrapes scrape all bills or events quickly – that is, with requests issues as quickly as the server will respond to them. This generally takes less than 30 minutes.',
    'hourly_processing': 'Refresh the document cache, compile bill and event packets, extract attachment text, update the search index, and confirm the search index and database contain the same number of bills at 10, 25, 40, and 55 minutes past the hour.',
    'refresh_guid': 'Sync Metro subjects with SmartLogic terms once nightly.',
}
