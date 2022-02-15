'''
Override Postgres and Haystack connections for the scrapers and LA Metro
containers.
'''
import sys

import dj_database_url


DATABASE_URL = os.getenv('LA_METRO_DATABASE_URL', 'postgresql://postgres:postgres@postgres/lametro')

DATABASES = {
    'default': dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=600,
        engine='django.contrib.gis.db.backends.postgis'
    )
}

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        'URL': os.getenv('LA_METRO_SOLR_URL', 'http://solr:8983/solr/lametro'),
    },
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'format': '[%(asctime)s][%(levelname)s] %(name)s '
                      '%(filename)s:%(funcName)s:%(lineno)d | %(message)s',
            'datefmt': '%H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'console',
            'stream': sys.stdout
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG'
    },
    'loggers': {
        'lametro': {
            'handlers': ['console'],
            'propagate': False,
        },
    }
}
