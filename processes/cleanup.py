import os
import glob
import datetime

# Path to parquet files
PARQUET_FILE = '/opt/airflow/parquet/*.parquet'

def main(days):
    '''
    Main function that searches for parquet files older than the
    given retention period and scrubs them from the folder.
    '''
    today = datetime.date.today()
    retention_period = datetime.timedelta(days=days)

    files = glob.glob(PARQUET_FILE)

    for file in files:
        creation_date = datetime.date.fromtimestamp(os.path.getctime(file))
        if (today - creation_date) > retention_period:
            os.remove(file)

if __name__ == '__main__':
    main(days=7) # Default retention period is 7 days but can be changed as needed
