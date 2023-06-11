FROM python:3.9

RUN apt-get install wget
RUN pip install pandas sqlalchemy psycopg2 prefect-gcp[cloud_storage] protobuf pyarrow pandas-gbq prefect_sqlalchemy

WORKDIR /app

COPY ingest_data.py ingest_data.py

ENTRYPOINT [ "python", "ingest_data.py" ]