import numpy as np
import pandas as pd
import pytest
from include.data_quality import data_quality_callable
from include.transform import transform_data_callable


def row(**overrides):
    values = dict(customer_id=1, name='Client', gender='male', age='25 years',
                  city=' paris ', country='France', email='test@example.org',
                  purchase_amount=30, feedback_score=4,
                  signup_date='2026-01-01', last_purchase_date='2026-02-01')
    values.update(overrides)
    return values


def test_valid_normalization():
    result = transform_data_callable(pd.DataFrame([row()]))
    data_quality_callable(result)
    assert result.iloc[0]['gender'] == 'M'
    assert result.iloc[0]['city'] == 'Paris'
    assert result.iloc[0]['age'] == 25


@pytest.mark.parametrize('changes', [
    {'purchase_amount': -10}, {'purchase_amount': None}, {'purchase_amount': 'incorrect'},
    {'purchase_amount': np.inf}, {'customer_id': None}, {'customer_id': ''},
    {'age': 121}, {'age': -1}, {'age': None}, {'age': 25.5},
    {'signup_date': 'incorrect'}, {'last_purchase_date': None},
])
def test_anomalies_are_not_hidden_by_transformation(changes):
    result = transform_data_callable(pd.DataFrame([row(**changes)]))
    with pytest.raises(ValueError, match='Anomalies de qualité'):
        data_quality_callable(result)


def test_conflicting_customer_rows_are_rejected():
    result = transform_data_callable(pd.DataFrame([row(), row(purchase_amount=40)]))
    with pytest.raises(ValueError, match='dupliqué'):
        data_quality_callable(result)


def test_exact_duplicate_and_empty_batch():
    result = transform_data_callable(pd.DataFrame([row(), row()]))
    assert len(data_quality_callable(result)) == 1
    with pytest.raises(ValueError, match='vide'):
        data_quality_callable(result.iloc[:0])


def test_missing_column():
    with pytest.raises(ValueError, match='absentes'):
        data_quality_callable(pd.DataFrame([row()]).drop(columns=['email']))
