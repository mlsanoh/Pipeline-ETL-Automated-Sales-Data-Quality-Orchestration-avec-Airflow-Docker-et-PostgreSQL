from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator

from include.extract import extract_data_callable
from include.transform import transform_data_callable
from include.data_quality import data_quality_callable
from include.load import load_data_callable

# DAG

with DAG (
    dag_id= "pipeline_sales",
    start_date = datetime(2026, 1, 1),
    schedule =None,
    catchup=False,
    max_active_runs=1,
) as dag :
    
     def extract_task():
        return extract_data_callable()

     def transform_task(ti):
        df = ti.xcom_pull(task_ids="extract_task")
        return transform_data_callable(df)

     def data_quality_task(ti):
        df = ti.xcom_pull(task_ids="transform_task")
        return data_quality_callable(df)

     def load_task(ti):
        df = ti.xcom_pull(task_ids="data_quality_task")
        return load_data_callable(df)



     extract_data = PythonOperator(
        task_id="extract_task",
        python_callable=extract_task
    )

     transform_data = PythonOperator(
        task_id='transform_task',
        python_callable=transform_task
    )
    
     data_quality = PythonOperator(
        task_id="data_quality_task",
        python_callable=data_quality_task
    )

     load_data = PythonOperator(
        task_id='load_task',
        python_callable=load_task
    )

extract_data >> transform_data >> data_quality >> load_data
