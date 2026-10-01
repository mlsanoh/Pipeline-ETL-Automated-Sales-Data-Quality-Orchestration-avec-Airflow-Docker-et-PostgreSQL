import pandas as pd


def transform_data_callable(df):
    df = df.copy()
    df.columns = df.columns.str.strip().str.lower().str.replace(r'\s+', '_', regex=True)

    # Normaliser sans masquer les anomalies financières ou les identifiants absents.
    df = df.drop_duplicates()
    df['purchase_amount'] = pd.to_numeric(df['purchase_amount'], errors='coerce')
    for col in ['gender', 'city', 'country']:
        df[col] = df[col].astype('string').str.strip().replace('', pd.NA).fillna('unknown')
    df['gender'] = df['gender'].str.lower().replace({'m': 'M', 'male': 'M', 'f': 'F', 'female': 'F'})
    df['country'] = df['country'].str.lower().replace({'india': 'India', 'ind': 'India'})
    df['city'] = df['city'].str.title()

    age = df['age'].astype('string').str.replace(r'\s*years?\s*', '', regex=True).str.strip()
    df['age'] = pd.to_numeric(age, errors='coerce')
    df['signup_date'] = pd.to_datetime(df['signup_date'], errors='coerce')
    df['last_purchase_date'] = pd.to_datetime(df['last_purchase_date'], errors='coerce')
    return df
