import os
import glob
import polars as pl

import nltk
from nltk.sentiment import SentimentIntensityAnalyzer


# Downloads vader lexicon if it does not exist locally
nltk.download('vader_lexicon')

# Path to parquet files
PARQUET_FILE = '/opt/airflow/parquet/*.parquet'


def read_latest_file():
    '''
    Reads latest parquet file. Raises an error if no file is available.
    '''
    files = glob.glob(PARQUET_FILE)

    try:
        latest_file = max(files, key=os.path.getctime)
    except ValueError:
        raise FileNotFoundError('No file found: Check folder contents.')
    
    df = pl.read_parquet(latest_file)
    return df


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


def sentiment_analysis(df):
    '''
    Checks to see if the file has already been processed for sentiment.
    Performs sentiment analysis on the "body" column of the DataFrame and
    adds the derived "sentiment" column for each email.
    '''
    if {'sentiment'}.issubset(df.columns):
        print('File has already been processed for sentiment.')
        exit()

    sia = SentimentIntensityAnalyzer()

    df = df.with_columns(pl.col('body').apply(lambda text: assign_sentiment \
                                             (sia.polarity_scores(text) \
                                             ['compound'])).alias('sentiment'))

    return df


def derive_and_save_sentiment():
    '''
    Derive sentiment from email(s) and save back to parquet file 
    '''
    df = read_latest_file()
    df = sentiment_analysis(df)
    df.write_parquet(max(glob.glob(PARQUET_FILE), key=os.path.getctime))
    print('Sentiment analysis completed for new emails.')


if __name__ == '__main__':
    derive_and_save_sentiment()
