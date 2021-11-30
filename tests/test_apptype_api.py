""""""
from os import getenv
from typing import Dict, List

import datetime as dt

import shimoku_api_python as shimoku


api_key: str = getenv('API_TOKEN')
business_id: str = getenv('BUSINESS_ID')
app_id: str = getenv('APP_ID')
report_id: str = getenv('REPORT_ID')


config = {
    'access_token': api_key
}

s = shimoku.Client(config)

