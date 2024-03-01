from shimoku import Client
from typing import Optional


def use_s(shimoku_client: Optional[Client] = None):  # error
    pass


def action(shimoku_client: Client):
    use_s(shimoku_client)
