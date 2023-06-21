""""""
from os import getenv

import shimoku_api_python as shimoku

access_token: str = getenv('API_TOKEN')
universe_id: str = getenv('UNIVERSE_ID')
business_id: str = getenv('BUSINESS_ID')
verbosity: str = getenv('VERBOSITY')

s = shimoku.Client(
    access_token=access_token,
    universe_id=universe_id,
    verbosity=verbosity,
)
s.set_workspace(uuid=business_id)


def test_ping():
    is_alive: bool = s.ping()
    assert is_alive


test_ping()
