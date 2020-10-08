from datetime import timedelta

from dags.constants import LA_METRO_STAGING_DATABASE_URL


SCRAPING_DAGS = {
    'windowed_bill_scrape': {
        'schedule_interval': [
            '5,20,35,50 * * * 0-4',
            '5,20,35,50 0-20 * * 5',
            '5,20,35,50 6-23 * * 6',
        ],
        'execution_timeout': timedelta(hours=1),
        'command': 'scraper_scripts/targeted-scrape.sh',
        'docker_environment': {
            'TARGET': 'bills',
            'WINDOW': 0.05,
        },
    },
    'fast_windowed_bill_scrape': {
        'schedule_interval': [
            '35,50 21-23 * * 5',
            '35,50 0-5 * * 6',
        ],
        'execution_timeout': timedelta(hours=1),
        'command': 'scraper_scripts/targeted-scrape.sh',
        'docker_environment': {
            'TARGET': 'bills',
            'WINDOW': 1,
            'RPM': 0,
        },
    },
    'fast_full_bill_scrape': {
        'schedule_interval': [
            '5 21-23 * * 5',
            '5 0-5 * * 6',
        ],
        'execution_timeout': timedelta(hours=1),
        'command': 'scraper_scripts/targeted-scrape.sh',
        'docker_environment': {
            'TARGET': 'bills',
            'WINDOW': 0,
            'RPM': 0,
        },
    },
    'full_scrape': {
        'schedule_interval': ['5 0 * * 0-5'],
        'execution_timeout': timedelta(hours=12),
        'command': 'scraper_scripts/full-scrape.sh',
        'docker_environment': {
            'LA_METRO_STAGING_DATABASE_URL': LA_METRO_STAGING_DATABASE_URL,
        },
    },
    # etc.
}