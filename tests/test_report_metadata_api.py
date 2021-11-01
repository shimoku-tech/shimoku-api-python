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


def test_get_report():
    result = s.report.get_report(report_id='asdf')
    print(result)


test_get_report()
