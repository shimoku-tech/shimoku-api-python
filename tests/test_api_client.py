""""""
from os import getenv

import shimoku_api_python as shimoku
import asyncio

access_token: str = getenv('API_TOKEN')
base_url: str = getenv('BASE_URL')
universe_id: str = getenv('UNIVERSE_ID')
business_id: str = getenv('BUSINESS_ID')
verbosity: str = getenv('VERBOSITY')
app_id: str = getenv('APP_ID')

s = shimoku.Client(
    access_token=access_token,
    universe_id=universe_id,
    business_id=business_id,
    verbosity=verbosity,
)


def test_request():
    result = asyncio.run(
        s._api_client.request(
            method='GET',
            url=f'{base_url}{business_id}/app/{app_id}/',
        )
    )
    assert result
    print(result)


def test_query_element():
    result = asyncio.run(
        s._api_client.query_element(
            method='GET',
            endpoint=f'business/{business_id}/app/{app_id}',
        )
    )
    assert result
    print(result)


def test_ping():
    is_alive: bool = s.ping()
    assert is_alive


test_request()
test_query_element()
test_ping()
