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

with DAG("update_database", default_args = default_args, schedule_interval="0 0 3 * *", template_searchpath='/opt/airflow/downloads', catchup=False) as dag:
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
    
    DeleteRawData = MySqlOperator(
        task_id = "delete_raw_data",
        mysql_conn_id = "mysql_conn",
        sql = DELETE_RAW_DATA_REQUEST
    )
    
    readyForCheckGz = DummyOperator(
        task_id = "ready_for_check_gz",
        trigger_rule=  TriggerRule.ONE_SUCCESS
    )
    
    isCategoryFileAvailable = FileSensor(
        task_id="is_category_file_available",
        fs_conn_id="downloadsFilePath",
        filepath="simplewiki-*-category.sql.gz",
        poke_interval=5,
        timeout=20
    )
    
    isCategoryLinkFileAvailable = FileSensor(
        task_id="is_category_link_file_available",
        fs_conn_id="downloadsFilePath",
        filepath="simplewiki-*-categorylinks.sql.gz",
        poke_interval=5,
        timeout=20
    )
    
    isPageFileAvailable = FileSensor(
        task_id="is_page_file_available",
        fs_conn_id="downloadsFilePath",
        filepath="simplewiki-*-page.sql.gz",
        poke_interval=5,
        timeout=20
    )
    
    isPageLinkFileAvailable = FileSensor(
        task_id="is_page_link_file_available",
        fs_conn_id="downloadsFilePath",
        filepath="simplewiki-*-pagelinks.sql.gz",
        poke_interval=5,
        timeout=20
    )
    
    isTemplateLinksFileAvailable = FileSensor(
        task_id="is_template_link_file_available",
        fs_conn_id="downloadsFilePath",
        filepath="simplewiki-*-templatelinks.sql.gz",
        poke_interval=5,
        timeout=20
    )
    
    readyForUnzip = DummyOperator(
        task_id = "read_for_unzip",
        trigger_rule=  TriggerRule.ALL_SUCCESS
    )
    
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
        poke_interval=5,
        timeout=20
    )
    
    readyForCompute = DummyOperator(
        task_id = "ready_for_compute",
        trigger_rule=  TriggerRule.ONE_SUCCESS
    )
    
    checkReadyForInsert = DummyOperator(
        task_id = "ready_for_data_insert",
        trigger_rule=  TriggerRule.ALL_SUCCESS
    )
    
    # create table
    createMetaData = MySqlOperator(
        task_id = "create_metadata",
        mysql_conn_id = "mysql_conn",
        sql = CREATE_METADATA_REQUEST
    )
    
    loadMetadata = MySqlOperator(
        task_id = "load_metadata",
        mysql_conn_id = "mysql_conn",
        sql = LOAD_METADATA_REQUEST
    )

    createPageLinkRequest = MySqlOperator(
        task_id = "create_page_link_data",
        mysql_conn_id = "mysql_conn",
        sql = CREATE_PAGE_LINK_REQUEST
    )    

    fetchPageLinkData = MySqlOperator(
        task_id = "load_page_link_data",
        mysql_conn_id = 'mysql_conn',
        sql = PAGE_LINK_DATA_REQUEST
    )

    createLinkDataCount = MySqlOperator(
        task_id = "create_link_data_count",
        mysql_conn_id = "mysql_conn",
        sql = CREATE_LINK_DATA_REQUEST
    )
    
    loadlinkCountTable = MySqlOperator(
        task_id = "load_link_count_data",
        mysql_conn_id = "mysql_conn",
        sql = LOAD_LINK_COUNT_REQUEST
    )
    
    createOutdatedPageTable = MySqlOperator(
        task_id = "create_outdated_page_data",
        mysql_conn_id = "mysql_conn",
        sql = CREATE_OUTDATED_PAGE_REQUEST
    )
    
    loadOutdatedPageTable = MySqlOperator(
        task_id = "load_outdated_page_data",
        mysql_conn_id = "mysql_conn",
        sql = OUTDATED_PAGE_REQUEST
    )
    
    createOutdatedDiffPageTable = MySqlOperator(
        task_id = "create_outdated_diff_page_data",
        mysql_conn_id = "mysql_conn",
        sql = CREATE_OUTDATED_DIFF_PAGE_REQUEST
    )
    
    loadOutdatedDiffPageTable = MySqlOperator(
        task_id = "load_outdated_diff_page_data",
        mysql_conn_id = "mysql_conn",
        sql = OUTDATED_PAGE_BY_CATEGORY_REQUEST
    )
    
    DeleteDownloadedFiles = BashOperator(
        task_id = "delete_downloaded_files",
        bash_command = """
            find $AIRFLOW_HOME/downloads/*.gz -exec rm {} \;
            find $AIRFLOW_HOME/downloads/*.sql -exec rm {} \; 
            find $AIRFLOW_HOME/downloads/compute -exec rm {} \; 
        """
    )
    
    
    
    
    # Data import  
    # importData = BashOperator(
    #     task_id = "import_data",
    #     bash_command = "insertData.sh "
    # )
    
    # importData = DockerOperator(
        # task_id = "import_data",
        # image = "mysql:5.7",
        # auto_remove = True,
        # command = """
            # mysql -u airflow airflow < /opt/airflow/downloads/simplewiki-20220220-category.sql
        # """
    # )
    
    # test1 = MySqlOperator(
    #     task_id='my_task2',
    #     mysql_conn_id = "mysql_conn",
    #     sql = '''simplewiki-20220220-categorylinks.sql''' 
    # )
    
    # test2 = MySqlOperator(
    #     task_id='my_task3',
    #     mysql_conn_id = "mysql_conn",
    #     sql = '''simplewiki-20220220-page.sql''' 
    # )
    
    # test3 = MySqlOperator(
    #     task_id='my_task4',
    #     mysql_conn_id = "mysql_conn",
    #     sql = '''simplewiki-latest-templatelinks.sql''' 
    # )
    
    [GetPrevLatestDate, GetCurrentLatestDate] >> ForkDownloadOrNot >> [DoNotDownload, DownloadFiles] 
    DownloadFiles >> DeleteRawData >> readyForCheckGz >> [isCategoryFileAvailable,isCategoryLinkFileAvailable, isPageFileAvailable, isPageLinkFileAvailable, isTemplateLinksFileAvailable] >> readyForUnzip 
    readyForUnzip >> unzippingFiles >> isReadyForCompute >> readyForCompute
    readyForCompute >> [createMetaData, createPageLinkRequest, createLinkDataCount, createOutdatedPageTable, createOutdatedDiffPageTable] >> checkReadyForInsert >> loadMetadata
    loadMetadata >> fetchPageLinkData >> loadlinkCountTable >> loadOutdatedPageTable >> loadOutdatedDiffPageTable >> DeleteDownloadedFiles
    
    