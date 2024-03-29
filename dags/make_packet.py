"""
Test config:
{
    "identifier": "2021-0530",
    "attachment_links":
    [
        "https://metro.legistar.com/ViewReport.ashx?M=R&N=TextL5&GID=557&ID=7916&GUID=LATEST&Title=Board+Report",
        "http://metro.legistar1.com/metro/attachments/53985307-4ce2-4688-83e0-42c4c7a17f0e.pdf",
        "http://metro.legistar1.com/metro/attachments/c96860a8-a26d-4022-9b6c-ca010c3d165e.docx"
    ]
}
"""
from datetime import timedelta

from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator

from constants import (
    START_DATE,
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    S3_BUCKET_NAME,
)


default_args = {
    "start_date": START_DATE,
    "execution_timeout": timedelta(minutes=5),
}

with DAG(
    "make_packet", default_args=default_args, schedule_interval=None, max_active_runs=1
) as dag:
    t1 = DockerOperator(
        task_id="make_packet",
        command='make upload_{{ dag_run.conf["identifier"] }}',
        image="ghcr.io/datamade/councilmatic-document-merger:latest",
        environment={
            "attachment_links": '{{ dag_run.conf["attachment_links"] }}',
            "AWS_DEFAULT_REGION": "us-east-1",
            "AWS_ACCESS_KEY_ID": AWS_ACCESS_KEY_ID,
            "AWS_SECRET_ACCESS_KEY": AWS_SECRET_ACCESS_KEY,
            "S3_BUCKET_NAME": S3_BUCKET_NAME,
        },
        force_pull=True,
        auto_remove=True,
    )
