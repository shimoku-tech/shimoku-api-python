""""""
from os import getenv

import shimoku_api_python as shimoku

api_key: str = getenv('API_TOKEN')
base_url: str = getenv('BASE_URL')
universe_id: str = getenv('UNIVERSE_ID')
business_id: str = getenv('BUSINESS_ID')
app_id: str = getenv('APP_ID')


config = {
    'access_token': api_key,
}

s = shimoku.Client(
    config=config,
    universe_id=universe_id,
)


def test_request():
    result = s.api_client.request(
        method='GET',
        url=f'{base_url}{business_id}/app/{app_id}/',
    )
    assert result.status_code == 200
    print(result)


def test_query_element():
    result = s.api_client.query_element(
        method='GET',
        element_name=f'{business_id}/app',
        element_id=app_id,
    )
    assert result.status_code == 200
    print(result)


def test_ping():
    is_alive: bool = s.ping()
    assert is_alive


test_request()
test_query_element()
test_ping()
