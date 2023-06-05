#!/usr/bin/env python
# coding: utf-8

import argparse
import os

from time import time

import pandas as pd
from sqlalchemy import create_engine

def main(params):
    user = params.user
    password = params.password
    host = params.host
    port = params.port
    db = params.db
    table_name = params.table_name
    url = params.url

    csv_name = 'output.csv'

    #dowload the CSV
    os.system(f"wget {url} -O {csv_name}")

    #Creating engine for SQL alchemy connection to postgres
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')

    #creating the data frame iteration
    df_iter = pd.read_csv(csv_name, iterator=True, chunksize=100000)

    #reading the next iteration
    df = next(df_iter)

    #preprocessing to convert some columns into datetime
    #in order to correspond to the type known by postgres
    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

    # Creating the table from the first line of the CSV file
    df.head(n=0).to_sql(name=table_name, con=engine, if_exists='replace')

    df.to_sql(name=table_name, con=engine, if_exists='append')

    #infinite loop for inserting the data by batch into postgres
    while True:
        t_start = time()
        
        df = next(df_iter)
        
        df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
        df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
        
        df.to_sql(name=table_name, con=engine, if_exists='append')
        
        t_end = time()
        
        print('inserted another chunk..., took %.3f seconds' % (t_end - t_start))

if __name__ == '__main__':
    #parsing argument
    #initiating parser
    parser = argparse.ArgumentParser(description='Ingest CSV data to postgres')

    #Arguments used :
    #>user, 
    #>password, 
    #>host, 
    #>port, 
    #>dbname, 
    #>table name, 
    #>url of the csv
    parser.add_argument('--user', help='user name for postgres')
    parser.add_argument('--password', help='password for postgres')
    parser.add_argument('--host', help='host for postgres')
    parser.add_argument('--port', help='port for postgres')
    parser.add_argument('--db', help='database name for postgres')
    parser.add_argument('--table_name', help='name of the table where we will write to ingested data')
    parser.add_argument('--url', help='url of the CSV file')

    #parse arguments
    args = parser.parse_args()
    
    main(args)
