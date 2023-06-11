#### Question 1. Load January 2020 data
Loading green data to GCS
1. number of rows : 447770

#### Question 2. Scheduling with Cron
Using the flow in etl_web_to_gcs.py, create a deployment to run on the first of every month at 5am UTC. What’s the cron schedule for that?
1. the answer : 0 5 1 * *

#### Question 3. Loading data to BigQuery
Make sure you have the parquet data files for Yellow taxi data for Feb. 2019 and March 2019 loaded in GCS:
1. prefect deployment run etl-parent-flow/docker-flow -p "months=[2, 3]" -p "year=2019"

After parameterization of etl_gcs_bq python script, load the yellow data from march and february 2019 to bigquery:
1. test the script by loading the green data to BQ : python homework/etl_gcs_to_bq.py
2. create the deployement : prefect deployment build ./homework/etl_gcs_to_bq.py:etl_main -n "homework-etl"
3. apply the deployment : prefect deployment apply etl_main-deployment.yaml
4. run the deployment to insert the data from 2019 (yellow) to bigquery: prefect deployment run etl-main/homework-etl -p "months=[2, 3]" -p "year=2019" -p "color=yellow"

Run your deployment to append this data to your BiqQuery table. How many rows did your flow code process?
1. the answer : 14851920
