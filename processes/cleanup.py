import os
import glob
import datetime


# Path to parquet files
RAW_FILES = '/opt/airflow/parquet/raw_files/*.parquet'
PROCESSED_FILES = '/opt/airflow/parquet/processed_files/*.parquet'


# Default retention period is 7 days
def parquet_cleaner(retention_days=7):
    '''
    Searches for parquet files older than the given retention
    period and scrubs them from the folders.
    '''
    today = datetime.date.today()
    retention_period = datetime.timedelta(days=retention_days)

    raw_files = glob.glob(RAW_FILES)
    
    for file in raw_files:
        creation_date = datetime.date.fromtimestamp(os.path.getctime(file))
        if (today - creation_date) > retention_period:
            os.remove(file)

    processed_files = glob.glob(PROCESSED_FILES)
    
    for file in processed_files:
        creation_date = datetime.date.fromtimestamp(os.path.getctime(file))
        if (today - creation_date) > retention_period:
            os.remove(file)


if __name__ == '__main__':
    parquet_cleaner()
