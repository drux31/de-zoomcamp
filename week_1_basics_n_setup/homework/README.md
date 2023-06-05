### Homework from week 1
#### Question 1. Knowing docker tags
docker run -help | grep string
the answer is  : --iidfile string

#### Question 2. Understanding docker first run
-- docker run -it python:3.9 bash
-- pip list
the answer is 3

#### Prepare Postgres
##### Run Postgres and load data as shown in the videos We'll use the green taxi trips from January 2019:
wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-01.csv.gz
gzip -d green_tripdata_2019-01.csv.gz

You will also need the dataset with zones (I already loaded zones):

wget https://s3.amazonaws.com/nyc-tlc/misc/taxi+_zone_lookup.csv

#### Download this data and put it into Postgres (with jupyter notebooks or with a pipeline)

#### Question 3. Count records
How many taxi trips were totally made on January 15?
##### The query :
select count(*) 
from green_taxi_data 
where date(lpep_pickup_datetime) = '2019-01-15' and date(lpep_dropoff_datetime) = '2019-01-15';
##### The answer :
20530

#### Question 4. Largest trip for each day
Which was the day with the largest trip distance Use the pick up time for your calculations.
##### The query :
select lpep_pickup_datetime, sum(trip_distance)
from green_taxi_data
group by lpep_pickup_datetime
order by 2 desc
limit 1
##### The answer :
2019-01-15

#### Question 5. The number of passengers
In 2019-01-01 how many trips had 2 and 3 passengers?
##### The query :
select 
    (select count(*) from green_taxi_data where passenger_count = 2 and date(lpep_pickup_datetime) = '2019-01-01') as nb_trip_with_2_passengers, 
    (select count(*) from green_taxi_data where passenger_count = 3 and date(lpep_pickup_datetime) = '2019-01-01') as nb_trip_with_3_passengers ;
##### The answer :
2: 1282 ; 3: 254

#### Question 6. Largest tip
For the passengers picked up in the Astoria Zone which was the drop off zone that had the largest tip? We want the name of the zone, not the id.
##### The query :
select gt.tip_amount, z."Zone"
from green_taxi_data gt
join zones z on gt."DOLocationID" = z."LocationID"
where "PULocationID" = 7
order by 1 desc 
limit 1;
##### The answer : 
Long Island City/Queens Plaza
