import pandas as pd 


def transform_data_callable(df):
    df = df.copy() 
    df.shape
    df.dtypes
    df.isnull().sum()
    df.head

    # Standarisation des colonnes
    df.columns = (
        df.columns
        .str.replace(' ', '_')
        .str.lower()
        .str.strip()
    )
    
    # Gardons uniquement les lignes où customer_id n'est pas vide
    df = df[df['customer_id'].notna()]

    # Suppression des doublons
    df = df.drop_duplicates()

    # Remplacement des valeurs manquantes
        # Valeur numerique
    for col in ['purchase_amount']:
        df[col] = df[col].fillna(df[col].median())
    
        # Valeur categorielle
    cat_cols = ['gender', 'city']
    df[cat_cols] = df[cat_cols].fillna('unknown')
    
    df['country'] = df['country'].fillna('india')

    # Convertir les montants négatifs en positifs (valeur absolue)
    df['purchase_amount'] = df['purchase_amount'].abs()

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
    df['age'] = df['age'].astype('Int64')
    # Remplacer les valeurs < 0 et > 120 par la médiane
    age_median = int(df[(df['age'] >= 0) & (df['age'] <= 120)]['age'].median())
    df.loc[(df['age'] < 0) | (df['age'] > 120), 'age'] = int(age_median)

    # Modification des types dates
    df['signup_date'] = pd.to_datetime(df['signup_date'], errors='coerce')
    df['last_purchase_date'] = pd.to_datetime(df['last_purchase_date'], errors='coerce')

    return df