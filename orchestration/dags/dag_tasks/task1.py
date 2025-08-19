import time
from datetime import datetime, timedelta
from typing import Any

import gspread
from airflow.models import Variable
from airflow.models.dag import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator, PythonVirtualenvOperator
from airflow.providers.amazon.aws.transfers.s3_to_redshift import \
    S3ToRedshiftOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from dag_tasks import airflow_variables
# from sqlalchemy import create_engine, String, DATE
from utils.module import faker_to_s3, googlesheet_to_s3, googlesheet_to_db, googlesheet_db_withPGhook

airflow_variables = airflow_variables

# Constants and Vraiables
BUCKET = "general-dumpss"
REDSHIFT_TABLE = "reg1_healthinfo"
POSTGRES_TABLE = "reg16_healthinfo"
IAM_ROLE_ARN = "arn:aws:iam::517819573047:role/redshift_s3_role"
USER = Variable.get('DB_USER')
PG_SECRET = Variable.get('PG_SECRET')
DB_HOST= Variable.get('DB_HOST')
DB_NAME = Variable.get('DB_NAME')

key = "healthinfo-records/healthinformatics{}.parquet".format(
    time.strftime("%Y-%m-%d_%H:%M:%S"))

filepath = "{}/healthinfo-records/healthinformatics{}.parquet".format(
    BUCKET, time.strftime("%Y-%m-%d_%H:%M:%S"))

filepath2 = "{}/healthinfo-gsheet/healthinformatics{}.parquet".format(
    BUCKET, time.strftime("%Y-%m-%d_%H:%M:%S"))

client = gspread.service_account_from_dict(
        Variable.get("CREDENTIALS_AIRFLOW_GSERVICE", deserialize_json=True)
    )

spreadsheet_source = "ptt_records"

postgres_conn_id="postgres_default"

to_rdsPG_args = {
      "client": client,
      "spreadsheet_name": spreadsheet_source,
      "conn_id": postgres_conn_id,
      "table": POSTGRES_TABLE,
}

default_args = {
    'owner': 'Taofeecoh',
    'start_date': datetime(2025, 7, 16),
    'retries': 3,
    'retry_delay': timedelta(minutes=1)
}


with DAG(
    dag_id='healthinfo_dag',
    default_args=default_args,
    schedule_interval='0 5 * * *',
    catchup=False
) as dag:

    start = EmptyOperator(task_id='start')

    to_s3 = PythonOperator(
        task_id='extract_to_s3',
        provide_context=True,
        python_callable=faker_to_s3,
        op_kwargs={
            "range_value": 10,
            "bucket": f's3://{BUCKET}/',
            "key": key
                   },
    )


    drive_to_s3 = PythonOperator(
        task_id='drive_to_s3',
        provide_context=True,
        python_callable=googlesheet_to_s3,
        op_kwargs={
            "client": client,
            "spreadsheet_name": spreadsheet_source,
            "file_path": filepath2
        }
    )


create_redshift_table = SQLExecuteQueryOperator(
        task_id='create_redshift_table',
        conn_id='redshift_default',
        sql="sql/redshift_table.sql"
    )

create_postgres_table = SQLExecuteQueryOperator(
        task_id='create_postgres_table',
        conn_id='postgres_default',
        sql="sql/postgres.sql"
    )


to_postgres = PythonOperator(
        task_id='load_to_postgres',
        provide_context=True,
        python_callable=googlesheet_db_withPGhook,
        op_kwargs=to_rdsPG_args
    )

copy_to_redshift = S3ToRedshiftOperator(
        task_id='copy_data_to_redshift',
        s3_bucket=BUCKET,
        s3_key=""
        "{{task_instance.xcom_pull(task_ids='extract_to_s3', key='key')}}"
        "",
        schema='public',
        table=REDSHIFT_TABLE,
        column_list=[
                "names",
                "sex ",
                "birthdate",
                "blood_group",
                "ssn",
                "mail",
                "jobs",
                "address",
                "residence",
                "diagnosis",
            ],
        redshift_conn_id='redshift_default',
        aws_conn_id='aws_default',
        copy_options=["FORMAT AS PARQUET"],
    )


end = EmptyOperator(task_id='end')

# (
#     start 
#     >>  to_s3 >> drive_to_s3
#     << [create_postgres_table, create_redshift_table] 
#     >> to_postgres << create_postgres_table >>
#     copy_to_redshift << create_redshift_table
#     << end
# )

start >> [to_postgres, copy_to_redshift]
# start >> drive_to_s3 >> create_postgres_table >> to_postgres
start >> [drive_to_s3, to_s3] >> create_postgres_table >> to_postgres
#to_postgres << create_postgres_table << start
copy_to_redshift << create_redshift_table << start

