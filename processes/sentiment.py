import os
import glob
import polars as pl

import nltk
from nltk.sentiment import SentimentIntensityAnalyzer


# Parquet file locations
RAW_FILES = '/opt/airflow/parquet/raw_files/*.parquet'
PROCESSED_FILES = '/opt/airflow/parquet/processed_files/*.parquet'


def latest_parquet():
    '''
    Reads latest parquet file. Raises an error if no file is available.
    '''
    files = glob.glob(RAW_FILES)

    try:
        latest_file = max(files, key=os.path.getctime)
    except ValueError:
        raise FileNotFoundError('No new file available.')
  
    return latest_file


def assign_sentiment(score):
    '''
    Assigns a sentiment label from the derived sentiment compound 
    score of each email.
    '''
    if score >= 0.3:
        return 'Positive'
    elif score <= -0.3:
        return 'Negative'
    else:
        return 'Neutral'


def sentiment_analysis():
    '''
    Performs sentiment analysis on the "body" column of the LazyFrame and
    adds the derived "sentiment" column for each email.
    '''
    # Downloads vader lexicon if it does not exist locally
    nltk.download('vader_lexicon')

    lf = pl.scan_parquet(latest_parquet())

    sia = SentimentIntensityAnalyzer()

    lf = lf.with_columns(
        pl.col('body')
          .map_elements(lambda text: assign_sentiment(sia.polarity_scores(text)['compound']))
          .alias('sentiment')
    ).collect(streaming=True)
    
    return lf


def derive_and_save_sentiment():
    '''
    Derive sentiment from email(s) and save back to parquet file 
    '''
    filename = os.path.basename(latest_parquet())
    lf = sentiment_analysis() 
    lf.write_parquet(f'/opt/airflow/parquet/processed_files/{filename}')
    
    print('Sentiment analysis completed for new emails.')


if __name__ == '__main__':
    derive_and_save_sentiment()
