import os
import logging

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from google.cloud import storage
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateExternalTableOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
import pyarrow.csv as pv
import pyarrow.parquet as pq
import gzip


PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
BUCKET = os.environ.get("GCP_GCS_BUCKET")
color = "yellow"
year = 2021
month = 1
dataset_file = f"{color}_tripdata_{year}-{month:02}"


#Fetch the data
dataset_url = f"https://github.com/DataTalksClub/nyc-tlc-data/releases/download/{color}/{dataset_file}.csv.gz"

path_to_local_home = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")
parquet_file = dataset_file.replace('.csv.gz', '.parquet')

BIGQUERY_DATASET = os.environ.get("BIGQUERY_DATASET", 'trips_data_all')


def format_to_parquet(src_file):
    if not src_file.endswith('.csv.gz'):
        logging.error("Can only accept source files in CSV format, for the moment")
        return
    table = pv.read_csv(src_file)
    pq.write_table(table, src_file.replace('.csv.gz', '.parquet'))


# NOTE: takes 20 mins, at an upload speed of 800kbps. Faster if your internet has a better upload speed
def upload_to_gcs(bucket, object_name, local_file):
    """
    Ref: https://cloud.google.com/storage/docs/uploading-objects#storage-upload-object-python
    :param bucket: GCS bucket name
    :param object_name: target path & file-name
    :param local_file: source path & file-name
    :return:
    """
    # WORKAROUND to prevent timeout for files > 6 MB on 800 kbps upload speed.
    # (Ref: https://github.com/googleapis/python-storage/issues/74)
    storage.blob._MAX_MULTIPART_SIZE = 5 * 1024 * 1024  # 5 MB
    storage.blob._DEFAULT_CHUNKSIZE = 5 * 1024 * 1024  # 5 MB
    # End of Workaround

    client = storage.Client()
    bucket = client.bucket(bucket)

    blob = bucket.blob(object_name)
    blob.upload_from_filename(local_file)


default_args = {
    "owner": "airflow",
    "start_date": days_ago(1),
    "depends_on_past": False,
    "retries": 1,
}

