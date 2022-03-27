from airflow import DAG
from datetime import datetime, timedelta
from airflow.sensors.http_sensor import HttpSensor
from airflow.operators.python_operator import PythonOperator, BranchPythonOperator
from airflow.sensors.filesystem import FileSensor
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.operators.mysql_operator import MySqlOperator
from airflow.utils.trigger_rule import TriggerRule
from utils.scrap import FileDateScrapper
from utils.download import download_files

from utils.query import LOAD_METADATA_REQUEST,CREATE_METADATA_REQUEST, CREATE_PAGE_LINK_REQUEST, PAGE_LINK_DATA_REQUEST, CREATE_LINK_DATA_REQUEST, LOAD_LINK_COUNT_REQUEST, CREATE_OUTDATED_PAGE_REQUEST, OUTDATED_PAGE_REQUEST, CREATE_OUTDATED_DIFF_PAGE_REQUEST, OUTDATED_PAGE_BY_CATEGORY_REQUEST
from utils.limit import ENTRY_LIMIT

# check if file is responding from server
# use bash operator to save the downloads
# use bash operator to unzip the downloads
# delete the existing data and load in the latest data.

# create join queries for the data needed, create a new table for this.
# run aggregation on the created table. 

default_args = {
    "owner" : "Alan",
    "start_date": datetime(2022,3,23),
    "retries" : 2, 
    "retry_delay" : timedelta(seconds=5)
}

with DAG("check_latest_date", default_args = default_args, schedule_interval="0 0 3 * *", template_searchpath='/opt/airflow/downloads', catchup=False) as dag:
    def get_prev_latest_date_str(**kwargs):
        with open("/opt/airflow/downloads/filedate.txt", "r") as f:
            lines = f.readlines()
            lines = [i.strip() for i in lines]
            kwargs['ti'].xcom_push(key='prev_latest_date', value=lines[0])
    
    def get_current_latest_date_str(**kwargs):
        FileDateScrapper().get_content(**kwargs)

    
    GetPrevLatestDate = PythonOperator(
        task_id = "get_prev_latest_date",
        python_callable = get_prev_latest_date_str 
    )
    
    GetCurrentLatestDate = PythonOperator(
        task_id = "get_current_latest_date",
        python_callable = get_current_latest_date_str
    )
    
    def branch(**kwargs):
        prev_latest_date =  kwargs['ti'].xcom_pull(task_ids='get_prev_latest_date', key='prev_latest_date')
        current_latest_date = kwargs['ti'].xcom_pull(task_ids='get_current_latest_date', key='current_latest_date')
        if prev_latest_date == current_latest_date:
            return 'skip_task'
        with open("/opt/airflow/downloads/filedate.txt", "w") as f:
            f.write(f"{current_latest_date}\n")
            
        return 'download_all_required_files' 
    
    ForkDownloadOrNot = BranchPythonOperator(
        task_id='branching',
        python_callable=branch,
        provide_context=True,
    )
    
    DoNotDownload = DummyOperator(
        task_id = "skip_task",
        trigger_rule=  TriggerRule.ONE_SUCCESS
    )
    
    DownloadFiles = PythonOperator(
        task_id = "download_all_required_files",
        python_callable = download_files
    )
    
    
    
    [GetPrevLatestDate, GetCurrentLatestDate] >> ForkDownloadOrNot >> [DoNotDownload, DownloadFiles]