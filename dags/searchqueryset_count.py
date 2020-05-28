from datetime import datetime, timedelta

from airflow import DAG

from base import DjangoOperator

default_args = {
    'start_date': datetime.now() - timedelta(hours=1),
    'execution_timeout': timedelta(minutes=1)
}

dag = DAG(
    'searchqueryset_count',
    default_args=default_args,
    schedule_interval=None
)


def searchqueryset_count():
    # Importing Haystack requires Django settings to be configured, so delay
    # the import until DAG runtime
    from haystack.query import SearchQuerySet
    print(len(SearchQuerySet().all()))
    return len(SearchQueryset().all())


searchqueryset_count = DjangoOperator(
    task_id='searchqueryset_count',
    dag=dag,
    python_callable=searchqueryset_count
)
