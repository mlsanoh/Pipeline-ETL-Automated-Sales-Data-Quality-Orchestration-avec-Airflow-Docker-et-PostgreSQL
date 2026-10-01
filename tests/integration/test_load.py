import os
import uuid
import pandas as pd
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
from include.load import load_data_callable
from include.transform import transform_data_callable


@pytest.fixture
def engine():
    url = os.getenv('TEST_POSTGRES_URL')
    if not url:
        pytest.skip('Configurer TEST_POSTGRES_URL pour une base de tests PostgreSQL.')
    admin = create_engine(url)
    schema = 'test_sales_' + uuid.uuid4().hex
    with admin.begin() as conn:
        conn.execute(text(f'CREATE SCHEMA {schema}'))
    engine = create_engine(url, connect_args={'options': f'-csearch_path={schema}'})
    try:
        yield engine
    finally:
        engine.dispose()
        with admin.begin() as conn:
            conn.execute(text(f'DROP SCHEMA {schema} CASCADE'))
        admin.dispose()


def batch(*records):
    rows = [dict(customer_id=key, name='Client', gender='male', age=30,
                 city='Paris', country='France', email='test@example.org',
                 purchase_amount=amount, feedback_score=4,
                 signup_date='2026-01-01', last_purchase_date='2026-02-01')
            for key, amount in records]
    return transform_data_callable(pd.DataFrame(rows))


def test_replay_updates_without_duplicates_and_keeps_other_customers(engine):
    load_data_callable(batch((1, 30), (2, 40)), engine)
    load_data_callable(batch((1, 60)), engine)
    load_data_callable(batch((1, 60)), engine)
    with engine.connect() as conn:
        assert conn.execute(text('SELECT customer_id, purchase_amount FROM sales_dwh ORDER BY customer_id')).all() == [(1, 60), (2, 40)]
        assert not conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = current_schema() AND tablename LIKE 'sales_stage_%'")).all()


def test_failed_insert_rolls_back_and_keeps_target(engine):
    load_data_callable(batch((1, 30)), engine)
    with engine.begin() as conn:
        conn.execute(text('ALTER TABLE sales_dwh ADD CONSTRAINT amount_limit CHECK (purchase_amount <= 100)'))
    with pytest.raises(IntegrityError):
        load_data_callable(batch((1, 90), (2, 1000)), engine)
    with engine.connect() as conn:
        assert conn.execute(text('SELECT customer_id, purchase_amount FROM sales_dwh')).all() == [(1, 30)]
        assert not conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = current_schema() AND tablename LIKE 'sales_stage_%'")).all()
