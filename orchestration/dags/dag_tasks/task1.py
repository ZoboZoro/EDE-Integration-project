import time
from datetime import datetime, timedelta

from airflow.models import DAG, Variable
from airflow.operators.python import PythonOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.amazon.aws.transfers.s3_to_redshift import S3ToRedshiftOperator
from dag_tasks import airflow_variables
from airflow.operators.empty import EmptyOperator
from utils.module import generate_fake_healthinformatics, extract_to_s3
import awswrangler as wr
import os
import boto3


airflow_variables = airflow_variables

BUCKET = "s3://general-dumps"
REDSHIFT_TABLE = "heathinfo"
IAM_ROLE_ARN = 'arn:aws:iam::517819573047:role/service-role/AmazonRedshift-CommandsAccessRole-20250801T191224'

key = "/healthinfo-records/healthinformatics{}.csv".format(
    time.strftime("%Y-%m-%d,%H:%M:%S"))

filepath = "{}/healthinfo-records/healthinformatics{}.csv".format(
    BUCKET, time.strftime("%Y-%m-%d,%H:%M:%S"))

copy_command = f"""
COPY public.{REDSHIFT_TABLE}
FROM '{filepath}'
IAM_ROLE '{IAM_ROLE_ARN}'
FORMAT AS CSV
IGNOREHEADER 1;
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
    end = EmptyOperator(task_id='end')

    to_s3 = PythonOperator(
        task_id='extract_to_s3',
        provide_context=True,
        python_callable=extract_to_s3,
        op_kwargs={
            "range_value": 10,
            "bucket": BUCKET,
            "key": key
                   },
)


    copy_task = SQLExecuteQueryOperator(
        task_id='copy_task',
        conn_id='redshift_default',
        parameters={
            "iam_role": IAM_ROLE_ARN
        },
        sql="""
        COPY public.heathinfo
        FROM '{{ ti.xcom_pull(task_ids="extract_to_s3") }}'
        IAM_ROLE '{{ parameters.iam_role }}'
        FORMAT AS CSV;
        """
)
    
#     load_to_redshift = PostgresOperator(
#     task_id="load_to_redshift",
#     postgres_conn_id="redshift_default",
#     sql=copy_command
# )
    
#     to_redshift = S3ToRedshiftOperator(
#         task_id='transfer_s3_to_redshift',
#         aws_conn_id="aws_default",
#         redshift_conn_id="redshift_default",
#         s3_bucket=BUCKET,
#         s3_key="{{ task_instance.xcom_pull(task_ids='extract_to_s3') }}",
#         schema="public",
#         table=REDSHIFT_TABLE,
#         copy_options=["csv",
#                       "IGNOREHEADER 1",
#                       # f"IAM_ROLE '{IAM_ROLE_ARN}'"
#                       ],
# )

start >> to_s3 >> copy_task >> end #  to_redshift
