#### procedure for a pipeline :
1. get the data from the web (wget for example) (extraction)
2. transform the data for correctness (transformation) - transform the csv file to parquet ans save it locally
3. ingest the data to database or cloud storage (loading)
4. upload data to bigquery from GCS.

those steps are called jobs, and each job depends on the state of the previous one.

DAG = Directed Acyclic Graph : one directionnal job execution / Data workflow = data pipeline


