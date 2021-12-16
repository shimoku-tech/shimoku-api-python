""""""
import json
from os import getenv
from typing import Dict, List

import datetime as dt

import pandas as pd

import shimoku_api_python as shimoku


api_key: str = getenv('API_TOKEN')
universe_id: str = getenv('UNIVERSE_ID')
business_id: str = getenv('BUSINESS_ID')
app_id: str = getenv('APP_ID')
report_id: str = getenv('REPORT_ID')
report_element: Dict[str, str] = dict(
    business_id=business_id,
    app_id=app_id,
    report_id=report_id
)


config = {
    'access_token': api_key,
}

s = shimoku.Client(
    config=config,
    universe_id=universe_id,
)


# Fixtures
data: Dict = {
    'a': [x for x in range(10)],
    'b': [x ** 2 for x in range(10)],
}
data_oriented: List = pd.DataFrame(data).to_dict(orient='records')
df = pd.DataFrame(data)
data_json: str = json.dumps(data_oriented)


def test_get_report_data():
    data_: List[Dict] = (
        s.data.get_report_data(
            business_id=business_id,
            app_id=app_id,
            report_id=report_id,
        )
    )
    assert data_


def test_update_report_data():
    original_data: List[Dict] = (
        s.data.get_report_data(
            business_id=business_id,
            app_id=app_id,
            report_id=report_id,
        )
    )

    s.data.update_report_data(
        business_id=business_id,
        app_id=app_id,
        report_id=report_id,
        report_data=data,
    )

    new_data: List[Dict] = (
        s.data.get_report_data(
            business_id=business_id,
            app_id=app_id,
            report_id=report_id,
        )
    )

    assert new_data == data_oriented

    # Revert it

    s.data.update_report_data(
        business_id=business_id,
        app_id=app_id,
        report_id=report_id,
        report_data=original_data,
    )

    restored_data: List[Dict] = (
        s.data.get_report_data(
            business_id=business_id,
            app_id=app_id,
            report_id=report_id,
        )
    )

    assert restored_data == original_data


def test_append_report_data():
    original_data: List[Dict] = (
        s.data.get_report_data(
            business_id=business_id,
            app_id=app_id,
            report_id=report_id,
        )
    )

    s.data.append_report_data(
        business_id=business_id,
        app_id=app_id,
        report_id=report_id,
        report_data=data,
    )

    s.data.append_report_data(
        business_id=business_id,
        app_id=app_id,
        report_id=report_id,
        report_data=df,
    )

    s.data.append_report_data(
        business_id=business_id,
        app_id=app_id,
        report_id=report_id,
        report_data=data_json,
    )

    new_data: List[Dict] = (
        s.data.get_report_data(
            business_id=business_id,
            app_id=app_id,
            report_id=report_id,
        )
    )

    assert new_data

    s.data.update_report_data(
        business_id=business_id,
        app_id=app_id,
        report_id=report_id,
        report_data=original_data,
    )

    restored_data: List[Dict] = (
        s.data.get_report_data(
            business_id=business_id,
            app_id=app_id,
            report_id=report_id,
        )
    )

    assert restored_data == original_data


test_get_report_data()
test_update_report_data()
test_append_report_data()
