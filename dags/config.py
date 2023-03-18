from datetime import timedelta

from dags.constants import LA_METRO_STAGING_DATABASE_URL


SCRAPING_DAGS = {
    'windowed_bill_scrape': {
        'description': (
            'Scrape bills with a window of 0.05 at 5, 20, 35, and 50 minutes '
            'past the hour. This generally takes somewhere between a few '
            'seconds and a few minutes, depending on the volume of updates.'
        ),
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
            'RPM': 60,
        },
    },
    'fast_windowed_bill_scrape': {
        'description': (
            'Scrape bills with a window of 1 at 35 and 50 minutes past the '
            'hour. This generally takes somewhere between a few seconds and a '
            'few minutes, depending on the volume of updates.'
        ),
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
        'description': (
            'Scrape all bills quickly at 5 past the hour. This generally takes '
            'less than 30 minutes.'
        ),
        'schedule_interval': [
            '5 21-23 * * 5',
            '5 0-5 * * 6',
        ],
        'execution_timeout': timedelta(minutes=90),
        'command': 'scraper_scripts/targeted-scrape.sh',
        'docker_environment': {
            'TARGET': 'bills',
            'WINDOW': 0,
            'RPM': 0,
        },
    },
    'windowed_event_scrape': {
        'description': (
            'Scrape events with a window of 0.05 at 0, 15, 30, and 45 minutes '
            'past the hour. This generally takes somewhere between a few '
            'seconds and a few minutes, depending on the volume of updates.'
        ),
        'schedule_interval': [
            '0,15,30,45 * * * 0-4',
            '0,15,30,45 0-20 * * 5',
            '0,15,30,45 6-23 * * 6',
        ],
        'execution_timeout': timedelta(hours=1),
        'command': 'scraper_scripts/targeted-scrape.sh',
        'docker_environment': {
            'TARGET': 'events',
            'WINDOW': 0.05,
            'RPM': 60,
        },
    },
    'fast_windowed_event_scrape': {
        'description': (
            'Scrape events with a window of 1 at 35 and 50 minutes past the '
            'hour. This generally takes somewhere between a few seconds and a '
            'few minutes, depending on the volume of updates.'
        ),
        'schedule_interval': [
            '30,45 21-23 * * 5',
            '30,45 0-5 * * 6',
        ],
        'execution_timeout': timedelta(hours=1),
        'command': 'scraper_scripts/targeted-scrape.sh',
        'docker_environment': {
            'TARGET': 'events',
            'WINDOW': 1,
            'RPM': 0,
        },
    },
    'fast_full_event_scrape': {
        'description': (
            'Scrape all events quickly on the hour. This generally takes less '
            'than 30 minutes.'
        ),
        'schedule_interval': [
            '0 21-23 * * 5',
            '0 0-5 * * 6',
        ],
        'execution_timeout': timedelta(hours=1),
        'command': 'scraper_scripts/targeted-scrape.sh',
        'docker_environment': {
            'TARGET': 'events',
            'WINDOW': 0,
            'RPM': 0,
        },
    },
    'person_scrape': {
        'description': (
            'Scrape all people and committees. Run in lieu of full scrape on '
            'Fridays, when all bills and events are scraped once an hour.'
        ),
        'schedule_interval': [
            '5 3 * * 6',
        ],
        'execution_timeout': timedelta(hours=1),
        'command': 'scraper_scripts/targeted-scrape.sh',
        'docker_environment': {
            'TARGET': 'people',
            'RPM': 60,
        },
    },
}
