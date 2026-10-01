import pandas as pd 


def transform_data_callable(df):
    df = df.copy()

    # Standarisation des colonnes
    df.columns = (
        df.columns
        .str.strip()
        .str.replace(' ', '_')
        .str.lower()
    )
    
    # Les identifiants absents seront détectés par le contrôle qualité.

    # Suppression des doublons
    df = df.drop_duplicates()

    # Convertir les montants en nombres sans inventer les valeurs manquantes.
    df['purchase_amount'] = pd.to_numeric(df['purchase_amount'], errors='coerce')
    
    # Valeurs catégorielles manquantes
    cat_cols = ['gender', 'city']
    df[cat_cols] = df[cat_cols].fillna('unknown')
    
    # Pour ce jeu de données indien, un pays manquant est supposé être l'Inde.
    df['country'] = df['country'].fillna('india')

    # Les montants négatifs restent visibles pour le contrôle qualité.

    # Normalisation des colonnes 
    for col in ['gender', 'country']:
        df[col] = df[col].str.strip().str.lower()

    gender_map = {
    'm': 'M',
    'male': 'M',
    'f': 'F',
    'female': 'F'
    }

    country_map = {
    'india': 'India',
    'ind': 'India'
    }

    df['gender'] = df['gender'].map(gender_map).fillna(df['gender'])
    df['country'] = df['country'].map(country_map).fillna(df['country'])

    df['city'] = df['city'].str.strip().str.title()

    # Uniformisatiion de la colonne age
    df['age'] = (
        df['age']
        .astype(str)
        .str.replace(r'\s*years?\s*', '', regex=True)
        .str.strip()
    )

    df['age'] = pd.to_numeric(df['age'], errors='coerce')
    # Les âges invalides restent visibles pour le contrôle qualité.

    # Modification des types dates
    df['signup_date'] = pd.to_datetime(df['signup_date'], errors='coerce')
    df['last_purchase_date'] = pd.to_datetime(df['last_purchase_date'], errors='coerce')

    return df
