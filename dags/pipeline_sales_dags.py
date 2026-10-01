from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from include.artifacts import read_artifact, write_artifact
from include.extract import extract_data_callable
from include.transform import transform_data_callable
from include.data_quality import data_quality_callable
from include.load import load_data_callable


def extract_task(run_id):
    return write_artifact(extract_data_callable(), run_id, 'raw')


def transform_task(ti, run_id):
    df = read_artifact(ti.xcom_pull(task_ids='extract_task'))
    return write_artifact(transform_data_callable(df), run_id, 'transformed')


def data_quality_task(ti):
    path = ti.xcom_pull(task_ids='transform_task')
    data_quality_callable(read_artifact(path))
    return path


def load_task(ti):
    load_data_callable(read_artifact(ti.xcom_pull(task_ids='data_quality_task')))


with DAG(
    dag_id='pipeline_sales', start_date=datetime(2026, 1, 1), schedule=None,
    catchup=False, max_active_runs=1,
    default_args={'owner': 'mlsanoh', 'retries': 2, 'retry_delay': timedelta(minutes=2)},
) as dag:
    extract_data = PythonOperator(task_id='extract_task', python_callable=extract_task)
    transform_data = PythonOperator(task_id='transform_task', python_callable=transform_task)
    data_quality = PythonOperator(task_id='data_quality_task', python_callable=data_quality_task)
    load_data = PythonOperator(task_id='load_task', python_callable=load_task, do_xcom_push=False)
    extract_data >> transform_data >> data_quality >> load_data