# NOTE: DAG declaration - using a Context Manager (an implicit way)
with DAG(
    dag_id="data_ingestion_gcs_dag",
    schedule_interval="@daily",
    default_args=default_args,
    catchup=False,
    max_active_runs=1,
    tags=['dtc-de'],
) as dag:

    download_dataset_task = BashOperator(
        task_id="download_dataset_task",
        bash_command=f"curl -sSL {dataset_url} > {path_to_local_home}/{dataset_file}"
    )

    format_to_parquet_task = PythonOperator(
        task_id="format_to_parquet_task",
        python_callable=format_to_parquet,
        op_kwargs={
            "src_file": f"{path_to_local_home}/{dataset_file}",
        },
    )

    # TODO: Homework - research and try XCOM to communicate output values between 2 tasks/operators
    local_to_gcs_task = PythonOperator(
        task_id="local_to_gcs_task",
        python_callable=upload_to_gcs,
        op_kwargs={
            "bucket": BUCKET,
            "object_name": f"raw/{parquet_file}",
            "local_file": f"{path_to_local_home}/{parquet_file}",
        },
    )

    """
    bigquery_external_table_task = BigQueryCreateExternalTableOperator(
        task_id="bigquery_external_table_task",
        table_resource={
            "tableReference": {
                "projectId": PROJECT_ID,
                "datasetId": BIGQUERY_DATASET,
                "tableId": "external_table",
            },
            "externalDataConfiguration": {
                "sourceFormat": "PARQUET",
                "sourceUris": [f"gs://{BUCKET}/raw/{parquet_file}"],
            },
        },
    )
    """
    """
    bigquery_external_table_task = BigQueryCreateExternalTableOperator(
        task_id="bigquery_external_table_task",
        destination_project_dataset_table=f"{BIGQUERY_DATASET}.external_table",
        bucket=BUCKET,
        source_objects= [f"gs://{BUCKET}/raw/{parquet_file}"],
         schema_fields=[
        {"name": "VendorID", "type": "INTEGER", "mode": "REQUIRED"},
        {"name": "tpep_pickup_datetime", "type": "TIMESTAMP", "mode": "NULLABLE"},
        {"name": "tpep_dropoff_datetime", "type": "TIMESTAMP", "mode": "NULLABLE"},
        {"name": "passenger_count", "type": "INTEGER", "mode": "NULLABLE"},
        {"name": "trip_distance", "type": "FLOAT", "mode": "NULLABLE"},
        {"name": "RatecodeID", "type": "FLOAT", "mode": "NULLABLE"},
        {"name": "store_and_fwd_flag", "type": "STRING", "mode": "NULLABLE"},
        {"name": "PULocationID", "type": "INTEGER", "mode": "NULLABLE"},
        {"name": "DOLocationID", "type": "INTEGER", "mode": "NULLABLE"},
        {"name": "payment_type", "type": "INTEGER", "mode": "NULLABLE"},
        {"name": "fare_amount", "type": "FLOAT", "mode": "NULLABLE"},
        {"name": "extra", "type": "FLOAT", "mode": "NULLABLE"},
        {"name": "mta_tax", "type": "FLOAT", "mode": "NULLABLE"},
        {"name": "tip_amount", "type": "FLOAT", "mode": "NULLABLE"},
        {"name": "tolls_amount", "type": "FLOAT", "mode": "NULLABLE"},
        {"name": "improvement_surcharge", "type": "FLOAT", "mode": "NULLABLE"},
        {"name": "total_amount", "type": "FLOAT", "mode": "NULLABLE"},
        {"name": "congestion_surcharge", "type": "FLOAT", "mode": "NULLABLE"},
    ],
    )
    """

    bigquery_external_table_task = BigQueryCreateExternalTableOperator(
        task_id="bigquery_external_table_task",
        table_resource={
            "tableReference": {
                "projectId": PROJECT_ID,
                "datasetId": BIGQUERY_DATASET,
                "tableId": "external_table",
            },
            "schema": {
                "fields": [
                    {"name": "VendorID", "type": "INTEGER", "mode": "REQUIRED"},
                    {"name": "tpep_pickup_datetime", "type": "TIMESTAMP", "mode": "NULLABLE"},
                    {"name": "tpep_dropoff_datetime", "type": "TIMESTAMP", "mode": "NULLABLE"},
                    {"name": "passenger_count", "type": "INTEGER", "mode": "NULLABLE"},
                    {"name": "trip_distance", "type": "FLOAT", "mode": "NULLABLE"},
                    {"name": "RatecodeID", "type": "FLOAT", "mode": "NULLABLE"},
                    {"name": "store_and_fwd_flag", "type": "STRING", "mode": "NULLABLE"},
                    {"name": "PULocationID", "type": "INTEGER", "mode": "NULLABLE"},
                    {"name": "DOLocationID", "type": "INTEGER", "mode": "NULLABLE"},
                    {"name": "payment_type", "type": "INTEGER", "mode": "NULLABLE"},
                    {"name": "fare_amount", "type": "FLOAT", "mode": "NULLABLE"},
                    {"name": "extra", "type": "FLOAT", "mode": "NULLABLE"},
                    {"name": "mta_tax", "type": "FLOAT", "mode": "NULLABLE"},
                    {"name": "tip_amount", "type": "FLOAT", "mode": "NULLABLE"},
                    {"name": "tolls_amount", "type": "FLOAT", "mode": "NULLABLE"},
                    {"name": "improvement_surcharge", "type": "FLOAT", "mode": "NULLABLE"},
                    {"name": "total_amount", "type": "FLOAT", "mode": "NULLABLE"},
                    {"name": "congestion_surcharge", "type": "FLOAT", "mode": "NULLABLE"},
                ]
            },
            "externalDataConfiguration": {
                "sourceFormat": "PARQUET",
                "compression": "GZIP",
                "sourceUris": [f"gs://{BUCKET}/raw/{parquet_file}"],
                #"csvOptions": {"skipLeadingRows": 1},
            },
        },
        bucket=BUCKET,
        #source_objects=[DATA_SAMPLE_GCS_OBJECT_NAME],
    )

    download_dataset_task >> format_to_parquet_task >> local_to_gcs_task >> bigquery_external_table_task

    """
    VendorID	tpep_pickup_datetime	tpep_dropoff_datetime	passenger_count	trip_distance	RatecodeID	store_and_fwd_flag	PULocationID	
    DOLocationID	payment_type	fare_amount	extra	mta_tax	tip_amount	tolls_amount	improvement_surcharge	total_amount	congestion_surcharge

    """