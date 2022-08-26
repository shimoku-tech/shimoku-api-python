""""""
from os import getenv

import pandas as pd

import shimoku_api_python as shimoku


api_key: str = getenv('API_TOKEN')
universe_id: str = getenv('UNIVERSE_ID')
business_id: str = getenv('BUSINESS_ID')
environment: str = getenv('ENVIRONMENT')
model_endpoint: str = getenv('MODEL_ENDPOINT')


s = shimoku.Client(
    config={'access_token': api_key},
    universe_id=universe_id,
    environment=environment,
)
s.ai.set_business(business_id)

filename: str = '../data/churn_test.csv'
df_test: pd.DataFrame = pd.read_csv(filename, index_col=0).head(10)
d_fail = {'a': 1, 'b': 2, 'c': 3}
df_test_fail: pd.DataFrame = pd.DataFrame(d_fail, index=[0])


def test_predict_categorical():
    df_pred, df_error = s.ai.predict_categorical(
        df_test=df_test_fail,
        model_endpoint=model_endpoint,
        explain=False,
    )
    assert df_pred.empty
    assert not df_error.empty

    df_pred, df_error = s.ai.predict_categorical(
        df_test=df_test,
        model_endpoint=model_endpoint,
        explain=False,
    )
    assert not df_pred.empty
    assert df_error.empty

    df_pred, df_error = s.ai.predict_categorical(
        df_test=df_test,
        model_endpoint=model_endpoint,
        explain=True,
    )
    assert not df_pred.empty
    assert df_error.empty


def test_predictive_table():
    target_column: str = 'NRO_POL'
    column_to_predict: str = 'churn_probability'
    menu_path: str = 'AI/Churn'
    order: int = 0

    s.ai.predictive_table(
        df_test=df_test,
        model_endpoint=model_endpoint,
        target_column=target_column,
        column_to_predict=column_to_predict,
        menu_path=menu_path,
        order=order,
        explain=True,
        prediction_type='categorical',
        add_filter_by_column_to_predict=False,
        add_search_by_target_column=True,
        extra_filter_columns=None,
        extra_search_columns=None,
    )


test_predict_categorical()
test_predictive_table()
