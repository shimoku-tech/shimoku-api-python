""""""
from os import getenv
from typing import Dict, List

from shimoku import Client


api_key: str = getenv("API_TOKEN")
universe_id: str = getenv("UNIVERSE_ID")

config = {
    "access_token": api_key,
}

s = Client(
    config=config,
    universe_id=universe_id,
    verbosity="DEBUG",
)


def test_get_universe_businesses():
    workspaces: List[Dict] = s.universes.get_universe_workspaces(uuid=universe_id)
    assert workspaces


test_get_universe_businesses()
