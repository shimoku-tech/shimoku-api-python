""""""
from os import getenv
from typing import Dict, List

import shimoku_api_python as shimoku
from shimoku_api_python.client import ApiClientError


api_key: str = getenv('API_TOKEN')
universe_id: str = getenv('UNIVERSE_ID')


config = {
    'access_token': api_key,
}

s = shimoku.Client(
    config=config,
    universe_id=universe_id,
    environment='production',
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


test_get_universe_businesses()
test_get_universe_app_types()
