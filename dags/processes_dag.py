from airflow import DAG
from airflow.operators.bash import BashOperator

from datetime import datetime, timedelta


# Default DAG arguments
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 6, 17),
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

# Email processing pipeline DAG that runs daily. Uses the BashOperator
# to run each task's .py file as a complete script rather than using
# the PythonOperator and importing the functions from each file. 

with DAG(dag_id='email_processing', 
         default_args=default_args, 
         schedule_interval='@daily', 
         catchup=False
) as email_dag:
    
    extract = BashOperator(
        task_id='extraction',
        bash_command='python /opt/airflow/processes/extraction.py',
        dag=email_dag
    )

    vader_sentiment = BashOperator(
        task_id= 'sentiment',
        bash_command ='python /opt/airflow/processes/sentiment.py',
        dag=email_dag
    )

    insert = BashOperator(
        task_id='insertion',
        bash_command='python /opt/airflow/processes/insertion.py',
        dag=email_dag
    )

extract >> vader_sentiment >> insert

# DAG for weekly parquet cleaner task. Same use of BashOperator as in previous DAG
with DAG(dag_id='parquet_cleaner', 
         default_args=default_args, 
         schedule_interval='@weekly', 
         catchup=False
) as parquet_dag:

    # Only a single task in in this dag
    cleaner = BashOperator(
        task_id='cleaner',
        bash_command='python /opt/airflow/processes/cleanup.py',
        dag=parquet_dag
    )

cleaner
