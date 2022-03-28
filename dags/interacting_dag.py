from airflow import DAG
from datetime import datetime, timedelta
from airflow.sensors.http_sensor import HttpSensor
from airflow.operators.python_operator import PythonOperator, BranchPythonOperator
from airflow.sensors.filesystem import FileSensor
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.operators.mysql_operator import MySqlOperator
from airflow.utils.trigger_rule import TriggerRule
from airflow.operators.docker_operator import DockerOperator
from utils.scrap import FileDateScrapper
from utils.download import download_files

from utils.query import LOAD_METADATA_REQUEST,DELETE_RAW_DATA_REQUEST, CREATE_METADATA_REQUEST, CREATE_PAGE_LINK_REQUEST, PAGE_LINK_DATA_REQUEST, CREATE_LINK_DATA_REQUEST, LOAD_LINK_COUNT_REQUEST, CREATE_OUTDATED_PAGE_REQUEST, OUTDATED_PAGE_REQUEST, CREATE_OUTDATED_DIFF_PAGE_REQUEST, OUTDATED_PAGE_BY_CATEGORY_REQUEST

default_args = {
    "owner" : "Alan",
    "start_date": datetime(2022,3,23),
    "retries" : 2, 
    "retry_delay" : timedelta(seconds=5)
}

with DAG("interacting_external_process", default_args = default_args, schedule_interval="0 0 3 * *", template_searchpath='/opt/airflow/downloads', catchup=False) as dag:
    unzippingFiles = BashOperator(
        task_id = "unzipping_files",
        bash_command = """
            find $AIRFLOW_HOME/downloads/*.gz -exec gunzip -k {} \; 
            touch $AIRFLOW_HOME/downloads/insert
        """
    )
    
    isReadyForCompute = FileSensor(
        task_id="is_ready_for_compute",
        fs_conn_id="downloadsFilePath",
        filepath="compute",
        poke_interval=30,
    )
    
    readyForCompute = DummyOperator(
        task_id = "ready_for_compute",
        trigger_rule=  TriggerRule.ONE_SUCCESS
    )
    
    
    
    unzippingFiles >> isReadyForCompute >> readyForCompute