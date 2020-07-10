'''
Override Postgres and Haystack connections for the scrapers and LA Metro
containers.
'''
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
