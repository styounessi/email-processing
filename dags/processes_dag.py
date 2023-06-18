from airflow import DAG
from airflow.operators.bash import BashOperator

from datetime import datetime, timedelta

# Default DAG arugments
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 6, 17),
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

'''
Email processing pipeline DAG that runs daily. Uses the BashOperator
to run each task's .py file as a complete script rather than using
the PythonOperator and importing the functions from each file. 
'''

with DAG(dag_id='email_processing', 
         default_args=default_args, 
         schedule_interval='@daily', 
         catchup=False
) as dag1:
    
    task_a = BashOperator(
        task_id='extraction',
        bash_command='python /opt/airflow/processes/extraction.py',
        dag=dag1
    )

    task_b = BashOperator(
        task_id= 'sentiment',
        bash_command ='python /opt/airflow/processes/sentiment.py',
        dag=dag1
    )

    task_c = BashOperator(
        task_id='insertion',
        bash_command='python /opt/airflow/processes/insertion.py',
        dag=dag1
    )

# Each task is dependent on the successful completion of the preceding task
task_a >> task_b >> task_c

# DAG for weekly parquet cleaner task. Same use of BashOperator as in previous DAG
with DAG(dag_id='parquet_cleaner', 
         default_args=default_args, 
         schedule_interval='@weekly', 
         catchup=False
) as dag2:

    # Only a single task in this one
    task_a = BashOperator(
        task_id='cleaner',
        bash_command='python /opt/airflow/processes/cleanup.py',
        dag=dag2
    )

task_a
