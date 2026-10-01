import logging
import numpy as np
import pandas as pd

logger = logging.getLogger('airflow.task')
EXPECTED_COLUMNS = [
    'customer_id', 'name', 'gender', 'age', 'city', 'country', 'email',
    'purchase_amount', 'feedback_score', 'signup_date', 'last_purchase_date',
]


def data_quality_callable(df):
    missing = sorted(set(EXPECTED_COLUMNS) - set(df.columns))
    if missing:
        raise ValueError(f'Colonnes obligatoires absentes : {missing}')
    if df.empty:
        raise ValueError('Le lot de données est vide.')

    # Compter toutes les anomalies avant de bloquer le chargement.
    amount = pd.to_numeric(df['purchase_amount'], errors='coerce')
    age = pd.to_numeric(df['age'], errors='coerce')
    invalid_ids = df['customer_id'].isna() | df['customer_id'].astype('string').str.strip().eq('').fillna(False)
    anomalies = {
        'customer_id absent': int(invalid_ids.sum()),
        'customer_id dupliqué': int(df['customer_id'].duplicated(keep=False).sum()),
        'purchase_amount invalide': int((amount.isna() | ~np.isfinite(amount) | (amount < 0)).sum()),
        'age invalide': int((age.isna() | ~age.between(0, 120) | (age % 1 != 0)).sum()),
        'signup_date invalide': int(pd.to_datetime(df['signup_date'], errors='coerce').isna().sum()),
        'last_purchase_date invalide': int(pd.to_datetime(df['last_purchase_date'], errors='coerce').isna().sum()),
    }
    anomalies = {rule: count for rule, count in anomalies.items() if count}
    if anomalies:
        logger.error('Contrôle qualité bloquant : %s', anomalies)
        raise ValueError(f'Anomalies de qualité : {anomalies}')

    invalid_gender = ~df['gender'].isin(['M', 'F', 'unknown'])
    if invalid_gender.any():
        logger.warning('Genre non reconnu : %s ligne(s).', int(invalid_gender.sum()))
    logger.info('Contrôles qualité réussis : %s lignes.', len(df))
    return df
