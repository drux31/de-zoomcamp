FROM prefecthq/prefect:2.10.12-python3.9

RUN pip install pandas prefect-gcp[cloud_storage] protobuf pyarrow pandas-gbq --trusted-host pypi.python.org --no-cache-dir

COPY flows /opt/prefect/flows
COPY data /opt/prefect/data


