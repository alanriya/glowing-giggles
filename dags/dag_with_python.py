from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator


default_args = {
    'owner': 'alan',
    'retry': 5,
    'retry_delay': timedelta(minutes=5)
}

def get_pandas():
    import pandas
    print(f"pandas with version: {pandas.__version__} ")


def get_requests():
    import requests
    print(f"requests with version: {requests.__version__}")


with DAG(
    default_args=default_args,
    dag_id="dag_with_python_dependencies_v03",
    start_date=datetime(2022, 3, 21),
    schedule_interval='@daily'
) as dag:
    task1 = PythonOperator(
        task_id='get_pandas',
        python_callable=get_pandas
    )
    
    task2 = PythonOperator(
        task_id='get_requests',
        python_callable=get_requests
    )

    
    task1 >> task2