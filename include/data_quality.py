import pandas as pd 
import logging

# On récupère le logger standard d'Airflow
logger = logging.getLogger("airflow.task")

def data_quality_callable(df):

    if df.empty:
        raise ValueError("Le lot de données est vide.")

    # Vérification de l'existence des colonnes et de leurs types attendus
    expected_columns =['customer_id', 'name', 'gender', 'age', 'city', 
        'country', 'email', 'purchase_amount', 'feedback_score', 
        'signup_date', 'last_purchase_date'
    ]
    
    for col in expected_columns:
        if col not in df.columns:
            logger.error(f"Colonne manquante : La colonne '{col}' est introuvable !")
            raise ValueError(f"La colonne obligatoire '{col}' est absente.")

    # Vérification des valeurs manquantes 
    cols_not_null = ['customer_id', 'purchase_amount']
    for col in cols_not_null:
        null_count = df[col].isna().sum()
        if null_count > 0:
            logger.error(f"Données corrompues : La colonne '{col}' contient {null_count} valeur(s) manquante(s) !")
            raise ValueError(f"Interdiction d'avoir des valeurs nulles dans '{col}'.")

    # Vérification de la colonne age
    age_anomalies = df[df['age'].isna() | (df['age'] < 0) | (df['age'] > 120)]
    if not age_anomalies.empty:
        logger.error(f"Anomalie d'âge : {len(age_anomalies)} ligne(s) ont un âge manquant ou invalide (hors 0-120) !")
        raise ValueError("Des âges sortent de la plage autorisée.")

    # Les dates non interprétables deviennent NaT pendant la transformation.
    date_cols = ['signup_date', 'last_purchase_date']
    for col in date_cols:
        invalid_count = df[col].isna().sum()
        if invalid_count > 0:
            logger.error(f"La colonne '{col}' contient {invalid_count} date(s) manquante(s) ou invalide(s).")
            raise ValueError(f"Dates manquantes ou invalides dans '{col}'.")

    # Vérification des valeurs cartegorielles 
    genres_autorises = ['M', 'F', 'unknown']
    genres_invalides = df[~df['gender'].isin(genres_autorises)]
    if not genres_invalides.empty:
        logger.warning(f" Valeurs de genre suspectes détectées sur {len(genres_invalides)} ligne(s).")

    # Vérification des valeurs négatives 
    achats_negatifs = df[df['purchase_amount'] < 0]
    if not achats_negatifs.empty:
        logger.error(f"Erreur financière : {len(achats_negatifs)} achat(s) ont un montant négatif !")
        raise ValueError("Le montant d'achat ne peut pas être inférieur à 0.")

    logger.info("TOUS LES TESTS SONT PASSÉS ! Les données sont prêtes pour le stockage.")

    return df
