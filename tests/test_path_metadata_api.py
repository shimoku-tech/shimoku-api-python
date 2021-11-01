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


def test_get_app_path_all_reports():
    result = s.path.get_app_path_all_reports(app_id=app_id, path='test')
    print(result)


test_get_app_path_all_reports()
