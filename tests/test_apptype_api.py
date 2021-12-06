""""""
from os import getenv
from typing import Dict, List

import datetime as dt

import shimoku_api_python as shimoku


api_key: str = getenv('API_TOKEN')
universe_id: str = getenv('UNIVERSE_ID')
app_type_id: str = getenv('app_type_id')


config = {
    'access_token': api_key,
}

s = shimoku.Client(
    config=config,
    universe_id=universe_id,
)


def test_get_universe_app_types():
    app_types: List[Dict] = s.app_type.get_universe_app_types()
    assert app_types


def test_get_universe_apps_by_type():
    apps: List[Dict] = (
        s.app_type.get_universe_apps_by_type(
            app_type_id=app_type_id,
        )
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


test_get_universe_app_types()
test_create_and_delete_app_type()

get_app_type = GetExplorerAPI.get_app_type
create_app_type = CreateExplorerAPI.create_app_type
update_app_type = UpdateExplorerAPI.update_app_type

get_universe_app_types = CascadeExplorerAPI.get_universe_app_types
get_apps_by_type = CascadeExplorerAPI.get_apps_by_type

delete_app_type = DeleteExplorerApi.delete_app_type
