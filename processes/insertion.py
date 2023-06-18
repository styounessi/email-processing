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

    # This is an inelegant and temporary solution that should be replaced at some point
    records = df.to_pandas().to_dict(orient='records') 
    
    combined_fields = ['from', 'subject', 'date']

    # Compound index (like a composite key in SQL) for duplicate record detection
    collection.create_index([(field, 1) for field in combined_fields],
                            unique=True)

    '''
    The idea below is to catch duplicate records from being inserted again. If a 
    BulkWriteError does happen, the parquet file should be investigated
    for duplicates compared to what already exists in the "emails" collection. 
    '''

    try:
        collection.insert_many(records, ordered=False)
    except BulkWriteError as bwe:
        print(bwe.details)
    else:
        print('Inserted records successfully.')

if __name__ == '__main__':
    main()
