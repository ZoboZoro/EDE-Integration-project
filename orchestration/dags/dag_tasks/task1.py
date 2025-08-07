import time
from datetime import datetime, timedelta

import gspread
from airflow.models import Variable
from airflow.models.dag import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.transfers.s3_to_redshift import \
    S3ToRedshiftOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from dag_tasks import airflow_variables
from utils.module import faker_to_s3, googlesheet_to_s3

airflow_variables = airflow_variables

BUCKET = "general-dumpss"
REDSHIFT_TABLE = "healthinfo"
IAM_ROLE_ARN = 'arn:aws:iam::517819573047:role/redshift_s3_role'

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


copy_command = f"""
COPY public.{REDSHIFT_TABLE}
FROM '{filepath}'
IAM_ROLE '{IAM_ROLE_ARN}'
FORMAT AS PARQUET;
"""


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


create_table = SQLExecuteQueryOperator(
        task_id='create_redshift_table',
        conn_id='redshift_default',
        sql='/sql_table.sql'
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

(
    start
    >> [to_s3, drive_to_s3]
    >> create_table
    >> copy_to_redshift
    >> end
)
