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

#Getting the data from GCS
@task(log_prints=True, retries=3)
def extract_from_gcs(color: str, year: int, month: int) -> Path:
    """Download trip data from GCS"""
    gcs_path = f"data/{color}/{color}_tripdata_{year}-{month:02}.parquet"
    gcs_block = GcsBucket.load("zoom-gcs")
    gcs_block.get_directory(from_path=gcs_path, local_path=f"data/")
    return Path(f"data/{gcs_path}")

@task(log_prints=True)
def write_bq(path: Path, color: str) -> pd.DataFrame:
    """Write DataFrame to BigQuery"""
    df = pd.read_parquet(path)
    df.to_gbq(
        destination_table=f"dezoomcamp.{color}_rides",
        project_id="prefect-de-zoomcamp-drux",
        credentials=gcp_credentials_block.get_credentials_from_service_account(),
        chunksize=500_000,
        if_exists="append",
    )

    return df

@flow()
def etl_gcs_to_bq(year: int, month: int, color: str) -> int:
    """Main ETL flow to load data into BigQuery"""
    path = extract_from_gcs(color, year, month)
    #df = transform(path)
    df = write_bq(path, color)

    return df.shape[0]

@flow(log_prints=True, retries=3)
def etl_main(months: list[int] = [1,], year: int = 2020, color: str = "green") -> None:
    nbRows = 0
    for month in months:
        nbRows += etl_gcs_to_bq(year, month, color)
    print(f"Number of rows processed : {nbRows}")

if __name__ == "__main__":
    etl_main()