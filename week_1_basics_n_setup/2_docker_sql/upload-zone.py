#!/usr/bin/env python
# coding: utf-8

from sqlalchemy import create_engine
import pandas as pd
import os

#creating the CSV zone file
csv_zone = 'zone.csv'

#looking for the URL
url = 'https://d37ci6vzurychx.cloudfront.net/misc/taxi+_zone_lookup.csv'

#getting the file from the internet into the CSV file
os.system(f"wget {url} -O {csv_zone}")

#creating the dataframe from the CSV file
df = pd.read_csv(csv_zone)

#create the engine for postgres connection
engine = create_engine('postgresql://root:root@localhost:5432/ny_taxi')

#Creating the datadaframe, creating the table and inserting data to postgres
df.head(n=0).to_sql(name='zones', con=engine, if_exists='replace')
df.to_sql(name='zones', con=engine, if_exists='append')