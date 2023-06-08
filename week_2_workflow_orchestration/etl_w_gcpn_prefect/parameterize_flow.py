from pathlib import Path
import pandas as pd
from prefect import flow, task
from prefect.tasks import task_input_hash
from datetime import timedelta

from prefect_gcp.cloud_storage import GcsBucket
gcp_cloud_storage_bucket_block = GcsBucket.load("zoom-gcs")

@task(log_prints=True, retries=3, cache_key_fn=task_input_hash, cache_expiration=timedelta(days=1))
def fetch(dataset_url: str) -> pd.DataFrame:
    """Read data from web into pandas DataFrame"""
    #if randint(0, 1) > 0:
    #    raise Exception

    df = pd.read_csv(dataset_url)
    return df

@task(log_prints=True)
def clean(df = pd.DataFrame) -> pd.DataFrame:
    """Fix dtype issues"""
    df['tpep_pickup_datetime'] = pd.to_datetime(df['tpep_pickup_datetime'])
    df['tpep_dropoff_datetime'] = pd.to_datetime(df['tpep_dropoff_datetime'])

    print(df.head(2))
    print(f"columns: {df.dtypes}")
    print(f"rows: {len(df)}")
    return df

@task(log_prints=True)
def write_local(df: pd.DataFrame, color: str, dataset_file: str) -> Path:
    """Wite DataFrame out"""
    path = Path(f"data/{color}/{dataset_file}.parquet")
    df.to_parquet(path, compression="gzip")
    return path

@task(log_prints=True)
def write_gcs(path: Path) -> None:
    """Uploading local parquet file to GCS"""
    gcs_block = GcsBucket.load("zoom-gcs")
    gcs_block.upload_from_path(
        from_path=f"{path}",
        to_path=path
    )    


@flow()
def etl_web_to_gcs(year: int, month: int, color: str) -> None:
    """ Thuis is the main ETL function """
    dataset_file = f"{color}_tripdata_{year}-{month:02}"
    dataset_url = f"https://github.com/DataTalksClub/nyc-tlc-data/releases/download/{color}/{dataset_file}.csv.gz"

    df = fetch(dataset_url)
    df_clean = clean(df)
    path = write_local(df_clean, color, dataset_file)
    write_gcs(path)


@flow(log_prints=True)
def etl_parent_flow(months: list[int] = [1, 2], year: int = 2021, color: str = "yellow") -> None :
    for month in months:
        etl_web_to_gcs(year, month, color)
    

if __name__ == '__main__':
    color = "yellow"
    months = [1, 2, 3]
    year = 2021
    etl_parent_flow(months, year, color)