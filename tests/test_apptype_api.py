""""""
from os import getenv
from typing import Dict, List

import datetime as dt

import shimoku_api_python as shimoku


api_key: str = getenv('API_TOKEN')
universe_id: str = getenv('UNIVERSE_ID')
business_id: str = getenv('BUSINESS_ID')


config = {
    'access_token': api_key,
}

s = shimoku.Client(
    config=config,
    universe_id=universe_id,
)
