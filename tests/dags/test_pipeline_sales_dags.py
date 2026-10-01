from airflow.models.dagbag import DagBag
from datetime import datetime
import pytz

def test_pipeline_sales_dags_config():

    dagbag = DagBag(dag_folder="dags", include_examples=False)
    
    # Vérification qu'il n'y a aucune erreur de syntaxe ou d'importation
    assert len(dagbag.import_errors) == 0, f"Erreurs de parsing dans le DAG : {dagbag.import_errors}"
    
    # Récupération du DAG
    dag_id = "pipeline_sales"
    assert dag_id in dagbag.dags, f"Le DAG {dag_id} n'a pas été trouvé dans le DagBag."
    dag = dagbag.dags[dag_id]
    
    # Vérification du DAG
    assert dag is not None, "Le DAG 'pipeline_sales' n'a pas pu être trouvé."
    assert dag.catchup is False
    
    # Vérification du nombre de tâches
    assert len(dag.tasks) == 4, f"Le DAG devrait avoir 4 tâches, il en a {len(dag.tasks)}"
    
    # Vérification de l'enchaînement des tâches
    extract_task = dag.get_task("extract_task")
    transform_task = dag.get_task("transform_task")
    data_quality_task = dag.get_task("data_quality_task")
    load_task = dag.get_task("load_task")

    assert transform_task in extract_task.downstream_list
    assert data_quality_task in transform_task.downstream_list
    assert load_task in data_quality_task.downstream_list
