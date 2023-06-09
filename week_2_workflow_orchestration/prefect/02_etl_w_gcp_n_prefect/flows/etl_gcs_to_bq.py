"""
Before running prefect command localy, one needs to start orion to enable the connection using the block
prefect orion start
"""
from pathlib import Path
import pandas as pd
from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket

from prefect_gcp import GcpCredentials
gcp_cloud_storage_bucket_block = GcsBucket.load("zoom-gcs")
gcp_credentials_block = GcpCredentials.load("zoom-gcp-creds")

@task(log_prints=True, retries=3)
def extract_from_gcs(color: str, year: int, month: int) -> Path:
    """Download trip data from GCS"""
    gcs_path = f"data/{color}/{color}_tripdata_{year}-{month:02}.parquet"
    gcs_block = GcsBucket.load("zoom-gcs")
    gcs_block.get_directory(from_path=gcs_path, local_path=f"../data/")
    return Path(f"../data/{gcs_path}")

@task(log_prints=True, retries=3)
def transform(path: Path) -> pd.DataFrame:
    """Data cleaning example"""
    df = pd.read_parquet(path)
    print(f"pre: missing passenger count: {df['passenger_count'].isna().sum()}")
    df['passenger_count'].fillna(0, inplace=True)
    print(f"post: missing passenger count: {df['passenger_count'].isna().sum()}")
    return df


@task(log_prints=True)
def write_bq(df: pd.DataFrame) -> None:
    """Write DataFrame to BigQuery"""

    df.to_gbq(
        destination_table="dezoomcap.rides",
        project_id="prefect-de-zoomcamp-drux",
        credentials=gcp_credentials_block.get_credentials_from_service_account(),
        chunksize=500_000,
        if_exists="append",
    )

@flow()
def etl_gcs_to_bg():
    """Main ETL flow to load data into BigQuery"""
    color = "yellow"
    year = 2021
    month = 1

    path = extract_from_gcs(color, year, month)
    df = transform(path)
    write_bq(df)


if __name__ == "__main__":
    etl_gcs_to_bg()