import os
import glob

import polars as pl
from pymongo import MongoClient
from pymongo.errors import BulkWriteError


# Parquet file location
PROCESSED_FILES = '/opt/airflow/parquet/processed_files/*.parquet'


def latest_parquet():
    '''
    Reads latest parquet file. Raises an error if no file is available.
    '''
    files = glob.glob(PROCESSED_FILES)

    try:
        latest_file = max(files, key=os.path.getctime)
    except ValueError:
        raise FileNotFoundError('No new file available.')
  
    return latest_file


def mongo_collection():
    '''
    Connects to MongoDB instance and returns the "emails"
    collection object.
    '''
    client = MongoClient('mongodb://mongodb:27017/')
    db = client['productDB']
    collection = db['emails']
    
    return client, collection


def process_and_insert_to_mongo():
    '''
    Read the latest parquet file, create a compound index, and insert
    new records into "emails" collection while skipping any duplicate
    records detected.
    '''
    lf = pl.scan_parquet(latest_parquet())
    records = lf.collect().to_dicts()
    
    client, collection = mongo_collection()

    combined_fields = ['from', 'subject', 'date']

    # Compound index (like a composite key in SQL) for duplicate record detection
    collection.create_index(
        [(field, 1) for field in combined_fields],
        unique=True
    )

    # Records are inserted and the number of records is printed
    try:
        insertion = collection.insert_many(records, ordered=False)
        num_records = len(insertion.inserted_ids)
    
    # If a 'BulkWriteError' does happen, print which record(s) were caught
    except BulkWriteError as bwe:
        num_records = bwe.details['nInserted']
        print(bwe.details)

    print(f'Total records inserted: {num_records}.')

    client.close()


if __name__ == '__main__':
    process_and_insert_to_mongo()
