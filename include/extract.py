import logging
import pandas as pd
from include.config import DATA_PATH


def extract_data_callable():
    df = pd.read_csv(DATA_PATH)
    logging.getLogger('airflow.task').info('Extraction : %s lignes.', len(df))
    return df
