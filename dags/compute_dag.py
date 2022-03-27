from airflow import DAG
from datetime import datetime, timedelta
from airflow.sensors.filesystem import FileSensor
from airflow.operators.dummy import DummyOperator
from airflow.utils.trigger_rule import TriggerRule
from airflow.operators.mysql_operator import MySqlOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.hooks.mysql_hook import MySqlHook

from utils.query import LOAD_METADATA_REQUEST,CREATE_METADATA_REQUEST, CREATE_PAGE_LINK_REQUEST, PAGE_LINK_DATA_REQUEST, CREATE_LINK_DATA_REQUEST, LOAD_LINK_COUNT_REQUEST, CREATE_OUTDATED_PAGE_REQUEST, OUTDATED_PAGE_REQUEST, CREATE_OUTDATED_DIFF_PAGE_REQUEST, OUTDATED_PAGE_BY_CATEGORY_REQUEST
from utils.limit import ENTRY_LIMIT


default_args = {
    "owner" : "Alan",
    "start_date": datetime(2022,3,23),
    "retries" : 2, 
    "retry_delay" : timedelta(seconds=5)
}

with DAG("compute_required_data", default_args = default_args, schedule_interval="0 1 4 * *", template_searchpath='/opt/airflow/downloads', catchup=False) as dag:
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
    
    # create table
    # create_first_table = MySqlOperator(
    #     task_id = "create_first_table",
    #     mysql_conn_id = "mysql_conn",
    #     sql = """
    #         DROP TABLE IF EXISTS `pagemetadata`;
    #         CREATE TABLE `pagemetadata` (
    #             `page_title` varbinary(255) NOT NULL DEFAULT '',
    #             `category` varbinary(255) NOT NULL DEFAULT '',
    #             `last_updated` timestamp NOT NULL
    #         )
    #     """
    # )
    
    # createMetadata = MySqlOperator(
    #     task_id = "create_metadata",
    #     mysql_conn_id = "mysql_conn",
    #     sql = METADATA_REQUEST
    # )

    # createPageLinkRequest = MySqlOperator(
    #     task_id = "create_page_link_data",
    #     mysql_conn_id = "mysql_conn",
    #     sql = CREATE_PAGE_LINK_REQUEST
    # )    

    # fetchPageLinkData = MySqlOperator(
    #     task_id = "insert_page_link_data",
    #     mysql_conn_id = 'mysql_conn',
    #     sql = PAGE_LINK_DATA_REQUEST
    # )

    # createLinkDataCount = MySqlOperator(
    #     task_id = "create_link_data_count",
    #     mysql_conn_id = "mysql_conn",
    #     sql = CREATE_LINK_DATA_REQUEST
    # )
    
    # loadlinkCountTable = MySqlOperator(
    #     task_id = "insert_link_count_data",
    #     mysql_conn_id = "mysql_conn",
    #     sql = LOAD_LINK_COUNT_REQUEST
    # )
    
    # createOutdatedPageTable = MySqlOperator(
    #     task_id = "create_outdated_page_data",
    #     mysql_conn_id = "mysql_conn",
    #     sql = CREATE_OUTDATED_PAGE_REQUEST
    # )
    
    # loadOutdatedPageTable = MySqlOperator(
    #     task_id = "load_outdated_page_data",
    #     mysql_conn_id = "mysql_conn",
    #     sql = OUTDATED_PAGE_REQUEST
    # )
    
    # createOutdatedDiffPageTable = MySqlOperator(
    #     task_id = "create_outdated_diff_page_data",
    #     mysql_conn_id = "mysql_conn",
    #     sql = CREATE_OUTDATED_DIFF_PAGE_REQUEST
    # )
    
    # loadOutdatedDiffPageTable = MySqlOperator(
    #     task_id = "load_outdated_diff_page_data",
    #     mysql_conn_id = "mysql_conn",
    #     sql = OUTDATED_PAGE_BY_CATEGORY_REQUEST
    # )
    
    
    [createMetaData, createPageLinkRequest, createLinkDataCount, createOutdatedPageTable, createOutdatedDiffPageTable] >> checkReadyForInsert >> loadMetadata
    loadMetadata >> fetchPageLinkData >> loadlinkCountTable >> loadOutdatedPageTable >> loadOutdatedDiffPageTable >> DeleteDownloadedFiles
    
    
    

    
    