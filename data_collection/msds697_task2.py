import airflow
from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from user_definition import *
from jobs_data_calls import *

# NOTE : In order to make sure it send configurations requests first, do not import your .py reading from gs.

def _write_jobs_to_gcs():
    data = get_jobs()
    data_seo = get_jobs_seo()
    write_json_to_gcs(bucket_name, f'{today}/jobs.json', service_account_key_file, data)
    write_json_to_gcs(bucket_name, f'{today}/jobs_seo.json', service_account_key_file, data_seo)

with DAG(dag_id="msds697-task2",
         start_date = datetime(2023, 1, 31), schedule_interval='@daily', catchup=False) as dag:

    create_insert_aggregate = SparkSubmitOperator(
        task_id="aggregate_creation",
        packages="com.google.cloud.bigdataoss:gcs-connector:hadoop2-1.9.17,org.mongodb.spark:mongo-spark-connector_2.12:3.0.1",
        exclude_packages="javax.jms:jms,com.sun.jdmk:jmxtools,com.sun.jmx:jmxri",
        conf={"spark.driver.userClassPathFirst":True,
             "spark.executor.userClassPathFirst":True,
            #  "spark.hadoop.fs.gs.impl":"com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem",
            #  "spark.hadoop.fs.AbstractFileSystem.gs.impl":"com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS",
            #  "spark.hadoop.fs.gs.auth.service.account.enable":True,
            #  "google.cloud.auth.service.account.json.keyfile":service_account_key_file,
             },
        verbose=True,
        application='aggregates_to_mongo.py'
    )

    write_jobs_to_gcs = PythonOperator(task_id = "write_jobs_to_gcs",
                                                    python_callable = _write_jobs_to_gcs,
                                                    dag=dag)
    write_jobs_to_gcs >> create_insert_aggregate
