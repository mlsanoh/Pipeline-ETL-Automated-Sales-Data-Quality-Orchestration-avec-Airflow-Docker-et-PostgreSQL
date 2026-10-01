import pandas as pd
import pytest
from include.transform import transform_data_callable
from include.data_quality import data_quality_callable


def sample_data():
    return pd.DataFrame([{
        'customer_id': 1,
        'name': 'Client',
        'gender': 'male',
        'age': '25 years',
        'city': ' paris ',
        'country': 'France',
        'email': 'test@example.org',
        'purchase_amount': 30,
        'feedback_score': 4,
        'signup_date': '2026-01-01',
        'last_purchase_date': '2026-02-01',
    }])


def test_valid_data():
    result = transform_data_callable(sample_data())
    data_quality_callable(result)
    assert result.loc[0, 'gender'] == 'M'
    assert result.loc[0, 'city'] == 'Paris'
    assert result.loc[0, 'age'] == 25


def test_negative_amount_is_rejected():
    df = sample_data()
    df.loc[0, 'purchase_amount'] = -30
    result = transform_data_callable(df)
    assert result.loc[0, 'purchase_amount'] == -30
    with pytest.raises(ValueError, match="montant d'achat"):
        data_quality_callable(result)


def test_invalid_age_is_rejected():
    df = sample_data()
    df['age'] = '150 years'
    result = transform_data_callable(df)
    assert result.loc[0, 'age'] == 150
    with pytest.raises(ValueError, match='âges'):
        data_quality_callable(result)


def test_missing_amount_is_rejected():
    df = sample_data()
    df['purchase_amount'] = None
    result = transform_data_callable(df)
    with pytest.raises(ValueError, match='purchase_amount'):
        data_quality_callable(result)


def test_missing_customer_id_is_rejected():
    df = sample_data()
    df['customer_id'] = None
    result = transform_data_callable(df)
    assert len(result) == 1
    with pytest.raises(ValueError, match='customer_id'):
        data_quality_callable(result)


def test_non_numeric_age_is_rejected():
    df = sample_data()
    df['age'] = 'incorrect'
    result = transform_data_callable(df)
    with pytest.raises(ValueError, match='âges'):
        data_quality_callable(result)


def test_empty_batch_is_rejected():
    df = sample_data().iloc[:0]
    with pytest.raises(ValueError, match='vide'):
        data_quality_callable(df)
