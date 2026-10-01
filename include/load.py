import pandas as pd
from sqlalchemy import create_engine
from include.config import PostgreSQL_CONN

def load_data_callable (df):
    print("Connexion à PostgreSQL")

    # Création du moteur SQLAlchemy pour PostgreSQL
    engine = create_engine(PostgreSQL_CONN)

    try:
        # Envoi des données dans PostgreSQL
        df.to_sql(
            name='sales_dwh', 
            con=engine, 
            if_exists='replace', 
            index=False,
            method='multi'
        )
        print("Chargement réussi ! Les données sont dans la table PostgreSQL 'sales_dwh'.")
        
    except Exception as e:
        print(f"Erreur lors de l'insertion dans PostgreSQL : {e}")
        raise e
    finally:
        engine.dispose()
