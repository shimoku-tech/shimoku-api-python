""""""
from os import getenv

import shimoku_api_python as shimoku

api_key: str = getenv('API_TOKEN')
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


# TODO pending https://trello.com/c/CNhYPEDe/
# TODO WiP after the trello card is solved
def test_create_delete_element():
    data = {
        'appBusinessId': '4fba34d2-fc73-4174-bc6e-47389f9dadc4',
        'owner': '4fba34d2-fc73-4174-bc6e-47389f9dadc4',
        'appTypeId': 'test',
        'trialDays': 30,
        '__typename': 'App',
        'hideTitle': True
    }
    result = s.api_client.query_element(
        method='POST',
        element_name=f'{business_id}/app',
        **{'data': data},
    )
    assert result.status_code == 200
    print(result)

    result = s.api_client.query_element(
        method='GET',
        element_name=f'{business_id}/app',
        element_id=app_id,
    )
    assert result.status_code == 200
    print(result)

    result = s.api_client.query_element(
        method='DELETE',
        element_name=f'{business_id}/app',
        element_id=new_app_id,
    )
    assert result.status_code == 200
    print(result)


# test_request()
# test_query_element()
test_create_delete_element()
