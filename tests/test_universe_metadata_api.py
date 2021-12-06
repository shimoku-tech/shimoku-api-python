""""""
from os import getenv
from typing import Dict, List

import shimoku_api_python as shimoku
from shimoku_api_python.client import ApiClientError


api_key: str = getenv('API_TOKEN')
universe_id: str = getenv('UNIVERSE_ID')
app_type_id: str = getenv('BUSINESS_ID')


config = {
    'access_token': api_key,
}

s = shimoku.Client(
    config=config,
    universe_id=universe_id,
)


def test_get_universe_businesses():
    businesses: List[Dict] = (
        s.universe.get_universe_businesses()
    )
    assert businesses


def test_get_universe_app_types():
    app_types: List[Dict] = (
        s.universe.get_universe_app_types()
    )
    assert app_types


def test_get_universe_apps_by_type():
    app_types: List[Dict] = (
        s.universe.get_universe_app_types()
    )
    app_types_ids: List[str] = [app_type['id'] for app_type in app_types]

    apps: List[Dict] = (
        s.universe.get_universe_apps_by_type(
            app_type_id=app_type_id,
        )
    )
    assert apps
    assert all([app['appTypeId'] is in app_types_ids for app in apps])


test_get_universe_businesses()
test_get_universe_app_types()
test_get_universe_apps_by_type()
