import logging
import uuid
from sqlalchemy import MetaData, Table, create_engine, select, text
from sqlalchemy.dialects.postgresql import insert
from include.config import postgres_url
from include.data_quality import data_quality_callable


def load_data_callable(df, engine=None):
    data_quality_callable(df)
    owns_engine = engine is None
    if owns_engine:
        engine = create_engine(postgres_url())
    if engine.dialect.name != 'postgresql':
        raise ValueError('Le chargement nécessite PostgreSQL.')
    stage_name = f'sales_stage_{uuid.uuid4().hex}'
    try:
        # Staging et UPSERT dans la même transaction : aucun DROP de la table cible.
        with engine.begin() as connection:
            df.to_sql(stage_name, connection, if_exists='fail', index=False, method='multi', chunksize=1000)
            connection.execute(text(f'CREATE TABLE IF NOT EXISTS sales_dwh (LIKE "{stage_name}" INCLUDING DEFAULTS)'))
            connection.execute(text('CREATE UNIQUE INDEX IF NOT EXISTS sales_dwh_customer_id_uq ON sales_dwh (customer_id)'))
            metadata = MetaData()
            stage = Table(stage_name, metadata, autoload_with=connection)
            target = Table('sales_dwh', metadata, autoload_with=connection)
            columns = list(df.columns)
            statement = insert(target).from_select(columns, select(*(stage.c[col] for col in columns)))
            statement = statement.on_conflict_do_update(
                index_elements=['customer_id'],
                set_={col: statement.excluded[col] for col in columns if col != 'customer_id'},
            )
            connection.execute(statement)
            stage.drop(connection)
        logging.getLogger('airflow.task').info('Chargement PostgreSQL : %s lignes.', len(df))
    finally:
        if owns_engine:
            engine.dispose()
