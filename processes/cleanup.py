import os
import glob
import datetime


# Path to parquet files
PARQUET_FILE = '/opt/airflow/parquet/*.parquet'


# Default retention period is 7 days
def parquet_cleaner(retention_days=7):
    '''
    Searches for parquet files older than the given retention
    period and scrubs them from the folder.
    '''
    today = datetime.date.today()
    retention_period = datetime.timedelta(days=retention_days)

    files = glob.glob(PARQUET_FILE)

    for file in files:
        creation_date = datetime.date.fromtimestamp(os.path.getctime(file))
        if (today - creation_date) > retention_period:
            os.remove(file)


if __name__ == '__main__':
    parquet_cleaner()
