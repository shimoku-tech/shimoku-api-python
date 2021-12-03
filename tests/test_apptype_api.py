""""""
from os import getenv
from typing import Dict, List

import datetime as dt

import shimoku_api_python as shimoku


api_key: str = getenv('API_TOKEN')
universe_id: str = getenv('UNIVERSE_ID')
business_id: str = getenv('BUSINESS_ID')


config = {
    'access_token': api_key,
}

s = shimoku.Client(
    config=config,
    universe_id=universe_id,
)


def test_create_and_delete_app_type():
    name: str = 'test_app_type'
    app_type: Dict = s.app_type.create_app_type(name)
    app_type_id: str = app_type['id']

    assert len(app_type_id) > 0

    app_type_from_db: Dict = (
        s.app_type.get_app_type(
            app_type_id=app_type_id,
        )
    )

    assert app_type_from_db == app_type
    assert app_type['createdAt'] == dt.date.today()
    del app_type_from_db

    result: Dict = (
        s.app_type.delete_app_type(
            app_type_id=app_type_id,
        )
    )

    assert result


test_create_and_delete_app_type()
