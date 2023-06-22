import os
import glob

import polars as pl
from pymongo import MongoClient
from pymongo.errors import BulkWriteError

# Path to parquet files
PARQUET_FILE = '/opt/airflow/parquet/*.parquet'

def read_latest_file():
    '''
    Reads latest parquet file. If one is not available, an error
    is raised to stop the script.
    '''
    files = glob.glob(PARQUET_FILE)

    try:
        latest_file = max(files, key=os.path.getctime)
    except ValueError:
        raise FileNotFoundError('No file found: Check folder contents.')
    
    # Read in as Polars DataFrame
    df = pl.read_parquet(latest_file)
    return df

def mongo_collection():
    '''
    Connects to MongoDB instance and returns the "emails"
    collection object.
    '''
    client = MongoClient('mongodb://mongodb:27017/')
    db = client['productDB']
    collection = db['emails']
    return collection

def main():
    '''
    Main function to read the latest parquet file, create a compound
    index, and insert new records into "emails" collection while skipping
    any duplicate records detected.
    '''
    df = read_latest_file()
    collection = mongo_collection()

    records = df.to_dicts()
    
    combined_fields = ['from', 'subject', 'date']

    # Compound index (like a composite key in SQL) for duplicate record detection
    collection.create_index([(field, 1) for field in combined_fields],
                            unique=True)

    '''
    The idea below is to catch existing records from being inserted again. If a 
    'BulkWriteError' does happen, it will print which record(s) were caught so
    they can be investigated further.
    '''

    try:
        insertion = collection.insert_many(records, ordered=False)
        num_records = len(insertion.inserted_ids)
    except BulkWriteError as bwe:
        num_records = bwe.details['nInserted']
        print(bwe.details)

    print(f'Total records inserted: {num_records}.')

if __name__ == '__main__':
    main()
