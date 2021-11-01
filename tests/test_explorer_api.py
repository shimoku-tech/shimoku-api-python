""""""
from os import getenv

import shimoku_api_python as shimoku

api_key: str = getenv('API_TOKEN')
business_id: str = getenv('BUSINESS_ID')
app_id: str = getenv('APP_ID')
base_url: str = getenv('BASE_URL')

config = {
    'access_token': api_key
}

s = shimoku.Client(config)


def test_get_business():
    result = s.explorer.get_business(business_id)
    assert result.status_code == 200
    print(result)


def test_get_app():
    result = s.explorer.get_app(app_id)
    assert result.status_code == 200
    print(result)


def test_get_report(report_id):
    result = s.explorer.get_report(report_id)
    assert result.status_code == 200
    print(result)


test_get_business()
test_get_app()
test_get_report(report_id='')
