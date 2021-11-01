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


def test_get_app():
    result = s.app.get_app(app_id)
    print(result)


test_get_app()
