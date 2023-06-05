## Week 1 - basics and environment setups :

### 2 Docker and SQL
#### Dataset
dataset used for the week :  https://github.com/DataTalksClub/nyc-tlc-data/releases/tag/yellow

#### initiating postgres service with docker
docker run -it \
  -e POSTGRES_USER="root" \ 
  -e POSTGRES_PASSWORD="root" \
  -e POSTGRES_DB="ny_taxi" \
  -v $(pwd)/ny_taxi_postgres_data:/var/lib/postgresql/data \
  -p 5432:5432 \
postgres:13

If we get the error Error starting userland proxy: listen tcp4 0.0.0.0:5432: bind: address already in use.
just stop the running the postgres running locally : 
#sudo systemctl stop postgresql.service

#### Accessing postgres with pgcli
pgcli -h localhost -p 5432 -u root -d db_name

password migth be asked

#### Accessing postgres using docker and pgadmin
docker run -it \
-e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
-e PGADMIN_DEFAULT_PASSWORD="root" \
-p 8080:80 \
dpage/pgadmin4


#### Running pg specifying network
1. create network : docker network create pg-network

2. sart pg server :
docker run -it \
-e POSTGRES_USER="root" \
-e POSTGRES_PASSWORD="root" \
-e POSTGRES_DB="ny_taxi" \
-v $(pwd)/ny_taxi_postgres_data:/var/lib/postgresql/data \
-p 5432:5432 \
--network=pg-network \
--name pg-database \
postgres:13

#### Run pg_admin within the same network 
docker run -it \
-e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
-e PGADMIN_DEFAULT_PASSWORD="root" \
-p 8080:80 \
--network=pg-network \
--name pgadmin \
dpage/pgadmin4

we will be able to call pgg-database from pg_admin.

#### Convert a jupyter notebook into a python script :
jupyter nbconvert --to=script document_name.ipynb

#### Command to ingest data from python file:
created a google storage file, since the CSV from NYC website is no longer available.
URL="https://storage.googleapis.com/yello-taxi-data/yellow_tripdata_2021-01.csv"

python ingest_data.py \
--user=root \
--password=root \
--host=localhost \
--port=5432 \
--db=ny_taxi \
--table_name=yellow_taxi_data \
--url=${URL}

rebuilding the docker container after modifying the pipeline source file (replacing it with the ingest_data file)
it may be necessary to change the owner of the pg data repository : sudo chown -R $USER ny_taxi_postgres_data/

docker build -t taxi_ingest:v001 .

dockerizing the pipeline (-it makes it possible to kill the container from the terminal)

docker run -it --network=pg-network \
taxi_ingest:v001 \
--user=root \
--password=root \
--host=pg-database \
--port=5432 \
--db=ny_taxi \
--table_name=yellow_taxi_data \
--url=${URL}

if having trouble with postgres authorization, just kill tht pg-database (docker stop pg-database \docker rm pg-database) container and run it again. 

It will somehow solve the issue.

#### Docker compose is a setup that help puts all docker configuration into one file.
To install docker compose, follow the instruction here : https://docs.docker.com/compose/gettingstarted/
once the yaml file is configured, the command to launch it is :
1. docker-compose up 
or
2. docker compose up -d (to get the terminal back).

#### To stop the running compose : 
docker-compose down
