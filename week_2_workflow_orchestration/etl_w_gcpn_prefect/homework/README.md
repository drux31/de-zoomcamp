#### Question 1. Load January 2020 data
Loading green data to GCS
1. number of rows : 447770

#### Question 2. Scheduling with Cron
Using the flow in etl_web_to_gcs.py, create a deployment to run on the first of every month at 5am UTC. What’s the cron schedule for that?
1. the answer : 0 5 1 * *

#### Question 3. Loading data to BigQuery
Make sure you have the parquet data files for Yellow taxi data for Feb. 2019 and March 2019 loaded in GCS:
1. prefect deployment run etl-parent-flow/docker-flow -p "months=[2, 3]" -p "year=2019"

